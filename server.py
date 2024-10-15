import socket

BUFFER_SIZE = 1024
PASSWORD = "securepassword"  # Set your desired password here

def broadcast_message(server, message, clients, exclude_addr=None):
    """
    Broadcasts a message to all connected clients except the one excluded.
    """
    for client in clients:
        if client != exclude_addr:
            server.sendto(message.encode(), client)

def handle_new_client(server, data, addr, clients, usernames):
    """
    Handles the authentication of a new client and adds them to the client list.
    Broadcasts the connection if successful.
    """
    if ":" in data:
        username, password = data.split(":", 1)

        # Check if the password is correct
        if password == PASSWORD:
            clients.append(addr)
            usernames.append(username)
            msg = f"New client: {username} from {addr[0]} has joined the chat."
            print(msg)

            # Broadcast the new client connection to all other clients
            broadcast_message(server, msg, clients, exclude_addr=addr)

            # Confirm successful connection to the client
            server.sendto(f"Welcome {username}!".encode(), addr)
        else:
            # Notify client of incorrect password
            server.sendto("Invalid password.".encode(), addr)
            print(f"Failed login attempt from {addr[0]}")
    else:
        # Reject connection if format is incorrect
        server.sendto("Invalid format. Use username:password.".encode(), addr)

def handle_client_message(server, data, addr, clients, usernames):
    """
    Handles a message sent by a connected client and broadcasts it to others.
    """
    if addr in clients:
        idx = clients.index(addr)
        msg = f"{usernames[idx]} says: {data}"
        broadcast_message(server, msg, clients, exclude_addr=addr)

def handle_client_disconnection(server, addr, clients, usernames):
    """
    Handles client disconnection and notifies others.
    """
    if addr in clients:
        idx = clients.index(addr)
        msg = f"Client {usernames[idx]} from {addr[0]} has left the chat."
        print(msg)

        # Broadcast the disconnection to all other clients
        broadcast_message(server, msg, clients)

        # Remove the client from the lists
        clients.pop(idx)
        usernames.pop(idx)

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
                handle_new_client(server, data, addr, clients, usernames)

            # Handle client disconnection
            elif data.lower() == "exit":
                handle_client_disconnection(server, addr, clients, usernames)

            # Handle client messages
            else:
                handle_client_message(server, data, addr, clients, usernames)

        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("Server stopped.")