import socket
import threading

SERVER_IP = "103.127.136.131"
SERVER_PORT = 8000
ADDR = (SERVER_IP, SERVER_PORT)

def sender(client, usn):
    while True:
        msg = input(f"{usn}: ")
        client.sendto(msg.encode(), ADDR)
        if msg == "exit":
            print("Exiting sender thread.")
            client.close()
            return

def receiver(client):
    while True:
        try:
            msg, _ = client.recvfrom(1024)
            print(msg.decode())
        except:
            print("Receiver thread exiting.")
            client.close()
            return

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    usn = input("Input username: ")
    client.sendto(usn.encode(), ADDR)

    send_thread = threading.Thread(target=sender, args=(client, usn))
    receive_thread = threading.Thread(target=receiver, args=(client,))

    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()

run_client()
