import socket


def main():
    replica_addresses = [("localhost", 5001), ("localhost", 5002)]

    while True:
        print("\n---------------------------")
        print("Escolha uma operação:")
        print("1. Depósito")
        print("2. Saque")
        print("3. Transferência")
        print("4. Consultar Saldo")
        print("---------------------------")

        opcao = input("\nDigite o número da operação: ")
        conta = input("Digite o número da conta: ")

        if opcao in ["1", "2", "3"]:
            valor = input("Digite o valor: ")
            if opcao == "3":
                conta_destino = input("Digite a conta destino: ")

        elif opcao != "4":
            print("Opção inválida")
            continue

        print("\n")

        if opcao in ["1", "2"]:
            message = f"{opcao},{conta},{valor}"
        elif opcao == "3":
            message = f"{opcao},{conta},{valor},{conta_destino}"
        elif opcao == "4":
            message = f"{opcao},{conta}"

        responses = []
        for address in replica_addresses:
            response = send_message(address, message)
            responses.append(response)

        for response in responses:
            print(response)


def send_message(address, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)
        s.sendall(message.encode())
        response = s.recv(1024).decode()
        return response


if __name__ == "__main__":
    main()
