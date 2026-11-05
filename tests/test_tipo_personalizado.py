"""Testes do tipo de cuidado digitado manualmente (Issue #17).

A opção "Outro" sai da lista e entra "Adicionar outro tipo…" (valor
"personalizado"), que usa o campo tipo_personalizado. Os identificadores
continuam a numeração da seção 6.1 do plano: V13-V16 são inválidos e
A03-A04 são válidos.
"""

import re
import sqlite3
from datetime import date, timedelta

import pytest

MSG_TIPO = "Selecione um tipo de cuidado válido."
MSG_TIPO_VAZIO = "Informe o tipo de cuidado."
MSG_TIPO_LONGO = "O tipo de cuidado pode ter no máximo 50 caracteres."


def cadastro(**alteracoes):
    dados = {
        "nome_pet": "Rex",
        "tipo_cuidado": "personalizado",
        "tipo_personalizado": "Banho e tosa",
        "descricao": "Banho mensal",
        "data": (date.today() + timedelta(days=10)).strftime("%d/%m/%Y"),
    }
    dados.update(alteracoes)
    return dados


@pytest.mark.parametrize(
    ("alteracao", "mensagem"),
    [
        pytest.param({"tipo_personalizado": ""}, MSG_TIPO_VAZIO, id="V13-tipo-digitado-vazio"),
        pytest.param(
            {"tipo_personalizado": "   "}, MSG_TIPO_VAZIO, id="V14-tipo-digitado-so-espacos"
        ),
        pytest.param(
            {"tipo_personalizado": "T" * 51}, MSG_TIPO_LONGO, id="V15-tipo-digitado-51-caracteres"
        ),
        pytest.param({"tipo_cuidado": "Outro"}, MSG_TIPO, id="V16-opcao-outro-removida"),
    ],
)
def test_tipo_personalizado_invalido_e_rejeitado(
    client, cuidados_gravados, alteracao, mensagem
):
    resposta = client.post("/", data=cadastro(**alteracao))

    assert resposta.status_code == 200
    assert mensagem in resposta.get_data(as_text=True)
    assert len(cuidados_gravados()) == 0


def test_tipo_personalizado_ausente_e_rejeitado(client, cuidados_gravados):
    dados = cadastro()
    del dados["tipo_personalizado"]

    resposta = client.post("/", data=dados)

    assert resposta.status_code == 200
    assert MSG_TIPO_VAZIO in resposta.get_data(as_text=True)
    assert len(cuidados_gravados()) == 0


def test_a03_tipo_digitado_e_gravado_sem_espacos_nas_pontas(client, cuidados_gravados):
    resposta = client.post("/", data=cadastro(tipo_personalizado="  Banho e tosa  "))

    assert resposta.status_code == 302
    gravados = cuidados_gravados()
    assert len(gravados) == 1
    assert gravados[0]["tipo_cuidado"] == "Banho e tosa"
    assert gravados[0]["status"] == "Pendente"


def test_a04_tipo_digitado_com_50_caracteres_e_aceito(client, cuidados_gravados):
    resposta = client.post("/", data=cadastro(tipo_personalizado="T" * 50))

    assert resposta.status_code == 302
    assert cuidados_gravados()[0]["tipo_cuidado"] == "T" * 50


def test_tipo_digitado_e_ignorado_quando_a_lista_tem_um_tipo_fixo(client, cuidados_gravados):
    resposta = client.post(
        "/", data=cadastro(tipo_cuidado="Vacina", tipo_personalizado="Qualquer coisa")
    )

    assert resposta.status_code == 302
    assert cuidados_gravados()[0]["tipo_cuidado"] == "Vacina"


def test_tipos_fixos_continuam_aceitos(client, cuidados_gravados):
    for tipo in ("Vacina", "Consulta", "Medicamento"):
        client.post("/", data=cadastro(tipo_cuidado=tipo, tipo_personalizado=""))

    assert [linha["tipo_cuidado"] for linha in cuidados_gravados()] == [
        "Vacina",
        "Consulta",
        "Medicamento",
    ]


def test_formulario_tem_a_opcao_de_digitar_outro_tipo(client):
    html = client.get("/").get_data(as_text=True)

    assert '<option value="personalizado">Adicionar outro tipo…</option>' in html
    assert '<option value="Outro"' not in html
    assert '<label for="tipo_personalizado">' in html
    assert re.search(r'id="tipo_personalizado"\s+name="tipo_personalizado"', html)


def test_escolha_e_texto_digitado_voltam_apos_erro(client):
    html = client.post("/", data=cadastro(nome_pet="")).get_data(as_text=True)

    assert '<option value="personalizado" selected>' in html
    assert 'value="Banho e tosa"' in html


def test_cuidado_antigo_do_tipo_outro_continua_aparecendo(client, banco_temporario):
    conexao = sqlite3.connect(banco_temporario)
    try:
        conexao.execute(
            "INSERT INTO cuidados (nome_pet, tipo_cuidado, descricao, data, status) "
            "VALUES ('Mia', 'Outro', 'Registro antigo', '2099-12-31', 'Pendente')"
        )
        conexao.commit()
    finally:
        conexao.close()

    html = client.get("/").get_data(as_text=True)

    assert '<span class="etiqueta etiqueta-tipo">Outro</span>' in html
