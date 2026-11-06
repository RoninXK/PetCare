"""Testes da edição de um cuidado cadastrado (Issue #3).

Identificadores E01-E13. A edição usa o mesmo formulário do cadastro,
preenchido com os dados do cuidado, e as mesmas validações. O status não
muda ao editar. Uma data que já passou só é aceita se for a mesma que o
cuidado já tinha, para que cuidados antigos possam ser corrigidos.
"""

import re
import sqlite3
from datetime import date, timedelta

import pytest

MSG_CSRF = "Não foi possível confirmar a origem do formulário."
DATA_FUTURA = (date.today() + timedelta(days=20)).strftime("%d/%m/%Y")


def gravar(banco, nome="Rex", tipo="Vacina", descricao="Antirrábica",
           data="2099-12-31", status="Pendente"):
    conexao = sqlite3.connect(banco)
    try:
        cursor = conexao.execute(
            "INSERT INTO cuidados (nome_pet, tipo_cuidado, descricao, data, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, tipo, descricao, data, status),
        )
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def registro(cuidados_gravados, id_cuidado):
    for linha in cuidados_gravados():
        if linha["id"] == id_cuidado:
            return dict(linha)
    return None


def edicao(**alteracoes):
    dados = {
        "nome_pet": "Thor",
        "tipo_cuidado": "Consulta",
        "descricao": "Check-up anual",
        "data": DATA_FUTURA,
    }
    dados.update(alteracoes)
    return dados


def test_e01_agenda_tem_link_de_edicao_em_cada_cuidado(client, cuidado_existente):
    html = client.get("/").get_data(as_text=True)

    assert f'href="/editar/{cuidado_existente}"' in html


def test_e02_pagina_de_edicao_vem_preenchida(client, cuidado_existente):
    resposta = client.get(f"/editar/{cuidado_existente}")
    html = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "Editar cuidado" in html
    assert "Novo cuidado" not in html
    assert re.search(rf'<form method="POST" action="/editar/{cuidado_existente}"', html)
    assert re.search(r'id="nome_pet"\s+name="nome_pet"[^>]*value="Rex"', html)
    assert '<option value="Vacina" selected>' in html
    assert re.search(r'id="descricao"\s+name="descricao"[^>]*value="Antirrábica"', html)
    assert re.search(r'id="data"\s+name="data"[^>]*value="31/12/2099"', html)
    assert "Salvar alterações" in html
    assert 'href="/">Cancelar</a>' in html


def test_e03_editar_cuidado_inexistente_retorna_404(client, cuidado_existente):
    assert client.get(f"/editar/{cuidado_existente + 1000}").status_code == 404


def test_e04_edicao_valida_altera_todos_os_campos(client, cuidados_gravados, cuidado_existente):
    resposta = client.post(f"/editar/{cuidado_existente}", data=edicao())

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/"
    gravado = registro(cuidados_gravados, cuidado_existente)
    assert gravado["nome_pet"] == "Thor"
    assert gravado["tipo_cuidado"] == "Consulta"
    assert gravado["descricao"] == "Check-up anual"
    assert gravado["data"] == (date.today() + timedelta(days=20)).isoformat()
    assert gravado["status"] == "Pendente"
    assert len(cuidados_gravados()) == 1


def test_e05_edicao_invalida_mostra_erros_e_nao_grava(
    client, cuidados_gravados, cuidado_existente
):
    antes = registro(cuidados_gravados, cuidado_existente)

    resposta = client.post(
        f"/editar/{cuidado_existente}", data=edicao(nome_pet="   ", data="31/02/2099")
    )
    html = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "Não foi possível salvar:" in html
    assert "<li>Informe o nome do pet.</li>" in html
    assert "Data inválida." in html
    assert "Editar cuidado" in html
    assert re.search(r'id="descricao"\s+name="descricao"[^>]*value="Check-up anual"', html)
    assert registro(cuidados_gravados, cuidado_existente) == antes


