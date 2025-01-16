from modulos.Connection import conectar

def buscar_rutas_en_un_radio(ubicacion,radio):

    try:
        result = str(ubicacion)
        result = result.split(",")
        long = result[0]
        lat = result[1]

        connection = conectar()
        cursor = connection.cursor()
        
        consulta = "'SRID=4326;POINT(" + str(long) + " " + str(lat) + ")'::geography"
        cursor.execute("SELECT ST_Distance("+consulta+", geometry::geography), id,itinerario,distancia,recorrido,ruta,sentido,tipo,terminal,origen,destino FROM all_rutas WHERE ST_DWithin("+consulta+", geometry::geography,"+ str(radio) + ") ORDER BY ST_GeomFromText('POINT(' || " + str(long) + " || ' ' || " + str(lat) + " || ')', 4326) <-> geometry;")
        resultados = cursor.fetchall()

        return resultados
            
    except TypeError:
        return -1
    except ValueError:
        return -1
    except Exception:
        return -1