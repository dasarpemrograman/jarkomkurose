              if msg == "exit":
                        # Remove client from dictionaries and acknowledge their exit
                        self.clients[addr][0] += 1
                        ack_msg = f"ACK {self.clients[addr][0]}".encode()
                        self.server_socket.sendto(ack_msg, addr)
                        # Clean up client data
                        del self.clients[addr]
                        del self.received_data[addr]
                        return