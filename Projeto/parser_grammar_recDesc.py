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
            nome = f"T_{nome}"
            
    return nome

def formatar_simbolo(s):
    if s == 'ε' or s:
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
    
    #Conseguimos simplificar os tokens fixos para um mapeamento simples
    #ex: '+' -> PLUS, '(' -> LPAREN, etc.
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
    parserLines.append("import sys")
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
    
    parserLines.append("__Parser__")
    parserLines.append('')
    parserLines.append("# Mapeamento para tokens simples")
    parserLines.append("# '(': LPAREN, etc.")
    parserLines.append("simpleT_map = {")
    parserLines.append("    " + ",\n    ".join(f"'{t}': '{s}'" for t, s in simpleToken.items()))
    parserLines.append("}")
    parserLines.append("")

    parserLines.append("def tokenizer(info):")
    parserLines.append("    lexer.input(info)")
    parserLines.append("    tokens = []")
    parserLines.append("    while True:")
    parserLines.append("        tok = lexer.token()")
    parserLines.append("        if not tok:")
    parserLines.append("            break")
    parserLines.append("        for t, s in simpleT_map.items():")
    parserLines.append("            if tok.type == t:")
    parserLines.append("                tokens.append((t, tok.value))")
    parserLines.append("    tokens.append((None, None))")
    parserLines.append("    return tokens")
    parserLines.append("")
    
    parserLines.append("# Variáveis globais para o parser")
    parserLines.append("token_stream = [] # Lista global para armazenar os tokens")
    parserLines.append("token_pos = 0 # Posição atual no token_stream")
    parserLines.append("actual_tipo = None # Tipo do token atual")
    parserLines.append("actual_lex = None # Lexema do token atual")
    parserLines.append('')

    parserLines.append('def advance():')
    parserLines.append('    global token_pos, actual_tipo, actual_lex')
    parserLines.append('    if token_pos < len(token_stream) - 1:')
    parserLines.append('        actual_tipo, actual_lex = token_stream[token_pos]')
    parserLines.append('        token_pos += 1')
    parserLines.append('    else:')
    parserLines.append('        actual_tipo, actual_lex = None, None')
    parserLines.append("")
    
    parserLines.append("def parser_gram(info):")
    parserLines.append("    global token_stream, token_pos, type_actual, lex_actual")
    parserLines.append("    token_stream = tokenizer(info)")
    parserLines.append("    token_pos = 0")
    parserLines.append("    lexer.lineno = 1")
    parserLines.append("    type_actual, lex_actual = token_stream[0]")
    parserLines.append(f"    result = p_{start}() ")
    parserLines.append("    if not result:")
    parserLines.append("        return None")
    parserLines.append("    return result")
    parserLines.append("")
    
    parserLines.append("def main():")
    parserLines.append("    if len(sys.argv) > 1:")
    parserLines.append("        with open(sys.argv[1], encoding='utf-8') as f:")
    parserLines.append('            print(f"Parsing file: {sys.argv[1]}")')
    parserLines.append('            source = f.read()')
    parserLines.append("    else:")
    parserLines.append('        print("No input file provided. Using default test string.")')
    parserLines.append('        source = "id + id * id"  # Exemplo de string de teste')
    parserLines.append('    try:')
    parserLines.append("        result = parser_gram(source)")
    parserLines.append("        result.pretty_print()  # Exemplo de uso do resultado")
    parserLines.append("    except Exception as e:")
    parserLines.append("        print(f'Erro durante o parsing: {e}')")
    parserLines.append("")
    parserLines.append("if __name__ == '__main__':")
    parserLines.append("    main()")

    return '\n'.join(parserLines)