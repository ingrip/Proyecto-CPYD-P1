import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

def recibir_mensajes(cliente):
    while True:
        try:
            mensaje = cliente.recv(1024).decode()
            print("\n" + mensaje)
        except:
            print("Conexión cerrada.")
            cliente.close()
            break

def enviar_mensajes(cliente):
    while True:
        mensaje = input()
        cliente.send(mensaje.encode())

def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORT))

    print("Conectado al servidor.")

    hilo_recibir = threading.Thread(target=recibir_mensajes, args=(cliente,))
    hilo_recibir.start()

    enviar_mensajes(cliente)

if __name__ == "__main__":
    iniciar_cliente()