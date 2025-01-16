import requests, pickle, psycopg2, networkx as nx
from geopy.distance import geodesic
from shapely import Point, wkt
from modulos.BusquedaParadasEnUnRadio import*

def calcular_ruta(grafo):

    # Inicializar variables para almacenar la mejor ruta
    mejor_suma_distancia = float('inf') 
    mejor_geometry_u = None
    mejor_geometry_d = None
    mejor_bus = None

    G = grafo
    nodo_destino = 'destino'
    nodo_ubicacion = 'ubicacion'
    rutas_procesadas = set()

    # Obtener los nodos conectados al "destino" y ordenarlos por distancia (de menor a mayor)
    aristas_destino = sorted(G.edges(nodo_destino, data=True), key=lambda x: x[2]['distancia'])
    nodos_conectados_destino = [(nodo, datos) for _, nodo, datos in aristas_destino]
    
    # Obtener los nodos conectados a la "ubicacion" y ordenarlos por distancia (de menor a mayor)
    aristas_ubicacion = sorted(G.edges(nodo_ubicacion, data=True), key=lambda x: x[2]['distancia'])
    nodos_conectados_ubicacion = [(nodo, datos) for _, nodo, datos in aristas_ubicacion]
    

    
    # Encontrar nodos con rutas semejantes
    nodo_semejante_destino = None
    nodo_semejante_ubicacion = None

    for nodo_d, datos_d in nodos_conectados_destino:
        ruta_destino = G.nodes[nodo_d].get('ruta')
        if ruta_destino in rutas_procesadas:
            continue
        rutas_procesadas.add(ruta_destino)

        for nodo_u, datos_u in nodos_conectados_ubicacion:
            ruta_ubicacion = G.nodes[nodo_u].get('ruta')
 
            # Si las rutas coinciden, seleccionar los nodos más cercanos
            if ruta_destino == ruta_ubicacion:
                nodo_semejante_destino = (nodo_d, datos_d)
                nodo_semejante_ubicacion = (nodo_u, datos_u)
                ruta_comun = ruta_destino
                buses_presentes = []
                # Recorrer todos los nodos del grafo
                for nodo, datos in G.nodes(data=True):
                    if 'placa' in datos and datos['ruta'] == ruta_comun:  # Verificar, si el nodo tiene "placa" es un bus y si es de esa ruta
                    # Verificar si el nodo tiene al menos una arista (no es aislado)
                        
                        if len(list(G.edges(nodo))) > 0:
                            # Calcular la distancia euclidiana entre este nodo y la ubicacion
                            distancia = distancia_euclidiana(datos['pos'], G.nodes[nodo_semejante_ubicacion[0]]['ubicacion_in_grafo'])
                            buses_presentes.append((nodo, datos, distancia))
                # encontrar el bus mas cercano a la parada
                if buses_presentes:
                    bus_mas_cercano = min(buses_presentes, key=lambda x: x[2])  # Seleccionar el nodo con menor distancia
                else:
                    bus_mas_cercano = None  # Si no hay buses disponibles
                if(bus_mas_cercano):
                    # Verificar con la API de OSRM
                    distancia_real_u, geometry_u = distancia_osrm(G.nodes['ubicacion'].get('pos'), datos_u['geometria'])
                    if distancia_real_u > 2000:
                        continue
                    distancia_real_d, geometry_d = distancia_osrm(G.nodes['destino'].get('pos'), datos_d['geometria'])
                    if distancia_real_d < 2000:
                        suma_distancias = distancia_real_u + distancia_real_d
                        # Verificar si la nueva suma es menor que la mejor suma registrada
                        if suma_distancias < mejor_suma_distancia:
                            mejor_suma_distancia = suma_distancias
                            mejor_parada_u = G.nodes[nodo_u]
                            mejor_geometry_u = geometry_u
                            mejor_distancia_u = distancia_real_u
                            mejor_parada_d = G.nodes[nodo_d]
                            mejor_geometry_d = geometry_d
                            mejor_distancia_d = distancia_real_d
                            mejor_bus = bus_mas_cercano
                            if mejor_suma_distancia < 1000:
                                break
                if nodo_semejante_ubicacion and nodo_semejante_destino:
                    break
        if mejor_suma_distancia < 1000:
            break
    if mejor_geometry_u and mejor_geometry_d and mejor_bus:
        convertir_point_a_lista(mejor_parada_u)
        convertir_point_a_lista(mejor_parada_d)
        ruta = {
            'tipo':"directa",
            'geometry_u': mejor_geometry_u,
            'distancia_u': mejor_distancia_u,
            'parada_u': mejor_parada_u,
            'bus': mejor_bus,
            'parada_d': mejor_parada_d,
            'geometry_d': mejor_geometry_d,
            'distancia_d': mejor_distancia_d,
        }
        print(mejor_suma_distancia)
        print(ruta)
        return ruta
    else:
        ruta = None
