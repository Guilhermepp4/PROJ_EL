from src.help_parsers import *
from src.classes_parser import *
from collections import Counter
import re

def simpleSeq(sequencia, terminals):
    first_result = {}
    for s in sequencia:
        symbol = s.simbolo
        if symbol in terminals:
            print(symbol)
            if symbol == 'ε':
                final_clean = 'ε'
            final_symbol = formatar_simbolo(symbol)
            if simpleT(final_symbol):
                final_clean = tokT(final_symbol[1:-1])
                final_clean = final_clean.lower()
            else:
                final_clean = SimpleToken(final_symbol)
                final_clean = final_clean.lower()
        else:
            clean = SimpleToken(symbol)
            final_clean = re.sub(r'(?<=[a-z0-9])([A-Z])', '_\1', clean).lower()
        first_result[symbol] = final_clean
    

    term_count = Counter(first_result.values())
    repeted = Counter()

    result = {}
    for key, term in first_result.items():
        if term_count[term] > 1:
            repeted[term] += 1
            result[key] = f"{term}_{repeted[term]}"
        else:
            result[key] = term

    print(result)
    return result

def gera_visitor(grammar):
    visitorLines = []
    visitorLines.append("'''")
    visitorLines.append("Welcome to the generated Visitor class for your grammar!")
    visitorLines.append("'''")
    visitorLines.append("")
    visitorLines.append("class CodeGen:")
    
    terminals = grammar.get_Terminals()
    nTerminals = grammar.get_nonterminals()
    for nt in nTerminals: 
        visitorLines.append(f"    def visit_{nt}(self, node):")
    
        for regra in grammar.regras:
            if regra.cabeca == nt:
                tem_epsilon = any(p.simbolo.simbolo == 'ε' for p in regra.producoes)
                
                for i, producao in enumerate(regra.producoes):
                    tem_varias = len(regra.producoes) > 1
                    sequencia = [producao.simbolo] + producao.listaSimbolos
                    result = simpleSeq(sequencia, terminals)
                    
                    if tem_varias:
                        if producao.simbolo.simbolo != 'ε':
                            if i == 0:
                                tamanho = len(sequencia)
                                visitorLines.append(f"      if len(node.children) == {tamanho} and node.children[0] == '{producao.simbolo.simbolo}':")
                                for i, s in enumerate(sequencia):
                                    clean_name = result[s.simbolo]
                                    if s.simbolo in terminals:
                                        visitorLines.append(f"          {clean_name} = node.children[{i}].lexama")
                                    else:
                                        visitorLines.append(f"          {clean_name} = self.visit(node.children[{i}])")
                                names = ','.join([f"{result[s.simbolo]} " for s in sequencia])
                                visitorLines.append(f"          return {names}")
                                visitorLines.append(f"")
                            else:
                                tamanho = len(sequencia)
                                visitorLines.append(f"      elif len(node.children) == {tamanho} and node.children[0] == '{producao.simbolo.simbolo}':")
                                for i, s in enumerate(sequencia):
                                    clean_name = result[s.simbolo]
                                    if s.simbolo in terminals:
                                        visitorLines.append(f"          {clean_name} = node.children[{i}].lexama")
                                    else:
                                        visitorLines.append(f"          {clean_name} = self.visit(node.children[{i}])")
                                names = ','.join([f"{result[s.simbolo]} " for s in sequencia])
                                visitorLines.append(f"          return {names}")
                                visitorLines.append(f"")
                
                    else:
                        if not tem_epsilon:
                            for i, s in enumerate(sequencia):
                                clean_name = result[s.simbolo]
                                if s.simbolo in terminals:
                                    visitorLines.append(f"      {clean_name} = node.children[{i}].lexama")
                                else:
                                    visitorLines.append(f"      {clean_name} = self.visit(node.children[{i}])")
                            names = ','.join([f"{result[s.simbolo]} " for s in sequencia])
                            visitorLines.append(f"      return {names}")
        if tem_epsilon:
                visitorLines.append(f"      return '' # Caso Epsilon")
        visitorLines.append("")
                        

    return "\n".join(visitorLines)