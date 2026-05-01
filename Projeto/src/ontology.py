def _norm(text):
    return text.strip().replace(" ", "_").replace("-", "_")

def generate_ontology(grammar, grammar_name, conflitos, first, follow):
    non_terminals = grammar.get_nonterminals()
    terminals = grammar.get_Terminals()
    start = grammar.get_inicial()
    roles = grammar.regras

    ontology_lines = []
    ontology_lines(f"@prefix : <' {NS} '> .")
    ontology_lines("@prefix : <http://www.semanticweb.org/ontologia#> .")
    ontology_lines("@prefix owl: <http://www.w3.org/2002/07/owl#> .")
    ontology_lines("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    ontology_lines("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    ontology_lines("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
    ontology_lines(f"@base : <' {NS} '> .")
    ontology_lines("")

    Gname = _norm(grammar_name)

    ontology_lines.append(f":Gram_{Gname} a :Gramatica ;")
    ontology_lines.append(f"    :name '{Gname}' .")
    ontology_lines.append(f"    :hasStartSymbol :start_{start} ;")
    if non_terminals:
        ontology_lines.append(f"    :hasNonTerminals {', '.join([f':NT_{nt}' for nt in non_terminals])} ;")
    if terminals:
        ontology_lines.append(f"    :hasTerminals {', '.join([f':T_{t}' for t in terminals])} ;")

    ontology_lines.append(f"    :hasProductions {', '.join([f':P_{_norm(nt.cabeca)}' for nt in roles])} .")    

