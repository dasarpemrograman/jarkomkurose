# Import library wis
import socket

# Definisi fungsi jalanin server wis
def run_server():
    # Definisikan ajah
    server_ip = "192.168.18.40"
    port = 8000
    clients = set()

    # Buat objek socket
    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    # Bind server ke IP dan port "Melayani di port dan IP tersebut"
    server.bind((server_ip,port))

    # Dengerin di port
    print("Server listening on",port)

    while True:
        # Menerima data dari klien
        data, addr = server.recvfrom(1024)
        clients.add(addr)  # Buffer size is 1024 bytes
        print(f"Received message: {data.decode()} from {addr}")
        print(clients)


run_server()