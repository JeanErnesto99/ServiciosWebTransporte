import geopandas as gpd # type: ignore
import os
from shapely.geometry import Point

def validacion_ubicacion(ubicacion):
    try:
        result = str(ubicacion)
        result = result.split(",")
        long = float(result[0])
        lat = float(result[1])
        punto = Point(long,lat)
        ruta_script = os.path.abspath(__file__)  # Ruta absoluta del script en ejecución
        urlProyecto = os.path.dirname(ruta_script)  # Directorio del script
        urlShapeFile = os.path.join(urlProyecto, "shp\\La Habana (Provincia).shp")
        gdfShapeFile = gpd.read_file(urlShapeFile)
        gdfUbicacion = gpd.GeoDataFrame(geometry=[punto])
        
        # Asegurar que ambos GeoDataFrames tengan el mismo CRS
        if gdfUbicacion.crs is None:
            gdfUbicacion.crs = gdfShapeFile.crs
        else:
            gdfUbicacion = gdfUbicacion.to_crs(gdfShapeFile.crs)
            
        resultado = gdfUbicacion.within(gdfShapeFile)
        if resultado.iloc[0] == True:
            return resultado.iloc[0]
        else:
            resultado = gdfUbicacion.intersects(gdfShapeFile)
    except Exception:
        return "Error en la ubicacion proporcionada"
    return resultado.iloc[0]
   
        