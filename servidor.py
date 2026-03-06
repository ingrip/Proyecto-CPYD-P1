# servidor.py
# servidor de chat en python con procesamiento en paralelo y manejo de múltiples clientes

import socket
import threading
from multiprocessing import Process

# configuracion del servidor
HOST = '127.0.0.1'
PORT = 5000
clientes = []  # lista de clientes conectados
lock = threading.Lock()  # lock para evitar race conditions

def broadcast(mensaje, cliente_emisor=None):
    # envia el mensaje a todos los clientes excepto al emisor
    with lock:
        for cliente in clientes:
            if cliente != cliente_emisor:
                try:
                    cliente.send(mensaje)
                except Exception as e:
                    print(f"[error] enviando a cliente: {e}")
                    cliente.close()
                    clientes.remove(cliente)

def manejar_cliente(cliente, direccion):
    # maneja un cliente en un hilo o proceso independiente
    print(f"[nueva conexion] {direccion} conectado.")
    try:
        while True:
            mensaje = cliente.recv(1024)
            if not mensaje:
                break
            print(f"[{direccion}] {mensaje.decode()}")
            broadcast(mensaje, cliente)
    except ConnectionResetError:
        print(f"[desconectado] {direccion} abruptamente")
    except Exception as e:
        print(f"[error] {direccion}: {e}")
    finally:
        with lock:
            if cliente in clientes:
                clientes.remove(cliente)
        cliente.close()
        print(f"[desconectado] {direccion}")

def iniciar_servidor():
    # inicia el servidor TCP, acepta clientes y lanza procesos para cada uno
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"[servidor activo] {HOST}:{PORT}")

    while True:
        try:
            cliente, direccion = servidor.accept()
            with lock:
                clientes.append(cliente)
            # crear un proceso independiente para el cliente
            p = Process(target=manejar_cliente, args=(cliente, direccion))
            p.start()
        except KeyboardInterrupt:
            print("\n[servidor detenido]")
            break
        except Exception as e:
            print(f"[error] aceptando cliente: {e}")

    # cerrar todos los clientes al detener el servidor
    with lock:
        for c in clientes:
            c.close()
    servidor.close()

if __name__ == "__main__":
    iniciar_servidor()