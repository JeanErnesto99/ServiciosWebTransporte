import binascii
from shapely import wkb

def transformar_coordenadas(wkb_string):
    # Decodificar la cadena WKB
    wkb_data = binascii.unhexlify(wkb_string)
    
    # Crear un objeto geometría usando shapely
    geom = wkb.loads(wkb_data)
    
    # Extraer las coordenadas
    if geom.geom_type == 'MultiLineString':
        coordinates = [list(line.coords) for line in geom.geoms]
    elif geom.geom_type == 'LineString':
        coordinates = [list(geom.coords)]
    else:
        raise ValueError("El tipo de geometría no es compatible")
    
    # Convertir coordenadas de tuplas a listas
    coordinates = [[list(coord) for coord in line] for line in coordinates]
    
    return coordinates