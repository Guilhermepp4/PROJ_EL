'''
Welcome to the generated Visitor class for your grammar!
'''

class CodeGen:
    def visit_Lista(self, node):
      lbrack = node.children[0].lexama
      elems = self.visit(node.children[1])
      rbrack = node.children[2].lexama
      return lbrack ,elems ,rbrack 

    def visit_Elems(self, node):
      if len(node.children) == 2 and node.children[0] == 'Elem':
          elem = self.visit(node.children[0])
          resto = self.visit(node.children[1])
          return elem ,resto 

      return '' # Caso Epsilon

    def visit_Resto(self, node):
      if len(node.children) == 3 and node.children[0] == ',':
          comma = node.children[0].lexama
          elem = self.visit(node.children[1])
          resto = self.visit(node.children[2])
          return comma ,elem ,resto 

      return '' # Caso Epsilon

    def visit_Elem(self, node):
      if len(node.children) == 1 and node.children[0] == 'INT':
          int = node.children[0].lexama
          return int 

      elif len(node.children) == 1 and node.children[0] == 'ID':
          id = node.children[0].lexama
          return id 

