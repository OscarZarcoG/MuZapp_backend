import os
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pydub import AudioSegment
from django.conf import settings
from django.core.files import File
from datetime import timedelta
import tempfile
import shutil


class AudioConverter:
    """Clase para manejar la conversión de audio desde YouTube y Spotify"""
    
    def __init__(self):
        # Configurar directorio de medios
        self.media_root = getattr(settings, 'MEDIA_ROOT', 'media')
        self.converted_audio_dir = os.path.join(self.media_root, 'converted_audio')
        
        # Crear directorio si no existe
        os.makedirs(self.converted_audio_dir, exist_ok=True)
        
        # Configurar Spotify (opcional - requiere credenciales)
        self.spotify_client = None
        try:
            client_id = getattr(settings, 'SPOTIFY_CLIENT_ID', None)
            client_secret = getattr(settings, 'SPOTIFY_CLIENT_SECRET', None)
            
            if client_id and client_secret:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.spotify_client = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
        except Exception as e:
            print(f"Error configurando Spotify: {e}")
    
    def convert_to_mp3(self, url, conversion_id):
        """Convertir URL a MP3"""
        try:
            if 'youtube.com' in url or 'youtu.be' in url:
                return self._convert_youtube_to_mp3(url, conversion_id)
            elif 'spotify.com' in url:
                return self._convert_spotify_to_mp3(url, conversion_id)
            else:
                return {
                    'success': False,
                    'error': 'URL no soportada. Solo YouTube y Spotify son compatibles.'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error durante la conversión: {str(e)}'
            }
    
    def _convert_youtube_to_mp3(self, url, conversion_id):
        """Convertir video de YouTube a MP3"""
        try:
            # Configurar yt-dlp
            temp_dir = tempfile.mkdtemp()
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'extractaudio': True,
                'audioformat': 'mp3',
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extraer información del video
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                uploader = info.get('uploader', 'Unknown')
                duration_seconds = info.get('duration', 0)
                
                # Descargar y convertir
                ydl.download([url])
                
                # Buscar el archivo MP3 generado
                mp3_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
                
                if not mp3_files:
                    return {
                        'success': False,
                        'error': 'No se pudo generar el archivo MP3'
                    }
                
                temp_mp3_path = os.path.join(temp_dir, mp3_files[0])
                
                # Mover archivo a directorio final
                final_filename = f"conversion_{conversion_id}_{title[:50]}.mp3"
                final_filename = self._sanitize_filename(final_filename)
                final_path = os.path.join(self.converted_audio_dir, final_filename)
                
                shutil.move(temp_mp3_path, final_path)
                
                # Obtener tamaño del archivo
                file_size = os.path.getsize(final_path)
                
                # Limpiar directorio temporal
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                return {
                    'success': True,
                    'title': title,
                    'artist': uploader,
                    'duration': timedelta(seconds=duration_seconds) if duration_seconds else None,
                    'file_path': f'converted_audio/{final_filename}',
                    'file_size': file_size
                }
                
        except Exception as e:
            # Limpiar en caso de error
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                'success': False,
                'error': f'Error procesando YouTube: {str(e)}'
            }
    
    def _convert_spotify_to_mp3(self, url, conversion_id):
        """Convertir canción de Spotify a MP3"""
        try:
            if not self.spotify_client:
                return {
                    'success': False,
                    'error': 'Spotify no está configurado. Se requieren credenciales de API.'
                }
            
            # Extraer ID de la canción de Spotify
            track_id = self._extract_spotify_track_id(url)
            
            if not track_id:
                return {
                    'success': False,
                    'error': 'No se pudo extraer el ID de la canción de Spotify'
                }
            
            # Obtener información de la canción
            track_info = self.spotify_client.track(track_id)
            
            title = track_info['name']
            artist = ', '.join([artist['name'] for artist in track_info['artists']])
            duration_ms = track_info['duration_ms']
            
            # Buscar la canción en YouTube
            search_query = f"{artist} {title} audio"
            youtube_url = self._search_youtube(search_query)
            
            if not youtube_url:
                return {
                    'success': False,
                    'error': 'No se encontró la canción en YouTube'
                }
            
            # Convertir desde YouTube
            result = self._convert_youtube_to_mp3(youtube_url, conversion_id)
            
            if result['success']:
                # Actualizar información con datos de Spotify
                result['title'] = title
                result['artist'] = artist
                result['duration'] = timedelta(milliseconds=duration_ms)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error procesando Spotify: {str(e)}'
            }
    
    def _extract_spotify_track_id(self, url):
        """Extraer ID de track de una URL de Spotify"""
        try:
            if '/track/' in url:
                track_id = url.split('/track/')[1].split('?')[0]
                return track_id
            return None
        except:
            return None
    
    def _search_youtube(self, query):
        """Buscar una canción en YouTube y retornar la primera URL"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(
                    f"ytsearch1:{query}",
                    download=False
                )
                
                if search_results and 'entries' in search_results and search_results['entries']:
                    return search_results['entries'][0]['webpage_url']
            
            return None
            
        except Exception as e:
            print(f"Error buscando en YouTube: {e}")
            return None
    
    def _sanitize_filename(self, filename):
        """Limpiar nombre de archivo para evitar caracteres problemáticos"""
        import re
        # Remover caracteres no válidos para nombres de archivo
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limitar longitud
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:96] + ext
        return filename