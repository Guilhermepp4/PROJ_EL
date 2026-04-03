import sys
import os
from parser_grammar import parser_gram
import pprint

GRAMMAR_EXAMPLE = """\
Program : Lista

Lista -> '[' Elems ']'
Elems -> ε
    | Elem ',' Elems
Elem -> INT | ID

INT = /[0-9]+/
"""


def exec_pipeline(info):
    print("Welcome to Grammar Playground\n")
    print("1º PASSO - Desenvolver AST\n")

    print("\n--- A processar gramática ---")
    resultado_ast = parser_gram(info)
    
    if resultado_ast:
        print("\nAST (Estrutura de Dados):")
        resultado_ast.print_tree()

    else:
        print("Erro: O parser não devolveu resultados.")


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
        print("Não foi detetada nenhuma gramática\n")
        print("Processar a gramática de exemplo\n") 
        exec_pipeline(GRAMMAR_EXAMPLE)  
    