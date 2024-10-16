import socket
import threading

class Server:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password
        self.clients = []
        self.usernames = []
        self.lock = threading.Lock()  # Ensure thread safety for shared data
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        try:
            self.server.bind((self.ip, self.port))
            print(f"Server binded to {self.ip}:{self.port}")
            self.listen()
        except Exception as e:
            print(f"Error starting server: {e}")

    def listen(self):
        while True:
            try:
                data, address = self.server.recvfrom(1024)
                threading.Thread(target=self.handle_client, args=(data, address), daemon=True).start()
            except Exception as e:
                print(f"Error receiving data: {e}")

    def handle_client(self, data, address):
        try:
            msg = data.decode()
            print(f"Received message from {address}: {msg}")

            if msg.startswith("/join "):
                self.join(msg, address)
            elif address not in self.clients:
                self.sendmsg("You have to join the chat first.", address)
            elif msg.startswith("/quit"):
                self.quit(address)
            elif msg.startswith("/msg "):
                self.chatone(msg, address)
            elif msg == "/list":
                self.send_active_users(address)
            else:
                self.chatall(f"{self.usn(address)}: {msg}", address)
        except Exception as e:
            print(f"Error handling client message: {e}")

    def join(self, message, address):
        parts = message.split(" ")
        if len(parts) < 3:
            self.sendmsg("Invalid join command. Usage: /join <username> <password>", address)
            return

        username = parts[1]
        password = parts[2]

        if password == self.password:
            with self.lock:
                self.clients.append(address)
                self.usernames.append(username)
            self.chatall(f"Gacor, {username} joined the chat!", address)
            self.sendmsg(f"Welcome, {username}!", address)
        else:
            self.sendmsg("You are not welcomed to the Steins;Gate.", address)

    def quit(self, address):
        usnm = self.usn(address)
        with self.lock:
            self.clients.remove(address)
            self.usernames.remove(usnm)
        self.chatall(f"{usnm} left the Gate of Steiner.", address)

    def chatone(self, message, sender_addr):
        parts = message.split(' ')
        if len(parts) < 3:
            self.sendmsg("Invalid private message format. Usage: /msg <username> <message>", sender_addr)
            return
        parts = message.split(' ', 3)
        username = parts[1]
        msg = parts[2]
        sender_usn = self.usn(sender_addr)

        if username in self.usernames:
            self.sendmsg(f"Private message from {sender_usn}: {msg}", self.adr(username))
        else:
            self.sendmsg(f"User {username} not found.", sender_addr)

    def chatall(self, message, sdr_addr):
        with self.lock:
            for tujuan in self.clients:
                if tujuan != sdr_addr:
                    self.sendmsg(message, tujuan)

    def sendmsg(self, msg, dest_addr):
        try:
            self.server.sendto(msg.encode(), dest_addr)
        except Exception as e:
            print(f"Error sending message: {e}")

    def usn(self, adr) -> str:
        with self.lock:
            idx = self.clients.index(adr)
        return self.usernames[idx]
    
    def adr(self, usn) -> str:
        with self.lock:
            idx = self.usernames.index(usn)
        return self.clients[idx]
    
    def send_active_users(self, address):
        with self.lock:
            if self.usernames:
                active_users = ", ".join(self.usernames)
                self.sendmsg(f"Active users: {active_users}", address)
            else:
                self.sendmsg("No active users.", address)

if __name__ == "__main__":
    server = Server("103.127.136.131", 8000, "steinsgate")
    server.start()
