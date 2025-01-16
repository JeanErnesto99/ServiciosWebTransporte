import psycopg2

def conectar():
    #Crear conexion
    connection = psycopg2.connect(
    host="localhost",
    database="BaseDataServer",
    user="postgres",
    password="postgres"
    ) 
    return connection