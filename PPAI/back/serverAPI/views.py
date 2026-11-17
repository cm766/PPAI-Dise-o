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
from .gestor.gestor_buscar_bolsin import GestorBuscarBolsin
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
    gestor = GestorBuscarBolsin(request.user)
    gestor.nuevaBusquedaBolsin()

    lista = []
    for bolsin_dict in BolsinSerializer(gestor.bolsines_enviados, many=True).data:
        ubicacion = gestor.ubicaciones.get(bolsin_dict['numeroBolsin'])
        if ubicacion is not None:
            bolsin_dict['latitud'] = ubicacion.latitud
            bolsin_dict['longitud'] = ubicacion.longitud
            bolsin_dict['ultimaActualizacion'] = ubicacion.ultima_actualizacion.isoformat()
            bolsin_dict['ubicacionDisponible'] = True
        else:
            # A3: el GPS Tracker no pudo informar la ubicación
            bolsin_dict['ubicacionDisponible'] = False
        lista.append(dict(bolsin_dict))

    return Response({
        'cm': gestor.cm_origen,
        'bolsines_enviados': lista,
        'mapa': gestor.mapa,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def buscarEmailGCM(request):
    try:
        data = request.data
        numero = data.get('numero')
        if not numero:
            return Response({'status': 'error', 'message': 'Falta número'}, status=400)

        gestor = GestorBuscarBolsin(request.user)
        if gestor.tomarSeleccionBolsin(numero) is None:
            return Response({'status': 'error', 'message': 'No encontrado'}, status=404)

        resultado = gestor.tomarConfEnvioCorreo(
            data.get('confirmacion', True),
            data.get('lat', 0.0),
            data.get('lng', 0.0),
            data.get('fecha', 'N/A'),
        )

        if resultado is None:
            # A5: el EB no confirmó el envío del correo
            return Response({'status': 'cancelado', 'message': 'No se envió el correo'}, status=200)

        return Response(resultado, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)