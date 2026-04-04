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