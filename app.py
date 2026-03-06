from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import firebase_admin
from firebase_admin import credentials, firestore
from google.protobuf.timestamp_pb2 import Timestamp
from google.cloud.firestore_v1 import _helpers
# inicializar firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# rutas de la web
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


# socket: recibir mensaje
@socketio.on('mensaje')
def handle_mensaje(data):
    now = datetime.now()
    data['hora'] = now.strftime("%H:%M")
    data['fecha'] = now.isoformat()

    # mensaje privado: usuarios especificos
    privado = data.get("privado", False)
    usuarios_privados = data.get("usuarios", [])

    # guardar en firestore
    db.collection("mensajes").add({
        "nombre": data['nombre'],
        "mensaje": data['mensaje'],
        "hora": data['hora'],
        "fecha": data['fecha'],
        "uid": data.get("uid"),
        "comunidad": data.get("comunidad"),
        "privado": privado,
        "usuarios": usuarios_privados
    })

    # emitir mensaje
    if privado:
        # enviar solo a los usuarios de la lista + remitente
        for uid in usuarios_privados + [data.get("uid")]:
            emit('message', data, room=uid)
    else:
        emit('message', data, broadcast=True)


# socket: cargar historial
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
        # convertir DatetimeWithNanoseconds a string
        if 'fecha' in m:
            fecha = m['fecha']
            if isinstance(fecha, _helpers.Timestamp):
                # Firestore devuelve un Timestamp, convertir a datetime
                m['fecha'] = fecha.ToDatetime().isoformat()
            elif isinstance(fecha, datetime):
                m['fecha'] = fecha.isoformat()
        mensajes.append(m)

    emit("historial", mensajes)
# manejar rooms (para privados)
@socketio.on('join')
def join(data):
    uid = data.get("uid")
    if uid:
        # unir al usuario a su sala privada (su UID)
        socketio.enter_room(uid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)