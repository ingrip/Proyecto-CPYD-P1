from datetime import datetime
from flask_socketio import leave_room
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
from flask import session, jsonify, request, redirect
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


@app.route('/chat/<comunidad>')
def chat(comunidad):

    if not session.get("uid"):
        return redirect("/login")

    return render_template("chat.html", comunidad=comunidad)
# recibir mensaje
@socketio.on('mensaje')
def handle_mensaje(data):

    print("MENSAJE RECIBIDO:", data)

    now = datetime.now()

    comunidad = data.get("comunidad")
    privado = data.get("privado", False)

    if not privado and not comunidad:
        print("MENSAJE SIN COMUNIDAD")
        return

    mensaje_doc = {
        "nombre": data['nombre'],
        "mensaje": data['mensaje'],
        "hora": now.strftime("%H:%M"),
        "fecha": now.isoformat(),
        "uid": data["uid"], 
        "comunidad": comunidad if not privado else None,
        "privado": privado,
        "usuarios": data.get("usuarios", [])
    }

    db.collection("mensajes").add(mensaje_doc)

    data["hora"] = mensaje_doc["hora"]
    data["fecha"] = mensaje_doc["fecha"]

    if privado:
        for uid in mensaje_doc["usuarios"]:
            socketio.emit("message", data, room=uid)
    else:
        socketio.emit("message", data, room=comunidad)

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
@app.route("/crear_sesion", methods=["POST"])
def crear_sesion():

    data = request.json

    session["usuario"] = data["nombre"]
    session["uid"] = data["uid"]
    session["foto"] = data["foto"]

    return jsonify({"ok": True})
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@socketio.on("leave_comunidad")
def leave_comunidad(data):
    comunidad = data.get("comunidad")
    if comunidad:
        leave_room(comunidad)
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)