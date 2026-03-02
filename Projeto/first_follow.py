from parser import grammar_dict

def compute_first():
    first = {nt : set() for nt in grammar_dict}
    reverserd_grammar = dict(reversed(list(grammar_dict.items())))


    changed = True
    while changed:
        changed = False
        for A in reverserd_grammar:
            for rhs in reverserd_grammar[A]:
                for symbol in rhs:
                    before = len(first[A])
                    #Se for terminal
                    if symbol not in reverserd_grammar:
                        #print("HERE",symbol)
                        first[A].add(symbol)
                        #print("HERE2",first[A])
                        break
                    
                    #Se não for terminal
                    else:
                        first[A] |= (first[symbol] - {"ε"})

                        if 'ε' not in first[symbol]:
                            break
                    if before != len(first[A]):
                        changed = True
    
    print("\nFirst")
    for f in first:
        print(f"{f} -> {first[f]}")

compute_first()