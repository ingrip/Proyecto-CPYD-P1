# servidor.py
# servidor de chat en python con chats por comunidad y privados
import socket
import threading
import json
from datetime import datetime

HOST = '127.0.0.1'
PORT = 5000

clientes = []  # lista de (socket, uid)
lock = threading.Lock()

def enviar_mensaje(data, cliente_emisor=None):
    with lock:
        if data.get('privado'):
            # enviar solo a usuarios indicados
            for cliente, uid in clientes:
                if uid in data['usuarios'] and cliente != cliente_emisor:
                    try:
                        cliente.send(json.dumps(data).encode())
                    except:
                        cliente.close()
                        clientes.remove((cliente, uid))
        else:
            # comunidad publica
            for cliente, uid in clientes:
                if cliente != cliente_emisor:
                    try:
                        cliente.send(json.dumps(data).encode())
                    except:
                        cliente.close()
                        clientes.remove((cliente, uid))

def manejar_cliente(cliente, direccion):
    try:
        cliente.send("envia tu uid:".encode())
        uid = cliente.recv(1024).decode().strip()
        with lock:
            clientes.append((cliente, uid))
        print(f"[conectado] {direccion} - uid:{uid}")

        while True:
            mensaje = cliente.recv(2048)
            if not mensaje:
                break
            try:
                data = json.loads(mensaje.decode())
            except:
                continue

            now = datetime.now()
            data['hora'] = now.strftime("%H:%M")
            data['fecha'] = now.isoformat()
            data['uid'] = uid

            print(f"[{direccion}] {data}")
            enviar_mensaje(data, cliente_emisor=cliente)

    except Exception as e:
        print(f"[error] {direccion}: {e}")
    finally:
        with lock:
            clientes[:] = [(c, u) for c, u in clientes if c != cliente]
        cliente.close()
        print(f"[desconectado] {direccion}")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"[servidor activo] {HOST}:{PORT}")

    try:
        while True:
            cliente, direccion = servidor.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(cliente, direccion))
            hilo.start()
    except KeyboardInterrupt:
        print("\n[servidor detenido]")
    finally:
        with lock:
            for c, _ in clientes:
                c.close()
        servidor.close()

if __name__ == "__main__":
    iniciar_servidor()