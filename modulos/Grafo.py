from shapely import wkb
from shapely.geometry import Point
import pickle, psycopg2, requests, binascii, networkx as nx, matplotlib.pyplot as plt, math 


def conectar():
    # Crear conexión
    connection = psycopg2.connect(
        host="localhost",
        database="BaseDataServer",
        user="postgres",
        password="postgres"
    ) 
    return connection

def crear_grafo():
    #Obtener las paradas y los recorridos de la BD
    connection = conectar()
    cursor = connection.cursor()
    query = """
            SELECT ruta, acumulado, distancia, geometry
            FROM all_paradas
        """
    query2 = """
            SELECT ruta, geometry
            FROM all_rutas
        """
    cursor.execute(query)
    paradas = cursor.fetchall()
    cursor.execute(query2)
    recorridos = cursor.fetchall()
    cursor.close()
    connection.close()
    paradas_convertidas = []  # Lista para almacenar las paradas con geometría convertida
    
    for parada in paradas:
        ruta, acumulado, dist, geometry_wkb = parada
        try:
            if geometry_wkb is None:
                print("No se añadio un nodo con geometry None")
                continue
            # Convertir WKB a objeto Point de Shapely
            punto_parada = wkb.loads(geometry_wkb, hex=True)
            
            # Verificar que la conversión fue exitosa
            if punto_parada:
                # Guardar la geometría convertida y la ruta en la lista de paradas convertidas
                paradas_convertidas.append({
                    'ruta': ruta,
                    'acumulado': acumulado, #Valor de la distancia recorrido desde el inicio de la ruta hasta esta parada
                    'distancia': dist, #Valor de la distancia desde la parada anterior hasta esta
                    'geometry': punto_parada  # Objeto Point 
                })
            else:
                print(f"Error: La geometría WKB '{geometry_wkb}' no se pudo convertir a un punto.")
        except Exception as e:
            print(f"Error al convertir WKB a punto: {e}")

    # Inicializar grafo usando NetworkX
    G = nx.Graph()
    p=0 #identificador global de paradas
    # Preparar/añadir paradas y aristas
    recorridos_ok=[]
    paradas_x_ruta = []
    for recorrido in recorridos:
        ruta_recorrido, geometry_wkb = recorrido
        if(ruta_recorrido in recorridos_ok):
            continue
        else:
            recorridos_ok.append(ruta_recorrido)
        recorrido_coords = transformar_coordenadas(geometry_wkb) # Convertir WKB a coordenadas
        for parada in paradas_convertidas:
            if(parada['ruta'] == ruta_recorrido):
                paradas_x_ruta.append(parada)

        if all('acumulado' in parada and parada['acumulado'] is not None for parada in paradas_x_ruta):
            paradas_x_ruta.sort(key=lambda parada: parada['acumulado'])
                   
            ordenada=True
        else:
            ordenada = False
        for parada in paradas_x_ruta:
            G.add_node(f'parada_{p}', ubicacion_in_grafo=parada['geometry'],
                        ruta=parada['ruta'],acumuludo=parada['acumulado'], distancia=['distancia'],
                        geometry=parada['geometry'])
            p += 1

        for i in range(len(paradas_x_ruta) - 1):
            parada_actual = paradas_x_ruta[i]
            parada_siguiente = paradas_x_ruta[i + 1]  # La siguiente parada en la lista
            # Encuentra los puntos más cercanos en recorrido_coords
            x, y, segmento_geom_wkt = obtener_fragmento_de_geometria(
            parada_actual.get('geometry'),
            parada_siguiente.get('geometry'),
            recorrido_coords
            )
            if(ordenada):
                dist= parada_siguiente.get('acumulado') - parada_actual.get('acumulado')
                dist = dist*1000 #Porque en la BD esta en km
            else:
                if(segmento_geom_wkt is not None):
                    dist=calcular_distancia_fragmento(segmento_geom_wkt)
            
            if(segmento_geom_wkt is not None):
                # Obtener los identificadores de los nodos
                nodo_inicio = f'parada_{p - len(paradas_x_ruta) + i}'
                nodo_fin = f'parada_{p - len(paradas_x_ruta) + i + 1}'
                # Actualizar el atributo 'ubicacion_in_grafo' para ambos nodos
                G.nodes[nodo_inicio]['ubicacion_in_grafo'] = x
                G.nodes[nodo_fin]['ubicacion_in_grafo'] = y

                # Añade la arista al grafo
                G.add_edge(nodo_inicio, nodo_fin, 
                        de_ruta=ruta_recorrido,distancia=dist, geometria=segmento_geom_wkt)            
          
        paradas_x_ruta.clear()                    
    guardar_grafo(G, 'grafo.pkl')

    return G
    #mostrar_grafo_grafico(G)
    
