from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, ListView
from .models import AudioConversion
from .serializers import (
    AudioConversionSerializer,
    ConvertAudioSerializer,
    AudioConversionListSerializer
)
from .utils import AudioConverter


class AudioConversionViewSet(viewsets.ModelViewSet):
    """ViewSet para manejar todas las operaciones CRUD de AudioConversion"""
    queryset = AudioConversion.objects.all()
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return AudioConversionListSerializer
        return AudioConversionSerializer
    
    @action(detail=False, methods=['post'])
    def convert(self, request):
        """Endpoint para convertir audio desde URL de YouTube o Spotify"""
        serializer = ConvertAudioSerializer(data=request.data)
        
        if serializer.is_valid():
            url = serializer.validated_data['url']
            
            try:
                # Crear instancia del convertidor
                converter = AudioConverter()
                
                # Determinar la plataforma
                if 'youtube.com' in url or 'youtu.be' in url:
                    platform = 'youtube'
                else:
                    platform = 'spotify'
                
                # Crear registro de conversión
                conversion = AudioConversion.objects.create(
                    original_url=url,
                    platform=platform,
                    status='processing'
                )
                
                # Procesar la conversión
                result = converter.convert_to_mp3(url, conversion.id)
                
                if result['success']:
                    # Actualizar el registro con la información obtenida
                    conversion.title = result.get('title', '')
                    conversion.artist = result.get('artist', '')
                    conversion.duration = result.get('duration')
                    conversion.audio_file = result.get('file_path', '')
                    conversion.file_size = result.get('file_size')
                    conversion.status = 'completed'
                    conversion.save()
                    
                    serializer = AudioConversionSerializer(conversion)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # Error en la conversión
                    conversion.status = 'failed'
                    conversion.error_message = result.get('error', 'Error desconocido')
                    conversion.save()
                    
                    return Response(
                        {'error': result.get('error', 'Error en la conversión')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except Exception as e:
                return Response(
                    {'error': f'Error interno del servidor: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Endpoint para descargar el archivo de audio convertido"""
        try:
            conversion = self.get_object()
            
            if not conversion.is_completed or not conversion.audio_file:
                return Response(
                    {'error': 'El archivo no está disponible para descarga'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Incrementar contador de descargas
            conversion.download_count += 1
            conversion.save()
            
            # Retornar el archivo
            response = FileResponse(
                conversion.audio_file.open('rb'),
                as_attachment=True,
                filename=f"{conversion.title or 'audio'}.mp3"
            )
            return response
            
        except AudioConversion.DoesNotExist:
            raise Http404("Conversión no encontrada")
        except Exception as e:
            return Response(
                {'error': f'Error al descargar el archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Views basadas en templates para la interfaz web
class HomeView(TemplateView):
    """Vista para la página principal con formulario de conversión"""
    template_name = 'home.html'


class ConversionsListView(ListView):
    """Vista para listar todas las conversiones"""
    model = AudioConversion
    template_name = 'conversions.html'
    context_object_name = 'conversions'
    paginate_by = 10
    ordering = ['-created_at']
    
    def get_queryset(self):
        return AudioConversion.objects.all()
