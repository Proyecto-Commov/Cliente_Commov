import socket
import threading
import queue
import time
import sys
from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

# Cola compartida para guardar el stream H.264
video_queue = queue.Queue(maxsize=30)  # Pequeño para stream VIVO (sin retraso)
h264_connection = None
h264_connected = threading.Event()  # Señal para indicar cuando se conectó el emisor
receptor_thread = None

def receptor_h264():
    """Thread que escucha y recibe el stream H.264 del emisor"""
    global h264_connection
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 5000))
    server_socket.listen(1)
    
    print("[WAITING] Esperando conexion H.264 desde emisor en puerto 5000...")
    sys.stdout.flush()  # Asegurar que se imprime inmediatamente
    
    try:
        h264_connection, addr = server_socket.accept()
        h264_connected.set()  # Señalar que se conectó el emisor
        print(f"[OK] Emisor conectado desde: {addr}")
        sys.stdout.flush()
        
        while True:
            data = h264_connection.recv(4096)
            if not data:
                print("[INFO] Emisor desconectado.")
                break
            
            # Agregar datos a la cola (descartar si está llena para no hacer lag)
            try:
                video_queue.put_nowait(data)
            except queue.Full:
                # Descartar frames antiguos si la cola está llena
                try:
                    video_queue.get_nowait()
                    video_queue.put_nowait(data)
                except queue.Empty:
                    pass
    except Exception as e:
        print(f"[ERROR] Error en receptor H.264: {e}")
    finally:
        if h264_connection:
            try:
                h264_connection.close()
            except:
                pass
        server_socket.close()
        h264_connected.clear()

@app.route('/')
def index():
    return render_template('index.html')

@sock.route('/video')
def video_stream(ws):
    """Envia el stream H.264 VIVO a clientes WebSocket (sin retrasos)"""
    print("[WEB] Cliente web conectado.")
    
    # LIMPIAR COLA: Descartar todos los frames antiguos para stream VIVO
    while True:
        try:
            video_queue.get_nowait()
        except queue.Empty:
            break
    
    # Esperar a que el emisor se conecte (timeout de 30 segundos)
    if not h264_connected.wait(timeout=30):
        print("[TIMEOUT] Timeout: Emisor no se conecto. Cliente desconectado.")
        try:
            ws.send(b"ERROR: Emisor no conectado")
        except:
            pass
        return
    
    try:
        while True:
            try:
                # Obtener datos de la cola con timeout
                data = video_queue.get(timeout=1)
                ws.send(data)
            except queue.Empty:
                # Timeout - continuar esperando
                continue
    except Exception as e:
        print(f"[WARNING] Error enviando a cliente: {e}")
    finally:
        print("[WEB] Cliente web desconectado.")

@app.before_request
def health_check():
    """Endpoint simple para verificar que el servidor está activo"""
    pass

@app.route('/health')
def health():
    return {
        'status': 'ok',
        'h264_connected': h264_connected.is_set(),
        'queue_size': video_queue.qsize()
    }

if __name__ == '__main__':
    print("=" * 60)
    print("[START] RECEPTOR WEB INICIADO")
    print("=" * 60)
    
    # Iniciar thread para recibir H.264
    receptor_thread = threading.Thread(target=receptor_h264, daemon=False)
    receptor_thread.start()
    
    # Dar un momento para que se inicie
    time.sleep(0.5)
    
    # Ejecuta el servidor Flask en el puerto 8080
    print("[WEB] Servidor Flask escuchando en puerto 8080...")
    print("[WEB] Accede a: http://localhost:8080")
    print("=" * 60 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n[STOP] Receptor web detenido.")
    finally:
        # Asegurar que el thread se detiene
        if receptor_thread and receptor_thread.is_alive():
            receptor_thread.join(timeout=2)