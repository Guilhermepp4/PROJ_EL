from grammar import grammar

EPSILON = "ε"

def compute_first(grammar):
    first = {nt: set() for nt in grammar.non_terminals}

    changed = True
    while changed:
        changed = False

        for prod in grammar.productions:
            head = prod.head
            body = prod.body

            # Caso produção A -> ε
            if body == [EPSILON]:
                if EPSILON not in first[head]:
                    first[head].add(EPSILON)
                    changed = True
                continue

            for symbol in body:
                # Se for terminal
                if symbol in grammar.terminals:
                    if symbol not in first[head]:
                        first[head].add(symbol)
                        changed = True
                    break

                # Se for não-terminal
                elif symbol in grammar.non_terminals:
                    before = len(first[head])

                    # Adiciona FIRST(symbol) menos ε
                    first[head] |= (first[symbol] - {EPSILON})

                    if len(first[head]) > before:
                        changed = True

                    # Se symbol NÃO tem ε, para
                    if EPSILON not in first[symbol]:
                        break
                else:
                    break
            else:
                # Se todos os símbolos podem gerar ε
                if EPSILON not in first[head]:
                    first[head].add(EPSILON)
                    changed = True

    print("FIRST:")
    for nt in first:
        print(f"{nt}: {first[nt]}")

    return first

def compute_follow(grammar, first):
    follow = {nt: set() for nt in grammar.non_terminals}
    follow[grammar.start_symbol].add("$")

    changed = True
    while changed:
        changed = False

        for prod in grammar.productions:
            head = prod.head
            body = prod.body

            for i, symbol in enumerate(body):
                if symbol in grammar.non_terminals:

                    # Caso exista símbolo a seguir
                    if i + 1 < len(body):
                        next_symbol = body[i+1]

                        # Se for terminal
                        if next_symbol in grammar.terminals:
                            if next_symbol not in follow[symbol]:
                                follow[symbol].add(next_symbol)
                                changed = True

                        # Se for não-terminal
                        elif next_symbol in grammar.non_terminals:
                            before = len(follow[symbol])

                            # FIRST(next) - ε
                            follow[symbol] |= (first[next_symbol] - {EPSILON})

                            if len(follow[symbol]) > before:
                                changed = True

                            # Se next pode gerar ε
                            if EPSILON in first[next_symbol]:
                                before = len(follow[symbol])
                                follow[symbol] |= follow[head]
                                if len(follow[symbol]) > before:
                                    changed = True

                    # Se for último símbolo
                    else:
                        before = len(follow[symbol])
                        follow[symbol] |= follow[head]
                        if len(follow[symbol]) > before:
                            changed = True

    print("\nFOLLOW:")
    for nt in follow:
        print(f"{nt}: {follow[nt]}")

    return follow

first = compute_first(grammar)
follow = compute_follow(grammar, first)