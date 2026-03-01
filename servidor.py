import socket
import threading

# Configuración
HOST = '127.0.0.1'
PORT = 5000

clientes = []
lock = threading.Lock()

def broadcast(mensaje, cliente_emisor=None):
    with lock:
        for cliente in clientes:
            if cliente != cliente_emisor:
                try:
                    cliente.send(mensaje)
                except:
                    cliente.close()
                    clientes.remove(cliente)

def manejar_cliente(cliente, direccion):
    print(f"[NUEVA CONEXIÓN] {direccion} conectado.")
    
    while True:
        try:
            mensaje = cliente.recv(1024)
            if not mensaje:
                break
            
            print(f"[{direccion}] {mensaje.decode()}")
            broadcast(mensaje, cliente)
        
        except:
            break

    with lock:
        clientes.remove(cliente)
    cliente.close()
    print(f"[DESCONECTADO] {direccion}")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()

    print(f"[SERVIDOR ACTIVO] {HOST}:{PORT}")

    while True:
        cliente, direccion = servidor.accept()
        
        with lock:
            clientes.append(cliente)
        
        hilo = threading.Thread(target=manejar_cliente, args=(cliente, direccion))
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()