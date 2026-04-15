'''
Parser Recursivo Descendente Gerado Automaticamente
'''

import ply.lex as lex
import re
import ply.yacc as yacc

#__Lexer__
print("Start the Lexer")
tokens = (
    'INT',
    'ID',
    'LBRACK',
    'RBRACK',
    'COMMA',
)

# Símbolos fixos (Variáveis têm precedência por ordem de tamanho de regex)
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_COMMA = r','
t_ignore = " 	"

# Terminais escritos explicitamente entre aspas: 'id', '+'
def t_INT(t):
    r'\[0\-9\]\+'
    return t

def t_ID(t):
    r'\[A\-Za\-z\]\+'
    return t

def t_error(t):
    print(f'Erro na linha {t.lineno}: Caractere ilegal "{t.value[0]}"')
    t.lexer.skip(1)

lexer = lex.lex()

#__Parser__
print("Start the Parser")