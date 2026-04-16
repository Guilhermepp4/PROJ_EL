import sys
import os
from parser_grammar import parser_gram
from parser_grammar_recDesc import gera_parser_recursivo
from parser_grammar_TopDown import gera_parser_TopDown
import time
from first_follow import *

# GRAMMAR_EXAMPLE = """
# Program : lista

# lista -> '['']'
#     | '[' Elems ']'

# Elems -> Elems "," Elem
#     | Elem

# Elem -> INT
# """

# GRAMMAR_EXAMPLE = """
# Program : S
# S -> '0' S '0'
#      | '1' S '1'
#      | '0'
#      | '1'
#      | 'ε'
# """

GRAMMAR_EXAMPLE = """
Program : Lista

Lista -> '[' Elems ']'
Elems -> Elem Resto
    | ε

Resto -> ',' Elem Resto
    | ε

Elem -> INT | ID

INT = /[0-9]+/

ID = /[A-Za-z]+/
"""

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

def conflitos(tabela, lista_conflitos, first, follow, resultado_ast):
    if lista_conflitos:
        print(lista_conflitos)
        print("🚨 A gramática possui conflitos:")
        sugestoes = sugerir_correcoes(first, follow, lista_conflitos, resultado_ast)
        for sug in sugestoes:
            print(f"Sugestão para {sug['tipo_real']}: {sug['titulo']}")
            for linha in sug['proposta']:
                print(f"  -> {linha}")
            print()

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
    conflitos(tabela, lista_conflitos, first, follow, resultado_ast)
    
    print("\n4º PASSO - Parsing LL(1)\n")
    if lista_conflitos:
        print("❗️ Atenção a gramática continha conflitos")
    else:
        print("✅ Gramática LL(1) válida!")

    print_tabela(tabela)

    print("\n5º PASSO - Gerar os Parsers\n")

    if lista_conflitos:
        print("❗️ Atenção a gramática escolhida, esta apresenta conflitos."
              +"\nTente aplicar as sugestões antes de gerar os parsers")
    else:
        # Gerar o parser recursivo descendente correspondente
        print("5.1.º Passo - Parser recursivo Descendente\n")
        f1_content = gera_parser_recursivo(resultado_ast, first, follow)

        #os.makedirs("parser_models", exist_ok=True)
        f_write = "RDParser.py"
        try:
            with open(f_write, "w", encoding='utf-8') as f:
                f.write(f1_content)
            print("✅ Sucesso: Parser recursivo descendente gerado!!!")
        except Exception as e:
            print(f"❗️ Error: {e} -> Não foi possivel escrever nem guardar o ficheiro {f_write}")

        print("5.2.º Passo - Parser Top-Down\n")
        # f2_content = gera_parser_TopDown()

        # os.makedirs("parser_models", exist_ok=True)
        # f_write = "parser_models/TDownParser.py"
        # try:
        #     with open(f_write, "w", encoding='utf-8') as f:
        #         f.write(f2_content)
        #     print("✅ Sucesso: Parser Top-Down dirigido por tabela gerado!!!")
        # except Exception as e:
        #     print(f"❗️ Error: {e} -> Não foi possivel escrever nem guardar o ficheiro {f_write}")


        # Gerar o parser Top-Down dirigido por tabela correspondente


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
        
        # for i in range(3):
        #     print(".", end="", flush=True)
        #     time.sleep(1)
        
        exec_pipeline(GRAMMAR_EXAMPLE)  
    