import socket
import threading

def receive_message(client):
    while True:
        msg, addr = client.recvfrom(1024)
        print(f"From {addr}: {msg.decode()}")        

def send_message(client, server_ip, server_port):
    while True:
        msg = input("Masukkan pesan: ")
        client.sendto(msg.encode(), (server_ip, server_port))

def run_server():
    server_ip = "172.20.10.5"
    server_port = 8000
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind((server_ip, server_port))
    print(f"Client connected to {server_ip}:{server_port}")

    receiver = threading.Thread(target=receive_message, args=(client,))
    sender = threading.Thread(target=send_message, args=(client, server_ip, server_port))

    receiver.start()
    sender.start()

    receiver.join()
    sender.join()

run_server()
