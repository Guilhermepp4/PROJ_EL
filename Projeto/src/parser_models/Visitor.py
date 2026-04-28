'''
Welcome to the generated Visitor class for your grammar!
'''

class VisitorBase:
  def visit(self, node):
    if node is None: return None
    if node.lexema is not None:
       return node.lexema

    method_name = 'visit_' + node.label
    method = getattr(self, method_name)
    return method(node)

  def visit_gen(self, node):
    partes = []

    for child in node.children:
      result = self.visit(child)
      if result is not None and str(result).strip():
         partes.append(result)

    return ' '.join(partes)

class CodeGen(VisitorBase):
  def visit_Lista(self, node):
    lbrack = node.children[0].lexema
    elems = self.visit(node.children[1])
    rbrack = node.children[2].lexema
    return self.visit_gen(node)

  def visit_Elems(self, node):
    if len(node.children) == 2 and node.children[0].label == 'Elem':
      elem = self.visit(node.children[0])
      resto = self.visit(node.children[1])
      return self.visit_gen(node)

    return None # Caso Epsilon

  def visit_Resto(self, node):
    if len(node.children) == 3 and node.children[0].label == ',':
      comma = node.children[0].lexema
      elem = self.visit(node.children[1])
      resto = self.visit(node.children[2])
      return self.visit_gen(node)

    return None # Caso Epsilon

  def visit_Elem(self, node):
    if len(node.children) == 1 and node.children[0].label == 'INT':
      int = node.children[0].lexema
      return self.visit_gen(node)

    elif len(node.children) == 1 and node.children[0].label == 'ID':
      id = node.children[0].lexema
      return self.visit_gen(node)

