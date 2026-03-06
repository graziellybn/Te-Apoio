from datetime import date

import pytest

from teapoio.domain.models.calendario import CalendarioRotina


def test_calendario_inicia_com_data_atual():
    calendario = CalendarioRotina()
    assert calendario.data_selecionada == date.today()


def test_calendario_permite_escolher_dia_mes_ano():
    calendario = CalendarioRotina()
    hoje = date.today()
    dia = 1
    mes = 1
    ano = hoje.year

    data = calendario.selecionar_data(dia, mes, ano)

    assert data == date(ano, mes, dia)
    assert calendario.data_selecionada == date(ano, mes, dia)


def test_calendario_rejeita_data_invalida():
    calendario = CalendarioRotina()
    ano = date.today().year

    with pytest.raises(ValueError):
        calendario.selecionar_data(31, 2, ano)


def test_calendario_rejeita_ano_diferente_do_atual():
    calendario = CalendarioRotina()
    ano_passado = date.today().year - 1

    with pytest.raises(ValueError):
        calendario.selecionar_data(1, 1, ano_passado)


def test_calendario_rejeita_data_futura():
    calendario = CalendarioRotina()
    amanha = date.today().fromordinal(date.today().toordinal() + 1)

    with pytest.raises(ValueError):
        calendario.selecionar_data(amanha.day, amanha.month, amanha.year)


def test_calendario_cria_rotina_na_data_selecionada():
    calendario = CalendarioRotina()
    hoje = date.today()
    calendario.selecionar_data(hoje.day, hoje.month, hoje.year)

    rotina = calendario.criar_rotina_para_data("123456")

    assert rotina.id_crianca == "123456"
    assert rotina.data_referencia == hoje


def test_exibir_mes_retorna_texto_do_calendario():
    calendario = CalendarioRotina()
    ano_teste = date.today().year
    texto_mes = calendario.exibir_mes(3, ano_teste)

    assert str(ano_teste) in texto_mes
    assert "Março" in texto_mes
    assert "dom seg ter qua qui sex sab" in texto_mes

    