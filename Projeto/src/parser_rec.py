import re
from classes_parser import *
from help_parsers import *

def _lookahead(sequencia, nt_pai, first_sets, follow_sets):
    """
    sequencia: lista de símbolos da produção (ex: ['ID', ':=', 'Expr'])
    nt_pai: o nome do NT da esquerda (ex: 'Atribuicao')
    first_sets: dicionário com os conjuntos FIRST de cada símbolo
    follow_sets: dicionário com os conjuntos FOLLOW de cada símbolo
    """
    res = set()
    anulavel = True

    # 1. Calcular o FIRST da sequência
    for simb in sequencia:
        nome_simbolo = simb.simbolo if hasattr(simb, 'simbolo') else str(simb)
    
        f_s = first_sets.get(nome_simbolo, {nome_simbolo})
    
        #print(f"DEBUG: Procurando {nome_simbolo} -> Encontrei: {f_s}")
        
        # f_s = first_sets.get(simb, {}) # Se não estiver no FIRST, é terminal
        # print(f_s)
        res.update(f_s - {'ε'})
        
        if 'ε' not in f_s:
            anulavel = False
            break
    
    # 2. Se a sequência toda for anulável (ou for vazia), adicionamos o FOLLOW do pai
    if anulavel:
        res.update(follow_sets.get(nt_pai, set()))
        
    return res
    
def gera_parser_recursivo(grammar, first_sets, follow_sets):
    start = grammar.get_inicial()
    terminals = grammar.get_Terminals()
    nTerminals = grammar.get_nonterminals()
    tokens = grammar.get_token()

    #print(tokens)
    terminals_formatada = [formatar_simbolo(s) for s in terminals]
    simpleToken = {}
    
    #Conseguimos simplificar os tokens fixos para um mapeamento simples
    #ex: '+' -> PLUS, '(' -> LPAREN, etc.
    #guardando no dicionário com LPAREN: '(', etc.
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
    
    parserLines.append("# Variáveis globais para o parser")
    parserLines.append("token_stream = [] # Lista global para armazenar os tokens")
    parserLines.append("token_pos = 0 # Posição atual no token_stream")
    parserLines.append("type_actual = None # Tipo do token atual")
    parserLines.append("lex_actual = None # Lexema do token atual")
    parserLines.append('')
    
    parserLines.append('def advance():')
    parserLines.append('    global token_stream, token_pos, type_actual, lex_actual')
    parserLines.append('    if token_pos < len(token_stream) - 1:')
    parserLines.append('        token_pos += 1')
    parserLines.append('    type_actual, lex_actual = token_stream[token_pos]')
    parserLines.append("")

    parserLines.append("def match(symbol):")
    parserLines.append("    if type_actual == symbol:")
    parserLines.append("        lex = lex_actual")
    parserLines.append("        advance()")
    parserLines.append("        return lex")
    parserLines.append("    raise SyntaxError(f'Erro: esperado {symbol}, mas encontrado {type_actual}')")
    parserLines.append("")
    
    for regra in grammar.regras:
        nt_name = regra.cabeca
        nt = SimpleToken(nt_name)
        parserLines.append(f"def p_{nt}():")
        rhs = ' | '.join([f"{prod.simbolo.simbolo} {' '.join(s.simbolo for s in prod.listaSimbolos)}" 
                          for prod in regra.producoes])
        parserLines.append(f"    '''{nt_name} : {rhs}'''")

        first_branch = True
        for prod in regra.producoes:
            sequencia = [prod.simbolo] + prod.listaSimbolos
            
            la = _lookahead(sequencia, nt_name, first_sets, follow_sets)
            la_nomes = []

            for t in la:
                nome_t = next((n for n, v in simpleToken.items() if v == t), t)
                la_nomes.append(nome_t)
            #print(la_nomes)
            condicao = ' or '.join([f"type_actual == '{t}'" for t in la_nomes])
            
            keyword = 'if' if first_branch else 'elif'
            parserLines.append(f"    {keyword} {condicao}:")
            parserLines.append(f"        children = []")

            for simb in sequencia:
                if simb.simbolo == 'ε':
                    parserLines.append(f"        children.append(Node('ε'))")
                elif simb.e_terminal:
                    desenho = simb.simbolo
                    nome_token = next((n for n, v in simpleToken.items() if v == desenho), desenho)
                    parserLines.append(f"        children.append(Node('{nome_token}', lexema=match('{nome_token}')))")
                else:
                    parserLines.append(f"        children.append(p_{SimpleToken(simb.simbolo)}())")
            
            parserLines.append(f"        return Node('{nt_name}', children=children)")
            first_branch = False


        else:
            parserLines.append(f"    raise SyntaxError(f'Erro em {nt_name}: inesperado {{type_actual}}')")
        parserLines.append("")

    parserLines.append("def parser_gram(info):")
    parserLines.append("    global token_stream, token_pos, type_actual, lex_actual")
    parserLines.append("    token_stream = tokenizer(info)")
    parserLines.append("    token_pos = 0")
    parserLines.append("    lexer.lineno = 1")
    parserLines.append("    type_actual, lex_actual = token_stream[0]")
    parserLines.append(f"    result = p_{SimpleToken(start)}() ")    
    parserLines.append("    if type_actual != 'final':")
    parserLines.append('        raise SyntaxError(f"Tokens extra após o fim: {type_actual}")')
    parserLines.append("    return result")
    parserLines.append("")
    
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
    parserLines.append("        sys.exit(1)")
    parserLines.append("")
    parserLines.append("if __name__ == '__main__':")
    parserLines.append("    main()")

    return '\n'.join(parserLines)