def mostrar_grafo_grafico(G):
    # Obtener posiciones de los nodos
    pos = nx.get_node_attributes(G, 'pos')
    
    # Dibujar nodos normales
    nodos_normales = [nodo for nodo in G.nodes() if nodo not in ['ubicacion', 'destino']]
    nx.draw_networkx_nodes(G, pos, nodelist=nodos_normales, node_color='blue', node_size=500)
    
    # Dibujar nodos especiales ('ubicacion' y 'destino') en rojo y más grandes
    nodos_especiales = ['ubicacion', 'destino']
    nx.draw_networkx_nodes(G, pos, nodelist=nodos_especiales, node_color='red', node_size=700)
    
    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=2)
    
    # Dibujar etiquetas de los nodos
    labels = {nodo: nodo for nodo in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=12)
    
    # Dibujar etiquetas de peso en las aristas
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Mostrar grafo
    plt.axis('off')
    plt.show()

def guardar_grafo(grafo, nombre_archivo):
    with open(nombre_archivo, 'wb') as archivo:
        pickle.dump(grafo, archivo)
    print(f"Grafo guardado en {nombre_archivo}.")

def cargar_grafo(nombre_archivo):

    with open(nombre_archivo, 'rb') as archivo:
        grafo = pickle.load(archivo)
    print(f"Grafo cargado desde {nombre_archivo}.")
    return grafo

def transformar_coordenadas(wkb_string):
    # Decodificar la cadena WKB
    wkb_data = binascii.unhexlify(wkb_string)
    # Crear un objeto geometría usando shapely
    geom = wkb.loads(wkb_data)
    # Extraer las coordenadas
    if geom.geom_type == 'MultiLineString':
        coordinates = [list(line.coords) for line in geom.geoms]  # Ajustar para MultiLineString
    elif geom.geom_type == 'LineString':
        coordinates = [list(geom.coords)]
    else:
        raise ValueError("El tipo de geometría no es compatible")
    # Convertir coordenadas de tuplas a listas
    coordinates = [[list(coord) for coord in line] for line in coordinates]
    return coordinates

def distancia_osrm(punto1, punto2):
    # Definir el endpoint de la API de OSRM
    url = f"http://router.project-osrm.org/route/v1/walking/{punto1[0]},{punto1[1]};{punto2[0]},{punto2[1]}?overview=full&geometries=geojson"

    # Hacer la solicitud a la API
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200 and data['routes']:
        # Extraer la distancia en metros
        distancia = data['routes'][0]['distance']
        # Extraer la geometría
        geometria = data['routes'][0]['geometry']
        return distancia, geometria
    else:
        raise ValueError("Error al calcular la distancia usando OSRM")

def obtener_fragmento_de_geometria(punto_inicio, punto_fin, recorrido_coords):
    
    def encontrar_punto_mas_cercano(punto, recorrido_coords):
        min_dist = float('inf')
        punto_cercano = None 
        for i, coordenadas in enumerate(recorrido_coords):
            punto_lista = Point(coordenadas[0], coordenadas[1])
            distancia = punto_lista.distance(punto)
            if distancia < min_dist:
                    min_dist = distancia
                    punto_cercano = coordenadas
        return punto_cercano
    recorrido = recorrido_coords[0]
    x=encontrar_punto_mas_cercano(punto_inicio, recorrido)
    y=encontrar_punto_mas_cercano(punto_fin, recorrido)
    # Encuentra el índice de los puntos cercanos
    idx_inicio = recorrido.index(x)
    idx_fin = recorrido.index(y)

    # Extrae el segmento de la geometría y convierte las coordenadas a tuplas
    segmento_coords = [tuple(coord) for coord in recorrido[idx_inicio:idx_fin+1]]
    if len(segmento_coords) < 2:
        segmento_coords = [tuple(coord) for coord in recorrido[idx_fin:idx_inicio+1]]
        if len(segmento_coords) < 2:
            print(f"Error: El segmento extraído tiene menos de 2 puntos. Segmento: {segmento_coords}")
            return None, None, None
    return x, y, segmento_coords

def calcular_distancia_fragmento(f):
    def haversine(coord1, coord2):
        R = 6371000  # Radio de la Tierra en metros
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convertir las coordenadas de grados a radianes
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Diferencias entre las coordenadas
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Fórmula de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c  # Distancia en metros
    
    # Calcular la distancia total
    distancia_total = 0
    for i in range(len(f) - 1):
        distancia_total += haversine(f[i], f[i + 1])

    return distancia_total