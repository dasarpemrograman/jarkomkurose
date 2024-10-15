import socket

BUFFER_SIZE = 1024

def broadcast_message(server, message, clients, sender_addr=None):
    """
    Broadcast a message to all connected clients except the sender.
    """
    for client in clients:
        if client != sender_addr:
            server.sendto(message.encode(), client)

def run_server():
    server_ip = "103.127.136.131"
    server_port = 8000

    # Create and bind the server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind((server_ip, server_port))
        print(f"Server binded on {server_ip}:{server_port}")
    except socket.error as e:
        print(f"Failed to bind server: {e}")
        return

    clients = []
    usernames = []

    while True:
        try:
            # Receive data from clients
            data, addr = server.recvfrom(BUFFER_SIZE)
            data = data.decode()

            # Handle new client connections
            if addr not in clients:
                clients.append(addr)
                usernames.append(data)
                print(f"New client: {data} from {addr[0]}")

                # Broadcast the connection message to all other clients
                connection_message = f"{data} has connected."
                broadcast_message(server, connection_message, clients, addr)

            # Handle client disconnection
            elif data.lower() == "exit":
                idx = clients.index(addr)
                disconnecting_user = usernames[idx]
                print(f"Client {disconnecting_user} disconnected.")
                
                # Broadcast the disconnection message to all other clients
                disconnection_message = f"{disconnecting_user} has disconnected."
                broadcast_message(server, disconnection_message, clients, addr)

                # Remove the client from the list
                clients.pop(idx)
                usernames.pop(idx)

            # Broadcast regular messages
            else:
                idx = clients.index(addr)
                msg = f"{usernames[idx]} says: {data}"
                print(msg)
                broadcast_message(server, msg, clients, addr)

        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


try:
    run_server()
except KeyboardInterrupt:
    print("Server stopped.")
