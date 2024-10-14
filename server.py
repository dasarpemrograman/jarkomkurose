# Import library wis
import socket

# Definisi fungsi jalanin server wis
def run_server():
    # Definisikan ajah
    server_ip = "127.0.0.1"
    port = 8000

    # Buat objek socket
    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    # Bind server ke IP dan port "Melayani di port dan IP tersebut"
    server.bind((server_ip,port))

    # Dengerin di port
    print("Server listening on",port)

    while True:
        # Menerima data dari klien
        data, addr = server.recvfrom(1024)  # Buffer size is 1024 bytes
        print(f"Received message: {data.decode()} from {addr}")


run_server()