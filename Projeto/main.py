import sys
import os
from parser_grammar import parser_gram
import time
from first_follow import compute_first, compute_follow

GRAMMAR_EXAMPLE = """\
Program : Lista

Lista -> '[' Elems ']'
Elems -> ε
    | Elem ',' Elems
Elem -> INT | ID

INT = /[0-9]+/
ID = /[A-Za-z]+/
"""
YELLOW = "\033[93m"


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
    print(first)
    #follow = compute_follow(resultado_ast)



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
    