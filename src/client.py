import socket
import sys
import threading
import os

IP_ADDRESS = "127.0.0.1" # Dirección IP del servidor
PORT = 5000 # Puerto del servidor

# Función para recibir mensajes
def receive_messages(sock):
    while True: # Bucle infinito para recibir mensajes
        try: # Intenta recibir el mensaje
            data = sock.recv(1024) # Recibe el mensaje del servidor
            if not data: # Si no se recibe el mensaje
                print("\n[!] Desconectado del servidor.", flush=True)
                break
            print(data.decode("utf-8"), end="", flush=True)
        except OSError: # Si hay un error al recibir el mensaje
            print("\n[!] Error de conexión con el servidor.", flush=True)
            break
    try: # Cerrar el socket
        sock.close()
    except OSError: # Si hay un error al cerrar el socket
        pass
    os._exit(0) # Termina el programa

# Función principal
def main():
    host = sys.argv[1] if len(sys.argv) > 1 else IP_ADDRESS # Obtiene la dirección IP del servidor
    port = int(sys.argv[2]) if len(sys.argv) > 2 else PORT # Obtiene el puerto del servidor
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crea un socket de cliente
    try: 
        sock.connect((host, port)) # Conecta el socket al servidor
    except (OSError, ConnectionRefusedError):
        print(f"[!] No se pudo conectar al servidor en {host}:{port}.", flush=True) # Si hay un error al conectar, muestra un mensaje y sale
        sys.exit(1)
        
    nickname = input("Nickname: ").strip() or "anon" # Obtiene el nickname del cliente
    try:
        sock.sendall(nickname.encode("utf-8")) # Envía el nickname al servidor
    except OSError: # Si hay un error al enviar el nickname
        print("[!] Error al enviar el nickname.", flush=True) 
        sock.close() # Cierra el socket
        sys.exit(1)
        
    print(f"Conectado como '{nickname}'. Escribe tus mensajes (Ctrl+C para salir):\n", flush=True) # Imprime el mensaje de bienvenida
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start() # Inicia el hilo de recepción
    try: # Bucle infinito para enviar mensajes
        while True: # Bucle infinito para enviar mensajes
            user_message = input() # Obtiene el mensaje del usuario
            sock.sendall((user_message + "\n").encode("utf-8")) # Envía el mensaje al servidor
    except (KeyboardInterrupt, EOFError): # Si hay un error al enviar el mensaje
        print("\nSaliendo...", flush=True)
    except OSError: # Si hay un error al enviar el mensaje
        print("\n[!] Error al enviar mensaje. Conexión cerrada.", flush=True)
    finally: # Finalmente
        sock.close() # Cierra el socket

if __name__ == "__main__": # Si el script es el principal
    main() # Ejecuta la función principal
