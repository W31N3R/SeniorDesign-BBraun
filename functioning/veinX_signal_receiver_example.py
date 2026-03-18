import socket

# Set up a socket to receive signals
HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen for signals

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Listening for signals on {HOST}:{PORT}...")

while True:
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
    message = data.decode()
    print(f"Received signal: {message}")