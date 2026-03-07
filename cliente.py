import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 5000

# pedir UID al iniciar
uid = input("Ingresa tu UID (usuario único): ").strip()

# comunidad o chat privado
modo = input("Deseas entrar a comunidad (c) o chat privado (p)? ").strip().lower()
if modo == 'c':
    destino = input("Nombre de la comunidad: ").strip()
    privado = False
    usuarios_privados = []
else:
    usuarios_privados = input("UIDs de usuarios privados (separados por coma): ").strip().split(',')
    privado = True
    destino = None

def recibir_mensajes(cliente):
    while True:
        try:
            mensaje = cliente.recv(4096).decode()
            data = json.loads(mensaje)
            if data.get("privado"):
                print(f"[PRIVADO] {data['nombre']} ({data['hora']}): {data['mensaje']}")
            else:
                print(f"[{data['comunidad']}] {data['nombre']} ({data['hora']}): {data['mensaje']}")
        except:
            print("Conexión cerrada.")
            cliente.close()
            break
def enviar_mensajes(cliente):
    while True:
        mensaje = input()
        if mensaje.strip() == "":
            continue

        if privado:
            data = {
                "mensaje": mensaje,
                "nombre": uid, 
                "privado": True,
                "usuarios": [uid, usuarios_privados[0]]  
            }
        else:
            # mensaje a la comunidad
            data = {
                "tipo": "comunidad",
                "comunidad": destino,
                "mensaje": mensaje,
                "nombre": uid,
            }

        cliente.send(json.dumps(data).encode())

def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORT))
    # enviar UID al servidor
    cliente.send(uid.encode())
    print("Conectado al servidor.")

    hilo_recibir = threading.Thread(target=recibir_mensajes, args=(cliente,))
    hilo_recibir.start()

    enviar_mensajes(cliente)

if __name__ == "__main__":
    iniciar_cliente()