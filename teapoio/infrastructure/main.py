from teapoio.domain.crianca import Crianca
from teapoio.domain.responsavel import Responsavel

def main():
    # Criando responsável
    resp = Responsavel("Maria", 35, "111.222.333-44", "maria@email.com", "9999-2222", "Mãe", None, 2)

    # Criando crianças
    crianca1 = Crianca("Lucas", 8, "123.456.789-00", "lucas@email.com", "9999-0000", "Maria", 2)
    crianca2 = Crianca("Ana", 6, "987.654.321-00", "ana@email.com", "9999-1111", "Maria", 1)

    # Adicionando crianças ao responsável
    resp.adicionar_crianca(crianca1)
    resp.adicionar_crianca(crianca2)

    # Listando informações das crianças
    print("Responsável:", resp.nome, "-", resp.tipo_responsavel)
    print("Crianças:")
    for c in resp.listar_criancas():
        print(f"Nome: {c.nome}\n, Idade: {c.idade}, Nível de suporte: {c.nivel_suporte}")

if __name__ == "__main__":
    main()

# Pra rodar: python -m teapoio.infrastructure.main
