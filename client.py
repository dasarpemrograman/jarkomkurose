import socket
import threading

class ReliableUDPClient:
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.seq_num = 0  # Start with sequence number 1
        self.lock = threading.Lock()  # Lock to manage access to the sequence number
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True  # Control flag for threads
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def send_message(self, message):
        # Check if the message is longer than 512 bytes
        chunk_size = 512
        if len(message) > chunk_size:
            # Send a special code to indicate long message
            self.send_single_message("LONG_MESSAGE")

            # Send the message in chunks
            for i in range(0, len(message), chunk_size):
                chunk = message[i:i + chunk_size]
                print(f"Sending chunk: {chunk}")
                self.send_single_message(chunk)

            # Send a special code to indicate the end of the message
            self.send_single_message("END_MESSAGE")
        else:
            # For regular messages
            self.send_single_message(message)

    def send_single_message(self, message):
        while True:
            msg_with_seq = f"{self.seq_num} {message}".encode()
            print(f"Sending: {msg_with_seq.decode()}")

            # Send message
            try:
                self.client_socket.sendto(msg_with_seq, self.server_address)

                # Wait for acknowledgment
                self.client_socket.settimeout(2)  # Timeout for waiting for an ACK
                ack, _ = self.client_socket.recvfrom(1024)
                ack_num = int(ack.decode().split()[1])  # Get the acknowledgment number
                print(f"Received ACK: {ack.decode()}")

                if ack_num == self.seq_num + 1:
                    break  # Exit loop if ACK matches the sent seq_num
            except socket.timeout:
                print("No ACK received. Resending message...")
            except ValueError as ve:
                print(f"Error decoding ACK: {ve}")
            except OSError as oe:
                print(f"Socket error: {oe}")
                break  # Exit loop on socket error

        # Increment the sequence number for the next message or chunk
        with self.lock:
            self.seq_num += 1

    def stop(self):
        self.running = False
        self.client_socket.close()
    
    def receive_messages(self):
        while self.running:
            try:
                self.client_socket.settimeout(1)  # Set a timeout to allow checking self.running
                data, _ = self.client_socket.recvfrom(1024)
                message = data.decode()
                if message.startswith("ACK"):
                    continue  # Skip printing ACKs
                print(f"\nReceived: {message}")
                print("Enter a message to send (or 'exit' to quit): ", end='', flush=True)
            except socket.timeout:
                continue  # Just skip if a timeout occurs
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def start(self):
        while self.running:
            user_input = input("Enter a message to send (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                self.running = False
                break
            self.send_message(user_input)

        self.stop()

if __name__ == "__main__":
    client = ReliableUDPClient('localhost', 12345)
    client.start()