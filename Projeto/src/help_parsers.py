import re

NOMES_SIMBOLOS = {
    ';': 'SEMICOLON',
    ':': 'COLON',
    ':=': 'ASSIGN',
    ',': 'COMMA',
    '.': 'DOT',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '[': 'LBRACK',
    ']': 'RBRACK',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'STAR',
    '/': 'DIV',
    '=': 'EQUALS'
}

#Função para simplificar um terminal EX: Elems' -> Elems_Prime
def SimpleToken(token):
    return re.sub(r'[^A-Za-z0-9]', '_', token.replace("'", "_Prime")).strip('_')

#Função para verificar se um terminal é um símbolo fixo (entre aspas) ou não
def simpleT(term):
    if term.startswith(("'", '"')) and term.endswith(("'", '"')):
        return True 
    return False

#Função que dá um nome a um token sobre aspas, ex: '+' -> PLUS, '(' -> LPAREN, etc
def tokT(inner):
    if inner in NOMES_SIMBOLOS:
        nome = NOMES_SIMBOLOS[inner]
    else:
        nome = re.sub(r'[^A-Za-z0-9]', '_', inner).strip('_').upper()
        
        if not nome:
            nome = str(ord(inner[0]))
            nome = f"T_{nome}"
            
    return nome

def formatar_simbolo(s):
    if s == 'ε' or s.isalnum():
        return s
    else:
        return f"'{s}'"