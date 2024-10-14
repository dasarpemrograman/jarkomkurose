import socket
import threading

def receive_message(client):
    while True:
        try:
            msg, addr = client.recvfrom(1024)
            print(f"\nFrom {addr}: {msg.decode()}\n", end="")
        except:
            break        

def send_message(client, server_ip, server_port):
    while True:
        msg = input("Masukkan pesan: ")
        if msg == "exit":
            client.close()
            break
        client.sendto(msg.encode(), (server_ip, server_port))


def run_server():
    server_ip = "192.168.18.39"
    server_port = 8000
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.connect((server_ip, server_port))
    print(f"Client connected to {server_ip}:{server_port}")

    receiver = threading.Thread(target=receive_message, args=(client,))
    sender = threading.Thread(target=send_message, args=(client, server_ip, server_port))

    receiver.start()
    sender.start()

    receiver.join()
    sender.join()

    print("Closed!")

run_server()