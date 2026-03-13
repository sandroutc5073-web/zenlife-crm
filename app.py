from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "zenlifecrm"


def conectar():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ======================
# LOGIN
# ======================

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = conectar()

        user = conn.execute(
            "SELECT * FROM usuarios WHERE usuario=? AND senha=?",
            (usuario,senha)
        ).fetchone()

        conn.close()

        if user:

            session["usuario"] = usuario
            return redirect("/")

        else:

            return "Usuário ou senha inválidos"

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.pop("usuario",None)

    return redirect("/login")


# ======================
# DASHBOARD
# ======================

@app.route("/")
def dashboard():

    if "usuario" not in session:
        return redirect("/login")

    conn = conectar()

    total_clientes = conn.execute(
        "SELECT COUNT(*) FROM clientes"
    ).fetchone()[0]

    total_leads = conn.execute(
        "SELECT COUNT(*) FROM leads"
    ).fetchone()[0]

    total_apolices = conn.execute(
        "SELECT COUNT(*) FROM apolices"
    ).fetchone()[0]

    leads_novos = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE status='Lead Novo'"
    ).fetchone()[0]

    propostas = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE status='Proposta Enviada'"
    ).fetchone()[0]

    fechados = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE status='Fechado'"
    ).fetchone()[0]

    if leads_novos > 0:
        conversao = round((fechados / leads_novos) * 100,1)
    else:
        conversao = 0

    vendas = conn.execute("""
        SELECT seguro, COUNT(*)
        FROM leads
        GROUP BY seguro
    """).fetchall()

    tipos = [v[0] for v in vendas]
    quantidades = [v[1] for v in vendas]

    conn.close()

    return render_template(
        "index.html",
        total_clientes=total_clientes,
        total_leads=total_leads,
        total_apolices=total_apolices,
        leads_novos=leads_novos,
        propostas=propostas,
        fechados=fechados,
        conversao=conversao,
        tipos=tipos,
        quantidades=quantidades
    )


# ======================
# CLIENTES
# ======================

@app.route("/clientes")
def clientes():

    conn = conectar()
    lista = conn.execute("SELECT * FROM clientes").fetchall()
    conn.close()

    return render_template("clientes.html",clientes=lista)


@app.route("/novo_cliente", methods=["POST"])
def novo_cliente():

    nome = request.form["nome"]
    telefone = request.form["telefone"]
    email = request.form["email"]

    conn = conectar()

    conn.execute(
        "INSERT INTO clientes (nome,telefone,email) VALUES (?,?,?)",
        (nome,telefone,email)
    )

    conn.commit()
    conn.close()

    return redirect("/clientes")


# ======================
# LEADS
# ======================

@app.route("/leads")
def leads():

    conn = conectar()
    lista = conn.execute("SELECT * FROM leads").fetchall()
    conn.close()

    return render_template("leads.html",leads=lista)


@app.route("/novo_lead", methods=["POST"])
def novo_lead():

    nome = request.form["nome"]
    telefone = request.form["telefone"]
    seguro = request.form["seguro"]
    origem = request.form["origem"]
    status = request.form["status"]

    conn = conectar()

    conn.execute("""
        INSERT INTO leads
        (nome,telefone,seguro,origem,status)
        VALUES (?,?,?,?,?)
    """,(nome,telefone,seguro,origem,status))

    conn.commit()
    conn.close()

    return redirect("/leads")


# ======================
# AGENDA
# ======================

@app.route("/agenda")
def agenda():

    conn = conectar()

    tarefas = conn.execute(
        "SELECT * FROM agenda ORDER BY data_contato"
    ).fetchall()

    conn.close()

    return render_template("agenda.html",tarefas=tarefas)


@app.route("/nova_tarefa", methods=["POST"])
def nova_tarefa():

    cliente = request.form["cliente"]
    descricao = request.form["descricao"]
    data = request.form["data"]

    conn = conectar()

    conn.execute("""
        INSERT INTO agenda
        (cliente,descricao,data_contato)
        VALUES (?,?,?)
    """,(cliente,descricao,data))

    conn.commit()
    conn.close()

    return redirect("/agenda")
    
# ======================
# APOLICES
# ======================

@app.route("/apolices")
def apolices():

    if "usuario" not in session:
        return redirect("/login")

    conn = conectar()

    lista = conn.execute(
        "SELECT * FROM apolices"
    ).fetchall()

    conn.close()

    return render_template("apolices.html", apolices=lista)


@app.route("/nova_apolice", methods=["POST"])
def nova_apolice():

    cliente = request.form["cliente"]
    seguro = request.form["seguro"]
    seguradora = request.form["seguradora"]
    valor = request.form["valor"]
    inicio = request.form["inicio"]
    renovacao = request.form["renovacao"]

    conn = conectar()

    conn.execute("""
        INSERT INTO apolices
        (cliente,seguro,seguradora,valor,data_inicio,data_renovacao)
        VALUES (?,?,?,?,?,?)
    """,(cliente,seguro,seguradora,valor,inicio,renovacao))

    conn.commit()
    conn.close()

    return redirect("/apolices")


if __name__ == "__main__":
    app.run(debug=True)