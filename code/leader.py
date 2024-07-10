import socket
import sys
import threading


def main():
    acceptor_addresses = [("localhost", 7001), ("localhost", 7002), ("localhost", 7003)]
    listen_address = ("localhost", int(sys.argv[1]))

    threading.Thread(target=listen_for_replicas, args=(listen_address, acceptor_addresses)).start()


def listen_for_replicas(listen_address, acceptor_addresses):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(listen_address)
        s.listen()
        print(f"Leader listening on {listen_address}")

        while True:
            conn, addr = s.accept()
            with conn:
                message = conn.recv(1024).decode()
                print(f"Recebido de {addr}: {message}")
                if message.startswith("4"):  # Consulta de saldo
                    response = send_message(acceptor_addresses[0], message)
                    conn.sendall(response.encode())
                else:
                    results = []
                    for acceptor_address in acceptor_addresses:
                        response = send_message(acceptor_address, message)
                        results.append(response)
                    consensus = all(r == "ACK" for r in results)
                    conn.sendall(b"ACK" if consensus else b"NACK")


def send_message(address, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)
        s.sendall(message.encode())
        response = s.recv(1024).decode()
        return response


if __name__ == "__main__":
    main()
