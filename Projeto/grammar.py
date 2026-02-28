grammar = r"""

start: rule+

rule : NT ARROW rhs

rhs : production ("|" production)*

production : symbol (TOKEN? symbol)*

symbol : NT | T | EPS | symbol | symbol

ARROW: "→"|"->" 
EPS: "ε"
LBRACKET: "["
RBRACKET: "]"
LPAREN: "("
RPAREN: ")"
TOKEN: /[\,\;]/

NT: /[A-Z][A-Za-z0-9_']*/
T: /[a-z0-9+*\/:=;\[\]\(\)\'\"]+/

%ignore /[ \t\f\n]+/
"""



# token = """
# NT     = identificador de não-terminal
# T      = identificador de terminal
# ARROW  = ->
# EPS    = ε
# """


# gramatica_com_conflitos1 = """
# lista -> '['']'
#         | '[' Elems ']'

# Elems -> Elems "," Elem
#          | Elem

# Elem -> int
# """

# gramatica_com_conflitos2 = """
#     S -> '0' S '0'
#     | '1' S '1'
#     | '0'
#     | '1'
#     | 'e' "epsilon"
# """


# gramatica_trabalhar = """
# Lista -> '[' Elems ']'

# Elems -> e
#     |   Elem ',' Elems

# Elem -> int
# """


# Guia_Projeto = """
# Linguagem -> parser(feito por nós) -> ASA(AST)
# """