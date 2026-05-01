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

    ontology_lines.append(f"    :hasProductions {', '.join([f':P_{_norm(nt.cabeca)}' for nt in roles])} ;")

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
    
    return '\n'.join(ontology_lines)