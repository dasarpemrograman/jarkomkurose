import socket
import threading

class ChatClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.joined = False

    def start(self, username, password):
        """Start the client and attempt to join the chat server."""
        while not self.joined:
            self.send_message(f"/join {username} {password}")
            if self.check_server_response():
                threading.Thread(target=self.receive_messages, daemon=True).start()
                self.handle_user_input()
            else:
                retry = input("Wrong password. Would you like to retry? (y/n): ").strip().lower()
                if retry != 'y':
                    print("Exiting...")
                    break
                password = input("Enter the chatroom password: ")

    def check_server_response(self):
        """Check the server's response after sending the join request."""
        try:
            data, _ = self.client_socket.recvfrom(1024)
            response = data.decode()

            if "You are not welcomed to the Steins;Gate" in response:
                print("Server: Wrong password.")
                return False
            else:
                print(response)  # Success message from the server
                self.joined = True
                return True
        except Exception as e:
            print(f"Error receiving message: {e}")
            return False

    def handle_user_input(self):
        """Continuously handle user input and send messages to the server."""
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
        try:
            self.client_socket.sendto(message.encode(), (self.server_host, self.server_port))
        except Exception as e:
            print(f"Error sending message: {e}")

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
    # Ask the user for the IP and port they want to connect to
    server_ip = input("Enter the server IP address: ")
    server_port = int(input("Enter the server port: "))

    username = input("Enter your username: ")
    password = input("Enter the chatroom password: ")

    client = ChatClient(server_ip, server_port)
    client.start(username, password)
