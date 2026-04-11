import sys
import os
from parser_grammar import parser_gram
import time
from first_follow import *

# GRAMMAR_EXAMPLE = """
# Program : S
# S -> '0' S '0'
#      | '1' S '1'
#      | '0'
#      | '1'
#      | 'ε'
# """

# GRAMMAR_EXAMPLE = """\
# Program : Lista

# Lista -> '[' Elems ']'
# Elems -> ε
#     | Elem ',' Elems
# Elem -> INT | ID

# INT = /[0-9]+/
# ID = /[A-Za-z]+/
# """

GRAMMAR_EXAMPLE = """
Program : S
S -> A | B
A -> 'id' '==' 'number'
B -> 'id' '=' 'number'
C -> C '+' 'number' | 'number'
D -> 'if' E 'then' F
E -> 'bool'
F -> 'stmt' G
G -> 'else' 'stmt' | ε
"""

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


def exec_pipeline(info):
    print("Welcome to Grammar Playground\n")
    #time.sleep(1)
    print("1º PASSO - Desenvolver AST\n")
    resultado_ast = processarAST(info)
    
    print("\n2º PASSO - Calcular Fisrt e o Follow\n")
    first = compute_first(resultado_ast)
    follow = compute_follow(first, resultado_ast)
    print_sets(first, follow)
    tabela, lista_conflitos = lookahead(resultado_ast, first, follow)

    if lista_conflitos:
        print("🚨 A gramática possui conflitos:")
        for c in lista_conflitos:
            print(f" - {c}")
        sugestoes= sugerir_correcoes(lista_conflitos)
        for sugestao in sugestoes:
            print(sugestao)
    
    else:
        print_tabela(tabela)
        print("✅ Gramática LL(1) válida!")



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
    