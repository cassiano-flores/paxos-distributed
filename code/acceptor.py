import socket
import sys
import threading

accounts = {}


def main():
    listen_address = ("localhost", int(sys.argv[1]))

    threading.Thread(target=listen_for_leaders, args=(listen_address,)).start()


def listen_for_leaders(listen_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(listen_address)
        s.listen()
        print(f"Acceptor listening on {listen_address}")

        while True:
            conn, addr = s.accept()
            with conn:
                message = conn.recv(1024).decode()
                print(f"Recebido de {addr}: {message}")

                operation = message.split(',')
                if operation[0] == "1":  # Depósito
                    value = int(operation[2])
                    accounts[operation[1]] = accounts.get(operation[1], 0) + value
                    response = f"Depósito de {value} na conta {operation[1]} efetuado"

                elif operation[0] == "2":  # Saque
                    value = int(operation[2])
                    if accounts.get(operation[1], 0) >= value:
                        accounts[operation[1]] -= value
                        response = f"Saque de {value} na conta {operation[1]} efetuado"
                    else:
                        response = "Saldo insuficiente"

                elif operation[0] == "3":  # Transferência
                    value = int(operation[2])
                    if accounts.get(operation[1], 0) >= value:
                        accounts[operation[1]] -= value
                        accounts[operation[3]] = accounts.get(operation[3], 0) + value
                        response = f"Transferência de {value} da conta {operation[1]} para conta {operation[3]} efetuada"
                    else:
                        response = "Saldo insuficiente"

                elif operation[0] == "4":  # Consultar Saldo
                    balance = {accounts.get(operation[1], 0)}
                    balance = next(iter(balance))
                    if balance != 0:
                        balance = balance / 4

                    response = f"Conta {operation[1]} possui saldo de {balance}"
                    conn.sendall(response.encode())
                    continue

                conn.sendall(b"ACK")


if __name__ == "__main__":
    main()
