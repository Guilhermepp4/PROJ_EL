import sys
import os
from parser_grammar import parser_gram
from parser_rec import gera_parser_recursivo
from parser_table import gera_parser_TopDown
from first_follow import *
from my_visitor import gera_visitor

GRAMMAR_EXAMPLE = """
Program : lista

lista -> '['']'
    | '[' Elems ']'

Elems -> Elems "," Elem
    | Elem

Elem -> INT
"""

# GRAMMAR_EXAMPLE = """
# Program : S
# S -> '0' S '0'
#      | '1' S '1'
#      | '0'
#      | '1'
#      | 'ε'
# """

# GRAMMAR_EXAMPLE = """
# Program : Lista

# Lista -> '[' Elems ']'
# Elems -> Elem Resto
#     | ε

# Resto -> ',' Elem Resto
#     | ε

# Elem -> INT | ID

# INT = /[0-9]+/

# ID = /[A-Za-z]+/
# """

# GRAMMAR_EXAMPLE = """
# Program : S
# S -> Stmt
# Stmt -> 'if' 'cond' 'then' Stmt ElsePart | 'other'
# ElsePart -> 'else' Stmt | ε
# """

def processarAST(info):
    print("-------- A processar gramática --------")
    resultado_ast = parser_gram(info)
    
    if resultado_ast:
        print("\n ✅ Gramática processada com sucesso")
        print("\nAST (Estrutura de Dados):")
        resultado_ast.print_tree()
        
        print(f"\nSimbolo inicial: {resultado_ast.get_inicial()}")
        print(f"Não Terminais: [{' - '.join(sorted(resultado_ast.get_nonterminals()))}]")
        print(f"Terminais:  [{' - '.join(sorted(resultado_ast.get_Terminals()))}]")
        print(f"Tokens: {resultado_ast.get_token()}")

    else:
        print("🚨 Erro: O parser não devolveu resultados 🚨")

    return resultado_ast

def conflitos(lista_conflitos, first, follow, resultado_ast):
    if lista_conflitos:
        sugestoes_para_html = []
        new_conflitos = []
        print(lista_conflitos)
        
        for conflito in lista_conflitos:
            new_conflito = conflito.split(" | ")
            new_conflitos.append(new_conflito[-1])
        print("🚨 A gramática possui conflitos:")
        
        sugestoes = sugerir_correcoes(first, follow, lista_conflitos, resultado_ast)
        for i, sug in enumerate(sugestoes):
            sugestoes_para_html.append({
                "tipo_real": sug['tipo_real'],
                "titulo": sug['titulo'],
                "conflito": new_conflitos[i],
                "proposta": sug['proposta']
            })

        return sugestoes_para_html

def makeFile(path, content, value):
    try:
        with open(path, "w", encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sucesso: {value} gerado!!!\n")
    except Exception as e:
            print(f"❗️ Error: {e} -> Não foi possivel escrever nem guardar o ficheiro {path}")

def exec_pipeline(info):
    print("Welcome to Grammar Playground\n")
    print("1º PASSO - Desenvolver AST\n")
    resultado_ast = processarAST(info)
    
    print("\n2º PASSO - Calcular Fisrt e o Follow\n")
    first = compute_first(resultado_ast)
    follow = compute_follow(first, resultado_ast)
    print_sets(first, follow)
    print_lookahead_simples(resultado_ast, first, follow)

    print("\n3º PASSO - Verificar se é LL(1)")
    tabela, lista_conflitos = checkLL1(resultado_ast, first, follow)
    conflitos(lista_conflitos, first, follow, resultado_ast)
    
    if lista_conflitos:
        print("❗️ Atenção a gramática contém conflitos")
    else:
        print("✅ Gramática LL(1) válida!")

    print_tabela(tabela)

    print("\n4º PASSO - Gerar os Parsers\n")

    if lista_conflitos:
        print("❗️ Atenção a gramática escolhida, esta apresenta conflitos."
              +"\nTente aplicar as sugestões antes de gerar os parsers")
    else:
        os.makedirs("parser_models", exist_ok=True)
        # Gerar o parser recursivo descendente correspondente
        print("4.1.º Passo - Parser recursivo Descendente")
        f1_content = gera_parser_recursivo(resultado_ast, first, follow)
        makeFile("parser_models/RDParser.py", f1_content, "Parser Recursivo Descendente")

        # Gerar o parser Top-Down dirigido por tabela correspondente
        print("4.2.º Passo - Parser Top-Down")
        f2_content = gera_parser_TopDown(resultado_ast, first, follow)
        makeFile("parser_models/TDownParser.py", f2_content, "Parser Top-Down dirigido por tabela")
    
    print("\n5º PASSO - Ações Semânticas via Funções de Visita\n")
    visitor_content = gera_visitor(resultado_ast)
    makeFile("parser_models/Visitor.py", visitor_content, "Visitor")

    print("Pipeline concluída com sucesso! 🎉\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file = sys.argv[1]
        try:
            with open(file, encoding='UTF-8') as f:
                info = f.read()
            print(f"Grámatica do ficheiro {file} lida com sucesso")
        
        except Exception as e:
            print(f"Erro encontrado - {e} \n")
            sys.exit(1)
        exec_pipeline(info)
    else:
        print("❌ Não foi detetada nenhuma gramática ❌")
        print("Processar a gramática de exemplo\n") 
        exec_pipeline(GRAMMAR_EXAMPLE)  
    