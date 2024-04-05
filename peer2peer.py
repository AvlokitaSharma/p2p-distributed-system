import socket
import threading
import os
import hashlib

PEER_PORT = 5000
FILE_DIRECTORY = "shared_files/"
PEERS = ["127.0.0.1:5001", "127.0.0.1:5002"]  # Example peer addresses




def get_file_index():
    return os.listdir(FILE_DIRECTORY)


def search_for_file(filename):
    for peer in PEERS:
        address, port = peer.split(":")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((address, int(port)))
                s.sendall(b"SEARCH " + filename.encode())
                response = s.recv(1024)
                if response == b"FOUND":
                    return peer
            except ConnectionRefusedError:
                continue
    return None


def handle_client(conn, addr):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        command, *args = data.decode().split()
        if command == "SEARCH":
            filename = args[0]
            if filename in get_file_index():
                conn.send(b"FOUND")
            else:
                conn.send(b"NOT FOUND")
        elif command == "GET":
            filename = args[0]
            with open(FILE_DIRECTORY + filename, 'rb') as f:
                conn.sendfile(f)
    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('0.0.0.0', PEER_PORT))
        server.listen()
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()



def request_file(filename, peer):
    address, port = peer.split(":")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((address, int(port)))
        s.sendall(b"GET " + filename.encode())
        with open(FILE_DIRECTORY + filename, 'wb') as f:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                f.write(data)



def calculate_checksum(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
