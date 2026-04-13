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

def print_lookahead_simples(gramatica, first, follow):
    print(f"{'NT':<10} {'Produção':<30} {'Lookahead Set'}")
    print("-" * 60)
    for regra in gramatica.regras:
        A = regra.cabeca
        for prod in regra.producoes:
            sequencia = [prod.simbolo] + prod.listaSimbolos
            
            f_seq = rool_seq(first, sequencia, A)
            
            la = f_seq - {'ε'}
            if 'ε' in f_seq:
                la = la.union(follow[A])
            
            prod_str = f"{A} -> {prod.simbolo.simbolo} " + " ".join([s.simbolo for s in prod.listaSimbolos])
            print(f"{A:<10} {prod_str:<30} {{ {', '.join(sorted(la))} }}")

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

def nonTerminalRole(gramatica, p, terminal_conflito, first, novas_opcoes_sufixo):
    regra_interna = next((r for r in gramatica.regras if r.cabeca == p.simbolo.simbolo), None)
    if regra_interna:
        for p_interna in regra_interna.producoes:
            seq = [p_interna.simbolo] + p_interna.listaSimbolos
            if terminal_conflito in rool_seq(first, seq, p.simbolo.simbolo):
                sufixo = " ".join([s.simbolo for s in p_interna.listaSimbolos])
                novas_opcoes_sufixo.append(sufixo if sufixo else "ε")

def terminalRole(p, terminal_conflito, novas_opcoes_sufixo):
    if p.simbolo.simbolo == terminal_conflito:
        sufixo = " ".join([s.simbolo for s in p.listaSimbolos])
        novas_opcoes_sufixo.append(sufixo if sufixo else "ε")


def rFatorizacao(first, nt, producoes, gramatica):
    grupos = {}
    for p in producoes:
        sequencia = [p.simbolo] + p.listaSimbolos
        f_seq = rool_seq(first, sequencia, nt)
        for terminal in f_seq:
            if terminal == 'ε': continue
            if terminal not in grupos: grupos[terminal] = []
            grupos[terminal].append(p)

    todas_as_sugestoes = []
    contador = 1 # Para criar S_Prime1, S_Prime2, ...

    for terminal_conflito, conflito in grupos.items():
        if len(conflito) > 1:
            nt_prime = f"{nt}_Prime{contador}"
            regra_base = f"{nt} -> {terminal_conflito} {nt_prime}"
            
            novas_opcoes_sufixo = []
            for p in conflito:
                # CASO 1: É um Não-Terminal (ex: S -> A) - Precisamos expandir
                if not p.simbolo.e_terminal:
                    nonTerminalRole(gramatica, p, terminal_conflito, first, novas_opcoes_sufixo)
                
                # CASO 2: É um Terminal direto (ex: S -> '0' S '0')
                else:
                    # Se o terminal da produção for igual ao terminal que causou o conflito
                    terminalRole(p, terminal_conflito, novas_opcoes_sufixo)
                    
            regra_derivada = f"{nt_prime} -> {' | '.join(dict.fromkeys(novas_opcoes_sufixo))}"
            todas_as_sugestoes.extend([regra_base, regra_derivada])
            contador += 1

    return todas_as_sugestoes if todas_as_sugestoes else None

def rRecursao(nt_name, producoes):
    recursivas = []
    non_recursivas = []
    for prod in producoes:
        if prod.simbolo.simbolo == nt_name:
            recursivas.append(prod.listaSimbolos)
        else:
            non_recursivas.append(prod.listaSimbolos)
        
    if not recursivas:
        return "None"
    
    nt_prime = f"{nt_name}'"
    
    # Nova Regra 1: A -> beta A'
    nova_regra_A = f"{nt_name} -> " + " | ".join([" ".join([s.simbolo for s in seq]) + f" {nt_prime}" for seq in non_recursivas])
    
    # Nova Regra 2: A' -> alpha A' | ε
    nova_regra_A_prime = f"{nt_prime} -> " + " | ".join([" ".join([s.simbolo for s in seq]) + f" {nt_prime}" for seq in recursivas]) + " | ε"
    
    return [nova_regra_A, nova_regra_A_prime]

def rFirstFollow(first, follow, nt, producoes):
    # Encontrar qual a produção que é anulável (tem ε no FIRST)
    prod_anulavel = None
    outras_prods = []
    
    for p in producoes:
        sequencia = [p.simbolo] + p.listaSimbolos
        if 'ε' in rool_seq(first, sequencia, nt):
            prod_anulavel = p
        else:
            outras_prods.append(p)
            
    if not prod_anulavel:
        return None

    # O conflito acontece com símbolos que estão no FOLLOW de 'nt'
    # e também no FIRST das outras produções
    terminais_conflito = set()
    for p in outras_prods:
        f_seq = rool_seq(first, [p.simbolo] + p.listaSimbolos, nt)
        conflito = f_seq.intersection(follow[nt])
        if conflito:
            terminais_conflito.update(conflito)

    if terminais_conflito:
        term_str = ", ".join(list(terminais_conflito))
        
        # Sugestão qualitativa: reestruturar para evitar a ambiguidade
        res = [
            f"❌ Conflito FIRST/FOLLOW no símbolo '{term_str}'",
            f"💡 Dica: A regra '{nt}' pode ser vazia, mas o que vem a seguir também começa com '{term_str}'.",
            f"👉 Sugestão: Tenta explicitamente incluir o caso de '{term_str}' na regra '{nt}' ou subir esse símbolo na hierarquia."
        ]
        return res
    
    return None

def sugerir_correcoes(first, follow, conflitos_detetados, gramatica):
    sugestoes = {}

    for c in conflitos_detetados:
        partes = c.split(" | ")
        tipo = partes[0]
        nt_prob = partes[1]
        chave = (tipo, nt_prob)

        regra_obj = next((r for r in gramatica.regras if r.cabeca == nt_prob), None)
        if not regra_obj: continue

        corrigida = None
        titulo = ""

        regra_prob = next((r for r in gramatica.regras if r.cabeca == nt_prob) ,None)
        if tipo == "FIRST/FIRST":
            corrigida = rFatorizacao(first, nt_prob, regra_prob.producoes, gramatica)
            titulo = f"Fatorização necessária em {nt_prob}"
        
        elif tipo == "FIRST/FOLLOW":
            corrigida = rFirstFollow(first, follow, nt_prob, regra_prob.producoes)
            titulo = f"Ambiguidade FIRST/FOLLOW em {nt_prob}"
        
        elif tipo == "REQ/ESQ":
            corrigida = rRecursao(nt_prob, regra_prob.producoes)
            titulo = f"Recursão à Esquerda em {nt_prob}"

        if corrigida:
            sugestoes[chave] = {
                    'tipo_real': tipo,
                    'titulo': titulo,
                    'proposta': corrigida
            }
            
    return list(sugestoes.values())