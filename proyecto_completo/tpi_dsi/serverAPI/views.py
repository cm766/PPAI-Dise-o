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
        gps = gestor.ubicaciones.get(bolsin_dict['numeroBolsin'])
        if gps:
            bolsin_dict['latitud'] = gps['latitud']
            bolsin_dict['longitud'] = gps['longitud']
            bolsin_dict['ultimaActualizacion'] = gps['ultima_actualizacion']
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
        resultado = gestor.notificarUbicacionDelBolsin(
            numero,
            data.get('lat', 0.0),
            data.get('lng', 0.0),
            data.get('fecha', 'N/A'),
        )

        if resultado is None:
            return Response({'status': 'error', 'message': 'No encontrado'}, status=404)

        return Response(resultado, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)