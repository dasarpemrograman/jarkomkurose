import socket
import threading

class UDPClient:
    def __init__(self, host='127.0.0.1', port=12345):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(2.0)
        self.sequence_number = 0
        self.username = None

    def start(self):
        password = input("Enter server password: ")
        self.client_socket.sendto(password.encode(), self.server_address)

        # Wait for server's response
        response, _ = self.client_socket.recvfrom(1024)
        if response.decode() == "Password accepted. Please send your username.":
            self.handle_username()
        else:
            print(response.decode())

    def handle_username(self):
        while True:
            username = input("Enter your username: ")
            self.client_socket.sendto(username.encode(), self.server_address)

            response, _ = self.client_socket.recvfrom(1024)
            response_message = response.decode()

            if response_message == "Username accepted. Welcome!":
                print(response_message)
                self.username = username
                break
            else:
                print(response_message)  # "Username already taken."

        # Start message handling
        self.start_message_handling()

    def start_message_handling(self):
        # Start thread for receiving messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Handle sending messages
        while True:
            message = input("Enter message (/msg <username> <message> for private): ")
            self.send_message(message)

    def send_message(self, message):
        message_with_seq = f"{self.sequence_number}:{message}"
        self.client_socket.sendto(message_with_seq.encode(), self.server_address)

        # Wait for ACK
        while True:
            try:
                ack, _ = self.client_socket.recvfrom(1024)
                ack_message = ack.decode()
                if ack_message.startswith("ACK:"):
                    ack_sequence_number = int(ack_message.split(":")[1])
                    if ack_sequence_number == self.sequence_number:
                        self.sequence_number += 1
                        break
            except socket.timeout:
                print("No ACK received, resending message...")
                self.client_socket.sendto(message_with_seq.encode(), self.server_address)

    def receive_messages(self):
        while True:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                print(data.decode())
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

# Run the client
if __name__ == "__main__":
    host = input("Masukkan host: ")
    port = int(input("Masukkan port: "))
    client = UDPClient(host,port)
    client.start()
