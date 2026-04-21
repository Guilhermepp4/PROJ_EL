import io
from contextlib import redirect_stdout
from flask import Flask, render_template, request
from datetime import datetime
from src.classes_parser import (Init, Regra, Producoes)
from src.first_follow import *
from src.parser_grammar import parser_gram
from src.main import GRAMMAR_EXAMPLE

app = Flask(__name__)

data_hora_local = datetime.now()
data_iso = data_hora_local.strftime('"%Y-%m-%dT%H:%M:%S')

@app.route('/')
@app.route('/start')
def index():
    return render_template("start.html", data_iso = data_iso)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboardRoute():
    if request.method == 'POST':
        # Quando o utilizador clica no botão, processamos a gramática
        info = request.form.get('grammar')
        
        grammar_obj = parser_gram(info)

        if grammar_obj is None:
            return render_template("dashboard.html", grammar_input=info, firsts={}, follows={}, ast_visual="", terminals=[], non_terminals=[], tokens={})

        nT = grammar_obj.get_nonterminals()
        T = grammar_obj.get_Terminals()
        Tok = grammar_obj.get_token()   

        f = io.StringIO()
        with redirect_stdout(f):
            grammar_obj.print_tree()
        ast_string = f.getvalue()

        first = compute_first(grammar_obj)
        follow = compute_follow(first, grammar_obj)
        
        return render_template("dashboard.html", 
                               grammar_input=info,
                               terminals=T,
                               non_terminals=nT,
                               tokens=Tok, 
                               firsts=first, 
                               follows=follow,
                               ast_visual=ast_string)
    
    else:
        return render_template("dashboard.html", 
                               grammar_input="", 
                               firsts={}, 
                               follows={},
                               ast_visual="",
                               terminals=[],
                               non_terminals=[],
                               tokens={}
                               )

# @app.route('/livro/<id_livro>')
# def livroRoute(id_livro):   
#     return render_template("livro.html", livro = livro)

# @app.route('/eventos')
# def eventosRoute():
#     return render_template("eventos.html", livros = livro)


if __name__ == '__main__':
    app.run(debug = True)