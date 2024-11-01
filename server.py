import socket
import threading

class Server:
    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        print(f"Server is running on {host}:{port}")
        self.clients = {} 
        self.received_data = {} 
        self.lock = threading.Lock() 
        self.password = "elpsycongroo"

    def is_name_unique(self, new_name):
        for client_info in self.clients.values():
            if client_info[1] == new_name: 
                return False
        return True
        
    def start(self):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            with self.lock:
                if data.decode() == "SYN":
                    self.server_socket.sendto("SYN".encode(),addr)
                elif data.decode().startswith("ACC"):
                    if addr not in self.clients:
                        parts = data.decode().split(maxsplit=2)
                        username = parts[2]
                        password = parts[1]
                        if password == self.password and self.is_name_unique(username):
                            self.server_socket.sendto("ACC".encode(),addr)
                            self.clients[addr] = [0,username] 
                            self.received_data[addr] = "" 
                            threading.Thread(target=self.broadcast, args=(f"*{username} has joined the conversation*".encode(),addr), daemon=True).start()
                        elif password != self.password:
                            self.server_socket.sendto("INCORRECT".encode(),addr)
                        else:
                            self.server_socket.sendto("TAKEN".encode(),addr)
                    else:
                        self.server_socket.sendto("ACC".encode(),addr)
                elif data.decode() == "FIN":
                    self.server_socket.sendto("FIN".encode(),addr)
                    del self.clients[addr]
                    del self.received_data[addr]
                else:
                    threading.Thread(target=self.handle_client, args=(data, addr), daemon=True).start()

    def broadcast(self, message, sender_addr):
        with self.lock:
            for client in self.clients:
                if client != sender_addr: 
                    self.server_socket.sendto(f"{self.clients[sender_addr][1]} : {message.decode()}".encode(), client)
                    print(f"Broadcasted to {client}: {message.decode()}")

    def handle_client(self, data, addr):
        try:
            seq_num, msg = self.decode_message(data)
            with self.lock:
                if seq_num == self.clients[addr][0]:
                    if msg == "END_MESSAGE":
                        self.received_data[addr] = "" 
                    elif msg == "LONG_MESSAGE":
                        print(f"Receiving long message from {addr} (Seq: {seq_num})")
                    else:
                        print(f"Received from {addr}: {msg} (Seq: {seq_num})")
                        self.received_data[addr] += msg 

                    self.clients[addr][0] += 1

                    ack_msg = f"ACK {self.clients[addr][0]}".encode()
                    self.server_socket.sendto(ack_msg, addr)
                    threading.Thread(target=self.broadcast, args=(msg.encode(),addr), daemon=True).start()

                else:
                    print(f"Unexpected sequence number from {addr}: (Seq: {seq_num}). Expected: {self.clients[addr][0]}")
                    ack_msg = f"ACK {self.clients[addr][0]}".encode()
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
    server = Server('172.20.10.2', 12346) #change to your local network
    server.start()