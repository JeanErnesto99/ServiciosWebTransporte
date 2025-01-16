from geopy.distance import geodesic
import networkx as nx


def agregar_ubi_y_dest(
    grafo: nx.Graph, ubicacion: str, destino: str
) -> nx.Graph:
    """
    Agrega nodos de ubicación y destino al grafo, conectándolos con paradas cercanas.

    Args:
        grafo (nx.Graph): Grafo al que se agregarán los nodos.
        ubicacion (str): Coordenadas de la ubicación en formato "lon,lat".
        destino (str): Coordenadas del destino en formato "lon,lat".

    Returns:
        nx.Graph: Grafo modificado con los nodos de ubicación y destino añadidos.
    """
    G = grafo
    ubicacion_coords = tuple(map(float, ubicacion.split(',')))
    destino_coords = tuple(map(float, destino.split(',')))

    # Añadir nodos de ubicación y destino
    G.add_node('ubicacion', pos=ubicacion_coords)
    G.add_node('destino', pos=destino_coords)

    # Conectar destino con paradas cercanas
    _conectar_paradas_cercanas(G, 'destino', destino_coords)

    # Conectar ubicación con paradas cercanas
    _conectar_paradas_cercanas(G, 'ubicacion', ubicacion_coords)

    return G


def _conectar_paradas_cercanas(
    grafo: nx.Graph, nodo: str, coordenadas: tuple
) -> None:
    """
    Conecta un nodo a paradas cercanas en el grafo.

    Args:
        grafo (nx.Graph): Grafo en el que se realizarán las conexiones.
        nodo (str): Nodo a conectar con las paradas cercanas.
        coordenadas (tuple): Coordenadas del nodo a conectar.
    """
    distancia_min = 1000
    while True:
        cont = 0
        for nodo_grafo, datos in grafo.nodes(data=True):
            if 'geometry' in datos:
                distancia_eucl = distancia_euclidiana(
                    coordenadas, datos['geometry'].coords[0]
                )
                if distancia_eucl < distancia_min:
                    cont += 1
                    grafo.add_edge(
                        nodo,
                        nodo_grafo,
                        distancia=distancia_eucl,
                        geometria=datos['geometry'].coords[0]
                    )
        if cont == 0:
            distancia_min += 500
        else:
            break


def distancia_euclidiana(punto1: tuple, punto2: tuple) -> float:
    """
    Calcula la distancia geodésica en metros entre dos puntos.

    Args:
        punto1 (tuple): Coordenadas del primer punto (lon, lat).
        punto2 (tuple): Coordenadas del segundo punto (lon, lat).

    Returns:
        float: Distancia en metros.
    """
    return geodesic(punto1, punto2).meters
