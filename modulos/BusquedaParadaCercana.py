from modulos.Connection import conectar

def buscar_parada_mas_cercana(ubicacion,cantidad):

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
                direccion, ruta, tipo, nº, nombre_par, 
                acumulado, distancia, nombre, orden 
            FROM all_paradas 
            ORDER BY ST_GeomFromText(%s, 4326) <-> geometry 
            LIMIT %s;
        """
        cursor.execute(query, (consulta, f'POINT({long} {lat})', cantidad))
        resultados = cursor.fetchall()

        total_paradas = len(resultados)

        if cantidad > total_paradas:
            cantidad = total_paradas

        # Cerrar la conexión
        cursor.close()
        connection.close()

        return resultados[:cantidad]
            
    except TypeError:
        return -1
    except ValueError:
        return -1
    except Exception:
        return -1

def buscar_paradas_cercanas_por_distancia(ubicacion, distancia):

    try:
        # Extraer longitud y latitud de la ubicación proporcionada
        result = str(ubicacion)
        result = result.split(",")
        long = result[0]
        lat = result[1]

        # Conectar a la base de datos
        connection = conectar()
        cursor = connection.cursor()

        # Consulta SQL para obtener las paradas dentro de la distancia especificada
        query = """
            SELECT 
                ST_Distance(geometry::geography, ST_SetSRID(ST_Point(%s, %s), 4326)::geography) AS distancia,
                ruta, geometry
            FROM all_paradas
            WHERE ST_DWithin(
                geometry::geography, 
                ST_SetSRID(ST_Point(%s, %s), 4326)::geography, 
                %s
            )
            ORDER BY distancia;
        """

        # Ejecutar la consulta con los parámetros
        cursor.execute(query, (long, lat, long, lat, distancia))
        resultados = cursor.fetchall()

        # Cerrar la conexión
        cursor.close()
        connection.close()

        # Procesar resultados para combinar paradas cercanas
        paradas_filtradas = []
        if resultados:
            for i in range(len(resultados)):
                distancia_actual = resultados[i][0]
                ruta_actual = resultados[i][1]
                geometry_actual = resultados[i][2]

                # Comprobar si la parada actual está suficientemente cerca de alguna parada ya filtrada
                combinada = False
                for parada in paradas_filtradas:
                    diferencia_distancia = distancia_actual - parada['distancia']

                    # Si la diferencia es menor o igual a x metros
                    if diferencia_distancia <= 5:
                        if ruta_actual not in parada['ruta'].split(", "):
                            parada['ruta'] += f", {ruta_actual}"
                        combinada = True
                        break

                if not combinada:
                    # Añadir nueva parada al listado si no se combinó con ninguna existente
                    paradas_filtradas.append({
                        'ruta': ruta_actual,
                        'geometry': geometry_actual,
                        'distancia': distancia_actual
                    })

        # Eliminar el campo 'distancia' antes de devolver los resultados
        for parada in paradas_filtradas:
            del parada['distancia']

        return paradas_filtradas

    except TypeError:
        return -1
    except ValueError:
        return -1
    except Exception:
        return -1