from modulos.Connection import conectar
from modulos.Invertir_coordenadas import invertir_coordenadas
from modulos.validacionUbicacion import validacion_ubicacion
from modulos.Crear_ruta_foot import*
from modulos.Crear_ruta_car import*
from modulos.Grafo import*
from modulos.agregar_bus_al_grafo import*
from modulos.calcular_ruta import*
from modulos.Obtener_pos import obtener_rutas_y_ubicaciones
from modulos.agregar_ubic_y_dest import*


def crear_ruta(ubicacion, destino):

    #Verificar si ir caminando es la mejor opcion    
    ruta_foot = crear_ruta_foot(ubicacion, destino)
    ruta_car = crear_ruta_car(ubicacion, destino)
    ruta_bus = None

    if(ruta_foot['resp'] is False):       #Si esta demasiado cerca, no tiene sentido crear ruta de omnibus
        grafo = cargar_grafo("grafo.pkl")
        
        info_bus = obtener_rutas_y_ubicaciones()
        
        grafo = agregar_bus_al_grafo(grafo, info_bus)
    
        grafo = agregar_ubi_y_dest(grafo, ubicacion, destino)
    
        ruta_bus = calcular_ruta(grafo)
          
    return ruta_foot, ruta_car, ruta_bus
