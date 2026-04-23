'''
Parser Recursivo Descendente Gerado Automaticamente
'''

import ply.lex as lex
import sys
import re
import ply.yacc as yacc

# Definição da classe Node para representar os nós da árvore de análise sintática

class Node:
    def __init__(self, name, children=None, lexema=None):
        self.name = name
        self.children = children if children is not None else []
        self.lexema = lexema

    def pretty_print(self, prefix='', is_last=True):
        conector = '└── ' if is_last else '├── '
        label = self.name
        if self.lexema:
            label += f': {self.lexema}'
        print(prefix + conector + label)
        new_prefix = prefix + ('    ' if is_last else '│   ')

        for i, child in enumerate(self.children):
            isLast = (i == len(self.children) - 1)
            child.pretty_print(new_prefix, isLast)

#__Lexer__
tokens = (
    'INT',
    'ID',
    'RBRACK',
    'COMMA',
    'LBRACK',
)

# Símbolos fixos (Variáveis têm precedência por ordem de tamanho de regex)
def t_RBRACK(t):
    r'\]'
    return t

def t_COMMA(t):
    r','
    return t

def t_LBRACK(t):
    r'\['
    return t

def t_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[A-Za-z]+'
    return t

t_ignore = " \t\n"
def t_error(t):
    print(f'Erro na linha {t.lineno}: Caractere ilegal "{t.value[0]}"')
    lexer.lineno += 1
    t.lexer.skip(1)

lexer = lex.lex()

#__Parser__

'''
Mapeamento para tokens simples
'(': LPAREN, etc.

simpleT_map = {
    'RBRACK': ']',
    'COMMA': ',',
    'LBRACK': '['
}
'''

def tokenizer(info):
    lexer.input(info)
    token_stream = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        token_stream.append((tok.type, tok.value))
    token_stream.append(('final', 'final'))
    return token_stream
# Variáveis globais para o parser
token_stream = [] # Lista global para armazenar os tokens
token_pos = 0 # Posição atual no token_stream
type_actual = None # Tipo do token atual
lex_actual = None # Lexema do token atual

def advance():
    global token_stream, token_pos, type_actual, lex_actual
    if token_pos < len(token_stream) - 1:
        token_pos += 1
    type_actual, lex_actual = token_stream[token_pos]

def match(symbol):
    if type_actual == symbol:
        lex = lex_actual
        advance()
        return lex
    raise SyntaxError(f'Erro: esperado {symbol}, mas encontrado {type_actual}')

def p_Lista():
    '''Lista : [ Elems ]'''
    if type_actual == 'LBRACK':
        children = []
        children.append(Node('LBRACK', lexema=match('LBRACK')))
        children.append(p_Elems())
        children.append(Node('RBRACK', lexema=match('RBRACK')))
        return Node('Lista', children=children)
    raise SyntaxError(f'Erro em Lista: inesperado {type_actual}')

def p_Elems():
    '''Elems : Elem Resto | ε '''
    if type_actual == 'ID' or type_actual == 'INT':
        children = []
        children.append(p_Elem())
        children.append(p_Resto())
        return Node('Elems', children=children)
    elif type_actual == 'RBRACK':
        children = []
        children.append(Node('ε'))
        return Node('Elems', children=children)
    raise SyntaxError(f'Erro em Elems: inesperado {type_actual}')

def p_Resto():
    '''Resto : , Elem Resto | ε '''
    if type_actual == 'COMMA':
        children = []
        children.append(Node('COMMA', lexema=match('COMMA')))
        children.append(p_Elem())
        children.append(p_Resto())
        return Node('Resto', children=children)
    elif type_actual == 'RBRACK':
        children = []
        children.append(Node('ε'))
        return Node('Resto', children=children)
    raise SyntaxError(f'Erro em Resto: inesperado {type_actual}')

def p_Elem():
    '''Elem : INT  | ID '''
    if type_actual == 'INT':
        children = []
        children.append(Node('INT', lexema=match('INT')))
        return Node('Elem', children=children)
    elif type_actual == 'ID':
        children = []
        children.append(Node('ID', lexema=match('ID')))
        return Node('Elem', children=children)
    raise SyntaxError(f'Erro em Elem: inesperado {type_actual}')

def parser_gram(info):
    global token_stream, token_pos, type_actual, lex_actual
    token_stream = tokenizer(info)
    print(token_stream)
    token_pos = 0
    lexer.lineno = 1
    type_actual, lex_actual = token_stream[0]
    result = p_Lista() 
    if type_actual != 'final':
        raise SyntaxError(f"Tokens extra após o fim: {type_actual}")
    return result

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            print(f"Parsing file: {sys.argv[1]}")
            source = f.read()
    else:
        print("No input file provided. Using default test string.")
    try:
        result = parser_gram(source)
        result.pretty_print()
    except Exception as e:
        print(f'Erro durante o parsing: {e}')

if __name__ == '__main__':
    main()