import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from urllib.parse import urlencode

from flask import Flask, abort, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect

app = Flask(__name__)
app.config["DATABASE"] = "petcare.db"

# A chave vem da variável de ambiente PETCARE_SECRET_KEY. Sem ela, uma chave
# aleatória é gerada a cada execução: funciona, mas formulários abertos antes
# de reiniciar o servidor deixam de ser aceitos.
app.config["SECRET_KEY"] = os.environ.get("PETCARE_SECRET_KEY") or secrets.token_hex(32)

csrf = CSRFProtect(app)

MSG_CSRF = (
    "Não foi possível confirmar a origem do formulário. "
    "Volte para a agenda e tente novamente."
)

TIPOS_CUIDADO = ("Vacina", "Consulta", "Medicamento")
TIPO_PERSONALIZADO = "personalizado"
LIMITE_NOME_PET = 100
LIMITE_DESCRICAO = 500
LIMITE_TIPO_PERSONALIZADO = 50
FORMATO_DATA = re.compile(r"\d{2}/\d{2}/\d{4}")


@contextmanager
def conectar_banco():
    """Abre a conexão com o banco e garante o fechamento.

    Se o bloco terminar sem erro, as alterações são gravadas (commit); se
    ocorrer uma exceção, são desfeitas (rollback). Em qualquer caso a
    conexão é fechada.
    """
    conexao = sqlite3.connect(app.config["DATABASE"])
    conexao.row_factory = sqlite3.Row
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def criar_banco():
    with conectar_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS cuidados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_pet TEXT NOT NULL,
                tipo_cuidado TEXT NOT NULL,
                descricao TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)


STATUS_DO_FILTRO = {"pendentes": "Pendente", "concluidos": "Concluído"}
FILTROS_PADRAO = {"busca": "", "status": "todos", "ordem": "antigos"}
CAMPOS_PESQUISADOS = ("nome_pet", "tipo_cuidado", "descricao")


def ler_filtros(parametros):
    """Filtros da agenda vindos da URL; valores desconhecidos viram o padrão."""
    status = parametros.get("status", "todos")
    ordem = parametros.get("ordem", "antigos")
    return {
        "busca": parametros.get("busca", "").strip(),
        "status": status if status in STATUS_DO_FILTRO else "todos",
        "ordem": ordem if ordem in ("antigos", "recentes") else "antigos",
    }


def filtros_alterados(filtros):
    """Só os filtros diferentes do padrão, para montar a URL."""
    return {nome: valor for nome, valor in filtros.items() if valor != FILTROS_PADRAO[nome]}


def endereco_da_agenda(filtros):
    return url_for("inicio", **filtros_alterados(filtros))


def listar_cuidados(busca="", status="todos", ordem="antigos"):
    """Cuidados da agenda, filtrados por status e texto e ordenados por data."""
    status_banco = STATUS_DO_FILTRO.get(status, "")
    with conectar_banco() as conexao:
        cuidados = conexao.execute("""
            SELECT * FROM cuidados
            WHERE (? = '' OR status = ?)
            ORDER BY
                CASE WHEN ? = 'recentes' THEN data END DESC,
                CASE WHEN ? = 'recentes' THEN id END DESC,
                data ASC,
                id ASC
        """, (status_banco, status_banco, ordem, ordem)).fetchall()

    if not busca:
        return cuidados

    termo = busca.casefold()
    return [
        cuidado for cuidado in cuidados
        if any(termo in cuidado[campo].casefold() for campo in CAMPOS_PESQUISADOS)
    ]


def inserir_cuidado(nome_pet, tipo_cuidado, descricao, data_banco):
    with conectar_banco() as conexao:
        conexao.execute("""
            INSERT INTO cuidados
            (nome_pet, tipo_cuidado, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)
        """, (nome_pet, tipo_cuidado, descricao, data_banco, "Pendente"))


def alterar_cuidado(sql, id_cuidado):
    """Executa um UPDATE ou DELETE pelo id e retorna quantos registros mudaram."""
    with conectar_banco() as conexao:
        return conexao.execute(sql, (id_cuidado,)).rowcount


