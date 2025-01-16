from modulos.Connection import conectar
#Este modulo es para rellenar los campos del select del menu de funcionalidades

def obtener_omnibus():
    try:
        connection = conectar()
        cursor = connection.cursor()
        query_car = """
            SELECT DISTINCT ruta 
            FROM all_car 
            ;
        """
        cursor.execute(query_car)
        datos_car = cursor.fetchall()  # Obtener todos los resultados
        return datos_car
    
    except Exception:
        return -1

print(obtener_omnibus)