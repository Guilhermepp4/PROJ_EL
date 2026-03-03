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
    
    # print("\nFirst")
    # for f in first:
    #     print(f"{f} -> {first[f]}")
    
    return first

def compute_follow(first):
    follow = {nt : set() for nt in grammar_dict}
    i=0
    for nt in grammar_dict:
        i = i + 1
        if i == 1:
            follow[nt].add('$')
            continue
        
        for A in grammar_dict:
            for production in grammar_dict[A]: 
                for j in range(0, len(production)-1):
                    if production[j] == nt:
                        if production[j+1] not in grammar_dict:
                            follow[nt].add(production[j+1])
                            break
                        else:
                            follow[nt] |= (first[production[j+1]] - {"ε"})
                        
                        
    print("\nFollow")
    for f in follow:
        print(f"{f} -> {follow[f]}")
                
            
    
first = compute_first()
compute_follow(first)