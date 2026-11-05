import re
import sqlite3
from datetime import date, datetime

from flask import Flask, redirect, render_template, request

app = Flask(__name__)
app.config["DATABASE"] = "petcare.db"

TIPOS_CUIDADO = ("Vacina", "Consulta", "Medicamento", "Outro")
LIMITE_NOME_PET = 100
LIMITE_DESCRICAO = 500
FORMATO_DATA = re.compile(r"\d{2}/\d{2}/\d{4}")


def conectar_banco():
    conexao = sqlite3.connect(app.config["DATABASE"])
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    conexao = conectar_banco()

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

    conexao.commit()
    conexao.close()


def converter_data(data_digitada):
    """Converte DD/MM/AAAA para date, ou retorna None se a data for inválida."""
    if not FORMATO_DATA.fullmatch(data_digitada):
        return None

    try:
        return datetime.strptime(data_digitada, "%d/%m/%Y").date()
    except ValueError:
        return None


def validar_cuidado(nome_pet, tipo_cuidado, descricao, data_digitada):
    """Retorna a lista de mensagens de erro do cadastro (vazia se estiver tudo certo)."""
    erros = []

    if not nome_pet.strip():
        erros.append("Informe o nome do pet.")
    elif len(nome_pet) > LIMITE_NOME_PET:
        erros.append(f"O nome do pet pode ter no máximo {LIMITE_NOME_PET} caracteres.")

    if tipo_cuidado not in TIPOS_CUIDADO:
        erros.append("Selecione um tipo de cuidado válido.")

    if not descricao.strip():
        erros.append("Informe a descrição do cuidado.")
    elif len(descricao) > LIMITE_DESCRICAO:
        erros.append(f"A descrição pode ter no máximo {LIMITE_DESCRICAO} caracteres.")

    data_convertida = converter_data(data_digitada)

    if data_convertida is None:
        erros.append("Data inválida. Digite uma data válida no formato DD/MM/AAAA.")
    elif data_convertida < date.today():
        erros.append("A data não pode ser anterior a hoje.")

    return erros


@app.route("/", methods=["GET", "POST"])
def inicio():

    erros = []

    if request.method == "POST":

        nome_pet = request.form.get("nome_pet", "")
        tipo_cuidado = request.form.get("tipo_cuidado", "")
        descricao = request.form.get("descricao", "")
        data_digitada = request.form.get("data", "")

        erros = validar_cuidado(nome_pet, tipo_cuidado, descricao, data_digitada)

        if erros:

            conexao = conectar_banco()

            cuidados = conexao.execute("""
                SELECT * FROM cuidados
                ORDER BY data ASC
            """).fetchall()

            conexao.close()

            return render_template(
                "index.html",
                cuidados=cuidados,
                erros=erros,
                dados=request.form
            )

        data_banco = converter_data(data_digitada).strftime("%Y-%m-%d")

        conexao = conectar_banco()

        conexao.execute("""
            INSERT INTO cuidados
            (nome_pet, tipo_cuidado, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            nome_pet,
            tipo_cuidado,
            descricao,
            data_banco,
            "Pendente"
        ))

        conexao.commit()
        conexao.close()

        return redirect("/")

    conexao = conectar_banco()

    cuidados = conexao.execute("""
        SELECT * FROM cuidados
        ORDER BY data ASC
    """).fetchall()

    conexao.close()

    return render_template(
        "index.html",
        cuidados=cuidados,
        erros=erros
    )


@app.route("/concluir/<int:id>")
def concluir(id):

    conexao = conectar_banco()

    conexao.execute("""
        UPDATE cuidados
        SET status = 'Concluído'
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect("/")


@app.route("/excluir/<int:id>")
def excluir(id):

    conexao = conectar_banco()

    conexao.execute("""
        DELETE FROM cuidados
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect("/")


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


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
