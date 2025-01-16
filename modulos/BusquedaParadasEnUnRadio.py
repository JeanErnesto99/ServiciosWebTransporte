from modulos.Connection import conectar

def buscar_parada_en_un_radio(ubicacion, radio):
    try:
        if radio > 0:
            result = str(ubicacion)
            result = result.split(",")
            long = result[0]
            lat = result[1]

            connection = conectar()
            cursor = connection.cursor()

            consulta = "'SRID=4326;POINT(" + str(long) + " " + str(lat) + ")'::geography"
            cursor.execute("""
                SELECT 
                    ST_Distance({0}, geometry::geography), 
                    direccion, 
                    ruta, 
                    tipo, 
                    nº, 
                    nombre_par, 
                    acumulado, 
                    distancia, 
                    nombre, 
                    orden,
                    ST_AsText(geometry)  -- Devuelve el valor de la columna geometry como texto
                FROM all_paradas 
                WHERE ST_DWithin({0}, geometry::geography, {1})
                ORDER BY ST_GeomFromText('POINT(' || {2} || ' ' || {3} || ')', 4326) <-> geometry;
            """.format(consulta, str(radio), str(long), str(lat)))

            resultados = cursor.fetchall()
            return resultados
    except Exception as e:
        print("Error:", e)


     