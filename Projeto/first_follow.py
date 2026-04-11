from classes_parser import Init, Simbolo

def compute_first(gramatica):
    first = {nt : set() for nt in gramatica.get_nonterminals()}
    result = set()
    changed = True
    while changed:
        changed = False
        for regra in gramatica.regras:
            A = regra.cabeca
            for prod in regra.producoes:
                
                sequencia = [prod.simbolo] + prod.listaSimbolos
                prev_len = len(first[A])
                
                let_continue = True
                let_continue = processar_simbolo(first, sequencia, A, result)

                if not let_continue:
                    break
                if let_continue:
                    first[A].add('ε')
                
                if len(first[A]) > prev_len:
                    changed = True
    return first

def processar_simbolo(first_dict, sequencia, pai, result):
    for s in sequencia:
        if s.e_terminal:
            if s.simbolo == 'ε':
                result.add('ε')
                return True
            else:
                first_dict[pai].add(s.simbolo)
                result.add(s.simbolo)
                return False
        else:
            son_first = first_dict.get(s.simbolo, set())
            first_dict[pai].update(son_first - {'ε'})
            result |= son_first - {'ε'}
            if 'ε' not in son_first:
                return False
    
    result.add('ε')
    return True

def rool_seq(first, aux_seq, name_s):
    result = set()
    processar_simbolo(first, aux_seq, name_s, result)
    return result

def simple_sequencia(sequencia, A, first, follow):
    changed = False
    for i, seq in enumerate(sequencia):
        if not seq.e_terminal:
            prev_len = len(follow[seq.simbolo])
            aux_seq = sequencia[i+1:]

            aux_first = rool_seq(first, aux_seq, seq.simbolo)
            follow[seq.simbolo] |= (aux_first - {'ε'})

            if 'ε' in aux_first:
                follow[seq.simbolo] |= follow[A]
            
            if prev_len != len(follow[seq.simbolo]):
                changed = True
    
    return changed


def compute_follow(first, gramatica):
    follow = {nt : set() for nt in gramatica.get_nonterminals()}

    changed = True
    while changed:
        changed = False
        for regra in gramatica.regras:
            A = regra.cabeca
            for prod in regra.producoes:
                sequencia = [prod.simbolo] + prod.listaSimbolos
                if simple_sequencia(sequencia, A, first, follow):
                    changed = True
    return follow

def print_sets(first, follow):
    print("\n" + "="*60)
    print(f"{'NT':<15} | {'FIRST':<20} | {'FOLLOW'}")
    print("-" * 60)
    
    for nt in sorted(first.keys()):
        str_first = "{" + ", ".join(sorted(list(first[nt]))) + "}"
        str_follow = "{" + ", ".join(sorted(list(follow.get(nt, set())))) + "}"
        
        print(f"{nt:<15} | {str_first:<20} | {str_follow}")
    
    print("="*60 + "\n")

def lookahead(gramatica, first, follow):
    """
    Constrói a Tabela de Análise LL(1).
    A tabela indica: "Se estou no Não-Terminal X e o Lookahead é Y, uso a Produção Z".
    """
    tabela_ll1 = {nt: {} for nt in gramatica.get_nonterminals()}
    conflitos = []

    for regra in gramatica.regras:
        A = regra.cabeca
        for prod in regra.producoes:
            sequencia = [prod.simbolo] + prod.listaSimbolos
            prod_str = str_producao(sequencia)
            
            # FIRST da sequência
            first_da_sequencia = rool_seq(first, sequencia, A)
            
            # 1. Verificar Recursão à Esquerda (REQ/ESQ)
            primeiro_da_prod = sequencia[0]
            if not primeiro_da_prod.e_terminal and primeiro_da_prod.simbolo == A:
                conflitos.append(f"REQ/ESQ | {A} | {prod_str}")

            # 2. Preencher tabela com FIRST (FIRST/FIRST)
            for terminal in first_da_sequencia:
                if terminal != 'ε':
                    if terminal in tabela_ll1[A]:
                        # Se já lá estava uma produção, temos o conflito detalhado!
                        prod_existente = tabela_ll1[A][terminal]
                        if prod_existente != prod_str: # Evita duplicados da mesma regra
                            conflitos.append(f"FIRST/FIRST | {A} | {terminal} | {prod_existente} VS {prod_str}")
                    else:
                        tabela_ll1[A][terminal] = prod_str

            # 3. Preencher tabela com FOLLOW se for anulável (FIRST/FOLLOW)
            if 'ε' in first_da_sequencia:
                for terminal_f in follow[A]:
                    if terminal_f in tabela_ll1[A]:
                        prod_existente = tabela_ll1[A][terminal_f]
                        conflitos.append(f"FIRST/FOLLOW | {A} | {terminal_f} | {prod_existente} VS {prod_str}")
                    else:
                        tabela_ll1[A][terminal_f] = prod_str

    return tabela_ll1, conflitos

