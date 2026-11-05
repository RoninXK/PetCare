"""Testes iniciais da estrutura do PetCare (Issue #9).

Verificam que a aplicação responde, que a página principal é renderizada
a partir de templates/index.html, que o banco temporário é inicializado e
que o banco real (petcare.db) não é alterado pelos testes.
"""

import sqlite3

import app as petcare
from tests.conftest import BANCO_REAL, hash_arquivo

COLUNAS_ESPERADAS = ["id", "nome_pet", "tipo_cuidado", "descricao", "data", "status"]


def test_configuracao_padrao_usa_petcare_db():
    """Sem configuração de teste, o aplicativo continua usando petcare.db."""
    assert petcare.app.config["DATABASE"] == "petcare.db"


def test_get_inicio_retorna_200(client):
    resposta = client.get("/")

    assert resposta.status_code == 200


def test_pagina_principal_renderiza(client):
    html = client.get("/").get_data(as_text=True)

    assert "<title>PetCare</title>" in html
    assert "Novo cuidado" in html
    assert "Agenda" in html
    for campo in ("nome_pet", "tipo_cuidado", "descricao", "data"):
        assert f'name="{campo}"' in html
    assert "Nenhum cuidado agendado." in html


def test_banco_temporario_inicializado(app_teste, banco_temporario):
    assert banco_temporario.exists()
    assert banco_temporario != BANCO_REAL

    conexao = sqlite3.connect(banco_temporario)
    try:
        colunas = [linha[1] for linha in conexao.execute("PRAGMA table_info(cuidados)")]
        total = conexao.execute("SELECT COUNT(*) FROM cuidados").fetchone()[0]
    finally:
        conexao.close()

    assert colunas == COLUNAS_ESPERADAS
    assert total == 0


def test_banco_real_nao_e_alterado(client, banco_temporario):
    hash_antes = hash_arquivo(BANCO_REAL)

    client.get("/")
    resposta = client.post(
        "/",
        data={
            "nome_pet": "Rex",
            "tipo_cuidado": "Vacina",
            "descricao": "Teste de isolamento",
            "data": "31/12/2099",
        },
    )

    assert resposta.status_code == 302
    assert hash_arquivo(BANCO_REAL) == hash_antes

    conexao = sqlite3.connect(banco_temporario)
    try:
        total = conexao.execute("SELECT COUNT(*) FROM cuidados").fetchone()[0]
    finally:
        conexao.close()

    assert total == 1
