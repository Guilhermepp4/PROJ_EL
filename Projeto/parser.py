from grammar import grammar
from lark import Token, Tree, Lark

parser = Lark(grammar, start="start")

# text = """Lista -> '[' Elems ']'
# Elems -> Elem Elems | ε
# Elem  -> int
# """
text = """Init -> Lista

Lista -> '[' ']' | '[' Elems ']'

Elems -> Elems "," Elem | Elem

Elem -> int
"""

tree = parser.parse(text)

# print("Parsed tree(AST): \n")
# print(tree.pretty())

grammar_dict = {}

for rule in tree.children:
    nt = str(rule.children[0])
    rhs = rule.children[2]
    productions = []
    for prod in rhs.children:
        symbols = []
        for s in prod.children:
            if isinstance(s, Token):    
                if s.type != "TOKEN":
                    symbols.append(str(s))
            elif isinstance(s, Tree):
                symbols.append(str(s.children[0]))
        productions.append(symbols)
    grammar_dict[nt] = productions
# print("\nGrammar Dictionary: \n")
# for x in grammar_dict.keys():
#     print(f"{x} -> {grammar_dict[x]}")