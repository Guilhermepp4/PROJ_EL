class Node:
    def print_tree(self, prefix="", last=True):
        pass

class Init(Node):
    def __init__(self, axioma, regras, tokens):
        self.axioma = axioma
        self.regras = regras
        self.tokens = tokens
    
    def print_tree(self, prefix="", last=True):
        print(prefix + "└── Init")
        new_prefix = prefix + "    "

        if self.regras == []:
            print(new_prefix + f"└── {self.axioma}")
        else:
            print(new_prefix + f"├── {self.axioma}")
        
        # Imprimir as regras
        if isinstance(self.regras, list):
            for i, r in enumerate(self.regras): 
                e_ultimo = (i == len(self.regras) - 1)
                r.print_tree(new_prefix, e_ultimo)
            
        # Imprimir os tokens
        if isinstance(self.tokens, list):
            for t in self.tokens: t.print_tree(new_prefix, True)
        elif self.tokens:
            self.tokens.print_tree(new_prefix, True)
        

class Regra(Node):
    def __init__(self, cabeca, producoes):
        self.cabeca = cabeca
        self.producoes = producoes
    
    def print_tree(self, prefix="", is_last=True):
        conector = "└── " if is_last else "├── "
        print(prefix + conector + f"{self.cabeca}")
        
        # Verifica se producoes não é None e se é uma lista
        if self.producoes is not None:
            if isinstance(self.producoes, list):
                for i, p in enumerate(self.producoes):
                    # Só chama print_tree se p não for None
                    if p is not None:
                        last = (i == len(self.producoes) - 1)
                        p.print_tree(prefix + "    ", last)
            else:
                self.producoes.print_tree(prefix + "    ", True)


class Producoes(Node):
    def __init__(self, simbolo, listaSimbolos):
        self.simbolo = simbolo
        self.listaSimbolos = listaSimbolos
    
    def print_tree(self, prefix="", is_last=True):
        # 1. Imprime o primeiro símbolo
        # Se houver mais símbolos na lista, este não é o último (is_last=False)
        tem_mais = len(self.listaSimbolos) > 0
        self.simbolo.print_tree(prefix, not tem_mais)
        
        # 2. Imprime o resto dos símbolos da lista
        for i, s in enumerate(self.listaSimbolos):
            ultimo_da_lista = (i == len(self.listaSimbolos) - 1)
            if isinstance(s, Node):
                s.print_tree(prefix, ultimo_da_lista)
            else:
                # Caso o símbolo seja apenas uma string (segurança)
                conector = "└── " if ultimo_da_lista else "├── "
                print(prefix + conector + str(s))

class Simbolo(Node):
    def __init__(self, simbolo, e_terminal):
        self.simbolo = simbolo
        self.e_terminal = e_terminal
    
    def print_tree(self, prefix="", is_last=True):
        conector = "└── " if is_last else "├── "
        tipo = "T" if self.e_terminal else "NT"
        print(prefix + conector + f"{tipo}: {self.simbolo}")

class tokenSection:
    def __init__(self, tokenDecl, producoes):
        self.tokenDecl = tokenDecl
        self.producoes = producoes

class token(Node):
    def __init__(self, simbolo, regex):
        self.simbolo = simbolo
        self.regex = regex
    
    def print_tree(self, prefix="", is_last=True):
        conector = "└── " if is_last else "├── "
        val = self.simbolo.simbolo if hasattr(self.simbolo, 'simbolo') else self.simbolo
        print(prefix + conector + f"Token: {val} = {self.regex}")