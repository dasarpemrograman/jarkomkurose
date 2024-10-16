import socket
import threading

class ChatClient:
    def __init__(self, server_host='103.127.136.131', server_port=8000):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self, username, password):
        """Start the client by joining the server."""
        self.send_message(f"/join {username} {password}")
        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.handle_user_input()

    def handle_user_input(self):
        """Continuously handle user input and send it to the server."""
        while True:
            message = input()
            if message == "/quit":
                self.send_message("/quit")
                print("You have left the chat.")
                break
            else:
                self.send_message(message)

    def send_message(self, message):
        """Send a message to the server."""
        self.client_socket.sendto(message.encode(), (self.server_host, self.server_port))

    def receive_messages(self):
        """Continuously receive messages from the server."""
        while True:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                print(data.decode())
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter the chatroom password: ")

    client = ChatClient()
    client.start(username, password)
