import socket

BUFFER_SIZE = 1024

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

            # Handle client disconnection
            elif data.lower() == "exit":
                idx = clients.index(addr)
                print(f"Client {usernames[idx]} disconnected.")
                clients.pop(idx)
                usernames.pop(idx)

            # Broadcast message to all other clients
            else:
                idx = clients.index(addr)
                msg = f"{usernames[idx]} says: {data}"
                for client in clients:
                    if client != addr:
                        server.sendto(msg.encode(), client)

        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("Server stopped.")