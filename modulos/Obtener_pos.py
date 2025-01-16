import random
from modulos.Connection import conectar

def obtener_ruta_y_ubicacion(nombre_ruta):
    try:
        connection = conectar()
        cursor = connection.cursor()

        # Obtener todas las rutas y placas que coinciden con el nombre de ruta
        query_car = """
            SELECT ruta, placa 
            FROM all_car 
            WHERE ruta = %s;
        """
        cursor.execute(query_car, (nombre_ruta,))
        datos_car = cursor.fetchall()  # Obtener todos los resultados

        if not datos_car:
            return None  # Si no se encontraron datos para la ruta, retornar None

        resultados = []

        # Obtener la geometría de la ruta desde all_rutas
        query_ruta = """
            SELECT geometry
            FROM all_rutas 
            WHERE ruta = %s;
        """
        cursor.execute(query_ruta, (nombre_ruta,))
        geometry = cursor.fetchone()

        # Dividir la geometría en partes usando ST_Subdivide
        query_subdivide = """
            SELECT ST_Subdivide(geometry, %s) AS geometria_subdividida
            FROM all_rutas
            WHERE ruta = %s;
        """
        max_vertices = 50  # dividir en partes con máximo x vértices
        cursor.execute(query_subdivide, (max_vertices, nombre_ruta))
        partes = cursor.fetchall()

        # Encontrar un punto dentro de cada parte subdividida
        puntos = []
        for parte in partes:
            query_punto = """
                SELECT ST_AsText(ST_PointOnSurface(%s)) AS punto_random;
            """
            cursor.execute(query_punto, (parte[0],))
            punto_random = cursor.fetchone()

            if punto_random and punto_random[0]:
                puntos.append(punto_random[0])

        # Asignar un punto aleatorio no repetido a cada elemento
        for idx, (ruta, placa) in enumerate(datos_car):
            if puntos:  # Asegurarse de que hay puntos disponibles
                punto_asignado = random.choice(puntos)  # Seleccionar un punto aleatorio
                puntos.remove(punto_asignado)  # Remover el punto asignado de la lista
                resultados.append({
                    'nombre_ruta': ruta,
                    'placa': placa,
                    'coordenadas': geometry[0],  # La geometría completa
                    'ubicacion': punto_asignado  # Punto aleatorio asignado sin repetición
                })

        return resultados if resultados else None

    except Exception as e:
        print(f"Error al obtener datos de las rutas: {e}")
        return None
    finally:
        if connection:
            connection.close()


def obtener_rutas_y_ubicaciones():  #todas
    try:
        connection = conectar()
        cursor = connection.cursor()

        # Obtener todas las rutas y placas
        query_car = """
            SELECT ruta, placa 
            FROM all_car;
        """
        cursor.execute(query_car)
        datos_car = cursor.fetchall() 

        if not datos_car:
            return None  

        resultados = []

        # Obtener la geometría de cada ruta 
        query_rutas = """
            SELECT ruta, geometry
            FROM all_rutas;
        """
        cursor.execute(query_rutas)
        datos_rutas = cursor.fetchall()

        for ruta, geometry in datos_rutas:
            # Dividir la geometría en partes usando ST_Subdivide
            query_subdivide = """
                SELECT ST_Subdivide(geometry, %s) AS geometria_subdividida
                FROM all_rutas
                WHERE ruta = %s;
            """
            max_vertices = 50  # dividir en partes con máximo x vértices
            cursor.execute(query_subdivide, (max_vertices, ruta))
            partes = cursor.fetchall()

            # Encontrar un punto dentro de cada parte subdividida
            puntos = []
            for parte in partes:
                query_punto = """
                    SELECT ST_AsText(ST_PointOnSurface(%s)) AS punto_random;
                """
                cursor.execute(query_punto, (parte[0],))
                punto_random = cursor.fetchone()

                if punto_random and punto_random[0]:
                    puntos.append(punto_random[0])

            # Asignar un punto aleatorio no repetido a cada elemento
            for idx, (ruta_car, placa) in enumerate(datos_car):
                if ruta_car == ruta and puntos:  # Asegurarse de que hay puntos disponibles
                    punto_asignado = random.choice(puntos)  # Seleccionar un punto aleatorio
                    puntos.remove(punto_asignado)  # Remover el punto asignado de la lista
                    resultados.append({
                        'nombre_ruta': ruta_car,
                        'placa': placa,
                        'coordenadas': geometry,  # La geometría completa
                        'ubicacion': punto_asignado  # Punto aleatorio asignado 
                    })

        return resultados if resultados else None

    except Exception as e:
        print(f"Error al obtener datos de las rutas: {e}")
        return None
    finally:
        if connection:
            connection.close()
