import socket
from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

# Buffer para guardar el último trozo de video recibido
video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_socket.bind(('0.0.0.0', 5000))
video_socket.listen(1)

@app.route('/')
def index():
    return render_template('index.html')

@sock.route('/video')
def video_stream(ws):
    print("Cliente web conectado.")
    conn, addr = video_socket.accept()
    try:
        while True:
            data = conn.recv(4096)
            if not data: break
            ws.send(data) # Enviamos los bits directos al navegador
    finally:
        conn.close()

if __name__ == '__main__':
    # Ejecuta el servidor en el puerto 8080
    app.run(host='0.0.0.0', port=8080)