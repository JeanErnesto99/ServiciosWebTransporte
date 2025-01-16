import requests # type: ignore
import polyline # type: ignore

def crear_ruta_foot(ubicacion, destino):
    # URL base de la API de OSRM en línea para caminar
    solo_caminar = False
    base_url = "http://router.project-osrm.org/route/v1/foot/"

    # Extraer coordenadas de la ubicación y destino
    lon_ubicacion, lat_ubicacion = ubicacion.split(',')
    lon_ubicacion, lat_ubicacion = float(lon_ubicacion), float(lat_ubicacion)
    lon_destino, lat_destino = destino.split(',')
    lon_destino, lat_destino = float(lon_destino), float(lat_destino)

    coordenadas = f"{lon_ubicacion},{lat_ubicacion};{lon_destino},{lat_destino}"
    url = f"{base_url}{coordenadas}?overview=full"
   
    # Realizar la solicitud HTTP
    respuesta = requests.get(url)
    data = respuesta.json()

    distancia = data['routes'][0]['distance']  # distancia en metros
    if(distancia <= 1000):
        solo_caminar = True
    
    geometria_ruta = data['routes'][0]['geometry']  # geometría de la ruta en formato encoded polyline
    coordenadas_ruta = polyline.decode(geometria_ruta)  # devuelve una lista de tuples (lat, lon)
    multiline_coords = [[[lon, lat] for lat, lon in coordenadas_ruta]]
    geometria_multilinestring = str(multiline_coords)

    resp = {
        'resp': solo_caminar,
        'distancia': distancia,
        'geometria': geometria_multilinestring
    }
    return resp