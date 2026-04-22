import io
from contextlib import redirect_stdout
from flask import Flask, render_template, request, session, redirect
from datetime import datetime
from src.classes_parser import (Init, Regra, Producoes)
from src.first_follow import *
from src.parser_grammar import parser_gram
from src.main import conflitos, GRAMMAR_EXAMPLE

app = Flask(__name__)

data_hora_local = datetime.now()
data_iso = data_hora_local.strftime('"%Y-%m-%dT%H:%M:%S')
app.secret_key = 'uma_chave'

@app.route('/')
@app.route('/start')
def index():
    return render_template("start.html", data_iso = data_iso)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboardRoute():
    if request.method == 'POST':
        # Quando o utilizador clica no botão, processamos a gramática
        info = request.form.get('grammar')
        session['grammar_text'] = info
    
    else:
        info = session.get('grammar_text',)
    
    if not info:
        return render_template("dashboard.html", grammar_input=info, firsts={}, follows={}, ast_visual="", terminals=[], non_terminals=[], tokens={})
    
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

@app.route('/reset')
def reset():
    session.pop('grammar_text', None)
    return redirect('/dashboard')

@app.route('/parsers')
def parsersRoute():
    grammar_text = session.get('grammar_text')

    if not grammar_text:
        return redirect('/dashboard')
    
    grammar_obj = parser_gram(grammar_text)
    nT = grammar_obj.get_nonterminals()
    first = compute_first(grammar_obj)
    follow = compute_follow(first, grammar_obj)

    tabela, lista_conflitos = checkLL1(grammar_obj, first, follow)
    conflitos(lista_conflitos, first, follow, grammar_obj)
    return render_template("parsers.html", tabela=tabela, conflitos=lista_conflitos, non_terminals=nT)

if __name__ == '__main__':
    app.run(debug = True)