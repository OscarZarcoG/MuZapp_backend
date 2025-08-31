# Instalación de FFmpeg

FFmpeg es una dependencia crítica para la funcionalidad de conversión de música de YouTube. Este archivo contiene instrucciones detalladas para instalar FFmpeg en diferentes sistemas operativos.

## Windows

### Opción 1: Usando winget (Recomendado)

```bash
winget install ffmpeg
```

### Opción 2: Descarga manual

1. Visita [https://ffmpeg.org/download.html#build-windows](https://ffmpeg.org/download.html#build-windows)
2. Descarga la versión "release builds" para Windows
3. Extrae el archivo ZIP a una carpeta (ej: `C:\ffmpeg`)
4. Agrega la carpeta `bin` al PATH del sistema:
   - Abre "Variables de entorno" desde el Panel de Control
   - Edita la variable PATH del sistema
   - Agrega la ruta: `C:\ffmpeg\bin`

### Verificación en Windows

```bash
ffmpeg -version
ffprobe -version
```

### Solución de problemas en Windows

Si ffmpeg no se reconoce después de la instalación:

1. **Reinicia la terminal/PowerShell**
2. **Agrega manualmente al PATH de la sesión**:
   ```powershell
   $env:PATH += ";C:\ruta\a\ffmpeg\bin"
   ```
3. **Verifica la ubicación de instalación de winget**:
   ```powershell
   Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Name "ffmpeg.exe"
   ```

## macOS

### Usando Homebrew (Recomendado)

```bash
# Instalar Homebrew si no está instalado
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar FFmpeg
brew install ffmpeg
```

### Usando MacPorts

```bash
sudo port install ffmpeg
```

### Verificación en macOS

```bash
ffmpeg -version
ffprobe -version
```

## Linux

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

### CentOS/RHEL/Fedora

```bash
# CentOS/RHEL
sudo yum install epel-release
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### Arch Linux

```bash
sudo pacman -S ffmpeg
```

### Verificación en Linux

```bash
ffmpeg -version
ffprobe -version
```

## Compilación desde código fuente

Si necesitas compilar FFmpeg desde el código fuente (para configuraciones específicas):

### Dependencias

```bash
# Ubuntu/Debian
sudo apt install build-essential yasm cmake libtool libc6 libc6-dev unzip wget libnuma1 libnuma-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install cmake yasm
```

### Compilación

```bash
# Descargar código fuente
wget https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg

# Configurar y compilar
./configure --enable-gpl --enable-libx264 --enable-libx265 --enable-libvpx --enable-libmp3lame
make -j$(nproc)
sudo make install
```

## Verificación de la instalación

Para verificar que FFmpeg está correctamente instalado y configurado:

```bash
# Verificar versión
ffmpeg -version
ffprobe -version

# Verificar codecs disponibles
ffmpeg -codecs | grep mp3
ffmpeg -codecs | grep aac

# Probar conversión simple
ffmpeg -f lavfi -i "sine=frequency=1000:duration=1" -c:a libmp3lame test.mp3
```

## Configuración para el proyecto Django

Una vez instalado FFmpeg, asegúrate de que el proyecto Django puede encontrarlo:

### Variables de entorno (opcional)

```bash
# Si FFmpeg no está en el PATH del sistema
export FFMPEG_BINARY="/ruta/a/ffmpeg"
export FFPROBE_BINARY="/ruta/a/ffprobe"
```

### Configuración en settings.py (si es necesario)

```python
# En AgendaMusicos/settings.py
import os

# Rutas personalizadas para FFmpeg (opcional)
FFMPEG_BINARY = os.environ.get('FFMPEG_BINARY', 'ffmpeg')
FFPROBE_BINARY = os.environ.get('FFPROBE_BINARY', 'ffprobe')
```

## Solución de problemas comunes

### Error: "ffmpeg not found"

1. Verifica que FFmpeg está instalado: `ffmpeg -version`
2. Verifica que está en el PATH: `which ffmpeg` (Linux/macOS) o `where ffmpeg` (Windows)
3. Reinicia la terminal después de la instalación
4. En Windows, verifica las variables de entorno del sistema

### Error: "Permission denied"

```bash
# Linux/macOS
sudo chmod +x /usr/local/bin/ffmpeg
sudo chmod +x /usr/local/bin/ffprobe
```

### Error: "Codec not found"

Algunos codecs pueden no estar disponibles en todas las compilaciones de FFmpeg. Verifica los codecs disponibles:

```bash
ffmpeg -codecs | grep -i mp3
ffmpeg -encoders | grep -i mp3
```

## Recursos adicionales

- [Documentación oficial de FFmpeg](https://ffmpeg.org/documentation.html)
- [Guía de compilación de FFmpeg](https://trac.ffmpeg.org/wiki/CompilationGuide)
- [FFmpeg para Windows](https://www.gyan.dev/ffmpeg/builds/)
- [Homebrew FFmpeg](https://formulae.brew.sh/formula/ffmpeg)