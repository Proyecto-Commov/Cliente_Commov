#!/usr/bin/env python3
import socket
import subprocess

def iniciar_receptor():
    # Configuración del servidor
    HOST = '0.0.0.0'  # Escucha en todas las interfaces de red
    PORT = 5000       # El mismo puerto que use el emisor
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    
    print(f"=== RECEPTOR INICIADO ===")
    print(f"Esperando conexión en el puerto {PORT}...")
    
    try:
        conn, addr = server_socket.accept()
        print(f"Conectado con el emisor en: {addr}")

        # Configurar ffplay para recibir el stream H.264 directo
        # Usamos parámetros de baja latencia para que no haya retraso
        ffplay_cmd = [
            'ffplay',
            '-f', 'h264',
            '-fflags', 'nobuffer',
            '-flags', 'low_delay',
            '-framedrop',
            '-alwaysontop',
            '-window_title', 'Streaming Directo Commov',
            '-i', '-'  # Leer de la entrada estándar (stdin)
        ]
        
        # Abrir el reproductor
        player = subprocess.Popen(ffplay_cmd, stdin=subprocess.PIPE)

        print("Recibiendo video... (Cierra la ventana de video para salir)")
        
        while True:
            # Recibir bloques de datos del socket
            data = conn.recv(4096)
            if not data:
                break
            
            # Enviar los datos recibidos a ffplay
            try:
                player.stdin.write(data)
                player.stdin.flush()
            except BrokenPipeError:
                # Ocurre si se cierra la ventana de ffplay
                break
                
    except KeyboardInterrupt:
        print("\nRecepción detenida manualmente.")
    finally:
        conn.close()
        server_socket.close()
        print("Conexiones cerradas.")

if __name__ == "__main__":
    iniciar_receptor()