#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
        rutas_procesadas.clear()
        distancia_real_u=float('inf') 
        distancia_real_d=float('inf')
        dist_u_mejor_de_lo_peor=float('inf')
        finish=False
        #mejor_suma_distancia=float('inf') 


        for nodo_d, datos_d in nodos_conectados_destino:
            ruta_destino = G.nodes[nodo_d].get('ruta')
            if ruta_destino in rutas_procesadas:
                continue
            rutas_procesadas.add(ruta_destino)

            # Buscar buses con ruta al destino 
            buses_destino = []
            for nodo, datos in G.nodes(data=True):
                if 'placa' in datos and datos['ruta'] == ruta_destino and len(list(G.edges(nodo))) > 0:
                    distancia = distancia_osrm(datos['pos'], G.nodes[nodo_d]['ubicacion_in_grafo'])
                    buses_destino.append((nodo, datos, distancia))

            # Buscar paradas intermedias con la misma ruta
            if buses_destino:
                distancia_real_d, geometry_d = distancia_osrm(G.nodes['destino'].get('pos'), datos_d['geometria'])
                if distancia_real_d > 2000:
                    continue
                paradas_intermedias = []
                for nodo_parada, datos_parada in G.nodes(data=True):
                    if datos_parada.get('ruta') == ruta_destino and 'placa' not in datos_parada and nodo_parada != nodo_ubicacion and nodo_parada != nodo_destino and nodo_parada not in nodos_conectados_destino and datos_parada not in nodos_conectados_ubicacion:
                        distancia_intermedia = distancia_euclidiana(G.nodes[nodo_parada].get('ubicacion_in_grafo'), G.nodes[nodo_d]['ubicacion_in_grafo'])
                        paradas_intermedias.append((nodo_parada, datos_parada, distancia_intermedia))
            else:
                continue    
            if paradas_intermedias:
                # Ordenar las paradas intermedias por distancia
                paradas_intermedias = sorted(paradas_intermedias, key=lambda x: x[2])
                # Para cada parada intermedia, buscar las paradas cercanas en un radio de 50 metros
                for parada_intermedia in paradas_intermedias:
                    ubicacion = parada_intermedia[1]['ubicacion_in_grafo']
                    # Si es un objeto POINT
                    if isinstance(ubicacion, Point):
                        long = str(ubicacion.x)
                        lat = str(ubicacion.y)
                    # Si es una lista con coordenadas
                    elif isinstance(ubicacion, list) and len(ubicacion) == 2:
                        long = str(ubicacion[0])
                        lat = str(ubicacion[1])
                    else:
                        raise ValueError("Formato de 'ubicacion_in_grafo' no reconocido.")
                    punto = long + "," + lat
                    radio = float(100)
                    paradas_in_radio = buscar_parada_en_un_radio(punto, radio)
                    if(paradas_in_radio is None):
                        continue
                    # Verificar coincidencias de ruta con paradas cercanas a la ubicación
                    for nodo_u, datos_u in nodos_conectados_ubicacion:
                        ruta_ubicacion = G.nodes[nodo_u].get('ruta')
                        
                        for parada_radio in paradas_in_radio:
                            if parada_radio[2] == ruta_ubicacion:  # Coincidencia de rutas
                                buses_ubicacion = []
                                for nodo, datos in G.nodes(data=True):
                                    if 'placa' in datos and datos['ruta'] == ruta_ubicacion and len(list(G.edges(nodo))) > 0:
                                        distancia = distancia_euclidiana(datos['pos'], G.nodes[nodo_u]['ubicacion_in_grafo'])
                                        buses_ubicacion.append((nodo, datos, distancia))
                                if buses_ubicacion: 
                                    buses_intermedio=[]
                                    for bus in buses_destino:
                                        distancia_bus = distancia_euclidiana(bus[1]['pos'], parada_intermedia[1]['ubicacion_in_grafo'])
                                        buses_intermedio.append((bus[0], bus[1], distancia_bus))
                                
                                    # Ordenar los buses según la distancia a la parada intermedia
                                    buses_intermedio = sorted(buses_intermedio, key=lambda x: x[2])
                                    buses_ubicacion = sorted(buses_ubicacion, key=lambda x: x[2])
                                    
                                    # Almacenar el bus más cercano a la ubicacion y al intermedio para el destino
                                    mejor_bus_intermedio = buses_intermedio[0] if buses_intermedio else None
                                    mejor_bus_ubicacion = buses_ubicacion[0] if buses_ubicacion else None
                                    
                                    # Calcular la distancia usando OSRM
                                    distancia_real_u, geometry_u = distancia_osrm(G.nodes['ubicacion'].get('pos'), datos_u['geometria'])
                                    if(distancia_real_u > 2000):
                                        if(dist_u_mejor_de_lo_peor > distancia_real_u):
                                            dist_u_mejor_de_lo_peor = distancia_real_u
                                            geom_u_mejor_de_lo_peor = geometry_u
                                            dist_d_mejor_de_lo_peor = distancia_real_d
                                            geom_d_mejor_de_lo_peor = geometry_d
                                            iden_u_mejor_de_lo_peor = nodo_u
                                            iden_d_mejor_de_lo_peor = nodo_d
                                            intermedia_mejor_de_lo_peor = parada_intermedia
                                            del_radio_mejor_de_lo_peor= parada_radio

                                    else:
                                        # Aplicar las conversiones necesarias antes de mandarlos
                                        parada_radio=parada_radio[10]
                                        punto_parada_radio = wkt.loads(parada_radio)
                                        parada_radio = (punto_parada_radio.x, punto_parada_radio.y)
                                        distancia_real_i, geometry_i = distancia_osrm(parada_intermedia[1]['ubicacion_in_grafo'], parada_radio)
                                        parada_intermedia = parada_intermedia[1]
                                        parada_u = G.nodes[nodo_u]
                                        parada_d = G.nodes[nodo_d]
                                        convertir_point_a_lista(parada_intermedia)
                                        convertir_point_a_lista(parada_u)
                                        convertir_point_a_lista(parada_d)
                                        finish=True
                                        rutacomb = {
                                            'tipo':"combinada",
                                            'distancia_u': distancia_real_u,
                                            'geometry_u': geometry_u,
                                            'parada_u': parada_u,
                                            'parada_intermedia': parada_intermedia,
                                            'distancia_real_intermedio':distancia_real_i,
                                            'geometry_i': geometry_i,
                                            'parada_del_radio': parada_radio,
                                            'parada_d': parada_d,
                                            'distancia_d': distancia_real_d,
                                            'geometry_d': geometry_d,
                                            'buses': [mejor_bus_intermedio, mejor_bus_ubicacion]
                                        }
                                        print(rutacomb)
                                        return rutacomb  # Ruta combinada encontrada
        if(finish is False):
            try:
                # Aplicar las conversiones necesarias antes de mandarlos
                print(del_radio_mejor_de_lo_peor)
                del_radio = del_radio_mejor_de_lo_peor[10]
                del_radio = wkt.loads(del_radio)
                del_radio_mejor_de_lo_peor = (del_radio.x, del_radio.y)
                distancia_real_i, geometry_i = distancia_osrm(intermedia_mejor_de_lo_peor[1]['ubicacion_in_grafo'], del_radio_mejor_de_lo_peor)
                intermedia_mejor_de_lo_peor=intermedia_mejor_de_lo_peor[1]
                parada_u_mejor_de_lo_peor = G.nodes[iden_u_mejor_de_lo_peor]
                parada_d_mejor_de_lo_peor = G.nodes[iden_d_mejor_de_lo_peor]
                convertir_point_a_lista(intermedia_mejor_de_lo_peor)
                convertir_point_a_lista(parada_u_mejor_de_lo_peor)
                convertir_point_a_lista(parada_d_mejor_de_lo_peor)
            
                rutacomb = {
                    'tipo':"combinada",
                    'distancia_u': dist_u_mejor_de_lo_peor,
                    'geometria_u': geom_u_mejor_de_lo_peor,
                    'parada_u': parada_u_mejor_de_lo_peor,
                    'parada_intermedia': intermedia_mejor_de_lo_peor,
                    'distancia_real_intermedio':distancia_real_i,
                    'geometry_i': geometry_i,
                    'parada_del_radio': del_radio_mejor_de_lo_peor,
                    'parada_d': parada_d_mejor_de_lo_peor,
                    'distancia_d': dist_d_mejor_de_lo_peor,
                    'geometry_d': geom_d_mejor_de_lo_peor,
                    'buses': [mejor_bus_intermedio, mejor_bus_ubicacion]
                }
                print(rutacomb)
                return rutacomb
            except Exception as e:
                print(f"No es posible establecer una ruta: {e}")
            return None

