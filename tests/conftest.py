"""Configuração compartilhada dos testes do PetCare.

Todos os testes usam um banco SQLite temporário, criado em um diretório
isolado do pytest (tmp_path). O banco real (petcare.db) nunca é aberto.

A proteção CSRF fica ligada em todos os testes. O fixture `client` pega
um token real emitido pela página inicial, na mesma sessão, e o envia nos
POSTs; o fixture `cliente_sem_token` não envia token nenhum.
"""

import hashlib
import re
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


PADRAO_TOKEN = re.compile(r'name="csrf_token" value="([^"]+)"')


def obter_token(cliente):
    """Token CSRF emitido pela página inicial para a sessão do cliente, se houver."""
    encontrado = PADRAO_TOKEN.search(cliente.get("/").get_data(as_text=True))
    return encontrado.group(1) if encontrado else None


class ClienteComToken:
    """Cliente de teste que envia nos POSTs o token CSRF real da sessão.

    O token é obtido da página inicial, como faria o navegador. Se a página
    não tiver token (código anterior ao P2), o POST segue sem ele.
    """

    def __init__(self, cliente):
        self._cliente = cliente

    def post(self, url, data=None, **kwargs):
        dados = dict(data or {})
        if "csrf_token" not in dados:
            token = obter_token(self._cliente)
            if token:
                dados["csrf_token"] = token
        return self._cliente.post(url, data=dados, **kwargs)

    def __getattr__(self, nome):
        return getattr(self._cliente, nome)


@pytest.fixture
def client(app_teste):
    """Cliente HTTP de teste que se comporta como o navegador (com token CSRF)."""
    return ClienteComToken(app_teste.test_client())


@pytest.fixture
def cliente_sem_token(app_teste):
    """Cliente HTTP de teste que nunca envia token CSRF."""
    return app_teste.test_client()


@pytest.fixture
def cuidado_existente(app_teste, banco_temporario):
    """Grava um cuidado pendente direto no banco temporário e devolve o id."""
    conexao = sqlite3.connect(banco_temporario)
    try:
        cursor = conexao.execute(
            "INSERT INTO cuidados (nome_pet, tipo_cuidado, descricao, data, status) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Rex", "Vacina", "Antirrábica", "2099-12-31", "Pendente"),
        )
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


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
