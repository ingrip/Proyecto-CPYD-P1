from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request
# inicializar firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
usuarios_activos = {}

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# rutas
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


# recibir mensaje
@socketio.on('mensaje')
def handle_mensaje(data):
    now = datetime.now()
    data['hora'] = now.strftime("%H:%M")
    data['fecha'] = now.isoformat()

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

    if privado:
        # emitir solo a los usuarios privados
        for uid in usuarios_privados:
            join_room(uid)  # asegurar que estén en la sala
            socketio.emit("message", data, room=uid)
    else:
        socketio.emit("message", data, to=data["comunidad"])


# cargar historial
@socketio.on('cargar_historial')
def cargar_historial(data):
    uid = data.get("uid")
    comunidad = data.get("comunidad")
    privado_con = data.get("privado_con")  # el uid del chat privado actual

    mensajes = []

    if comunidad:
        docs = db.collection("mensajes") \
            .where("comunidad", "==", comunidad) \
            .order_by("fecha") \
            .limit(50) \
            .stream()
    elif privado_con:
        # cargar solo mensajes del chat privado actual
        docs = db.collection("mensajes") \
            .where("privado", "==", True) \
            .where("usuarios", "array_contains", uid) \
            .order_by("fecha") \
            .limit(50) \
            .stream()
    else:
        docs = []

    for doc in docs:
        m = doc.to_dict()
        # filtrar solo del chat privado actual
        if privado_con and m.get("privado"):
            if privado_con not in m.get("usuarios", []):
                continue
        if "fecha" in m:
            try:
                m["fecha"] = m["fecha"].isoformat()
            except:
                m["fecha"] = str(m["fecha"])
        mensajes.append(m)

    emit("historial", mensajes)


# unirse a sala

@socketio.on('join')
def join(data):
    uid = data.get("uid")
    nombre = data.get("nombre")
    if uid:
        join_room(uid)
        usuarios_activos[request.sid] = {"uid": uid, "nombre": nombre}  # guardar por socket.id
    # emitir lista actualizada a todos
    emit("usuarios_activos", [{"uid": u["uid"], "nombre": u["nombre"]} for u in usuarios_activos.values()], broadcast=True)

@socketio.on('disconnect')
def disconnect():
    # eliminar solo al socket que se desconecta
    if request.sid in usuarios_activos:
        usuarios_activos.pop(request.sid)
    # emitir lista actualizada a todos
    emit("usuarios_activos", [{"uid": u["uid"], "nombre": u["nombre"]} for u in usuarios_activos.values()], broadcast=True)

@socketio.on("join_comunidad")
def join_comunidad(data):
    comunidad = data.get("comunidad")
    if comunidad:
        join_room(comunidad)



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)