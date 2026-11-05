"""Configuração compartilhada dos testes do PetCare.

Todos os testes usam um banco SQLite temporário, criado em um diretório
isolado do pytest (tmp_path). O banco real (petcare.db) nunca é aberto.
"""

import hashlib
import sqlite3
from pathlib import Path

import pytest

import app as petcare

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
BANCO_REAL = RAIZ_PROJETO / "petcare.db"


def hash_arquivo(caminho):
    """Retorna o SHA-256 do arquivo, ou None se ele não existir."""
    if not caminho.exists():
        return None
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


@pytest.fixture
def banco_temporario(tmp_path):
    """Caminho de um banco SQLite novo e exclusivo para o teste."""
    return tmp_path / "petcare_teste.db"


@pytest.fixture
def app_teste(banco_temporario, monkeypatch):
    """Aplicação configurada para usar só o banco temporário.

    O monkeypatch restaura a configuração original ao final de cada teste.
    """
    monkeypatch.setitem(petcare.app.config, "DATABASE", str(banco_temporario))
    monkeypatch.setitem(petcare.app.config, "TESTING", True)

    assert Path(petcare.app.config["DATABASE"]).resolve() != BANCO_REAL.resolve()

    petcare.criar_banco()
    return petcare.app


@pytest.fixture
def client(app_teste):
    """Cliente HTTP de teste do Flask."""
    return app_teste.test_client()


@pytest.fixture
def cuidados_gravados(app_teste, banco_temporario):
    """Função que devolve os cuidados gravados no banco temporário."""

    def consultar():
        conexao = sqlite3.connect(banco_temporario)
        conexao.row_factory = sqlite3.Row
        try:
            return conexao.execute("SELECT * FROM cuidados").fetchall()
        finally:
            conexao.close()

    return consultar
