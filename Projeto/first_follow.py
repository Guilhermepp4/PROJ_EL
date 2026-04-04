from classes_parser import Init, Simbolo

def compute_first(gramatica):
    first = {nt : set() for nt in gramatica.get_nonterminals()}
    changed = True
    while changed:
        changed = False
        for regra in gramatica.regras:
            A = regra.cabeca
            for prod in regra.producoes:
                sequencia = [prod.simbolo] + prod.listaSimbolos
                prev_len = len(first[A])
                
                # --- AQUI ESTÁ A LÓGICA ---
                pode_continuar = True
                for s in sequencia:
                    # A função altera o set 'first[A]' e diz-nos se paramos
                    pode_continuar = processar_simbolo(first, s, A)
                    if not pode_continuar:
                        break
                
                if pode_continuar:
                    first[A].add('ε')
                # --------------------------

                if len(first[A]) > prev_len:
                    changed = True
    return first

def processar_simbolo(first_dict, s, pai):
    if s.e_terminal:
        if s.simbolo == 'ε':
            return True # É vazio, deixa passar para o próximo
        else:
            first_dict[pai].add(s.simbolo)
            return False # Terminal real, BLOQUEIA a sequência
    else:
        filho_first = first_dict.get(s.simbolo, set())
        first_dict[pai].update(filho_first - {'ε'})
        return 'ε' in filho_first # Só continua se o filho tiver ε

def compute_follow():
    a=0
    return a
    # reverserd_grammar = dict(reversed(list(gramatica)))
    
    # changed = True
    # while changed:
    #     changed = False
    #     for A in reverserd_grammar:
    #         for rhs in reverserd_grammar[A]:
    #             for symbol in rhs:
    #                 before = len(first[A])
    #                 #Se for terminal
    #                 if symbol not in reverserd_grammar:
    #                     #print("HERE",symbol)
    #                     first[A].append(symbol)
    #                     #print("HERE2",first[A])
    #                     break
                    
    #                 #Se não for terminal
    #                 else:
    #                     first[A] += first[symbol]

    #                     if 'ε' not in first[symbol]:
    #                         break
    #                     first[A].remove('ε')
    #                 if before != len(first[A]):
    #                     changed = True
    
    # print("First")
    # for f in first:
    #     print(f"{f} -> {first[f]}")
    
    return first