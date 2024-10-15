import socket

def run_server():
    server_ip = "103.127.136.131"
    server_port = 8000

    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server.bind((server_ip,server_port))
    print(f"Server binded on {server_ip}:{server_port}")
    clients = []

    while True:
        data, addr = server.recvfrom(1024)
        if addr not in clients:
            clients.append(addr)
            print(f"New client: {addr}")
        elif data.decode() == "exit":
            clients.remove(addr)
            print(f"{addr} closed connection.")
        print(f"Received message from {addr}: {data.decode()}")

        for client in clients:
            if client != addr:
                server.sendto(data,client)


run_server()