def buscar_cuidado(id_cuidado):
    """Retorna o cuidado com esse id, ou None se ele não existir."""
    with conectar_banco() as conexao:
        return conexao.execute(
            "SELECT * FROM cuidados WHERE id = ?", (id_cuidado,)
        ).fetchone()


def atualizar_cuidado(id_cuidado, nome_pet, tipo_cuidado, descricao, data_banco):
    """Grava os novos dados do cuidado. O status não muda."""
    with conectar_banco() as conexao:
        conexao.execute("""
            UPDATE cuidados
            SET nome_pet = ?, tipo_cuidado = ?, descricao = ?, data = ?
            WHERE id = ?
        """, (nome_pet, tipo_cuidado, descricao, data_banco, id_cuidado))


def dados_do_formulario(cuidado):
    """Dados de um cuidado gravado no formato em que o formulário os mostra."""
    tipo = cuidado["tipo_cuidado"]
    personalizado = tipo not in TIPOS_CUIDADO
    return {
        "nome_pet": cuidado["nome_pet"],
        "tipo_cuidado": TIPO_PERSONALIZADO if personalizado else tipo,
        "tipo_personalizado": tipo if personalizado else "",
        "descricao": cuidado["descricao"],
        "data": data_br(cuidado["data"]),
    }


def pagina_inicial(erros=(), dados=None, edicao=None):
    filtros = ler_filtros(request.args)
    alterados = filtros_alterados(filtros)
    return render_template(
        "index.html",
        cuidados=listar_cuidados(**filtros),
        erros=erros,
        dados=dados,
        edicao=edicao,
        filtros=filtros,
        filtros_ativos=bool(alterados),
        consulta_filtros=urlencode(alterados)
    )


def converter_data(data_digitada):
    """Converte DD/MM/AAAA para date, ou retorna None se a data for inválida."""
    if not FORMATO_DATA.fullmatch(data_digitada):
        return None

    try:
        return datetime.strptime(data_digitada, "%d/%m/%Y").date()
    except ValueError:
        return None


def tipo_escolhido(tipo_cuidado, tipo_personalizado):
    """Tipo que vai para o banco: o da lista ou o digitado, sem espaços nas pontas."""
    if tipo_cuidado == TIPO_PERSONALIZADO:
        return tipo_personalizado.strip()
    return tipo_cuidado


def validar_cuidado(
    nome_pet, tipo_cuidado, descricao, data_digitada, tipo_personalizado="", data_atual=None
):
    """Retorna a lista de mensagens de erro do cadastro (vazia se estiver tudo certo).

    Na edição, data_atual é a data já gravada (AAAA-MM-DD). Ela continua
    aceita mesmo que já tenha passado, para que cuidados antigos possam ser
    corrigidos; qualquer outra data passada é recusada.
    """
    erros = []

    if not nome_pet.strip():
        erros.append("Informe o nome do pet.")
    elif len(nome_pet) > LIMITE_NOME_PET:
        erros.append(f"O nome do pet pode ter no máximo {LIMITE_NOME_PET} caracteres.")

    if tipo_cuidado == TIPO_PERSONALIZADO:
        tipo_digitado = tipo_personalizado.strip()
        if not tipo_digitado:
            erros.append("Informe o tipo de cuidado.")
        elif len(tipo_digitado) > LIMITE_TIPO_PERSONALIZADO:
            erros.append(
                f"O tipo de cuidado pode ter no máximo {LIMITE_TIPO_PERSONALIZADO} caracteres."
            )
    elif tipo_cuidado not in TIPOS_CUIDADO:
        erros.append("Selecione um tipo de cuidado válido.")

    if not descricao.strip():
        erros.append("Informe a descrição do cuidado.")
    elif len(descricao) > LIMITE_DESCRICAO:
        erros.append(f"A descrição pode ter no máximo {LIMITE_DESCRICAO} caracteres.")

    data_convertida = converter_data(data_digitada)

    if data_convertida is None:
        erros.append("Data inválida. Digite uma data válida no formato DD/MM/AAAA.")
    elif data_convertida < date.today() and data_convertida.isoformat() != data_atual:
        erros.append("A data não pode ser anterior a hoje.")

    return erros


