# 🎬 Commov Sistema Integrado - Guía de Funcionamiento

## Arquitectura del Sistema

```
SERVIDOR (SERVIDOR_COMMOV)
├── Cámara (WebCam)
│   └── FFmpeg (H.264 Encoding)
│       └── emisor_directo.py
│           └── Puerto 5000 (TCP Socket)

CLIENTE (CLIENTE_COMMOV)
├── receptor_web.py (Puerto 5000 entrada, Puerto 8080 salida)
│   ├── Thread H.264: Recibe bitstream en puerto 5000
│   ├── Cola (Queue): Buffer para datos
│   └── WebSocket: Envía a navegadores via puerto 8080
│
└── Navegador
    └── http://localhost:8080
        └── JMuxer (Reproductor H.264 en JavaScript)
```

## Flujo de Datos

```
Cámara 📹 
  ↓
FFmpeg (video_capture.py)
  ↓
H.264 bitstream
  ↓
emisor_directo.py → socket.sendall() → Puerto 5000
  ↓
receptor_web.py (thread H.264)
  ↓
Queue (video_queue)
  ↓
WebSocket @ /video
  ↓
Navegador → JMuxer → <video> tag
```

## Modo de Uso

### Opción 1: Uso Distribuido (Recomendado)

**Máquina 1 (Servidor - Emisor):**
```bash
cd c:\SERVIDOR_COMMOV
python emisor_directo.py
```

**Máquina 2 (Cliente - Receptor):**
```bash
cd c:\CLIENTE_COMMOV
pip install -r requirements.txt
python receptor_web.py
# Luego abre el navegador en http://localhost:8080
```

### Opción 2: Todo en una Máquina (Desarrollo)

```bash
cd c:\SERVIDOR_COMMOV
python iniciar_todo.py
# Automáticamente iniciará el receptor y emisor
# Abre http://localhost:8080 en el navegador
```

## Requisitos

### Sistema Operativo
- **Windows 10+**, **macOS**, o **Linux**
- Python 3.8+

### Software Externo
- **FFmpeg** (debe estar instalado en el PATH)
  - Windows: https://ffmpeg.org/download.html
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`

### Dependencias Python (Cliente)

```bash
pip install -r requirements.txt
```

Contiene:
- Flask==2.3.0
- Flask-Sock==0.2.9
- Werkzeug==2.3.0

### Dependencias Python (Servidor)

El servidor NO requiere dependencias Python. Solo necesita FFmpeg instalado en el sistema.

## Configuración

### Cambiar IP del Receptor

**Archivo:** `SERVIDOR_COMMOV/emisor_directo.py` (línea ~20)

```python
IP_RECEPTOR = "127.0.0.1"  # Cambiar a la IP del cliente
PUERTO = 5000
```

Si el cliente está en otra máquina:
```python
IP_RECEPTOR = "192.168.1.100"  # IP del cliente
```

### Cambiar Parámetros de Video

**Archivo:** `SERVIDOR_COMMOV/emisor_directo.py`

```python
config = VideoCaptureConfig(
    width=640,           # Ancho en píxeles
    height=480,          # Alto en píxeles
    fps=30,              # Fotogramas por segundo
    bitrate="1500k",     # Bitrate (más alto = mejor calidad)
    preset="ultrafast",  # ultrafast, superfast, veryfast, faster, fast
    crf=35               # Calidad (0-51, menor = mejor)
)
```

### Cambiar Puertos

- **Puerto H.264:** `receptor_web.py` línea 8 y `emisor_directo.py` línea 21
- **Puerto Web:** `receptor_web.py` última línea (por defecto 8080)

## Troubleshooting

### ❌ "Conexión rechazada" (Connection refused)

**Problema:** El emisor no puede conectarse al receptor.

**Soluciones:**
1. Verificar que `receptor_web.py` está ejecutándose
2. Verificar la IP: `ip receptor` debe coincidir con la configurada en `emisor_directo.py`
3. Verificar firewall: Puerto 5000 debe estar abierto
4. En la misma máquina, usar `127.0.0.1`
5. En máquinas diferentes, usar la IP local (ej: `192.168.x.x`)

```bash
# Probar conectividad
telnet <IP_RECEPTOR> 5000
```

### ❌ "FFmpeg not found" o "FileNotFoundError"

**Problema:** FFmpeg no está instalado o no está en el PATH.

**Soluciones:**
1. Instalar FFmpeg desde https://ffmpeg.org
2. Verificar que está en el PATH: `ffmpeg -version`
3. Reiniciar terminal después de instalar

### ❌ "No video displayed" (Sin video en navegador)

**Posibles causas:**
1. El emisor no está conectado → Verificar con `receptor_web.py` en modo debug
2. Navegador no soporta H.264 → Intentar en Chrome o Edge
3. JMuxer no cargó → Verificar conexión a internet (CDN)
4. WebSocket falló → Verificar consola del navegador (F12)

**Debug:**
```bash
# En navegador, abre F12 (DevTools) y mira Console
# Debe ver: "Cliente web conectado"
```

### ❌ "Laggy video" o "Stuttering"

**Soluciones:**
1. Reducir resolución o bitrate en `emisor_directo.py`
2. Reducir `fps` de 30 a 24 o 15
3. Usar preset más rápido: `superfast` o `ultrafast`
4. Aumentar bitrate: `2500k` → `3000k` o más

### ❌ "Cannot bind to port" (Puerto ya en uso)

**Problema:** El puerto 5000 o 8080 está en uso.

**Soluciones:**
1. Terminar procesos Python que usen el puerto:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

2. O cambiar el puerto en el código

## Performance Tips

1. **Para baja latencia:** Usar `preset="ultrafast"` y bitrate bajo (1500k)
2. **Para mejor calidad:** Usar `preset="fast"` y bitrate alto (3000k+)
3. **Para wifi:** Reducir resolución a 480p o 360p
4. **Para LAN rápida:** Aumentar resolución a 1080p

## Monitoreo

**Endpoint de salud:**

```bash
curl http://localhost:8080/health
```

Respuesta:
```json
{
  "status": "ok",
  "h264_connected": true,
  "queue_size": 5
}
```

- `h264_connected`: ¿Está conectado el emisor?
- `queue_size`: Cuántos chunks hay en cola (ideal < 30)

## Seguridad (Para Producción)

⚠️ **Importante:** Este código NO está protegido para producción. Para uso en red:

1. ❌ NO expongas el puerto 8080 a internet directamente
2. ✅ USA HTTPS/WSS con certificados válidos
3. ✅ AÑADE autenticación (tokens, API keys)
4. ✅ USA cortafuegos para limitar acceso
5. ✅ CORRE en HTTPS reverse proxy (nginx, Apache)

## Logs y Debug

### Ver logs detallados

**Servidor:**
```python
# En emisor_directo.py, cambiar:
# logging.basicConfig(level=logging.INFO)
```

**Cliente:**
```python
# En receptor_web.py, los logs ya están activos
# Ver salida de terminal
```

**Navegador:**
```javascript
// En Console (F12):
// Mira WebSocket messages y errores de JMuxer
```

---

**¿Problemas?** Revisa los logs del servidor y cliente. La mayoría de errores están documentados en TROUBLESHOOTING.

