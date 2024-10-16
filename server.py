import socket
import threading

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12345, password='secret123'):
        self.host = host
        self.port = port
        self.password = password
        self.clients = {}  # Store active clients as {address: username}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def start(self):
        """Start the server and begin listening for messages."""
        self.server_socket.bind((self.host, self.port))
        print(f"Server started on {self.host}:{self.port}")
        self.listen()

    def listen(self):
        """Continuously listen for messages from clients."""
        while True:
            try:
                data, client_address = self.server_socket.recvfrom(1024)
                self.handle_message(data.decode('utf-8'), client_address)
            except Exception as e:
                print(f"Error receiving message: {e}")

    def handle_message(self, message, client_address):
        """Process incoming messages based on their command."""
        if message.startswith("/join "):
            self.handle_join(message, client_address)
        elif client_address not in self.clients:
            self.send_message("Error: Please join using /join <username> <password>", client_address)
        elif message.startswith("/quit"):
            self.handle_quit(client_address)
        elif message.startswith("/msg "):
            self.handle_private_message(message, client_address)
        else:
            self.broadcast(f"{self.clients[client_address]}: {message}", client_address)

    def handle_join(self, message, client_address):
        """Process a client's join request with username and password."""
        try:
            _, username, password = message.split(' ')
            if password == self.password:
                self.clients[client_address] = username
                self.send_message(f"Welcome to the chat, {username}!", client_address)
                self.broadcast(f"{username} has joined the chat.", client_address)
            else:
                self.send_message("Error: Invalid password.", client_address)
        except ValueError:
            self.send_message("Error: Invalid join command. Use /join <username> <password>", client_address)

    def handle_quit(self, client_address):
        """Handle a client leaving the chat."""
        username = self.clients.pop(client_address, None)
        if username:
            self.broadcast(f"{username} has left the chat.", client_address)

    def handle_private_message(self, message, sender_address):
        """Send a private message from one user to another."""
        try:
            _, target_username, private_message = message.split(' ', 2)
            sender_username = self.clients[sender_address]
            self.send_private_message(sender_username, target_username, private_message, sender_address)
        except ValueError:
            self.send_message("Error: Invalid private message format. Use /msg <username> <message>", sender_address)

    def send_private_message(self, sender_username, target_username, message, sender_address):
        """Send a private message to the target username if they exist."""
        for client_address, username in self.clients.items():
            if username == target_username:
                self.send_message(f"Private from {sender_username}: {message}", client_address)
                return
        self.send_message(f"Error: User {target_username} not found.", sender_address)

    def broadcast(self, message, sender_address):
        """Broadcast a message to all clients except the sender."""
        for client_address in self.clients:
            if client_address != sender_address:
                self.send_message(message, client_address)

    def send_message(self, message, client_address):
        """Send a message to a specific client."""
        self.server_socket.sendto(message.encode('utf-8'), client_address)

if __name__ == "__main__":
    server = ChatServer()
    server.start()