@app.route("/", methods=["GET", "POST"])
def inicio():

    if request.method != "POST":
        return pagina_inicial()

    nome_pet = request.form.get("nome_pet", "")
    tipo_cuidado = request.form.get("tipo_cuidado", "")
    tipo_personalizado = request.form.get("tipo_personalizado", "")
    descricao = request.form.get("descricao", "")
    data_digitada = request.form.get("data", "")

    erros = validar_cuidado(
        nome_pet, tipo_cuidado, descricao, data_digitada, tipo_personalizado
    )

    if erros:
        return pagina_inicial(erros, request.form)

    data_banco = converter_data(data_digitada).strftime("%Y-%m-%d")
    inserir_cuidado(
        nome_pet, tipo_escolhido(tipo_cuidado, tipo_personalizado), descricao, data_banco
    )

    return redirect(endereco_da_agenda(ler_filtros(request.args)))


@app.route("/editar/<int:id_cuidado>", methods=["GET", "POST"])
def editar(id_cuidado):

    cuidado = buscar_cuidado(id_cuidado)

    if cuidado is None:
        abort(404)

    if request.method != "POST":
        return pagina_inicial(dados=dados_do_formulario(cuidado), edicao=cuidado)

    nome_pet = request.form.get("nome_pet", "")
    tipo_cuidado = request.form.get("tipo_cuidado", "")
    tipo_personalizado = request.form.get("tipo_personalizado", "")
    descricao = request.form.get("descricao", "")
    data_digitada = request.form.get("data", "")

    erros = validar_cuidado(
        nome_pet, tipo_cuidado, descricao, data_digitada, tipo_personalizado,
        data_atual=cuidado["data"]
    )

    if erros:
        return pagina_inicial(erros, request.form, edicao=cuidado)

    data_banco = converter_data(data_digitada).strftime("%Y-%m-%d")
    atualizar_cuidado(
        id_cuidado, nome_pet, tipo_escolhido(tipo_cuidado, tipo_personalizado),
        descricao, data_banco
    )

    return redirect(endereco_da_agenda(ler_filtros(request.args)))


@app.route("/concluir/<int:id_cuidado>", methods=["POST"])
def concluir(id_cuidado):

    alterados = alterar_cuidado("""
        UPDATE cuidados
        SET status = 'Concluído'
        WHERE id = ?
    """, id_cuidado)

    if alterados == 0:
        abort(404)

    return redirect(endereco_da_agenda(ler_filtros(request.args)))


@app.route("/excluir/<int:id_cuidado>", methods=["POST"])
def excluir(id_cuidado):

    alterados = alterar_cuidado("""
        DELETE FROM cuidados
        WHERE id = ?
    """, id_cuidado)

    if alterados == 0:
        abort(404)

    return redirect(endereco_da_agenda(ler_filtros(request.args)))


@app.errorhandler(CSRFError)
def erro_csrf(erro):
    pagina = (
        '<!DOCTYPE html>\n<html lang="pt-BR">\n<head><meta charset="UTF-8">'
        "<title>PetCare</title></head>\n"
        f'<body>\n<p>{MSG_CSRF}</p>\n<p><a href="/">Voltar para a agenda</a></p>\n'
        "</body>\n</html>\n"
    )
    return pagina, 400


@app.template_filter("data_br")
def data_br(data):

    try:
        data_convertida = datetime.strptime(
            data,
            "%Y-%m-%d"
        )

        return data_convertida.strftime("%d/%m/%Y")

    except ValueError:
        return data


def modo_debug():
    """O modo debug fica desligado, a não ser que PETCARE_DEBUG seja "1"."""
    return os.environ.get("PETCARE_DEBUG") == "1"


if __name__ == "__main__":
    criar_banco()
    app.run(debug=modo_debug())
