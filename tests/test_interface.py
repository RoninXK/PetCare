"""Testes da interface da página principal (Issue #15).

Protegem o que a modernização da interface acrescentou e que os outros
testes não verificam: a folha de estilos, os rótulos associados aos
campos, o bloco de erros e a diferença visual entre pendente e concluído.
"""

import re
import sqlite3


def gravar(banco, nome, status):
    conexao = sqlite3.connect(banco)
    try:
        conexao.execute(
            "INSERT INTO cuidados (nome_pet, tipo_cuidado, descricao, data, status) "
            "VALUES (?, 'Vacina', 'd', '2099-12-31', ?)",
            (nome, status),
        )
        conexao.commit()
    finally:
        conexao.close()


def test_folha_de_estilos_e_servida_e_usada_na_pagina(client):
    html = client.get("/").get_data(as_text=True)
    css = client.get("/static/style.css")

    assert '<link rel="stylesheet" href="/static/style.css">' in html
    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html
    assert css.status_code == 200
    assert css.mimetype == "text/css"


def test_cada_campo_tem_rotulo_associado(client):
    html = client.get("/").get_data(as_text=True)

    for campo in ("nome_pet", "tipo_cuidado", "descricao", "data"):
        assert f'<label for="{campo}">' in html
        assert re.search(rf'id="{campo}"\s+name="{campo}"', html), campo


def test_erros_aparecem_num_alerta(client, cuidados_gravados):
    html = client.post(
        "/",
        data={"nome_pet": "", "tipo_cuidado": "X", "descricao": "d", "data": "31/12/2099"},
    ).get_data(as_text=True)

    alerta = re.search(r'<div class="alerta-erro" role="alert">(.*?)</div>', html, re.DOTALL)
    assert alerta is not None
    assert "<li>Informe o nome do pet.</li>" in alerta.group(1)
    assert "<li>Selecione um tipo de cuidado válido.</li>" in alerta.group(1)
    assert len(cuidados_gravados()) == 0


def test_sem_erros_nao_ha_alerta(client):
    assert 'role="alert"' not in client.get("/").get_data(as_text=True)


def test_pendente_e_concluido_tem_aparencia_diferente(client, banco_temporario):
    gravar(banco_temporario, "Rex", "Pendente")
    gravar(banco_temporario, "Bob", "Concluído")

    html = client.get("/").get_data(as_text=True)

    assert html.count('class="cuidado cuidado-pendente"') == 1
    assert html.count('class="cuidado cuidado-concluido"') == 1
    assert '<span class="etiqueta etiqueta-pendente">Pendente</span>' in html
    assert '<span class="etiqueta etiqueta-concluido">Concluído</span>' in html
    assert html.count('class="botao botao-concluir"') == 1
