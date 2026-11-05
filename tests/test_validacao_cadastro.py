"""Testes do P1: validação dos dados no cadastro de cuidados (Issue #1).

Os identificadores V01-V12 (casos inválidos) e A01-A02 (casos válidos)
seguem a seção 6.1 do PLANO_MELHORIA_PARTE2.md. Um caso inválido só é
considerado rejeitado quando a página volta com a mensagem de erro e
nenhum registro é gravado.
"""

from datetime import date, timedelta

import pytest

MSG_NOME_VAZIO = "Informe o nome do pet."
MSG_NOME_LONGO = "O nome do pet pode ter no máximo 100 caracteres."
MSG_TIPO = "Selecione um tipo de cuidado válido."
MSG_DESCRICAO_VAZIA = "Informe a descrição do cuidado."
MSG_DESCRICAO_LONGA = "A descrição pode ter no máximo 500 caracteres."
MSG_DATA_INVALIDA = "Data inválida. Digite uma data válida no formato DD/MM/AAAA."
MSG_DATA_PASSADA = "A data não pode ser anterior a hoje."


def formatar(dia):
    return dia.strftime("%d/%m/%Y")


def cadastro_valido(**alteracoes):
    """Dados de um cadastro válido, com data futura."""
    dados = {
        "nome_pet": "Rex",
        "tipo_cuidado": "Vacina",
        "descricao": "Vacina antirrábica",
        "data": formatar(date.today() + timedelta(days=30)),
    }
    dados.update(alteracoes)
    return dados


def assert_rejeitado(resposta, cuidados_gravados, mensagem):
    assert resposta.status_code == 200
    assert mensagem in resposta.get_data(as_text=True)
    assert len(cuidados_gravados()) == 0


@pytest.mark.parametrize(
    ("alteracao", "mensagem"),
    [
        pytest.param({"nome_pet": ""}, MSG_NOME_VAZIO, id="V01-nome-vazio"),
        pytest.param({"nome_pet": "   "}, MSG_NOME_VAZIO, id="V02-nome-so-espacos"),
        pytest.param({"descricao": ""}, MSG_DESCRICAO_VAZIA, id="V03-descricao-vazia"),
        pytest.param({"descricao": "   "}, MSG_DESCRICAO_VAZIA, id="V04-descricao-so-espacos"),
        pytest.param({"tipo_cuidado": ""}, MSG_TIPO, id="V05-tipo-vazio"),
        pytest.param({"tipo_cuidado": "Banho"}, MSG_TIPO, id="V06-tipo-fora-da-lista"),
        pytest.param({"data": "2026-12-01"}, MSG_DATA_INVALIDA, id="V07-data-formato-invalido"),
        pytest.param({"data": "31/02/2027"}, MSG_DATA_INVALIDA, id="V08-data-inexistente"),
        pytest.param(
            {"data": formatar(date.today() - timedelta(days=1))},
            MSG_DATA_PASSADA,
            id="V09-data-passada",
        ),
        pytest.param({"nome_pet": "R" * 101}, MSG_NOME_LONGO, id="V10-nome-101-caracteres"),
        pytest.param(
            {"descricao": "D" * 501}, MSG_DESCRICAO_LONGA, id="V11-descricao-501-caracteres"
        ),
    ],
)
def test_cadastro_invalido_e_rejeitado(client, cuidados_gravados, alteracao, mensagem):
    resposta = client.post("/", data=cadastro_valido(**alteracao))

    assert_rejeitado(resposta, cuidados_gravados, mensagem)


CAMPOS_E_MENSAGENS = [
    ("nome_pet", MSG_NOME_VAZIO),
    ("tipo_cuidado", MSG_TIPO),
    ("descricao", MSG_DESCRICAO_VAZIA),
    ("data", MSG_DATA_INVALIDA),
]


def test_v12_campo_ausente_e_rejeitado_com_mensagem(client, cuidados_gravados):
    """V12: cada um dos quatro campos é retirado da requisição, um por vez."""
    for campo, mensagem in CAMPOS_E_MENSAGENS:
        dados = cadastro_valido()
        del dados[campo]

        resposta = client.post("/", data=dados)

        assert resposta.status_code != 400, f"campo ausente: {campo}"
        assert_rejeitado(resposta, cuidados_gravados, mensagem)


def test_a01_cadastro_com_data_futura_e_aceito(client, cuidados_gravados):
    dados = cadastro_valido()

    resposta = client.post("/", data=dados)

    assert resposta.status_code == 302
    gravados = cuidados_gravados()
    assert len(gravados) == 1
    assert gravados[0]["nome_pet"] == "Rex"
    assert gravados[0]["tipo_cuidado"] == "Vacina"
    assert gravados[0]["descricao"] == "Vacina antirrábica"
    assert gravados[0]["data"] == (date.today() + timedelta(days=30)).isoformat()
    assert gravados[0]["status"] == "Pendente"


def test_a02_data_de_hoje_e_limites_exatos_sao_aceitos(client, cuidados_gravados):
    dados = cadastro_valido(
        nome_pet="N" * 100,
        descricao="D" * 500,
        data=formatar(date.today()),
    )

    resposta = client.post("/", data=dados)

    assert resposta.status_code == 302
    gravados = cuidados_gravados()
    assert len(gravados) == 1
    assert gravados[0]["nome_pet"] == "N" * 100
    assert gravados[0]["descricao"] == "D" * 500
    assert gravados[0]["data"] == date.today().isoformat()
    assert gravados[0]["status"] == "Pendente"


def test_dados_digitados_permanecem_no_formulario_apos_erro(client, cuidados_gravados):
    """Critério de aceitação de P1 (seção 7 do plano)."""
    dados = cadastro_valido(tipo_cuidado="Consulta", data="31/02/2027")

    html = client.post("/", data=dados).get_data(as_text=True)

    assert 'value="Rex"' in html
    assert 'value="Vacina antirrábica"' in html
    assert 'value="31/02/2027"' in html
    assert '<option value="Consulta" selected>' in html
    assert len(cuidados_gravados()) == 0
