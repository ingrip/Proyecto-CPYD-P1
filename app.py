from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

usuarios_conectados = []
lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Usuario conectado")

@socketio.on('disconnect')
def handle_disconnect():
    print("Usuario desconectado")

@socketio.on('mensaje')
def handle_mensaje(data):
    with lock:
        print(f"Mensaje recibido: {data}")
        data['hora'] = datetime.now().strftime("%H:%M")
        emit('message', data, broadcast=True)
        
@socketio.on('escribiendo')
def handle_escribiendo(data):
    emit('escribiendo', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)