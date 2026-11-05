"""Testes da pesquisa e dos filtros da agenda (Issue #19).

Identificadores F01-F15. Os filtros chegam pela URL (busca, status, ordem)
e são aplicados no servidor.
"""

import re
import sqlite3

import pytest

CUIDADOS = [
    ("Rex", "Vacina", "Vacina antirrábica", "2026-12-10", "Pendente"),
    ("Mia", "Consulta", "Retorno ao veterinário", "2026-11-20", "Concluído"),
    ("Bob", "Banho e tosa", "Banho mensal com 50% de desconto", "2027-01-05", "Pendente"),
    ("Luna", "Medicamento", "Vermífugo", "2026-11-25", "Concluído"),
]


@pytest.fixture
def agenda(app_teste, banco_temporario):
    conexao = sqlite3.connect(banco_temporario)
    try:
        conexao.executemany(
            "INSERT INTO cuidados (nome_pet, tipo_cuidado, descricao, data, status) "
            "VALUES (?, ?, ?, ?, ?)",
            CUIDADOS,
        )
        conexao.commit()
    finally:
        conexao.close()


def pets(client, url):
    """Nomes dos pets mostrados na agenda, na ordem da página."""
    html = client.get(url).get_data(as_text=True)
    return re.findall(r'<h3 class="cuidado-pet">([^<]*)</h3>', html)


def test_f01_sem_filtros_mostra_tudo_da_data_mais_antiga_para_a_mais_nova(client, agenda):
    assert pets(client, "/") == ["Mia", "Luna", "Rex", "Bob"]


def test_f02_pesquisa_pelo_nome(client, agenda):
    assert pets(client, "/?busca=Rex") == ["Rex"]


def test_f03_pesquisa_pelo_tipo(client, agenda):
    assert pets(client, "/?busca=consulta") == ["Mia"]


def test_f04_pesquisa_pela_descricao(client, agenda):
    assert pets(client, "/?busca=vermífugo") == ["Luna"]


def test_f05_pesquisa_ignora_maiusculas_e_espacos_nas_pontas(client, agenda):
    assert pets(client, "/?busca=%20%20rEx%20") == ["Rex"]


def test_f06_pesquisa_trata_porcentagem_e_sublinhado_como_texto(client, agenda):
    assert pets(client, "/?busca=50%25") == ["Bob"]
    assert pets(client, "/?busca=%25") == ["Bob"]
    assert pets(client, "/?busca=_") == []


def test_f07_somente_pendentes(client, agenda):
    assert pets(client, "/?status=pendentes") == ["Rex", "Bob"]


def test_f08_somente_concluidos(client, agenda):
    assert pets(client, "/?status=concluidos") == ["Mia", "Luna"]


def test_f09_mais_recentes_primeiro(client, agenda):
    assert pets(client, "/?ordem=recentes") == ["Bob", "Rex", "Luna", "Mia"]


def test_f10_pesquisa_status_e_ordem_juntos(client, agenda):
    assert pets(client, "/?busca=a&status=pendentes&ordem=recentes") == ["Bob", "Rex"]


def test_f11_valores_desconhecidos_caem_no_padrao(client, agenda):
    resposta = client.get("/?status=xyz&ordem=aleatoria")

    assert resposta.status_code == 200
    assert pets(client, "/?status=xyz&ordem=aleatoria") == ["Mia", "Luna", "Rex", "Bob"]


def test_f12_pesquisa_sem_resultado_tem_mensagem_propria(client, agenda):
    html = client.get("/?busca=girafa").get_data(as_text=True)

    assert "Nenhum cuidado encontrado com esses filtros." in html
    assert "Nenhum cuidado agendado." not in html


def test_f13_formulario_de_filtros_mostra_o_que_esta_aplicado(client, agenda):
    html = client.get("/?busca=Rex&status=concluidos&ordem=recentes").get_data(as_text=True)

    assert re.search(r'<form[^>]*method="GET"[^>]*class="filtros"', html)
    assert re.search(r'id="busca"\s+name="busca"[^>]*value="Rex"', html)
    assert '<option value="concluidos" selected>' in html
    assert '<option value="recentes" selected>' in html
    assert '<label for="busca">' in html


def test_f14_concluir_excluir_e_cadastrar_mantem_os_filtros(client, agenda, cuidados_gravados):
    id_rex = next(c["id"] for c in cuidados_gravados() if c["nome_pet"] == "Rex")
    id_bob = next(c["id"] for c in cuidados_gravados() if c["nome_pet"] == "Bob")

    concluir = client.post(f"/concluir/{id_rex}?status=pendentes&ordem=recentes")
    excluir = client.post(f"/excluir/{id_bob}?busca=bob")
    cadastrar = client.post(
        "/?status=pendentes",
        data={
            "nome_pet": "Thor",
            "tipo_cuidado": "Vacina",
            "descricao": "Reforço",
            "data": "31/12/2099",
        },
    )

    assert concluir.status_code == 302
    assert concluir.headers["Location"] == "/?status=pendentes&ordem=recentes"
    assert excluir.headers["Location"] == "/?busca=bob"
    assert cadastrar.headers["Location"] == "/?status=pendentes"


def test_f15_pesquisa_com_trecho_de_sql_nao_altera_nada(client, agenda, cuidados_gravados):
    antes = [tuple(c) for c in cuidados_gravados()]

    for texto in ("' OR '1'='1", "x'; DROP TABLE cuidados; --"):
        resposta = client.get("/", query_string={"busca": texto})
        assert resposta.status_code == 200
        assert pets(client, "/?" + "busca=" + texto.replace("%", "%25")) == []

    assert [tuple(c) for c in cuidados_gravados()] == antes
