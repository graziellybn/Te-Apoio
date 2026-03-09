from datetime import date

import pytest

from teapoio.domain.models.calendario import CalendarioRotina


def test_calendario_inicia_com_data_atual():
    """Valida se o calendário inicia com a data atual selecionada"""
    calendario = CalendarioRotina()
    assert calendario.data_selecionada == date.today()


def test_calendario_permite_escolher_dia_mes_ano():
    """Valida se o calendário permite escolher um dia, mês e ano específicos e atualiza a data selecionada corretamente"""
    calendario = CalendarioRotina()
    hoje = date.today()
    dia = 1
    mes = 1
    ano = hoje.year

    data = calendario.selecionar_data(dia, mes, ano)

    assert data == date(ano, mes, dia)
    assert calendario.data_selecionada == date(ano, mes, dia)


def test_calendario_rejeita_data_invalida():
    """Valida se o calendário rejeita uma data inválida (ex: 31 de fevereiro) e lança um erro"""
    calendario = CalendarioRotina()
    ano = date.today().year

    with pytest.raises(ValueError):
        calendario.selecionar_data(31, 2, ano)


def test_calendario_rejeita_ano_diferente_do_atual():
    """Valida se o calendário rejeita um ano diferente do atual e lança um erro"""
    calendario = CalendarioRotina()
    ano_passado = date.today().year - 1

    with pytest.raises(ValueError):
        calendario.selecionar_data(1, 1, ano_passado)


def test_calendario_rejeita_data_futura():
    """Valida se o calendário rejeita uma data futura e lança um erro"""
    calendario = CalendarioRotina()
    amanha = date.today().fromordinal(date.today().toordinal() + 1)

    with pytest.raises(ValueError):
        calendario.selecionar_data(amanha.day, amanha.month, amanha.year)


def test_calendario_cria_rotina_na_data_selecionada():
    """Valida se o calendário cria uma rotina para a data selecionada e vincula corretamente o ID da criança e a data de referência"""
    calendario = CalendarioRotina()
    hoje = date.today()
    calendario.selecionar_data(hoje.day, hoje.month, hoje.year)

    rotina = calendario.criar_rotina_para_data("123456")

    assert rotina.id_crianca == "123456"
    assert rotina.data_referencia == hoje


def test_exibir_mes_retorna_texto_do_calendario():
    """Valida se o método exibir_mes retorna um texto do calendário contendo o mês e o ano corretos"""
    calendario = CalendarioRotina()
    ano_teste = date.today().year
    texto_mes = calendario.exibir_mes(3, ano_teste)

    assert str(ano_teste) in texto_mes
    assert "Março" in texto_mes
    assert "dom seg ter qua qui sex sab" in texto_mes


def test_calendario_aceita_fabrica_rotina_customizada():
    """Valida se o calendário aceita uma fábrica de rotina customizada e utiliza essa fábrica para criar a rotina corretamente"""
    class FabricaFake:
        def criar(self, id_crianca, data_referencia):
            return {"id": str(id_crianca), "data": data_referencia}

    calendario = CalendarioRotina(fabrica_rotina=FabricaFake())
    hoje = date.today()
    calendario.selecionar_data(hoje.day, hoje.month, hoje.year)

    rotina = calendario.criar_rotina_para_data("123456")

    assert rotina["id"] == "123456"
    assert rotina["data"] == hoje

    