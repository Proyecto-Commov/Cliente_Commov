#!/usr/bin/env python3
import socket
import subprocess
import sys

def iniciar_receptor():
    # Configuración del servidor
    HOST = '0.0.0.0'  # Escucha en todas las interfaces de red
    PORT = 5000       # Puerto para recibir H.264
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    
    print(f"=== RECEPTOR INICIADO ===")
    print(f"Esperando conexión H.264 en el puerto {PORT}...")
    print(f"Asegúrate de que el emisor envía a esta dirección IP.")
    
    try:
        conn, addr = server_socket.accept()
        print(f"Conectado con el emisor en: {addr}")

        # Configurar ffplay para recibir el stream H.264 directo
        # Parámetros de baja latencia
        ffplay_cmd = [
            'ffplay',
            '-f', 'h264',
            '-fflags', 'nobuffer',
            '-flags', 'low_delay',
            '-framedrop',
            '-alwaysontop',
            '-window_title', 'Streaming Directo Commov',
            '-i', '-'  # Leer de stdin
        ]
        
        # Abrir el reproductor
        print("Iniciando reproductor ffplay...")
        player = subprocess.Popen(ffplay_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        print("Recibiendo video... (Cierra la ventana de video para salir)")
        
        bytes_recibidos = 0
        while True:
            # Recibir bloques de datos del socket
            data = conn.recv(4096)
            if not data:
                print("Conexión cerrada por el emisor.")
                break
            
            bytes_recibidos += len(data)
            
            # Enviar los datos recibidos a ffplay
            try:
                player.stdin.write(data)
                player.stdin.flush()
            except (BrokenPipeError, IOError):
                # Ocurre si se cierra la ventana de ffplay
                print("Reproductor cerrado.")
                break
        
        print(f"Total de bytes recibidos: {bytes_recibidos}")
                
    except KeyboardInterrupt:
        print("\nRecepción detenida manualmente.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
        server_socket.close()
        print("Conexiones cerradas.")

if __name__ == "__main__":
    iniciar_receptor()