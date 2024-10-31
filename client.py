import socket
import threading
import time

class ReliableUDPClient:
    def __init__(self):
        self.server_address = ("",0)
        self.seq_num = 0  # Start with sequence number 1
        self.lock = threading.Lock()  # Lock to manage access to the sequence number
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True  # Control flag for threads
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()
        self.accepted = False
        self.connected = False
        self.name = ""

    def message_segmentation(self, message):
        # Check if the message is longer than 512 bytes
        chunk_size = 512
        if len(message) > chunk_size:
            # Send a special code to indicate long message
            self.send_message("LONG_MESSAGE")

            # Send the message in chunks
            for i in range(0, len(message), chunk_size):
                chunk = message[i:i + chunk_size]
                print(f"Sending chunk: {chunk}")
                self.send_message(chunk)

            # Send a special code to indicate the end of the message
            self.send_message("END_MESSAGE")
        else:
            # For regular messages
            self.send_message(message)

    def send_message(self, message):
        while True:
            msg_with_seq = f"{self.seq_num} {message}".encode()
            print(f"Sending: {msg_with_seq.decode()}")

            # Send message
            try:
                self.client_socket.sendto(msg_with_seq, self.server_address)

                # Wait for acknowledgment
                self.client_socket.settimeout(3)  # Timeout for waiting for an ACK
                ack, _ = self.client_socket.recvfrom(1024)
                ack_num = int(ack.decode().split()[1])  # Get the acknowledgment number
                print(f"Received ACK: {ack.decode()}")

                if ack_num == self.seq_num + 1:
                    break  # Exit loop if ACK matches the sent seq_num
            except socket.timeout:
                print("No ACK received. Resending message...")
                time.sleep(2)
            except ValueError as ve:
                print(f"Error decoding ACK: {ve}")
            except OSError as oe:
                print(f"Socket error: {oe}")
                break  # Exit loop on socket error

        # Increment the sequence number for the next message or chunk
        with self.lock:
            self.seq_num += 1
    
    def receive_messages(self):
        while self.running:
            try:
                self.client_socket.settimeout(1)  # Set a timeout to allow checking self.running
                data, _ = self.client_socket.recvfrom(1024)
                message = data.decode()
                if message.startswith("ACK"):
                    continue  # Skip printing ACKs
                print(f"\n{message}")
                print("> ", end='', flush=True)
            except socket.timeout:
                continue  # Just skip if a timeout occurs
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def start(self):
        while not self.connected:
            ip = input("Type your desired IP Address: ")
            port = input("Type the desired port: ")
            self.server_address = (ip,int(port))
            
            self.client_socket.sendto("SYN".encode(),self.server_address)
            try:
                self.client_socket.settimeout(2)
                data, _ = self.client_socket.recvfrom(1024)
                if data.decode() == "SYN":
                    self.connected = True
            except socket.timeout:
                print("the server you are trying to reach is currently offline")

        while not self.accepted:
            username = input("What is your name: ")
            password = input("What is the password: ")
            initial_message = f"ACC {username} {password}".encode()
            self.client_socket.sendto(initial_message, self.server_address)
            try:
                self.client_socket.settimeout(2)
                data, _ = self.client_socket.recvfrom(1024)
                if data.decode() == "ACC":
                    self.accepted = True
                    self.name = username
                    print("Welcome to SERN (Socket Emulation for Reliable Networking)")
                elif data.decode() == "INCORRECT":
                    print("incorrect password")
                elif data.decode() == "TAKEN":
                    print("username is already taken")
            except socket.timeout:
                print("server is not responding")

        while self.running:
            user_input = input("> ")
            if user_input.lower() == 'exit':
                while True:
                    self.client_socket.sendto("FIN".encode(),self.server_address)
                    try:
                        self.client_socket.settimeout(2)
                        data, _ = self.client_socket.recvfrom(1024)
                        if data.decode() == "FIN":
                            print("Thank you for using SERN, may goodness comes to your life in every alternative timelines.")
                            self.running = False
                            break
                    except socket.timeout:
                        print("server is not responding")

                    self.running = False
            else:
                self.message_segmentation(user_input)
                    

if __name__ == "__main__":
    client = ReliableUDPClient()
    client.start()