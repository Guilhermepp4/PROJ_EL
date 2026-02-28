class Symbol:
    def __init__(self, name, is_terminal=False):
        self.name = name
        self.is_terminal = is_terminal

    def __repr__(self):
        return self.name


class Production:
    def __init__(self, left, right):
        """
        left  -> NonTerminal (Symbol)
        right -> list of Symbols
        """
        self.left = left
        self.right = right

    def __repr__(self):
        right_str = " ".join(sym.name for sym in self.right)
        return f"{self.left.name} -> {right_str}"


class Grammar:
    def __init__(self):
        self.terminals = set()
        self.nonterminals = set()
        self.productions = []
        self.start_symbol = None

        self.first = {}    
        self.follow = {}
        self.table = {}

    def add_terminal(self, name):
        sym = Symbol(name, True)
        self.terminals.add(sym)
        return sym

    def add_nonterminal(self, name):
        sym = Symbol(name, False)
        self.nonterminals.add(sym)
        return sym

    def add_production(self, left, right):
        prod = Production(left, right)
        self.productions.append(prod)
        return prod

    def set_start(self, symbol):
        self.start_symbol = symbol
