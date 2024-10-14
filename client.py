import socket

# Definisi fungsi untuk client
def run_client():
    # Definisikan IP dan port server
    server_ip = "127.0.0.1"
    port = 8000

    # Buat objek socket UDP
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Buat pesan untuk dikirim
    message = "Hello, Server!"

    try:
        # Kirim pesan ke server
        client.sendto(message.encode(), (server_ip, port))
        print(f"Message sent to {server_ip}:{port}")

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Tutup koneksi socket
        client.close()

# Jalankan client
run_client()