def test_e06_salvar_cuidado_inexistente_retorna_404(client, cuidados_gravados, cuidado_existente):
    resposta = client.post(f"/editar/{cuidado_existente + 1000}", data=edicao())

    assert resposta.status_code == 404
    assert registro(cuidados_gravados, cuidado_existente)["nome_pet"] == "Rex"


def test_e07_tipo_digitado_aparece_no_campo_proprio(client, banco_temporario):
    id_cuidado = gravar(banco_temporario, tipo="Banho e tosa")

    html = client.get(f"/editar/{id_cuidado}").get_data(as_text=True)

    assert '<option value="personalizado" selected>' in html
    assert re.search(
        r'id="tipo_personalizado"\s+name="tipo_personalizado"[^>]*value="Banho e tosa"', html
    )


def test_e08_editar_para_um_tipo_digitado(client, cuidados_gravados, cuidado_existente):
    resposta = client.post(
        f"/editar/{cuidado_existente}",
        data=edicao(tipo_cuidado="personalizado", tipo_personalizado="  Banho e tosa "),
    )

    assert resposta.status_code == 302
    assert registro(cuidados_gravados, cuidado_existente)["tipo_cuidado"] == "Banho e tosa"


def test_e09_data_passada_so_e_aceita_se_for_a_que_ja_estava(
    client, cuidados_gravados, banco_temporario
):
    ontem = date.today() - timedelta(days=1)
    anteontem = date.today() - timedelta(days=2)
    id_cuidado = gravar(banco_temporario, data=ontem.isoformat(), status="Concluído")

    mantendo = client.post(
        f"/editar/{id_cuidado}",
        data=edicao(descricao="Corrigida", data=ontem.strftime("%d/%m/%Y")),
    )
    trocando = client.post(
        f"/editar/{id_cuidado}",
        data=edicao(descricao="Outra", data=anteontem.strftime("%d/%m/%Y")),
    )

    assert mantendo.status_code == 302
    assert trocando.status_code == 200
    assert "A data não pode ser anterior a hoje." in trocando.get_data(as_text=True)
    gravado = registro(cuidados_gravados, id_cuidado)
    assert gravado["descricao"] == "Corrigida"
    assert gravado["data"] == ontem.isoformat()


def test_e10_status_nao_muda_ao_editar(client, cuidados_gravados, banco_temporario):
    id_cuidado = gravar(banco_temporario, status="Concluído")

    client.post(f"/editar/{id_cuidado}", data=edicao())

    assert registro(cuidados_gravados, id_cuidado)["status"] == "Concluído"


@pytest.mark.parametrize("token", [None, "token-invalido"], ids=["sem-token", "token-invalido"])
def test_e11_edicao_sem_token_valido_e_rejeitada(
    cliente_sem_token, cuidados_gravados, cuidado_existente, token
):
    cliente_sem_token.get("/")
    dados = edicao()
    if token:
        dados["csrf_token"] = token

    resposta = cliente_sem_token.post(f"/editar/{cuidado_existente}", data=dados)

    assert resposta.status_code == 400
    assert MSG_CSRF in resposta.get_data(as_text=True)
    assert registro(cuidados_gravados, cuidado_existente)["nome_pet"] == "Rex"


def test_e12_edicao_mantem_os_filtros_da_agenda(client, cuidado_existente):
    html = client.get("/?busca=rex&status=pendentes").get_data(as_text=True)
    pagina = client.get(f"/editar/{cuidado_existente}?busca=rex").get_data(as_text=True)
    resposta = client.post(f"/editar/{cuidado_existente}?busca=rex", data=edicao())

    assert f'href="/editar/{cuidado_existente}?busca=rex&amp;status=pendentes"' in html
    assert f'action="/editar/{cuidado_existente}?busca=rex"' in pagina
    assert 'href="/?busca=rex">Cancelar</a>' in pagina
    assert resposta.headers["Location"] == "/?busca=rex"


def test_e13_abrir_a_edicao_nao_altera_o_banco(client, cuidados_gravados, cuidado_existente):
    antes = [dict(c) for c in cuidados_gravados()]

    client.get(f"/editar/{cuidado_existente}")

    assert [dict(c) for c in cuidados_gravados()] == antes
