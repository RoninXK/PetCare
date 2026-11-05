"""Testes de regressão da refatoração do acesso ao banco e do modo debug (Issue #13)."""

import sqlite3

import pytest

import app as petcare

INSERIR = (
    "INSERT INTO cuidados (nome_pet, tipo_cuidado, descricao, data, status) "
    "VALUES ('Rex', 'Vacina', 'd', '2099-12-31', 'Pendente')"
)


def test_conexao_grava_e_fecha_quando_o_bloco_termina_bem(app_teste, cuidados_gravados):
    with petcare.conectar_banco() as conexao:
        conexao.execute(INSERIR)

    assert len(cuidados_gravados()) == 1
    with pytest.raises(sqlite3.ProgrammingError):
        conexao.execute("SELECT 1")


def test_conexao_desfaz_e_fecha_quando_ha_erro(app_teste, cuidados_gravados):
    with pytest.raises(RuntimeError), petcare.conectar_banco() as conexao:
        conexao.execute(INSERIR)
        raise RuntimeError("falha simulada")

    assert len(cuidados_gravados()) == 0
    with pytest.raises(sqlite3.ProgrammingError):
        conexao.execute("SELECT 1")


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        pytest.param(None, False, id="sem-variavel"),
        pytest.param("0", False, id="zero"),
        pytest.param("true", False, id="texto-true"),
        pytest.param("1", True, id="um"),
    ],
)
def test_modo_debug_so_liga_com_petcare_debug_1(monkeypatch, valor, esperado):
    if valor is None:
        monkeypatch.delenv("PETCARE_DEBUG", raising=False)
    else:
        monkeypatch.setenv("PETCARE_DEBUG", valor)

    assert petcare.modo_debug() is esperado
