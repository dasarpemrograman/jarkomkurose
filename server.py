import socket
import threading

class UDPServer:
    def __init__(self, host='udp.alfikrona.com', port=9000, password="securepassword"):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        self.password = password
        self.clients = {}  # {client_address: {'username': <username>, 'sequence_number': <seq_num>}}
        self.usernames_to_addresses = {}  # {username: client_address}

    def start(self):
        print(f"Server started on {self.server_socket.getsockname()}")
        while True:
            try:
                data, client_address = self.server_socket.recvfrom(1024)
                message = data.decode()
                if client_address not in self.clients:
                    # Expecting the password for a new connection
                    self.handle_new_connection(client_address, message)
                else:
                    # Handle client messages
                    self.handle_client_message(client_address, message)
            except Exception as e:
                print(f"Error in server: {e}")

    def handle_new_connection(self, client_address, message):
        """Handle new client connection by validating password and checking for unique username."""
        if message == self.password:
            self.server_socket.sendto("Password accepted. Please send your username.".encode(), client_address)
            username_data, _ = self.server_socket.recvfrom(1024)
            username = username_data.decode()

            # Ensure unique username
            while username in self.usernames_to_addresses:
                self.server_socket.sendto("Username already taken. Please choose another username.".encode(), client_address)
                username_data, _ = self.server_socket.recvfrom(1024)
                username = username_data.decode()

            # Register the client
            self.clients[client_address] = {'username': username, 'sequence_number': -1}
            self.usernames_to_addresses[username] = client_address
            self.server_socket.sendto("Username accepted. Welcome!".encode(), client_address)
            print(f"New client connected: {username} from {client_address}")

            # Start a new thread for this client
            threading.Thread(target=self.listen_to_client, args=(client_address,)).start()
        else:
            self.server_socket.sendto("Incorrect password. Connection refused.".encode(), client_address)

    def listen_to_client(self, client_address):
        """Handle continuous message reception and processing from a specific client."""
        client_info = self.clients[client_address]
        while True:
            try:
                data, _ = self.server_socket.recvfrom(1024)
                message = data.decode()
                sequence_number, msg = message.split(":", 1)
                sequence_number = int(sequence_number)

                # Check message order
                if sequence_number == client_info['sequence_number'] + 1:
                    client_info['sequence_number'] = sequence_number
                    self.handle_message(client_info['username'], client_address, msg)
                    # Send ACK
                    self.server_socket.sendto(f"ACK:{sequence_number}".encode(), client_address)
                else:
                    print(f"Out-of-order message from {client_address} (Seq: {sequence_number}).")
            except Exception as e:
                print(f"Error handling client {client_info['username']}: {e}")
                break

    def handle_message(self, username, client_address, message):
        """Process a message (broadcast or private)."""
        if message.startswith("/msg"):
            # Handle private message
            parts = message.split(" ", 2)
            if len(parts) == 3:
                recipient_username = parts[1]
                private_message = parts[2]
                self.send_private_message(username, recipient_username, private_message)
            else:
                print(f"Invalid private message format from {username}.")
        else:
            # Broadcast message
            self.broadcast_message(username, message)

    def broadcast_message(self, sender_username, message):
        """Broadcast a message to all connected clients."""
        full_message = f"{sender_username}: {message}"
        for client_address in self.clients:
            self.server_socket.sendto(full_message.encode(), client_address)

    def send_private_message(self, sender_username, recipient_username, message):
        """Send a private message to a specific client."""
        if recipient_username in self.usernames_to_addresses:
            recipient_address = self.usernames_to_addresses[recipient_username]
            full_message = f"Private from {sender_username}: {message}"
            self.server_socket.sendto(full_message.encode(), recipient_address)
        else:
            print(f"User {recipient_username} not found for private message.")

# Run the server
if __name__ == "__main__":
    server = UDPServer()
    server.start()