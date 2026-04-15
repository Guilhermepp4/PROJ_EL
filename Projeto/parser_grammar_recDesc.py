import re
from first_follow import rool_seq
from classes_parser import *

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

def simpleT(term):
    if term.startswith(("'", '"')) or term.startswith(('"', '"')):
        return True 
    return False

def tokT(inner):
    if inner in NOMES_SIMBOLOS:
        nome = NOMES_SIMBOLOS[inner]
    else:
        nome = re.sub(r'[^A-Za-z0-9]', '_', inner).strip('_').upper()
        
        if not nome:
            nome = str(ord(inner[0]))
            
    return nome

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

    print(tokens)
    terminals_formatada = [formatar_simbolo(s) for s in terminals]
    simpleToken = {}
    for t in terminals_formatada:
        if simpleT(t):
            token = tokT(t[1:-1])
            simpleToken[token] = t[1:-1]
    
    parserLines = []
    parserLines.append("'''")
    parserLines.append("Parser Recursivo Descendente Gerado Automaticamente")
    parserLines.append("'''")
    parserLines.append("")
    parserLines.append("import ply.lex as lex")
    parserLines.append("import re")
    parserLines.append("import ply.yacc as yacc")
    parserLines.append("")
    parserLines.append("#__Lexer__")
    parserLines.append('print("Start the Lexer")')
    parserLines.append('tokens = (')
    for t in tokens:
        parserLines.append(f"    '{t}',")
    for t in simpleToken:
        parserLines.append(f"    '{t}',")
    parserLines.append(')')
    parserLines.append("")
    parserLines.append("# Símbolos fixos (Variáveis têm precedência por ordem de tamanho de regex)")
    for t, s in simpleToken.items():
        parserLines.append(f"t_{t} = r'{re.escape(s)}'")
    parserLines.append('t_ignore = " \t"')
    parserLines.append("")
    parserLines.append("# Terminais escritos explicitamente entre aspas: 'id', '+'")
    
    for t, s in tokens.items():
        parserLines.append(f"def t_{t}(t):")
        parserLines.append(f"    r'{re.escape(s)}'")
        parserLines.append(f"    return t")
        parserLines.append("")
    parserLines.append("def t_error(t):")
    parserLines.append("    print(f'Erro na linha {t.lineno}: Caractere ilegal \"{t.value[0]}\"')")
    parserLines.append("    t.lexer.skip(1)")
    parserLines.append("")
    parserLines.append("lexer = lex.lex()")


    parserLines.append("")    
    parserLines.append('#__Parser__')    
    parserLines.append('print("Start the Parser")')
    return '\n'.join(parserLines)