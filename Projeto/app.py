import io
import re
from contextlib import redirect_stdout
from flask import Flask, render_template, request, session, redirect
from datetime import datetime
from src.classes_parser import (Init, Regra, Producoes)
from src.first_follow import *
from src.parser_grammar import parser_gram
from src.main import conflitos, GRAMMAR_EXAMPLE
from src.parser_table import gera_parser_TopDown
from src.parser_rec import gera_parser_recursivo

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

@app.route('/autofix', methods=['POST'])
def autofix():
    # Limpa o target para garantir que temos apenas o nome (ex: "lista")
    raw_target = request.form.get('target', '').strip()
    target = raw_target.split('->')[0].split(' ')[0].strip()

    novas_regras_str = request.form.get('new_rules')
    grammar_text = session.get('grammar_text', "")

    if not target or not novas_regras_str:
        return redirect('/parsers')

    linhas = grammar_text.split('\n')
    nova_gramatica = []
    indice_insercao = -1
    
    # Prepara as regras para serem inseridas com a indentação correta
    regras_novas = [r.strip() for r in novas_regras_str.split(';') if r.strip()]
    
    i = 0
    while i < len(linhas):
        linha_original = linhas[i]
        linha_limpa = linha_original.strip()
        
        if re.match(rf"^{re.escape(target)}\s*(->|:)", linha_limpa):
            if indice_insercao == -1:
                indice_insercao = i
            
            # Pular a linha atual e todas as que começam com '|'
            i += 1
            while i < len(linhas) and linhas[i].strip().startswith('|'):
                i += 1
            continue
        
        nova_gramatica.append(linha_original)
        i += 1

    # Inserção no local correto
    if indice_insercao != -1:
        for j, regra in enumerate(regras_novas):
            nova_gramatica.insert(indice_insercao + j, regra)
    else:
        # Se não achou a regra original, anexa ao fim
        nova_gramatica.extend(regras_novas)

    # Atualiza a sessão
    session['grammar_text'] = "\n".join(nova_gramatica).strip()
    
    # O print agora deve aparecer se o fluxo chegar aqui
    print(f"DEBUG: Regra {target} substituída com sucesso.")
    
    return redirect('/parsers')

@app.route('/parsers')
def parsersRoute():
    grammar_text = session.get('grammar_text')

    if not grammar_text:
        return redirect('/dashboard')
    
    print(grammar_text)
    grammar_obj = parser_gram(grammar_text)
    if grammar_obj is None:
        # Em vez de crashar, volta ao dashboard com um aviso
        return "Erro: A gramática gerada pelo Autofix é inválida. Verifique o console."
    nT = grammar_obj.get_nonterminals() 
    first = compute_first(grammar_obj)
    follow = compute_follow(first, grammar_obj)

    tabela, lista_conflitos = checkLL1(grammar_obj, first, follow)
    sugestões = conflitos(lista_conflitos, first, follow, grammar_obj)
    if sugestões:    
        for s in sugestões:
            print(f"💡 Sugestão: {s}")
    return render_template("parsers.html", tabela=tabela, conflitos=lista_conflitos, sugestoes=sugestões, non_terminals=nT)

@app.route('/generate_parser', methods=['POST'])
def generate_parser():
    grammar_text = session.get('grammar_text')
    option = request.form.get('action_id')

    if not grammar_text:
        return redirect('/dashboard')
    
    grammar_obj = parser_gram(grammar_text)
    if grammar_obj is None:
        return "Erro: A gramática é inválida. Verifique o console."
    
    first = compute_first(grammar_obj)
    follow = compute_follow(first, grammar_obj)

    if option == 'Table':
        parser_code = gera_parser_TopDown(grammar_obj, first, follow)
    else:
        parser_code = gera_parser_recursivo(grammar_obj, first, follow)

    # Salva o código do parser em um arquivo
    with open(f"generated_parser{option}.py", "w") as f:
        f.write(parser_code)
    
    return "Parser gerado com sucesso! O código foi salvo em 'generated_parser.py'."

if __name__ == '__main__':
    app.run(debug = True)