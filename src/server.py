import socket
import threading

# Configuración del servidor
MAX_MESSAGE_LENGTH = 500  # Longitud máxima permitida de un mensaje
BUFFER_SIZE = 1024        # Tamaño del buffer para recibir datos
IP_ADDRESS = "127.0.0.1" # Dirección IP del servidor
PORT = 5000 # Puerto del servidor

clients = {}  # Diccionario global que almacena los clientes conectados {socket: nickname}
clients_lock = threading.RLock() # Lock para proteger el acceso concurrente al diccionario de clientes

# Función para verificar que el mensaje sea válido
def check_message(message):
    if not message or not message.strip(): # Verifica que el mensaje no esté vacío
        return False, "El mensaje no puede estar vacio."
    
    if len(message) > MAX_MESSAGE_LENGTH: # Verifica que el mensaje no supere la longitud máxima
        return False, f"El mensaje excede los {MAX_MESSAGE_LENGTH} caracteres."
    
    return True, "" # Verifica que el mensaje sea válido

# Función para enviar un mensaje a todos los clientes
def broadcast(message, sender=None):
    data = (message + "\n").encode("utf-8") # Convierte el mensaje a bytes y añade un salto de línea
    with clients_lock: # Bloquea el acceso al diccionario de clientes para evitar condiciones de carrera
        for client_sock in list(clients): # Itera sobre los clientes conectados
            if client_sock is sender: # Salta el mensaje si es el remitente
                continue
            try:
                client_sock.sendall(data) # Envía el mensaje al cliente
            except OSError: # Si hay un error al enviar el mensaje
                remove_client(client_sock) # Elimina el cliente

# Función para eliminar un cliente del servidor
def remove_client(client_sock):
    nickname = clients.pop(client_sock, None)
    try:
        client_sock.close() # Cierra la conexión con el cliente
    except OSError:
        pass
    if nickname: # Si el cliente tiene un nickname
        print(f"[-] {nickname} ha salido del chat", flush=True)
        broadcast(f"** {nickname} ha salido del chat **") # Envía un mensaje a todos los clientes

# Función para manejar un cliente conectado
def handle_client(client_sock, addr):
    buffer = "" # Buffer para almacenar los datos recibidos
    try:
        nickname_data = client_sock.recv(BUFFER_SIZE) # Recibe el nickname del cliente
        if not nickname_data: # Si no se recibe el nickname
            client_sock.close() # Cierra la conexión
            return
        nickname = nickname_data.decode("utf-8").strip() # Convierte el nickname a string
        
        if not nickname: # Si el nickname está vacío
            nickname = f"anon-{addr[1]}" # Asigna un nickname por defecto

        with clients_lock: # Bloquea el acceso al diccionario de clientes
            clients[client_sock] = nickname # Añade el cliente al diccionario

        print(f"[+] {nickname} se ha unido al chat desde {addr[0]}:{addr[1]}", flush=True)
        broadcast(f"** {nickname} se ha unido al chat **", sender=client_sock) # Envía un mensaje a todos los clientes
        while True: # Bucle infinito para recibir mensajes
            message_data = client_sock.recv(BUFFER_SIZE) # Recibe el mensaje del cliente
            if not message_data: # Si no se recibe el mensaje
                break

            buffer += message_data.decode("utf-8") # Añade el mensaje al buffer

            while "\n" in buffer: # Mientras haya un salto de línea en el buffer
                message_line, buffer = buffer.split("\n", 1) # Divide el buffer en dos
                is_valid, error_reason = check_message(message_line) # Verifica que el mensaje sea válido
                
                if not is_valid: # Si el mensaje no es válido
                    try: # Intenta enviar un mensaje de error
                        error_msg = f"[ERROR] {error_reason}\n"
                        client_sock.sendall(error_msg.encode("utf-8"))
                    except OSError:
                        pass
                    continue

                with clients_lock: # Bloquea el acceso al diccionario de clientes
                    current_nickname = clients.get(client_sock, nickname) # Obtiene el nickname del cliente
                
                print(f"[{current_nickname}]: {message_line}", flush=True)
                broadcast(f"[{current_nickname}]: {message_line}", sender=client_sock) # Envía el mensaje a todos los clientes

    except OSError: # Si hay un error al recibir el mensaje
        pass
    finally: # Finalmente
        with clients_lock: # Bloquea el acceso al diccionario de clientes
            remove_client(client_sock) # Elimina el cliente

# Función para iniciar el servidor
def start_server(host=IP_ADDRESS, port=PORT): # host y port son los parámetros de la función
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crea un socket de servidor
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reutilizar la dirección del socket
    server_sock.bind((host, port)) # Vincula el socket a la dirección y el puerto
    server_sock.listen() # Pone el socket en modo de escucha
    return server_sock

# Bucle principal de aceptación de conexiones
def accept_loop(server_sock):
    server_sock.settimeout(1.0) # Establece un timeout para permitir interrumpir con Ctrl+C en Windows
    while True: # Bucle infinito para aceptar conexiones
        try: # Intenta aceptar una conexión
            client_sock, addr = server_sock.accept() # Acepta una conexión
            client_sock.settimeout(None) # Asegura que la conexión con el cliente sea bloqueante
        except socket.timeout:
            continue
        except OSError: # Si hay un error al aceptar la conexión
            break # Sale del bucle
        
        thread = threading.Thread(target=handle_client,args=(client_sock, addr),daemon=True) # Crea un hilo para manejar el cliente
        thread.start() # Inicia el hilo

# Iniciación del servidor
if __name__ == "__main__": # Si el script es ejecutado directamente
    srv = start_server(IP_ADDRESS, PORT) # Inicia el servidor
    print(f"[+] Servidor escuchando en {IP_ADDRESS}:{PORT}") # Imprime el mensaje de bienvenida
    
    try: # Intenta aceptar conexiones
        accept_loop(srv) # Acepta conexiones
    except KeyboardInterrupt: # Si hay un error al aceptar conexiones
        print("\n[!] Servidor detenido.") # Imprime el mensaje de despedida
    finally: # Finalmente
        srv.close() # Cierra el servidor
