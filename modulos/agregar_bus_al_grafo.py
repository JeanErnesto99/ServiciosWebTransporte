import networkx as nx
from shapely import wkt
from modulos.Grafo import calcular_distancia_fragmento
from modulos.convertir_coordenadas import transformar_coordenadas


def agregar_bus_al_grafo(grafo: nx.Graph, info_bus: list) -> nx.Graph:
    """
    Agrega buses al grafo, asignando nodos y conectándolos según la geometría de las aristas.

    Args:
        grafo (nx.Graph): Grafo al que se agregarán los nodos y aristas.
        info_bus (list): Lista de información de los buses con datos como nombre de ruta, ubicación, coordenadas y placa.

    Returns:
        nx.Graph: Grafo modificado con los buses añadidos.
    """
    G = grafo

    for bus in info_bus:
        nombre_ruta = bus['nombre_ruta']
        ubicacion_punto_wkt = wkt.loads(bus['ubicacion'])
        coordenadas_punto = (ubicacion_punto_wkt.x, ubicacion_punto_wkt.y)
        wkb_data = bus['coordenadas']
        coordinates = transformar_coordenadas(wkb_data)

        # Añadir el nodo del bus al grafo
        bus_id = f"bus_{nombre_ruta}"
        i = 1
        while bus_id in G.nodes:
            bus_id = f"bus{i}_{nombre_ruta}"
            i += 1

        G.add_node(
            bus_id,
            ruta=nombre_ruta,
            pos=coordenadas_punto,
            coordenadas_ruta=coordinates,
            placa=bus['placa']
        )

        # Buscar la arista correspondiente y verificar la geometría
        for u, v, edge_data in G.edges(data=True):
            if edge_data.get('geometria') and edge_data.get('de_ruta') == nombre_ruta:
                if coordenadas_punto in edge_data['geometria']:
                    geometria_arista = edge_data['geometria']
                    distancia_arista = edge_data['distancia']

                    # Convertir la geometría de la arista en una lista de coordenadas
                    recorrido = list(geometria_arista)
                    node_u = tuple(G.nodes[u]['ubicacion_in_grafo'])
                    idx_u = recorrido.index(node_u)
                    idx_nuevo_nodo = recorrido.index(coordenadas_punto)

                    # Obtener los segmentos de geometría
                    segmento_u_nuevo = recorrido[idx_u:idx_nuevo_nodo + 1]
                    distancia_u_nuevo = calcular_distancia_fragmento(segmento_u_nuevo)
                    distancia_nuevo_v = distancia_arista - distancia_u_nuevo

                    # Actualizar las aristas
                    G.add_edge(
                        u, bus_id,
                        ruta=edge_data['de_ruta'],
                        distancia=distancia_u_nuevo,
                        geometria=geometria_arista
                    )
                    G.add_edge(
                        bus_id, v,
                        ruta=edge_data['de_ruta'],
                        distancia=distancia_nuevo_v,
                        geometria=geometria_arista
                    )
                    G.remove_edge(u, v)
                    break

    return G
