from first_follow import checkLL1
from help_parsers import *

def gera_parser_TopDown(grammar, first, follow):
    start = grammar.get_inicial()
    terminals = grammar.get_Terminals()
    nTerminals = grammar.get_nonterminals()
    tokens = grammar.get_token()

    #colocamos os literals entre aspas para facilitar a identificação de símbolos fixos
    terminals_formatada = [formatar_simbolo(s) for s in terminals]
    simpleToken = {}
    
    #Conseguimos simplificar os tokens fixos para um mapeamento simples
    #ex: '+' -> PLUS, '(' -> LPAREN, etc.
    #guardando no dicionário com LPAREN: '(', etc.
    for t in terminals_formatada:
        #Verifica se o terminal está entre aspas
        if simpleT(t):
            #gera um nome de token simplificado
            token = tokT(t[1:-1])
            simpleToken[token] = t[1:-1]
    
    table, _= checkLL1(grammar, first, follow)
    parserLines = []
    parserLines.append("#Parser Top-Down dirigido por tabela")
    parserLines.append("")
    parserLines.append("import ply.lex as lex")
    parserLines.append("import sys")
    parserLines.append("import re")
    parserLines.append("import ply.yacc as yacc")
    parserLines.append("")
    parserLines.append("# Definição da classe Node para representar os nós da árvore de análise sintática")
    parserLines.append("")
    parserLines.append("class Node:")
    parserLines.append("    def __init__(self, name, children=None, lexema=None):")
    parserLines.append("        self.name = name")
    parserLines.append("        self.children = children if children is not None else []")
    parserLines.append("        self.lexema = lexema")
    parserLines.append("")
    parserLines.append("    def pretty_print(self, prefix='', is_last=True):")
    parserLines.append("        conector = '└── ' if is_last else '├── '")
    parserLines.append("        label = self.name")
    parserLines.append("        if self.lexema:")
    parserLines.append("            label += f': {self.lexema}'")
    parserLines.append("        print(prefix + conector + label)")
    parserLines.append("        new_prefix = prefix + ('    ' if is_last else '│   ')")
    parserLines.append("")
    parserLines.append("        for i, child in enumerate(self.children):")
    parserLines.append("            isLast = (i == len(self.children) - 1)")
    parserLines.append("            child.pretty_print(new_prefix, isLast)")
    parserLines.append("")
    parserLines.append("#__Lexer__")
    parserLines.append('tokens = (')
    for t in tokens:
        parserLines.append(f"    '{t}',")
    for t in simpleToken:
        parserLines.append(f"    '{t}',")
    parserLines.append(')')
    parserLines.append("")
    
    #print(f"DEBUG simpleToken: {simpleToken}")
    #print(f"DEBUG tokens: {tokens}")
    parserLines.append("# Símbolos fixos (Variáveis têm precedência por ordem de tamanho de regex)")
    for t, s in sorted(simpleToken.items(), key=lambda x: -len(x[1])):
        parserLines.append(f"def t_{t}(t):")
        # Usamos re.escape apenas aqui, porque são símbolos literais
        parserLines.append(f"    r'{re.escape(s)}'")
        parserLines.append(f"    return t")
        parserLines.append("")
    
    for t, s in tokens.items():
        parserLines.append(f"def t_{t}(t):")
        # AQUI NÃO USAMOS re.escape(s), usamos o s direto (a regex)
        parserLines.append(f"    r'{s}'")
        # Pequeno extra geral: se for um inteiro, converte logo o valor
        if t.upper() == 'INT' or t.upper() == 'NUMBER' or t.upper() == 'FLOAT':
            parserLines.append(f"    t.value = int(t.value)")
        parserLines.append(f"    return t")
        parserLines.append("")
    parserLines.append('t_ignore = " \\t\\n"')
    parserLines.append("def t_error(t):")
    parserLines.append("    print(f'Erro na linha {t.lineno}: Caractere ilegal \"{t.value[0]}\"')")
    parserLines.append("    lexer.lineno += 1")
    parserLines.append("    t.lexer.skip(1)")
    parserLines.append("")
    parserLines.append("lexer = lex.lex()")
    parserLines.append("")
    parserLines.append("#__Parser__")
    parserLines.append('')
    parserLines.append("'''")
    parserLines.append("Mapeamento para tokens simples")
    parserLines.append("'(': LPAREN, etc.")
    parserLines.append('')
    parserLines.append("simpleT_map = {")
    parserLines.append("    " + ",\n    ".join(f"'{t}': '{s}'" for t, s in simpleToken.items()))
    parserLines.append("}")
    parserLines.append("'''")
    parserLines.append("")

    parserLines.append("table_formatada = {")
    for nt, sequencia in table.items():
        parserLines.append(f"    '{nt}': {{")
        for t, producao in sequencia.items():
            t = formatar_simbolo(t)
            if simpleT(t):
                t = tokT(t[1:-1])

            if 'ε' == producao:
                rhs = []
            else:
                rhs = [s for s in producao.split()]
            
            virgula = "," if t != list(sequencia.keys())[-1] else ""
            parserLines.append(f"        '{t}': {rhs}{virgula}")
        
        virgula = ",\n" if nt != list(table.keys())[-1] else ""
        parserLines.append(f"    }}{virgula}")
    parserLines.append("}")
    parserLines.append("")


    parserLines.append("def tokenizer(info):")
    parserLines.append("    lexer.input(info)")
    parserLines.append("    token_stream = []")
    parserLines.append("    while True:")
    parserLines.append("        tok = lexer.token()")
    parserLines.append("        if not tok:")
    parserLines.append("            break")
    parserLines.append("        token_stream.append((tok.type, tok.value))")    
    parserLines.append("    token_stream.append(('final', 'final'))")
    parserLines.append("    return token_stream")
    parserLines.append("")
    
    parserLines.append('def advance():')
    parserLines.append('    global token_stream, token_pos, type_actual, lex_actual')
    parserLines.append('    if token_pos < len(token_stream) - 1:')
    parserLines.append('        token_pos += 1')
    parserLines.append('    type_actual, lex_actual = token_stream[token_pos]')
    parserLines.append("")

    parserLines.append(f"NONTERMINALS = {list(nTerminals)}")
    parserLines.append(f"START_SYMBOL = '{start}'")
    parserLines.append("")

    parserLines.append("# Variáveis globais para o parser")
    parserLines.append("token_stream = [] # Lista global para armazenar os tokens")
    parserLines.append("token_pos = 0 # Posição atual no token_stream")
    parserLines.append("type_actual = None # Tipo do token atual")
    parserLines.append("lex_actual = None # Lexema do token atual")
    parserLines.append("")
    parserLines.append("def parser_gram(info):")
    parserLines.append("    global token_stream, token_pos, type_actual, lex_actual")
    parserLines.append("    token_stream = tokenizer(info)")
    parserLines.append("    token_pos = 0")
    parserLines.append("    type_actual, lex_actual = token_stream[0]")
    parserLines.append("    ")
    parserLines.append("    raiz = Node(START_SYMBOL)")
    parserLines.append("    stack = [(START_SYMBOL, raiz)]")
    parserLines.append("")
    parserLines.append("    while stack:")
    parserLines.append("        top_sym, no_pai = stack.pop()")
    parserLines.append("")
    parserLines.append("        if top_sym in NONTERMINALS:")
    parserLines.append("            if type_actual not in table_formatada[top_sym]:")
    parserLines.append("                raise SyntaxError(f'Erro: {top_sym} não tem regra para {type_actual}')")
    parserLines.append("            ")
    parserLines.append("            producao = table_formatada[top_sym][type_actual]")
    parserLines.append("            ")
    parserLines.append("            filhos_nodes = [Node(s) for s in producao]")
    parserLines.append("            no_pai.children = filhos_nodes")
    parserLines.append("            ")
    parserLines.append("            for i in range(len(producao)-1, -1, -1):")
    parserLines.append("                if producao[i] != 'ε':")
    parserLines.append("                    stack.append((producao[i], filhos_nodes[i]))")
    parserLines.append("")
    parserLines.append("        else: # É Terminal")
    parserLines.append("            if top_sym == type_actual or top_sym == lex_actual:")
    parserLines.append("                no_pai.lexema = lex_actual")
    parserLines.append("                advance()")
    parserLines.append("            elif top_sym == 'ε':")
    parserLines.append("                continue")
    parserLines.append("            else:")
    parserLines.append("                raise SyntaxError(f'Esperado {top_sym}, mas obtido {lex_actual}')")
    parserLines.append("")
    parserLines.append("    return raiz")
    parserLines.append("")

    parserLines.append("    ")

    parserLines.append("def main():")
    parserLines.append("    if len(sys.argv) > 1:")
    parserLines.append("        with open(sys.argv[1], encoding='utf-8') as f:")
    parserLines.append('            print(f"Parsing file: {sys.argv[1]}")')
    parserLines.append('            source = f.read()')
    parserLines.append("    else:")
    parserLines.append('        print("No input file provided. Using default test string.")')
    parserLines.append('    try:')
    parserLines.append("        result = parser_gram(source)")
    parserLines.append("        result.pretty_print()")
    parserLines.append("    except Exception as e:")
    parserLines.append("        print(f'Erro durante o parsing: {e}')")
    parserLines.append("")
    parserLines.append("if __name__ == '__main__':")
    parserLines.append("    main()")
    return '\n'.join(parserLines)