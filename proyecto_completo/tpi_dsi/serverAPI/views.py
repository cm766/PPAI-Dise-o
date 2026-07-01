from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UsuarioSerializer, BolsinSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .models import * 
from .servicio.XTR4500LTracker import XTR4500LTracker
from .servicio.googleMap import GoogleMap
from django.contrib.auth import authenticate


@api_view(['POST'])
def login(request):
    
    username = request.data.get("username")
    password = request.data.get("password")

    #Autenticación del usuario
    user_auth = authenticate(username=username, password=password)

    if user_auth is None:
        return Response(
            {"message": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Creacion de token Token
    token, created = Token.objects.get_or_create(user=user_auth)

    # Obtener tu modelo Usuario
    usuario = get_object_or_404(Usuario, user=user_auth)

    #para que solo tenga una solo sesion
    Sesion.objects.filter(usuario=usuario).delete()  
    sesion_actual = Sesion.objects.create(usuario=usuario)

    serializer = UsuarioSerializer(usuario)
    
    return Response({
        "token": token.key,
        "user": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    # Eliminar el token del usuario
    if request.user.is_authenticated:
        request.user.auth_token.delete()


    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def nuevaBusquedaBolsin(request):
    
    cm_nombre = buscarCMUsuarioLog(request.user)
    
    bolsines_enviados = buscarBolsinesEnviados(cm_nombre)

    gps_data = {}

    for bolsin in bolsines_enviados:
        try:
            tracker = XTR4500LTracker("KEY_XTR_123")
            datos_gps = tracker.obtener_ubicacion(bolsin.getNumeroBolsin())
            
            gps_data[bolsin.getNumeroBolsin()] = {
                'latitud': datos_gps['latitud'],
                'longitud': datos_gps['longitud'],
                'ultimaActualizacion': datos_gps['ultima_actualizacion']
            }
        except Exception as e:
            print(f"Error al obtener GPS: {e}")
            continue

    serializer = BolsinSerializer(bolsines_enviados, many=True)
    lista_bolsines_con_gps = []
    for bolsin_dict in serializer.data:
        num = bolsin_dict['numeroBolsin']
        if num in gps_data:
            bolsin_dict.update(gps_data[num])
        
        lista_bolsines_con_gps.append(bolsin_dict)

    servidorMapa = GoogleMap()
    mapa = servidorMapa.getMapa()

    return Response({
        'cm': cm_nombre,
        'bolsines_enviados': lista_bolsines_con_gps,
        'mapa' : mapa,
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def buscarEmailGCM(request):
    try:
        data = request.data
        numero = data.get('numero')
        lat = data.get('lat', 0.0)
        lng = data.get('lng', 0.0)
        fecha = data.get('fecha', 'N/A')
        if not numero:
            return Response({'status': 'error', 'message': 'Falta número'}, status=400)

        bolsin_principal = Bolsin.objects.filter(numeroBolsin=numero).first()
        if not bolsin_principal:
            return Response({'status': 'error', 'message': 'No encontrado'}, status=404)
        cm_destino = bolsin_principal.getCMDestino()
        emails = [emp.getEmail() for emp in Empleado.objects.filter(asignadoA=cm_destino) if emp.sosGerenteCM()]
        email_final = emails[0] if emails else 'sin@email.com'

        return llamarCUNotificarUbicacionDelBolsin(
            email_final, 
            numero, 
            data.get('lat', 0.0), 
            data.get('lng', 0.0), 
            data.get('fecha', 'N/A')
        )

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

def llamarCUNotificarUbicacionDelBolsin(email, numero, lat, lng, fecha):
    
    return Response({
        'status': 'success',
        'message': 'Notificación enviada correctamente',
    
        'emailGcm': email,
        'numeroBolsin': numero, 
        'coordenadas': {'lat': float(lat), 'lng': float(lng)}, 
        'fechaHora': fecha
    }, status=status.HTTP_200_OK)


def buscarBolsinesEnviados(cm_nombre):
    return [
            b for b in Bolsin.objects.all() 
            if b.sosEnviado() and b.esTuCMOrigen(cm_nombre)
        ]

def buscarCMUsuarioLog(usuario_autenticado):
    sesion_activa = Sesion.objects.filter(usuario__user=usuario_autenticado).latest('id') 
    usuario = sesion_activa.usuario 
    return usuario.obtenerEmpleado().getCM().getNombre()