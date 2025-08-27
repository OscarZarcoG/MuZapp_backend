from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Pais, Estado, Municipio, Colonia
from .serializers import (
    PaisSerializer, EstadoSerializer, MunicipioSerializer, 
    ColoniaSerializer, ColoniaDetailSerializer
)


class ColoniaListView(generics.ListAPIView):
    """Vista para listar todas las colonias con filtros"""
    queryset = Colonia.objects.select_related('municipio__estado__pais').all()
    serializer_class = ColoniaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['codigo_postal', 'ciudad', 'municipio', 'asentamiento']
    search_fields = ['nombre', 'ciudad', 'municipio__nombre', 'municipio__estado__nombre']
    ordering_fields = ['nombre', 'codigo_postal', 'ciudad']
    ordering = ['nombre']


class ColoniaDetailView(generics.RetrieveAPIView):
    """Vista para obtener detalles de una colonia específica"""
    queryset = Colonia.objects.select_related('municipio__estado__pais').all()
    serializer_class = ColoniaDetailSerializer


@api_view(['GET'])
def buscar_por_codigo_postal(request, codigo_postal):
    """
    Endpoint específico para buscar información completa por código postal.
    Retorna todas las colonias que coincidan con el código postal dado.
    """
    try:
        # Convertir a entero para la búsqueda
        cp = int(codigo_postal)
        
        # Buscar todas las colonias con ese código postal
        colonias = Colonia.objects.select_related(
            'municipio__estado__pais'
        ).filter(codigo_postal=cp)
        
        if not colonias.exists():
            return Response({
                'error': 'No se encontraron colonias con el código postal proporcionado',
                'codigo_postal': codigo_postal
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Serializar los datos
        serializer = ColoniaSerializer(colonias, many=True)
        
        # Estructura de respuesta organizada
        response_data = {
            'codigo_postal': codigo_postal,
            'total_colonias': colonias.count(),
            'colonias': serializer.data
        }
        
        # Si solo hay una colonia, agregar información adicional
        if colonias.count() == 1:
            colonia = colonias.first()
            response_data['informacion_completa'] = {
                'colonia': colonia.nombre,
                'ciudad': colonia.ciudad,
                'municipio': colonia.municipio.nombre if colonia.municipio else None,
                'estado': colonia.municipio.estado.nombre if colonia.municipio else None,
                'pais': colonia.municipio.estado.pais.nombre if colonia.municipio else None,
                'asentamiento': colonia.asentamiento
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response({
            'error': 'El código postal debe ser un número válido',
            'codigo_postal': codigo_postal
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def buscar_colonias_por_municipio(request, municipio_id):
    """
    Endpoint para buscar todas las colonias de un municipio específico
    """
    try:
        colonias = Colonia.objects.select_related(
            'municipio__estado__pais'
        ).filter(municipio_id=municipio_id)
        
        if not colonias.exists():
            return Response({
                'error': 'No se encontraron colonias para el municipio especificado',
                'municipio_id': municipio_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ColoniaSerializer(colonias, many=True)
        
        return Response({
            'municipio_id': municipio_id,
            'total_colonias': colonias.count(),
            'colonias': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EstadoListView(generics.ListAPIView):
    """Vista para listar todos los estados"""
    queryset = Estado.objects.select_related('pais').all()
    serializer_class = EstadoSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nombre', 'pais__nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class MunicipioListView(generics.ListAPIView):
    """Vista para listar todos los municipios"""
    queryset = Municipio.objects.select_related('estado__pais').all()
    serializer_class = MunicipioSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado']
    search_fields = ['nombre', 'estado__nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']