def str_producao(sequencia):
    """Auxiliar para transformar a lista de objetos Simbolo em texto"""
    return " ".join([s.simbolo for s in sequencia])

def print_tabela(tabela):
    print("\n--- Tabela de Análise LL(1)---")
    for nt, caminhos in tabela.items():
        for t, prod in caminhos.items():
            print(f"M[{nt}, {t}] = {prod}")

def sugerir_correcoes(conflitos_detetados):
    sugestoes = set()
    for c in conflitos_detetados:
        partes = c.split(" | ")
        tipo = partes[0]

        if tipo == "FIRST/FIRST":
            nt , simbolo, regras = partes[1], partes[2], partes[3]
            sugestoes.add(f"💡 No Não-Terminal '{nt}', o símbolo '{simbolo}' inicia duas regras: [{regras}].\n"+
                             "👉 Sugestão: Tenta aplicar Fatorização a Esquerda\n")
        elif tipo == "FIRST/FOLLOW":
            nt, simbolo, regras = partes[1], partes[2], partes[3]
            sugestoes.add(f"💡 No Não-Terminal '{nt}', o símbolo '{simbolo}' pode vir do FOLLOW ou de uma regra alternativa: [{regras}].\n"
                          f"👉 Sugestão: Verifica se a gramática é ambígua ou se podes reestruturar o símbolo '{nt}'.")
        elif tipo == "REQ/ESQ":
            nt, regra = partes[1], partes[2]
            sugestoes.add(f"💡 O Não-Terminal '{nt}' chama-se a si próprio na regra '{regra}'.\n"+
                          f"👉 Sugestão: Substitui a recursão à esquerda por recursão à direita.\n")
    return sugestoes






























def _first_of_seq(symbols, first_map, nts, result):
    if not symbols:
        result.add('ε')
        return True
    for sym in symbols:
        if sym == 'ε':
            result.add('ε')
            return True
        elif not sym.get_is_terminal() and sym.get_value() in nts:
            sym_first = first_map.get(sym.get_value(), set())
            result |= (sym_first - {'ε'})
            if 'ε' not in sym_first:
                return False
        else:
            result.add(sym.get_value())
            return False
    result.add('ε')
    return True


def first_of_seq(symbols, first_map, nts):
    result = set()
    _first_of_seq(symbols, first_map, nts, result)
    return result

def build_parse_table(grammar, first, follow):
    nts = grammar.get_nonterminals()
    table = {}
    for rule in grammar.regras:
        A = rule.cabeca
        for seq in rule.producoes:
            seq_first = first_of_seq(seq.simbolo, first, nts)
            for terminal in seq_first - {'ε'}:
                cell = table.setdefault((A, terminal), [])
                if not any(s is seq for s in cell):
                    cell.append(seq)
            if 'ε' in seq_first:
                for terminal in follow[A]:
                    cell = table.setdefault((A, terminal), [])
                    if not any(s is seq for s in cell):
                        cell.append(seq)
    return table

def print_parse_table(table, grammar):
    nts   = sorted(grammar.get_nonterminals())
    terms = sorted(grammar.get_terminals() | {'$'})
    col_w = max(12, max(len(t) for t in terms) + 2)
    row_w = max(len(nt) for nt in nts) + 2
    header = f"{'':>{row_w}}" + ''.join(f"{t:^{col_w}}" for t in terms)
    print(header)
    print("─" * len(header))
    for nt in nts:
        row = f"{nt:>{row_w}}"
        for t in terms:
            cell = table.get((nt, t), [])
            if not cell:
                row += f"{'':^{col_w}}"
            elif len(cell) == 1:
                s = f"{nt}→{repr(cell[0])}"
                if len(s) > col_w - 1:
                    s = s[:col_w - 4] + '...'
                row += f"{s:^{col_w}}"
            else:
                row += f"{'[CONFLITO]':^{col_w}}"
        print(row)