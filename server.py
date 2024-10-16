import socket
import threading

class Server:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password
        self.clients = []
        self.usernames = []
        self.server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def start(self):
        self.server.bind((self.ip,self.port))
        print(f"Server binded to {self.ip}:{self.port}")
        self.listen()

    def listen(self):
        while True:
            data, address = self.server.recvfrom(1024)
            threading.Thread(target=self.handle_client, args=(data, address)).start()

    def handle_client(self, data, address):
        msg : str = data.decode()
        print(f"Received message from {address}: {msg}")

        if msg.startswith("/join "):
            self.join(msg,address)
        elif address not in self.clients:
            self.sendmsg("You have to join",address)
        elif msg.startswith("/quit"):
            self.quit(address)
        elif msg.startswith("/msg "):
            self.chatone(msg,address)
        else:
            self.chatall(f"{self.usn(address)}: {msg}",address)

    def join(self, message:str, address):
        parts = message.split(" ")
        if len(parts) < 3:
            self.sendmsg("Invalid join command",address)
            return
        
        username = parts[1]
        password = parts[2]

        if password == self.password:
            self.clients.append(address)
            self.usernames.append(username)
            self.chatall(f"Gacor, {username} join ges!",address)
            self.sendmsg(f"Welcome, {username}!",address)
        else:
            self.sendmsg("You are not welcomed to the Steins;Gate",address)

    def quit(self, address):
        usnm = self.usn(address)
        self.clients.remove(address)
        self.usernames.remove(self.usn(address))
        self.chatall(f"{usnm} left the Gate of Steiner",address)

    def chatone(self, message:str, sender_addr):
        parts = message.split(' ')
        if len(parts) < 3:
            self.sendmsg("Error",sender_addr)
            return
        
        parts = message.split(' ',3)
        username = parts[1]
        msg = parts[2]
        sender_usn = self.usn(sender_addr)

        for tujuan in self.usernames:
            if tujuan == username:
                self.sendmsg(f"Pesan pribadi dari {sender_usn}: {msg}",self.adr(username))
                return
            
        self.sendmsg(f"User {username} tidak ditemukan.",sender_addr)

    def chatall(self, message, sdr_addr):
        for tujuan in self.clients:
            self.sendmsg(message,sdr_addr)

    def sendmsg(self, msg, dest_addr):
        msg = msg.encode()
        self.server.sendto(msg,dest_addr)

    def usn(self, adr) -> str:
        idx = self.clients.index(adr)
        return self.usernames[idx]
    
    def adr(self, usn) -> str:
        idx = self.usernames.index(usn)
        return self.clients[idx]

if __name__ == "__main__":
    server = Server("103.127.136.131",8000,"steinsgate")
    server.start()