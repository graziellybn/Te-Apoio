import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from teapoio.domain.models.pessoa import Pessoa


def teste_pessoa_ok():
    pessoa = Pessoa("João Silva", "15/03/1990")
    assert pessoa.nome == "João Silva"
    assert isinstance(pessoa.id_pessoa, str)
    assert len(pessoa.id_pessoa) == 6
    info = pessoa.exibir_informacoes()
    info_normalizado = info.lower().replace("ç", "c").replace("õ", "o").replace("ã", "a")
    assert "informacoes" in info_normalizado
    print(info)


def teste_idade_status():
    pessoa = Pessoa("Maria Santos", "10/05/2010")
    idade = pessoa.calcular_idade()
    status = pessoa.obter_status_idade()

    assert idade >= 0
    assert status in {"Responsável", "Criança"}
    assert pessoa.verificar_maioridade() == (idade >= 18)
    print(f"Idade {idade} - {status}")


def teste_crianca():
    pessoa = Pessoa("Ana Souza", "10/05/2015")
    assert pessoa.verificar_maioridade() is False
    assert pessoa.obter_status_idade() == "Criança"
    print(f"Teste criança: {pessoa.nome} -> {pessoa.obter_status_idade()}")


def teste_nome_invalido():
    try:
        Pessoa("João123", "15/03/1990")
        assert False, "Nome inválido deveria dar erro"
    except ValueError as e:
        print(f"Nome inválido: {e}")


def teste_data_invalida():
    try:
        Pessoa("João Silva", "31/02/1990")
        assert False, "Data inválida deveria dar erro"
    except ValueError as e:
        print(f"Data inválida: {e}")


if __name__ == "__main__":
    teste_pessoa_ok()
    teste_idade_status()
    teste_crianca()
    teste_nome_invalido()
    teste_data_invalida()
