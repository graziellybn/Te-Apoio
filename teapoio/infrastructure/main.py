from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel

def main():
    # Criando responsável
    resp = Responsavel(
        nome="Maria",
        idade=35,
        cpf="111.222.333-44",
        email="maria@email.com",
        telefone="9999-2222",
        tipo_responsavel="Mãe",
        endereco=None,
        quant_criancas=2
    )

    # Criando crianças
    crianca1 = Crianca(
        nome="Lucas",
        idade=8,
        cpf="123.456.789-00",
        email="lucas@email.com",
        telefone="9999-0000",
        responsavel=resp,
        nivel_suporte="moderado"
    )

    crianca2 = Crianca(
        nome="Ana",
        idade=6,
        cpf="987.654.321-00",
        email="ana@email.com",
        telefone="9999-1111",
        responsavel=resp,
        nivel_suporte="baixo"
    )

    # Adicionando crianças ao responsável
    resp.adicionar_crianca(crianca1)
    resp.adicionar_crianca(crianca2)

    # Exibindo informações formatadas
    print("=== Responsável ===")
    print(f"Nome: {resp.nome}")
    print(f"Tipo: {resp.tipo_responsavel}")
    print("\n=== Crianças ===")
    for c in resp.listar_criancas():
        print(f"Nome: {c.nome}")
        print(f"Idade: {c.idade}")
        print(f"Nível de suporte: {c.nivel_suporte}")
        print("-" * 30)

if __name__ == "__main__":
    main()


# Pra rodar: python -m teapoio.infrastructure.main
