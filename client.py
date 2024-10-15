import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

BUFFER_SIZE = 1024

class ClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("UDP Chat Client")
        
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Entry area for typing messages
        self.message_entry = tk.Entry(master)
        self.message_entry.pack(padx=10, pady=10, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)

        # Buttons for sending and exiting
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.exit_button = tk.Button(master, text="Exit", command=self.exit_chat)
        self.exit_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Initialize the client socket
        self.server_ip = "103.127.136.131"  # Replace with your server IP
        self.server_port = 8000  # Replace with your server port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Get the username
        self.username = simpledialog.askstring("Username", "Enter your username", parent=self.master)
        if self.username:
            self.client_socket.sendto(self.username.encode(), (self.server_ip, self.server_port))

        # Start a thread to listen for incoming messages
        self.running = True
        self.listen_thread = threading.Thread(target=self.listen_for_messages)
        self.listen_thread.start()

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            try:
                # Send the message to the server
                self.client_socket.sendto(message.encode(), (self.server_ip, self.server_port))
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")

    def listen_for_messages(self):
        while self.running:
            try:
                # Receive messages from the server
                data, addr = self.client_socket.recvfrom(BUFFER_SIZE)
                message = data.decode()

                # Update the chat area with the new message
                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, message + "\n")
                self.chat_area.yview(tk.END)
                self.chat_area.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to receive message: {e}")
                break

    def exit_chat(self):
        try:
            # Send 'exit' message to notify the server
            self.client_socket.sendto("exit".encode(), (self.server_ip, self.server_port))
            self.running = False
            self.client_socket.close()
            self.master.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to exit: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = ClientGUI(root)
    root.mainloop()
