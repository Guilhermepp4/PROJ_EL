import io
import re
from contextlib import redirect_stdout
from flask import Flask, render_template, request, session, redirect, make_response, jsonify
from datetime import datetime
import subprocess
import sys
import tempfile
import os
import uuid
import importlib.util

sys.dont_write_bytecode = True
sys.path.insert(0, 'src')

from classes_parser import (Init, Regra, Producoes)
from first_follow import *
from parser_grammar import parser_gram
from main import conflitos, GRAMMAR_EXAMPLE
from parser_table import gera_parser_TopDown
from parser_rec import gera_parser_recursivo
from my_visitor import gera_visitor
from ontology import generate_ontology

app = Flask(__name__)


data_hora_local = datetime.now()
data_iso = data_hora_local.strftime('"%Y-%m-%dT%H:%M:%S')
app.secret_key = 'uma_chave'


def gerar_codigo_do_parser(parser_grama, type):
    first = compute_first(parser_grama)
    follow = compute_follow(first, parser_grama)
    if type == 'Table':
        return gera_parser_TopDown(parser_grama, first, follow)
    else:
        return gera_parser_recursivo(parser_grama, first, follow)

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
    file_name = request.form.get('file_name', '').strip()

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

    response = make_response(parser_code)
    response.headers['Content-Disposition'] = f'attachment; filename={file_name}'
    response.headers['Content-Type'] = 'text/x-python'
        
    return response

@app.route('/set_mode/<mode>')
def set_mode(mode):
    session['mode'] = mode
    return redirect('/test')

@app.route('/test')
def test_page():
    mode = session.get('mode', 'parsing')
    grammar_text = session.get('grammar_text')
    
    context = {
        'visitor_content': "",
        'resultado': None
    }

    if mode == 'visitor' and grammar_text:
        grammar_obj = parser_gram(grammar_text)
        context['visitor_content'] = gera_visitor(grammar_obj)

    return render_template("test.html", **context)
    
@app.route('/run_test', methods=['POST'])
def run_test():
    gramma = session.get('grammar_text')
    parser_type = request.form.get('parser_type')
    test_input = request.form.get('test_input', '').strip()
    
    parser_gramma = parser_gram(gramma)
    codigo_gerado = gerar_codigo_do_parser(parser_gramma, parser_type)

    # 2. Criar um ficheiro temporário para o código e outro para o input
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as pf:
        pf.write(codigo_gerado)
        path_parser = pf.name

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode='w', encoding='utf-8') as inf:
        inf.write(test_input)
        path_input = inf.name

    try:
        res = subprocess.run(
            [sys.executable, path_parser, path_input],
            capture_output=True,
            text=True,
            timeout=5
        )

        lines = res.stdout.splitlines()
        finalTree = "Program\n"+"\n".join(lines[1:])
        if res.returncode != 1:
            resultado = {
                'status': 'success',
                'output': finalTree, 
            }
        else:
            for line in lines[1:]:
                    error_message = line
                    break
            resultado = {
                'status': 'error',
                'error': error_message or res.stderr.strip() or "Erro desconhecido durante a execução do parser."
            }

    except Exception as e:
        resultado = {'status': 'error', 'error': str(e)}
    finally:
        if os.path.exists(path_parser): os.remove(path_parser)
        if os.path.exists(path_input): os.remove(path_input)

    return render_template("test.html", resultado=resultado, last_input=test_input)


@app.route('/generate_visitor_to_ui', methods=['POST'])
def generate_visitor_to_ui():
    grammar_text = session.get('grammar_text')
    if not grammar_text:
        return jsonify({'status': 'error', 'message': 'Sem gramática'})

    grammar_obj = parser_gram(grammar_text)
    visitor_code = gera_visitor(grammar_obj)    
    return jsonify({'status': 'success', 'code': visitor_code})


@app.route('/generate_visitor', methods=['POST'])
def generate_visitor():
    grammar_text = session.get('grammar_text')
    file_name = request.form.get('file_name', '').strip()

    if not grammar_text:
        return redirect('/dashboard')
    
    grammar_obj = parser_gram(grammar_text)
    if grammar_obj is None:
        return "Erro: A gramática é inválida. Verifique o console."
    
    visitor_code = gera_visitor(grammar_obj)

    response = make_response(visitor_code)
    response.headers['Content-Disposition'] = f'attachment; filename={file_name}'
    response.headers['Content-Type'] = 'text/x-python'
        
    return response

@app.route('/run_visitor', methods=['POST'])
def run_visitor():
    grammar_t = session.get('grammar_text')
    if not grammar_t:
        return redirect('/dashboard')
    
    grammar = parser_gram(grammar_t)
    if grammar is None:
         return render_template("test.html", resultado={'status': 'error', 'error': 'Erro ao processar gramática.'}, visitor_content="")

    test_input = request.form.get('test_input', '').strip()
    
    codigo_gerado = gerar_codigo_do_parser(grammar, 'Table')
    
    unique_name = f"visitor_parser_{uuid.uuid4().hex}"
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as pf:
        pf.write(codigo_gerado)
        path_parser = pf.name
    
    codigo_do_editor = request.form.get('visitor_code', '').strip()
    
    if codigo_do_editor:
        visitor_content = codigo_do_editor
    else:
        visitor_content = gera_visitor(grammar)
            
    try:
        spec = importlib.util.spec_from_file_location(unique_name, path_parser)
        module = importlib.util.module_from_spec(spec)
        sys.modules[unique_name] = module
        spec.loader.exec_module(module)
        
        tree_object = module.parser_gramTD(test_input)
        vis_ns = {}
        
        exec(visitor_content, vis_ns)
        CodeGen = vis_ns.get('CodeGen')

        if not CodeGen:
            raise Exception("Classe CodeGen não encontrada no código do Visitor.")

        visitor_result = CodeGen().visit(tree_object)

        f = io.StringIO()
        with redirect_stdout(f):
            tree_object.pretty_print()
        tree_visual = f.getvalue()

        resultado = {
            'status': 'success',
            'output': 'Program\n'+tree_visual,
            'output_visitor': visitor_result
        }

    except Exception as e:
        resultado = {
            'status': 'error', 
            'error': f"Erro na execução: {str(e)}"
        }

    finally:
        # 7. Limpeza absoluta
        if os.path.exists(path_parser):
            try:
                os.remove(path_parser)
                if "dynamic_parser" in sys.modules:
                    del sys.modules["dynamic_parser"]
            except:
                pass

    return render_template("test.html", resultado=resultado, last_input=test_input, visitor_content=visitor_content)

@app.route('/generate_ontology', methods=['POST'])
def generateOntology():
    grammar_text = session.get('grammar_text')
    file_name = request.form.get('file_name', '').strip()

    if not grammar_text:
        return redirect('/dashboard')
    
    grammar_obj = parser_gram(grammar_text)
    if grammar_obj is None:
        return "Erro: A gramática é inválida. Verifique o console."
    
    first = compute_first(grammar_obj)
    follow = compute_follow(first, grammar_obj)
    
    _, lista_conflitos = checkLL1(grammar_obj, first, follow)

    ontology_code = generate_ontology(grammar_obj, file_name, lista_conflitos, first, follow)

    response = make_response(ontology_code)
    response.headers['Content-Disposition'] = f'attachment; filename={file_name}'
    response.headers['Content-Type'] = 'text/x-python'
        
    return response

if __name__ == '__main__':
    app.run(debug = True)