def convertir_point_a_lista(nodo):
    # Recorre los atributos del nodo y transforma los valores tipo POINT
    for key, value in nodo.items():
        if isinstance(value, Point):
            # Transforma el POINT a una lista de [longitud, latitud]
            nodo[key] = [value.x, value.y]

def distancia_osrm(punto1, punto2):
     # Asegúrate de que ambos puntos son tuplas de coordenadas (lat, long)
    if isinstance(punto1, Point):
        punto1 = (punto1.x, punto1.y)  # Extraer latitud y longitud del objeto Point
    if isinstance(punto2, Point):
        punto2 = (punto2.x, punto2.y)  # Extraer latitud y longitud del objeto Point
    # Definir el endpoint de la API de OSRM
    url = f"http://router.project-osrm.org/route/v1/foot/{punto1[0]},{punto1[1]};{punto2[0]},{punto2[1]}?overview=full&geometries=geojson"

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

def distancia_euclidiana(punto1, punto2):
     # Asegúrate de que ambos puntos son tuplas de coordenadas (lat, long)
    if isinstance(punto1, Point):
        punto1 = (punto1.y, punto1.x)  # Extraer latitud y longitud del objeto Point
    if isinstance(punto2, Point):
        punto2 = (punto2.y, punto2.x)  # Extraer latitud y longitud del objeto Point
    print(punto1)
    print(punto2)
    return geodesic(punto1, punto2).meters
  
