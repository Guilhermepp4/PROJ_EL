from grammar import grammar
from lark import Lark

parser = Lark(grammar, start="start")

text = """Program → StmtList
StmtList → Stmt StmtList'
StmtList' → ; Stmt StmtList' | ε
Stmt → id := Expr
Expr → Term Expr'
Expr' → + Term Expr' | ε
Term → id | number
"""

tree = parser.parse(text)

print(tree.pretty())