import socket

def run_server():
    server_ip = "192.168.18.39"
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
        print(f"Received message from {addr}: {data.decode()}")

        for client in clients:
            if client != addr:
                server.sendto(data,client)


run_server()
