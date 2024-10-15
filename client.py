import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("UDP Chat Client")

        # Display for messages
        self.chat_display = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=15, width=50)
        self.chat_display.pack(padx=10, pady=10)
        self.chat_display.config(state=tk.DISABLED)

        # Input field for sending messages
        self.message_entry = tk.Entry(self.master, width=40)
        self.message_entry.pack(padx=10, pady=5)
        self.message_entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(self.master, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        # Close button
        self.close_button = tk.Button(self.master, text="Close", command=self.close_connection)
        self.close_button.pack(pady=5)

        self.server_ip = "103.127.136.131"
        self.server_port = 8000
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((self.server_ip, self.server_port))

        # Start the receiving thread
        self.receiver_thread = threading.Thread(target=self.receive_message)
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def receive_message(self):
        while True:
            try:
                msg, addr = self.client.recvfrom(1024)
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.insert(tk.END, f"From {addr}: {msg.decode()}\n")
                self.chat_display.config(state=tk.DISABLED)
                self.chat_display.yview(tk.END)
            except:
                break

    def send_message(self, event=None):
        msg = self.message_entry.get()
        if msg:
            self.client.sendto(msg.encode(), (self.server_ip, self.server_port))
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"You: {msg}\n")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.yview(tk.END)
            self.message_entry.delete(0, tk.END)
        if msg == "exit":
            self.close_connection()

    def close_connection(self):
        self.client.sendto("exit".encode(),self.server_ip)
        self.client.close()
        self.master.quit()

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
