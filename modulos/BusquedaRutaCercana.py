from modulos.Connection import conectar

def buscar_ruta_mas_cercana(ubicacion,cantidad):

    try:
        result = str(ubicacion)
        result = result.split(",")
        long = result[0]
        lat = result[1]

        connection = conectar()
        cursor = connection.cursor()

        consulta = f"SRID=4326;POINT({long} {lat})"
        query = """
            SELECT 
                ST_Distance(%s::geography, geometry::geography) AS distance, 
                id, itinerario, distancia, recorrido, ruta, sentido, tipo, 
                terminal, origen, destino 
            FROM all_rutas 
            ORDER BY ST_GeomFromText(%s, 4326) <-> geometry 
            LIMIT %s;
        """
        cursor.execute(query, (consulta, f'POINT({long} {lat})', cantidad))
        resultados = cursor.fetchall()

        total_paradas = len(resultados)

        if cantidad > total_paradas:
            cantidad = total_paradas

        return resultados[:cantidad]
            
    except TypeError:
        return -1
    except ValueError:
        return -1
    except Exception:
        return -1



  