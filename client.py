import socket

# Definisi fungsi untuk client
def run_client():
    # Definisikan IP dan port server
    server_ip = "192.168.18.40"
    port = 8000

    # Buat objek socket UDP
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    # Buat pesan untuk dikirim
    message = input()

    while message != "exit":
        try:
            # Kirim pesan ke server
            client.sendto(message.encode(), (server_ip, port))
            print(f"{message} sent to {server_ip}:{port}")

        except Exception as e:
            print(f"Error: {e}")
        message = input()

# Jalankan client
run_client()
