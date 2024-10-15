import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

BUFFER_SIZE = 1024

class ChatClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("UDP Chat Client")
        self.master.geometry("400x500")

        self.client_socket = None
        self.server_ip = "103.127.136.131"
        self.server_port = 8000
        self.username = ""
        self.password = ""

        # Username input
        self.label_username = tk.Label(master, text="Username:")
        self.label_username.pack(pady=5)
        self.entry_username = tk.Entry(master, width=30)
        self.entry_username.pack(pady=5)

        # Password input
        self.label_password = tk.Label(master, text="Password:")
        self.label_password.pack(pady=5)
        self.entry_password = tk.Entry(master, width=30, show="*")
        self.entry_password.pack(pady=5)

        # Connect button
        self.button_connect = tk.Button(master, text="Connect", command=self.connect_to_server)
        self.button_connect.pack(pady=10)

        # Chat window
        self.chat_window = scrolledtext.ScrolledText(master, state='disabled', width=50, height=15)
        self.chat_window.pack(padx=10, pady=10)

        # Message entry
        self.entry_message = tk.Entry(master, width=40)
        self.entry_message.pack(side=tk.LEFT, padx=10, pady=5)
        self.entry_message.config(state='disabled')

        # Send button
        self.button_send = tk.Button(master, text="Send", command=self.send_message, state='disabled')
        self.button_send.pack(side=tk.LEFT, padx=10, pady=5)

        # Disconnect button
        self.button_disconnect = tk.Button(master, text="Disconnect", command=self.disconnect_from_server, state='disabled')
        self.button_disconnect.pack(pady=10)

        self.receive_thread = None

    def connect_to_server(self):
        # Get username and password
        self.username = self.entry_username.get().strip()
        self.password = self.entry_password.get().strip()

        if not self.username or not self.password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        # Create socket and attempt connection
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        auth_message = f"{self.username}:{self.password}"
        self.client_socket.sendto(auth_message.encode(), (self.server_ip, self.server_port))

        # Wait for server's response
        response, _ = self.client_socket.recvfrom(BUFFER_SIZE)
        response = response.decode()

        if response.startswith("Welcome"):
            self.update_chat_window(response)
            self.entry_message.config(state='normal')
            self.button_send.config(state='normal')
            self.button_disconnect.config(state='normal')
            self.button_connect.config(state='disabled')

            # Start receiving messages
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
        else:
            messagebox.showerror("Error", response)

    def receive_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(BUFFER_SIZE)
                self.update_chat_window(message.decode())
            except socket.error:
                break

    def send_message(self):
        message = self.entry_message.get().strip()
        if message:
            self.client_socket.sendto(message.encode(), (self.server_ip, self.server_port))
            self.entry_message.delete(0, tk.END)

        # Disconnect if the message is "exit"
        if message.lower() == "exit":
            self.disconnect_from_server()

    def update_chat_window(self, message):
        self.chat_window.config(state='normal')
        self.chat_window.insert(tk.END, message + "\n")
        self.chat_window.config(state='disabled')
        self.chat_window.see(tk.END)

    def disconnect_from_server(self):
        if self.client_socket:
            self.client_socket.sendto("exit".encode(), (self.server_ip, self.server_port))
            self.client_socket.close()
            self.update_chat_window("You have disconnected.")
            self.entry_message.config(state='disabled')
            self.button_send.config(state='disabled')
            self.button_disconnect.config(state='disabled')
            self.button_connect.config(state='normal')


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()
