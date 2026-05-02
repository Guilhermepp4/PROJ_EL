NS = "http://rpcw.di.uminho.pt/2026/Proj_EL/"

def _norm(text):
    return text.strip().replace(" ", "_").replace("-", "_")

def generate_ontology(grammar, grammar_name, conflitos, first, follow):
    non_terminals = grammar.get_nonterminals()
    terminals = grammar.get_Terminals()
    start = grammar.get_inicial()
    roles = grammar.regras
    ll_1 = len(conflitos) == 0

    ontology_lines = []
    ontology_lines.append(f"@prefix : <' {NS} '> .")
    ontology_lines.append("@prefix : <http://www.semanticweb.org/ontologia#> .")
    ontology_lines.append("@prefix owl: <http://www.w3.org/2002/07/owl#> .")
    ontology_lines.append("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    ontology_lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    ontology_lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
    ontology_lines.append(f"@base : <' {NS} '> .")
    ontology_lines.append("")

    Gname = _norm(grammar_name)

    ontology_lines.append(f"# Gramática {Gname}")
    ontology_lines.append(f":Gram_{Gname} a :Gramatica ;")
    ontology_lines.append(f"    :name '{Gname}' .")
    ontology_lines.append(f"    :hasStartSymbol :start_{start} ;")
    ontology_lines.append(f"    :isLL1 {'true' if ll_1 else 'false'} ;")
    if non_terminals:
        ontology_lines.append(f"    :hasNonTerminals {', '.join([f':NT_{nt}' for nt in non_terminals])} ;")
    if terminals:
        ontology_lines.append(f"    :hasTerminals {', '.join([f':T_{t}' for t in terminals])} ;")

    ontology_lines.append(f"    :hasRoles {', '.join([f':R_{_norm(nt.cabeca)}' for nt in roles])} ;")

    if conflitos:
        ontology_lines.append(f"    :hasConflicts {', '.join([f':Conflict_{_norm(c)}' for c in conflitos])} .")  
    ontology_lines.append("")

    ontology_lines.append(f"# Start Symbol")
    ontology_lines.append(f":StartSymbol_{start} a :StartSymbol ;")
    ontology_lines.append(f"    :name '{_norm(start)}' .")
    ontology_lines.append("")

    ontology_lines.append(f"# Non-Terminals")
    for nt in non_terminals:
        ontology_lines.append(f":NT_{_norm(nt)} a :NonTerminal ;")
        ontology_lines.append(f"    :name '{_norm(nt)}' ;")
        ontology_lines.append(f"    :belongsTo :Gram_{Gname} ;")
        ontology_lines.append(f"    :hasFirstSet {', '.join([f':T_{t}' for t in first[nt]])} ;")
        ontology_lines.append(f"    :hasFollowSet {', '.join([f':T_{t}' for t in follow[nt]])} .")
        ontology_lines.append("")
    
    ontology_lines.append(f"# Terminals")
    for t in terminals:
        ontology_lines.append(f":T_{_norm(t)} a :Terminal ;")
        ontology_lines.append(f"    :name '{_norm(t)}' ;")
        ontology_lines.append(f"    :belongsTo :Gram_{Gname} ;")
        # ontology_lines.append(f"    :hasRegex :Reg{regex} .")
        ontology_lines.append("")
    

    ontology_lines.append(f"# Conjunto First")
    for nt in non_terminals:
        fid=f":first_{_norm(nt)}"
        first_members = sorted(first.get(nt, set()))
        ontology_lines.append(f"{fid} a :FirstSet ;")
        if first_members:
            firsts = []
            for m in first_members:
                if m == 'ε':
                    firsts.append(":epsilon")
                elif m in terminals:
                    firsts.append(f":T_{_norm(m)}")
                else:
                    firsts.append(f":NT_{_norm(m)}")
            ontology_lines.append(f"    :hasMembers {', '.join(firsts)} .")
        ontology_lines.append("")

    ontology_lines.append(f"# Conjunto Follow")
    for nt in non_terminals:
        fod=f":follow_{_norm(nt)}"
        follow_members = sorted(follow.get(nt, set()))
        ontology_lines.append(f"{fod} a :FollowSet ;")
        if follow_members:
            follows = []
            for m in follow_members:
                if m == 'ε':
                    firsts.append(":epsilon")
                elif m in terminals:
                    firsts.append(f":T_{_norm(m)}")
                else:
                    firsts.append(f":NT_{_norm(m)}")
            ontology_lines.append(f"    :hasMembers {', '.join(firsts)} .")
        ontology_lines.append("")
    
    ontology_lines.append(f"# Roles")
    
    for rule in roles:
        head = f"{_norm(rule.cabeca)}"
        pid = f":R_{head}"
        
        producoes = []
        for i, prod in enumerate(rule.producoes):
            prod_id = f":P_{head}_{i}"
            producoes.append(prod_id)
        
        ontology_lines.append(f"{pid} a :Role ;")
        ontology_lines.append(f"    :hasHead :NT_{_norm(rule.cabeca)} ;")
        if prod:
            ontology_lines.append(f"    :hasProductions {', '.join(producoes)} .")
        ontology_lines.append("")

        for i, prod in enumerate(rule.producoes):
            prodid = f":P_{head}_{i}"
            its_null= prod == ['ε']
            ontology_lines.append(f"{prodid} a :Production ;")
            sequencia = [prod.simbolo] + prod.listaSimbolos
            if not its_null:
                ontology_lines.append(f"    :hasSymbols {', '.join([f':T_{_norm(s.simbolo)}' if s.simbolo in terminals else f':NT_{_norm(s.simbolo)}' for s in sequencia])} .")
            else:
                ontology_lines.append(f"    :hasSymbols :epsilon .")
            ontology_lines.append("")

    if conflitos:
        ontology_lines.append(f"# Conflitos")
        for c in conflitos:
            cid = f":Conflict_{_norm(c)}"
            ontology_lines.append(f"{cid} a :Conflict ;")
            ontology_lines.append(f"    :description '{c}' .")
    return '\n'.join(ontology_lines)