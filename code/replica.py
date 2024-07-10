import socket
import sys
import threading


def main():
    replica_id = sys.argv[1]
    leader_addresses = [("localhost", 6001), ("localhost", 6002)]
    listen_address = ("localhost", int(replica_id))

    threading.Thread(target=listen_for_env, args=(listen_address, leader_addresses, replica_id)).start()


def listen_for_env(listen_address, leader_addresses, replica_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(listen_address)
        s.listen()
        print(f"Replica {replica_id} listening on {listen_address}")

        while True:
            conn, addr = s.accept()
            with conn:
                message = conn.recv(1024).decode()
                print(f"Recebido de {addr}: {message}")
                if message.startswith("4"):  # Consulta de saldo
                    response = send_message(leader_addresses[0], message)
                    conn.sendall(response.encode())
                else:
                    responses = []
                    for leader_address in leader_addresses:
                        response = send_message(leader_address, message)
                        responses.append(response)
                    consensus = all(r == "ACK" for r in responses)

                    operation = message.split(',')
                    # if consensus:
                    if operation[0] == "1":
                        response = f"\nReplica {replica_id}: efetuou depósito de {operation[2]} na conta {operation[1]}"
                    elif operation[0] == "2":
                        response = f"\nReplica {replica_id}: efetuou um saque de {operation[2]} na conta {operation[1]}"
                    elif operation[0] == "3":
                        response = f"\nReplica {replica_id}: efetuou transferência de {operation[2]} da conta {operation[1]} para conta {operation[3]}"
                    # else:
                    #     response = f"\nReplica {replica_id}: operação falhou"
                    conn.sendall(response.encode())


def send_message(address, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)
        s.sendall(message.encode())
        response = s.recv(1024).decode()
        return response


if __name__ == "__main__":
    main()
