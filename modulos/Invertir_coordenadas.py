def invertir_coordenadas(coordenadas):
    # Dividir las coordenadas en latitud y longitud
    latitud, longitud = coordenadas.split(',')
    
    # Invertir el orden
    return f"{longitud},{latitud}"