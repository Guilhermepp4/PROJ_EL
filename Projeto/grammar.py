grammar = r"""

start: rule+

rule : NT ARROW rhs

rhs : production ("|" production)*

production : symbol (TOKEN? symbol)*

symbol : NT | T | EPS 

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