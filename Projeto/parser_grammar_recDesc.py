import re
from first_follow import rool_seq
def simpleT(term):
    if term.startswith(("'", '"')) or term.startswith(('"', '"')):
        return True 
    return False

def tokT(inner):
    nome = re.sub(r'[^A-Za-z0-9]', '_', inner).strip('_').upper()
    if not nome:
        nome = str(ord(inner[0]))
        #print(nome)
    return 'TOK_' + nome 

def formatar_simbolo(s):
    if s == 'ε' or s.isalnum():
        return s
    else:
        return f"'{s}'"

def gera_parser_recursivo(grammar, first_sets, follow_sets):
    start = grammar.get_inicial()
    terminals = grammar.get_Terminals()
    nTerminals = grammar.get_nonterminals()
    tokens = grammar.get_token()

    terminals_formatada = [formatar_simbolo(s) for s in terminals]
    #print(f"[{', '.join(terminals_formatada)}]")
    #print(terminals)
    for t in terminals_formatada:
        if simpleT(t):
            ola = tokT(t[1:-1])
    return "\n"