"""
    
def conectar():
# Crear conexión
    connection = psycopg2.connect(
        host="localhost",
        database="BaseDataServer",
        user="postgres",
        password="postgres"
    ) 
    return connection

def cargar_grafo(nombre_archivo):

    with open(nombre_archivo, 'rb') as archivo:
        grafo = pickle.load(archivo)
    print(f"Grafo cargado desde {nombre_archivo}.")
    return grafo

def buscar_parada_en_un_radio(ubicacion,radio):

    try:
        if radio > 0:
            radio = float(radio)
            result = str(ubicacion)
            result = result.split(",")
            long = result[0]
            lat = result[1]

            connection = conectar()
            cursor = connection.cursor()

            consulta = "'SRID=4326;POINT(" + str(long) + " " + str(lat) + ")'::geography"
            cursor.execute("SELECT ST_Distance("+consulta+", geometry::geography), direccion, ruta, tipo, nº, nombre_par, acumulado, distancia, nombre, orden FROM all_paradas WHERE ST_DWithin("+consulta+", geometry::geography,"+ str(radio) + ") ORDER BY ST_GeomFromText('POINT(' || " + str(long) + " || ' ' || " + str(lat) + " || ')', 4326) <-> geometry;")
            resultados = cursor.fetchall()

            return resultados
            
    except TypeError:
        return -1
    except ValueError:
        return -1
    except Exception:
        return -1

grafo = cargar_grafo("grafocojone.pkl")
calcular_ruta(grafo)
"""