from django.shortcuts import render
from shapely.wkb import loads as wkb_loads
from modulos.validacionUbicacion import*
from modulos.BusquedaParadaCercana import*
from modulos.BusquedaRutaCercana import*
from modulos.BusquedaParadasEnUnRadio import*
from modulos.BusquedaRutasEnUnRadio import*
from modulos.Obtener_pos import*
from modulos.convertir_coordenadas import*
from modulos.obtener_info_omnibus import*
from modulos.Crear_ruta_personalizada import*
from django.shortcuts import render
import json
from django.http import JsonResponse


def inicio(request):
 
    return render(request, "menu.html")

def seleccionar_destino(request):
    ubicacion = request.GET["ubicacion"]
    context = {'ubicacion': ubicacion}
    return render(request, 'mapa_ruta_pers.html', context)

def validar_ubicacion(request):
    ubicacion = request.GET["ubicacion"]
    respuesta=validacion_ubicacion(ubicacion)
    respuesta=str(respuesta)
    if respuesta == "True":
        rutas = obtener_omnibus()
        rutas = [ruta[0] for ruta in rutas]
        context = {'ubicacion': ubicacion, 'rutas': rutas}
        return render(request, "seleccionFuncionalidad.html",context)
    elif respuesta == "False":
        return render(request, "menu_falla_fuera_habana.html")
    else:
        return render(request, "menu_falla_datos.html")

def parada_cercana(request):

    cantidad = str(request.GET["cantidad"])
    ubicacion = str(request.GET["ubicacion"])
    try:
        if ("," in cantidad or "." in cantidad):
           cantidad = float(cantidad)
           cantidad = round(cantidad)
        else:
            cantidad = int(cantidad)

        if cantidad > 0:
            resultado=buscar_parada_mas_cercana(ubicacion,cantidad)
            if resultado != -1:
                context= {'resultado': resultado}
                return render(request, "mostrarResultadosParadas.html",context)
            else:
                context = {'ubicacion': ubicacion}
                return render(request, "errorEn1.html",context)
        else:
            context = {'ubicacion': ubicacion}
            return render(request, "errorEn1.html",context)
    except Exception:
        context = {'ubicacion': ubicacion}
        return render(request, "errorEn1.html",context)
    
def ruta_cercana(request):

    cantidad = str(request.GET["cantidad"])
    ubicacion = str(request.GET["ubicacion"])
    try:   
        if ("," in cantidad or "." in cantidad):
           cantidad = float(cantidad)
           cantidad = round(cantidad)
        else:
            cantidad = int(cantidad)
              
        if cantidad > 0:
            resultado=buscar_ruta_mas_cercana(ubicacion,cantidad)
            if resultado != -1:
                context= {'resultado': resultado}
                return render(request, "mostrarResultadosRutas.html",context)
            else:
                context = {'ubicacion': ubicacion}
                return render(request, "errorEn2.html",context)
        else:
            context = {'ubicacion': ubicacion}
            return render(request, "errorEn2.html",context)
    except Exception:
        context = {'ubicacion': ubicacion}
        return render(request, "errorEn2.html",context)

def parada_radio(request):
    
    radio = str(request.GET["radio"])
    ubicacion = str(request.GET["ubicacion"])
    try:
        radio = float(radio)

        if radio > 0:
            resultado=buscar_parada_en_un_radio(ubicacion,radio)
            if resultado != -1:
                context= {'resultado': resultado}
                return render(request, "mostrarResultadosParadas.html",context)
            else:
                context = {'ubicacion': ubicacion}
                return render(request, "errorEn3.html",context)
        else:
            context = {'ubicacion': ubicacion}
            return render(request, "errorEn3.html",context)
    except Exception:
        context = {'ubicacion': ubicacion}
        return render(request, "errorEn3.html",context)

def ruta_radio(request):
    
    radio = str(request.GET["radio"])
    ubicacion = str(request.GET["ubicacion"])
    try:
        radio = float(radio)

        if radio > 0:
            resultado=buscar_rutas_en_un_radio(ubicacion,radio)
            if resultado != -1:
                context= {'resultado': resultado}
                return render(request, "mostrarResultadosRutas.html",context)
            else:
                context = {'ubicacion': ubicacion}
                return render(request, "errorEn4.html",context)
        else:
            context = {'ubicacion': ubicacion}
            return render(request, "errorEn4.html",context)
    except Exception:
        context = {'ubicacion': ubicacion}
        return render(request, "errorEn4.html",context)
    
def obtener_posiciones(request):
    nombre_ruta = request.GET.get("nombre_ruta")

    try:
        if nombre_ruta:
            if(nombre_ruta == "Todas"):
                resultados = obtener_rutas_y_ubicaciones()
            else:
                resultados = obtener_ruta_y_ubicacion(nombre_ruta)

            if resultados:

                respuestas = []
               
                for resultado in resultados:
                    # Transformar las coordenadas obtenidas a un formato que lea el mapa
                    coords = transformar_coordenadas(resultado['coordenadas'])
                    
                    # Obtener el punto random en formato WKT
                    ubicacion_wkt = resultado['ubicacion']

                    # Extraer longitud y latitud del WKT
                    punto_str = ubicacion_wkt.replace('POINT(', '').replace(')', '')
                    long, lat = punto_str.split()

                    respuestas.append({
                        'nombre_ruta': resultado['nombre_ruta'],
                        'placa': resultado['placa'],
                        'long': long,
                        'lat': lat,
                        'coordenadas': coords
                    })

                context = {
                    'respuestas': json.dumps(respuestas)
                }
                return render(request, "mostrar_posiciones.html", context)
            else:
                context = {'error': 'No se encontraron datos para la ruta especificada.'}
                return render(request, "error.html", context)
        else:
            context = {'error': 'No se proporcionó un nombre de ruta válido.'}
            return render(request, "error.html", context)

    except Exception as e:
        context = {'error': f'Error al procesar la solicitud: {str(e)}'}
        return render(request, "error.html", context)


def crear_ruta_personalizada(request):
    if request.method == 'GET':
        # Obtener los datos del GET
        ubicacion_usuario = request.GET.get('ubicacion', None)
        destino = request.GET.get('destino', None)

        if not ubicacion_usuario or not destino:
            return JsonResponse({'mensaje': 'Ubicación o destino no proporcionado'}, status=400)
        
    destino = invertir_coordenadas(destino)
    validacion = str(validacion_ubicacion(ubicacion_usuario))
    if validacion != "True":
        return JsonResponse({'mensaje': 'Ubicacion actual fuera de los limites de La Habana'}, status=400)
        
    else:
        validacion = str(validacion_ubicacion(destino))
        if validacion != "True":
            return JsonResponse({'mensaje': 'Destino seleccionado fuera de los limites de La Habana'}, status=400)  

        ruta_foot, ruta_car, ruta_bus = crear_ruta(ubicacion_usuario, destino)
        #ACUERDATE LO DEL RENDER EN EL SOLO A PIE
        if ruta_bus is None:
            context = {
                'ubicacion': ubicacion_usuario,
                'destino': destino,
                'ruta_foot': json.dumps(ruta_foot),
                'ruta_car': json.dumps(ruta_car)
            }
            return render(request, 'mapa_ruta_pers.html', context)
            
        else:
            context = {
                'ubicacion': ubicacion_usuario,
                'destino': destino,
                'ruta_foot': json.dumps(ruta_foot),
                'ruta_car': json.dumps(ruta_car),
                'ruta_bus': json.dumps(ruta_bus)
            }
            return render(request, 'mapa_ruta_pers.html', context)
        
