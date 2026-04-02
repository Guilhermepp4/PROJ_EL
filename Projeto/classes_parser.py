class Regra:
    """Representa uma regra completa: Cabeca -> Producoes"""
    def __init__(self, cabeca, producoes):
        self.cabeca = cabeca      # String (ex: 'Lista')
        self.producoes = producoes # Lista de objetos Producao

    def __repr__(self):
        return f"{self.cabeca} -> {' | '.join(map(str, self.producoes))}"

    def print_tree(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}Regra: {self.cabeca}")
        
        # O prefixo para os filhos depende se esta regra é a última da lista
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, prod in enumerate(self.producoes):
            last_prod = (i == len(self.producoes) - 1)
            prod.print_tree(new_prefix, last_prod)

class Producao:
    """Representa uma alternativa de uma regra (sequência de símbolos)"""
    def __init__(self, simbolos):
        self.simbolos = simbolos # Lista de objetos Simbolo ou lista vazia para epsilon

    def __repr__(self):
        return " ".join(map(str, self.simbolos)) if self.simbolos else "ε"

    def print_tree(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}Produção")
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        if not self.simbolos:
            print(f"{new_prefix}└── ε (Vazio)")
        else:
            for i, sym in enumerate(self.simbolos):
                last_sym = (i == len(self.simbolos) - 1)
                sym.print_tree(new_prefix, last_sym)

class Simbolo:
    """Representa um símbolo individual (Terminal, Não-Terminal, 'quoted' ou epsilon)"""
    def __init__(self, valor, child):
        self.valor = valor
        self.e_terminal = e_terminal

    def __repr__(self):
        return self.valor

    def print_tree(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        separator = "  " if is_last else "| "
        print(f"{prefix}{connector}{separator}: {self.valor}")