"""Testes do P2: concluir e excluir por POST, com CSRF e confirmação (Issue #2).

Os identificadores C01-C09 seguem a seção 6.2 do PLANO_MELHORIA_PARTE2.md.
C03, C04 e C05 são executados em duas variações: sem token e com token
inválido. A proteção CSRF fica ligada em todos os testes.
"""

import re
from datetime import date, timedelta

import pytest

MSG_CSRF = "Não foi possível confirmar a origem do formulário."

VARIACOES_TOKEN = [
    pytest.param(None, id="sem-token"),
    pytest.param("token-invalido", id="token-invalido"),
]


def dados_do_token(token):
    return {} if token is None else {"csrf_token": token}


def registro(cuidados_gravados, id_cuidado):
    for linha in cuidados_gravados():
        if linha["id"] == id_cuidado:
            return linha
    return None


def test_c01_get_nao_conclui(client, cuidados_gravados, cuidado_existente):
    resposta = client.get(f"/concluir/{cuidado_existente}")

    assert resposta.status_code == 405
    assert registro(cuidados_gravados, cuidado_existente)["status"] == "Pendente"


def test_c02_get_nao_exclui(client, cuidados_gravados, cuidado_existente):
    resposta = client.get(f"/excluir/{cuidado_existente}")

    assert resposta.status_code == 405
    assert registro(cuidados_gravados, cuidado_existente) is not None


@pytest.mark.parametrize("token", VARIACOES_TOKEN)
def test_c03_concluir_sem_token_valido_e_rejeitado(
    cliente_sem_token, cuidados_gravados, cuidado_existente, token
):
    cliente_sem_token.get("/")

    resposta = cliente_sem_token.post(
        f"/concluir/{cuidado_existente}", data=dados_do_token(token)
    )

    assert resposta.status_code == 400
    assert MSG_CSRF in resposta.get_data(as_text=True)
    assert registro(cuidados_gravados, cuidado_existente)["status"] == "Pendente"


@pytest.mark.parametrize("token", VARIACOES_TOKEN)
def test_c04_excluir_sem_token_valido_e_rejeitado(
    cliente_sem_token, cuidados_gravados, cuidado_existente, token
):
    cliente_sem_token.get("/")

    resposta = cliente_sem_token.post(
        f"/excluir/{cuidado_existente}", data=dados_do_token(token)
    )

    assert resposta.status_code == 400
    assert MSG_CSRF in resposta.get_data(as_text=True)
    assert registro(cuidados_gravados, cuidado_existente) is not None


@pytest.mark.parametrize("token", VARIACOES_TOKEN)
def test_c05_cadastro_sem_token_valido_e_rejeitado(cliente_sem_token, cuidados_gravados, token):
    cliente_sem_token.get("/")
    dados = {
        "nome_pet": "Rex",
        "tipo_cuidado": "Vacina",
        "descricao": "Antirrábica",
        "data": (date.today() + timedelta(days=30)).strftime("%d/%m/%Y"),
    }
    dados.update(dados_do_token(token))

    resposta = cliente_sem_token.post("/", data=dados)

    assert resposta.status_code == 400
    assert MSG_CSRF in resposta.get_data(as_text=True)
    assert len(cuidados_gravados()) == 0


def test_c06_concluir_com_token_valido(client, cuidados_gravados, cuidado_existente):
    resposta = client.post(f"/concluir/{cuidado_existente}")

    assert resposta.status_code == 302
    assert registro(cuidados_gravados, cuidado_existente)["status"] == "Concluído"


def test_c07_excluir_com_token_valido(client, cuidados_gravados, cuidado_existente):
    resposta = client.post(f"/excluir/{cuidado_existente}")

    assert resposta.status_code == 302
    assert registro(cuidados_gravados, cuidado_existente) is None


def test_c08_formulario_de_exclusao_tem_post_token_e_confirmacao(client, cuidado_existente):
    html = client.get("/").get_data(as_text=True)

    formulario = re.search(
        rf'<form[^>]*action="/excluir/{cuidado_existente}"[^>]*>(.*?)</form>',
        html,
        re.DOTALL,
    )

    assert formulario is not None, "formulário de exclusão não encontrado"
    abertura = formulario.group(0).split(">", 1)[0]
    assert 'method="POST"' in abertura
    assert "return confirm(" in abertura
    assert re.search(r'name="csrf_token" value="[^"]+"', formulario.group(1))
    assert f'href="/excluir/{cuidado_existente}"' not in html


def test_c09_id_inexistente_retorna_404(client, cuidados_gravados, cuidado_existente):
    id_inexistente = cuidado_existente + 1000

    concluir = client.post(f"/concluir/{id_inexistente}")
    excluir = client.post(f"/excluir/{id_inexistente}")

    assert concluir.status_code == 404
    assert excluir.status_code == 404
    gravados = cuidados_gravados()
    assert len(gravados) == 1
    assert gravados[0]["status"] == "Pendente"
