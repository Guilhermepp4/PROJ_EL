import ply.yacc as yacc
from src.my_lexer import lexer, tokens
from src.classes_parser import (Init, Regra, Producoes, 
                            Simbolo, token)

# --- PARSER (Monta a AST) ---
def p_init(p):
    '''init : program newlines lista_regras token_section'''
    p[0] = Init(axioma=p[1], regras=p[3], tokens=p[4])
    #p[0] = {'axioma': p[1], 'regras': p[3], 'tokens': p[4]}

def p_program(p):
    '''program : PROGRAM COLON NON_TERMINAL'''
    p[0] = p[3]

def p_lista_regras(p):
    '''lista_regras : regra lista_regras'''
    #p[0] = Lista_Regra(cabeca = p[1], producoes = p[2])
    p[0] = [p[1]] + p[2]

def p_lista_regras_empty(p):
    '''lista_regras : '''
    p[0] = []

def p_regra_newLine(p):
    '''regra : NON_TERMINAL ARROW lista_producoes newlines'''
    p[0] = Regra(cabeca=p[1], producoes=p[3])
    #p[0] = {'cabeca': p[1], 'producoes': p[3]}

def p_regra_sem_newLine(p):
    '''regra : NON_TERMINAL ARROW lista_producoes'''
    p[0] = Regra(cabeca=p[1], producoes=p[3])
    #p[0] = {'cabeca': p[1], 'producoes': p[3]}

def p_lista_producoes(p):
    '''lista_producoes : producao lista_producoes_rest'''
    #p[0] = Lista_Producoes(cabeca=p[1], producoes=p[2])
    p[0] = [p[1]] + p[2]

def p_lista_producoes_rest(p):
    '''lista_producoes_rest : PIPE producao lista_producoes_rest'''
    #p[0] = Lista_Producoes(cabeca=p[2], producoes=p[3])
    p[0] = [p[2]] + p[3]

def p_lista_producoes_rest_empty(p):
    '''lista_producoes_rest : '''
    p[0] = []

def p_producao(p):
    '''producao : simbolo lista_simbolos'''
    p[0] = Producoes(simbolo=p[1], listaSimbolos=p[2])
    #p[0] = [p[1]] + p[2]


def p_lista_simbolos(p):
    '''lista_simbolos : simbolo lista_simbolos'''
    #p[0] = Producoes(simbolo=p[1], listaSimbolos=p[2])
    p[0] = [p[1]] + p[2]

def p_lista_simbolos_empty(p):
    '''lista_simbolos : '''
    p[0] = []

def p_simbolo_epsilon(p):
    '''simbolo : EPSILON'''
    p[0] = Simbolo(simbolo='ε', e_terminal=True)
    #p[0] = ['ε']

def p_simbolo_term(p):
    '''simbolo : TERMINAL'''
    p[0] = Simbolo(simbolo=p[1], e_terminal=True)
    #p[0] = p[1]

def p_simbolo_non_term(p):
    '''simbolo : NON_TERMINAL'''
    p[0] = Simbolo(simbolo=p[1], e_terminal=False)
    #p[0] = p[1]

def p_token_section(p):
    """token_section : token_decl token_section"""
    #p[0] = tokenSection(Simbolo(simbolo=p[1]), producoes=p[2])
    p[0] = [p[1]] + p[2]

def p_token_section_empty(p):
    """token_section : """
    p[0] = []

def p_token_newline(p):
    """token_decl : TERMINAL EQUALS REGEX newlines"""
    s_name = Simbolo(simbolo=p[1], e_terminal=True)
    p[0] = token(simbolo=s_name, regex=p[3])
    #p[0] = (p[1], p[3])

def p_token_sem_newline(p):
    """token_decl : TERMINAL EQUALS REGEX"""
    s_name = Simbolo(simbolo=p[1], e_terminal=True)
    p[0] = token(simbolo=s_name, regex=p[3])
    #p[0] = (p[1], p[3])

def p_newlines(p):
    """newlines : NEWLINE
               | NEWLINE newlines"""
    pass

def p_error(p):
    if p:
        print(f"Erro sintático! Não esperava o token {p.value} (Tipo: {p.type}) na linha {p.lineno}")
    else:
        print("Erro sintático no fim do ficheiro!")

parser = yacc.yacc(start='init')

def parser_gram(info):
    lexer.lineno = 1
    result = parser.parse(info)

    if not result:
        return None

    return result