import socket
import threading

class UDPClient:
    def __init__(self, host='udp.alfikrona.com', port=9000, max_retries=3):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(5.0)  # 5 seconds timeout for ACKs or responses
        self.sequence_number = 0
        self.username = None
        self.max_retries = max_retries  # Maximum number of retries for unacknowledged messages

    def start(self):
        password = input("Enter server password: ").strip()
        self.client_socket.sendto(password.encode(), self.server_address)

        # Wait for server's response
        try:
            response, _ = self.client_socket.recvfrom(1024)
            if response.decode() == "Password accepted. Please send your username.":
                self.handle_username()
            else:
                print(response.decode())
        except socket.timeout:
            print("Server not responding. Exiting.")
            return

    def handle_username(self):
        while True:
            username = input("Enter your username: ").strip()
            if len(username) == 0:
                print("Username cannot be empty. Please try again.")
                continue

            self.client_socket.sendto(username.encode(), self.server_address)

            try:
                response, _ = self.client_socket.recvfrom(1024)
                response_message = response.decode()

                if response_message == "Username accepted. Welcome!":
                    print(response_message)
                    self.username = username
                    break
                else:
                    print(response_message)  # "Username already taken or invalid."
            except socket.timeout:
                print("Server not responding to username submission. Retrying...")

        # Start message handling
        self.start_message_handling()

    def start_message_handling(self):
        # Start thread for receiving messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Handle sending messages
        while True:
            message = input("Enter message (/msg <username> <message> for private): ").strip()
            self.send_message(message)

    def send_message(self, message):
        if len(message) == 0:
            print("Cannot send an empty message.")
            return
        
        retries = 0
        message_with_seq = f"{self.sequence_number}:{message}"
        while retries < self.max_retries:
            self.client_socket.sendto(message_with_seq.encode(), self.server_address)

            try:
                # Wait for ACK
                ack, _ = self.client_socket.recvfrom(1024)
                ack_message = ack.decode()
                if ack_message.startswith("ACK:"):
                    ack_sequence_number = int(ack_message.split(":")[1])
                    if ack_sequence_number == self.sequence_number:
                        self.sequence_number += 1
                        print(f"Message sent successfully with Seq: {self.sequence_number}")
                        return
            except socket.timeout:
                print(f"No ACK received for message. Retrying ({retries+1}/{self.max_retries})...")
                retries += 1
        
        print(f"Failed to send message after {self.max_retries} attempts. Giving up.")

    def receive_messages(self):
        while True:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                print(data.decode())
            except socket.timeout:
                print("Timed out waiting for messages from the server.")
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

# Run the client
if __name__ == "__main__":
    client = UDPClient()
    client.start()
