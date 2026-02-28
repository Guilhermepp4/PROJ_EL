from grammar import Grammar

g = Grammar()

# Terminais
id_ = g.add_terminal("id")
number = g.add_terminal("number")
plus = g.add_terminal("+")
assign = g.add_terminal(":=")
semi = g.add_terminal(";")
epsilon = g.add_terminal("ε")

# Não-terminais
Program = g.add_nonterminal("Program")
StmtList = g.add_nonterminal("StmtList")
StmtListP = g.add_nonterminal("StmtList'")
Stmt = g.add_nonterminal("Stmt")
Expr = g.add_nonterminal("Expr")
ExprP = g.add_nonterminal("Expr'")
Term = g.add_nonterminal("Term")

g.set_start(Program)

# Produções
g.add_production(Program, [StmtList])
g.add_production(StmtList, [Stmt, StmtListP])
g.add_production(StmtListP, [semi, Stmt, StmtListP])
g.add_production(StmtListP, [epsilon])
g.add_production(Stmt, [id_, assign, Expr])
g.add_production(Expr, [Term, ExprP])
g.add_production(ExprP, [plus, Term, ExprP])
g.add_production(ExprP, [epsilon])
g.add_production(Term, [id_])
g.add_production(Term, [number])