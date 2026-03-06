from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/comunidades')
def comunidades():
    return render_template("comunidades.html")


@app.route('/chat/<comunidad>')
def chat(comunidad):
    return render_template("chat.html", comunidad=comunidad)


@socketio.on('mensaje')
def handle_mensaje(data):
    now = datetime.now()
    data['hora'] = now.strftime("%H:%M")
    data['fecha'] = now.isoformat()
    db.collection("mensajes").add({
        "nombre": data['nombre'],
        "mensaje": data['mensaje'],
        "hora": data['hora'],
        "fecha": data['fecha'],
        "uid": data.get("uid"),
        "comunidad": data.get("comunidad")
    })

    emit('message', data, broadcast=True)

@socketio.on('cargar_historial')
def cargar_historial(data):
    comunidad = data['comunidad']
    mensajes = []

    docs = db.collection("mensajes") \
        .where("comunidad", "==", comunidad) \
        .order_by("fecha") \
        .limit(50) \
        .stream()

    for doc in docs:
        m = doc.to_dict()
        if 'fecha' in m and isinstance(m['fecha'], datetime):
            m['fecha'] = m['fecha'].isoformat()
        mensajes.append(m)

    emit("historial", mensajes)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)