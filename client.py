import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

SERVER_IP = "103.127.136.131"
SERVER_PORT = 8000
ADDR = (SERVER_IP, SERVER_PORT)
PASSWORD = "inipassword"

class ChatClient:
    def __init__(self, root):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.root = root
        self.root.title("UDP Chat Client")

        # Create GUI components
        self.chat_window = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', width=50, height=20)
        self.chat_window.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.entry_message = tk.Entry(self.root, width=40)
        self.entry_message.grid(row=1, column=0, padx=10, pady=10)
        self.entry_message.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_chat)
        self.exit_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.username = self.prompt_username()
        if self.username:
            # Send the username and password to the server
            credentials = f"{self.username}:{PASSWORD}"
            self.client.sendto(credentials.encode(), ADDR)

            # Wait for the server's response about password validation
            response, _ = self.client.recvfrom(1024)
            response = response.decode()

            if response == "Password invalid":
                messagebox.showerror("Error", "Invalid password. Connection rejected by the server.")
                self.root.quit()  # Exit the app if the password is invalid
            else:
                # Start receiving messages in a new thread if connected successfully
                threading.Thread(target=self.receive_message, daemon=True).start()
        else:
            self.root.quit()

    def prompt_username(self):
        username = simpledialog.askstring("Username", "Enter your username:")
        return username

    def send_message(self, event=None):
        message = self.entry_message.get()
        if message:
            if message.lower() == "exit":
                self.exit_chat()
            else:
                self.client.sendto(message.encode(), ADDR)
                self.entry_message.delete(0, tk.END)

    def receive_message(self):
        while True:
            try:
                message, _ = self.client.recvfrom(1024)
                self.display_message(message.decode())
            except:
                self.display_message("Connection closed.")
                break

    def display_message(self, message):
        self.chat_window.config(state='normal')
        self.chat_window.insert(tk.END, message + "\n")
        self.chat_window.config(state='disabled')
        self.chat_window.yview(tk.END)

    def exit_chat(self):
        self.client.sendto("exit".encode(), ADDR)
        self.client.close()
        self.root.quit()

# Run the Tkinter GUI
if __name__ == "__main__":
    root = tk.Tk()
    client_app = ChatClient(root)
    root.mainloop()
