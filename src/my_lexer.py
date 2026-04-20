import ply.lex as lex
import re

tokens = (
    'ARROW', 'PIPE', 'EPSILON', 
    'EQUALS', 'TERMINAL', 'NON_TERMINAL',
    'REGEX', 'NEWLINE', 'COLON', 'PROGRAM'
)


# Símbolos fixos (Variáveis têm precedência por ordem de tamanho de regex)
t_ARROW     = r'->|→'
t_EQUALS    = r'='
t_COLON     = r':'
t_ignore = ' \t'

# Terminais escritos explicitamente entre aspas: 'id', '+'
def t_EPSILON(t):
    r'ε'
    t.type = 'EPSILON'
    return t

def t_TERMINAL_QUOTED(t):
    r"\'[^\']+\'|\"[^\"]+\""
    t.value = t.value[1:-1]
    t.type = 'TERMINAL'
    return t

def t_REGEX(t):
    r'/[^/]+/'
    t.value = t.value[1:-1]
    return t

def t_IDENTIFIER(t):
    r"[A-Za-z][A-Za-z0-9_]*'*"
    value = t.value
    base = value.lower()

    if base == 'program':
        t.type = 'PROGRAM'
    
    elif base == 'epsilon':
        t.type = 'EPSILON'
    
    elif re.fullmatch(r'[A-Z][A-Z0-9_]*', value):
        if len(value) == 1:
            t.type = 'NON_TERMINAL'
        else:
            t.type = 'TERMINAL'
    else:
        t.type = 'NON_TERMINAL'
    return t

def t_PIPE(t):
    r'\|'
    return t

def t_NEWLINE(t):
    r'\n([ \t]*\n)*[ \t]*'
    t.lexer.lineno += t.value.count('\n')
    rest = t.lexer.lexdata[t.lexer.lexpos:]
    if rest.lstrip(' \t').startswith('|'):
        return None
    return t

def t_COMMENT(t):
    r'\«[^»]*'
    pass

def t_error(t):
    print(f"Erro na linha {t.lineno}: Caractere ilegal '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()