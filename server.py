import socket
import threading

class ReliableUDPServer:
    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        print(f"Server is running on {host}:{port}")
        self.clients = {}  # Store client addresses and their expected seq numbers
        self.received_data = {}  # Store received data for each client
        self.lock = threading.Lock()  # Add a lock for thread safety

    def start(self):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            with self.lock:
                if addr not in self.clients:
                    self.clients[addr] = 0  # Initialize client's expected seq number
                    self.received_data[addr] = ""  # Initialize received data for this client
            threading.Thread(target=self.handle_client, args=(data, addr), daemon=True).start()
            threading.Thread(target=self.broadcast, args=(data,addr), daemon=True).start()

    def broadcast(self, message, sender_addr):
        with self.lock:
            for client in self.clients:
                if client != sender_addr:  # Don't send the message back to the sender
                    self.server_socket.sendto(message, client)
                    print(f"Broadcasted to {client}: {message.decode()}")

    def handle_client(self, data, addr):
        try:
            seq_num, msg = self.decode_message(data)

            with self.lock:
                # Check if this is the expected sequence number for this client
                if seq_num == self.clients[addr]:
                    # Process the received message
                    if msg == "END_MESSAGE":
                        print(f"Full message received from {addr}. Broadcasting.")
                        full_message = f"Message from {addr}: {self.received_data[addr]}".encode()
                        self.broadcast(full_message, addr)  # Broadcast the complete message
                        self.received_data[addr] = ""  # Reset for the next message
                    elif msg == "LONG_MESSAGE":
                        print(f"Receiving long message from {addr} (Seq: {seq_num})")
                    else:
                        print(f"Received from {addr}: {msg} (Seq: {seq_num})")
                        self.received_data[addr] += msg  # Accumulate chunks

                    # Increment the expected sequence number for this client
                    self.clients[addr] += 1

                    # Send acknowledgment back to the client
                    ack_msg = f"ACK {self.clients[addr]}".encode()
                    self.server_socket.sendto(ack_msg, addr)

                else:
                    print(f"Unexpected sequence number from {addr}: (Seq: {seq_num}). Expected: {self.clients[addr]}")
                    ack_msg = f"ACK {self.clients[addr]}".encode()
                    self.server_socket.sendto(ack_msg, addr)

        except ValueError as ve:
            print(f"Error decoding message from {addr}: {ve}. Data received: {data.decode()}")

    def decode_message(self, data):
        parts = data.decode().split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError("Invalid message format. Expected 'seq_num msg'.")
        seq_num = int(parts[0])
        msg = parts[1]
        return seq_num, msg

if __name__ == "__main__":
    server = ReliableUDPServer('localhost', 12346)
    server.start()