import typing
from base import *
from Lexer import Lexer, Token


class Node:
  pass


class Node:
  root: Node
  nodes: typing.List[Node]
  value: Token

  def __init__(
      self, 
      root: Node=None,
      value: Token=None):
    self.root = root
    self.value = value
    self.nodes = []

  def add(self, value: Token) -> Node:
    node = Node(self, value)
    self.nodes.append(node)
    return node

  def pop(self):
    return self.nodes.pop()

  def add_node(self, node: Node):
    node.root = self
    self.nodes.append(node)

  @property
  def last(self):
    return self.nodes[-1]

  @property
  def lvl(self):
    if self.root is None:
      return 0
    return self.root.lvl + 1

  @property
  def isNotEmpty(self):
    return not not self.nodes

  def leftRoot(self):
    if not self.nodes:
      yield self
    for n in self.nodes:
      n.leftRoot()

  def optLeftRoot(self):
    go = self.nodes
    while go:
      tmp = go.pop(0)
      yield tmp
      go = tmp.nodes + go

  def printTree(self):
    for t in self.optLeftRoot():
      print(t)

  def copy(self):
    return Node(self.root, self.value)

  def __str__(self) -> str:
    return f"(lvl={self.lvl}  id={id(self)}  p={id(self.root) if self.root else self.root}  v={self.value})"
    

class SyntaxTree:
  root_stack: typing.List[Node]
  lexer: Lexer
  _functors = dict
  _joiner: Node
  _df_joiner: Node
  _groups_num: int

  def __init__(self):
    self.lexer = Lexer()
    self._functors = {
      GROUP_BRACKET: self.op_group_brackets,
      SQ_BRACKET: self.op_sq_brackets,
      REPEATS: self.op_uno_left,
      OR: self.change_joiner,
      KLINI: self.op_uno_left,
      META: self.op_binary_join,
      META_NUM: self.op_meta_num,
      CHAR: self.op_binary_join,
      EMPTY: self.op_binary_join
    }
    self.clear()

  def clear(self):
    self.root_stack = [Node()]
    self._df_joiner = Node(None, Token(CONCAT, '.'))
    self._joiner = self._df_joiner.copy()
    self._groups_num = 0
    self.lexer.clear()

  def build(self, s: str):
    gen = self.lexer.lex(s)
    for t in gen:
      self._functors[t.tag](t)

    if len(self.root_stack) > 1:
      raise PatternError("syntax tree")
    return self.root_stack[0]

  def change_joiner(self, t: Token):
    if t.tag == OR:
      self._joiner = Node(None, t)

  def op_binary_join(self, t: Token):
    tmp = self.root_stack[-1]
    if tmp.isNotEmpty:
      self.__join(tmp.pop(), Node(None, t), tmp)
    else:
      self.root_stack[-1].add(t)

  def op_uno_left(self, t: Token):
    ch = self.root_stack[-1].pop()
    tmp = self.root_stack[-1].add(t)
    tmp.add_node(ch)

  def op_brackets(self, t: Token):
    if self._isOpenBracket(t):
      tmp = Node(None, t)
      self.__root_concat(self.root_stack[-1], tmp)
      self.root_stack.append(tmp)
      return None
    else:
      return self.root_stack.pop()

  def op_group_brackets(self, t: Token):
    tmp = self.op_brackets(t)
    if tmp:
      self._groups_num += 1
      tmp.value = Token(GROUP_BRACKET, self._groups_num)

  def op_sq_brackets(self, t: Token):
    if self._df_joiner.value.tag == CONCAT:
      self._df_joiner = Node(None, Token(OR, '|'))
    else:
      self._df_joiner = Node(None, Token(CONCAT, '.'))
    self._joiner = self._df_joiner.copy()
    tmp = self.op_brackets(t)
    self.op_binary_join(Token(EMPTY, '#'))
    if tmp:
      root = tmp.root
      root.nodes.remove(tmp)
      root.add_node(tmp.pop())

  def op_meta_num(self, t: Token):
    val = int(t.value)
    if val > self._groups_num:
      raise PatternError('group index out off range')
    self.op_binary_join(t)

  def __root_concat(self, n1: Node, n2: Node):
    if n1.isNotEmpty:
      ch = n1.pop()
      self.__join(ch, n2, n1)
    else:
      n1.add_node(n2)

  def __join(self, n1: Node, n2: Node, root: Node):
    self._joiner.add_node(n1)
    self._joiner.add_node(n2)
    root.add_node(self._joiner)
    self._joiner = self._df_joiner.copy()

  def _isOpenBracket(self, t: Token):
    return t.value in "(["

  def nullable(self, n: Node):
    tag = n.value.tag
    if tag == OR:
      return self.nullable(n.nodes[0]) or self.nullable(n.nodes[1])
    elif tag == CONCAT:
      return self.nullable(n.nodes[0]) and self.nullable(n.nodes[1])
    elif tag == KLINI or tag == EMPTY:
      return True
    elif tag == REPEATS:
      return self.nullable(n.nodes[0])
    elif tag == META_NUM:
      return self.nullable(self._groups[int(n.value.value)])
    else:
      return False

  def firstpos(self, n: Node):
    tag = n.value.tag
    if tag == OR:
      return self.firstpos(n.nodes[0]) | self.firstpos(n.nodes[1])
    elif tag == CONCAT:
      if self.nullable(n.nodes[0]):
        return self.firstpos(n.nodes[0]) | self.firstpos(n.nodes[1])
      return self.nullable(n.nodes[0])
    elif tag == KLINI:
      return self.firstpos(n.nodes[0])
    elif tag == REPEATS:
      return self.firstpos(n.nodes[0])
    elif tag == EMPTY:
      return set()
    else:
      return set(n.value.value)

  def lastpos(self, n: Node):
    pass

  def followpos(self, n: Node):
    pass

if __name__ == '__main__':
  tree = SyntaxTree()
  test = r"asd*((geg)[]([123\{\]]*)){3}"
  # test = r"(12)|b"
  # test = r"(nana)|((n*[a]){3})"
  # test = r"asd*(nad)|((cur\{))as[123]{6}[]\#"
  # test = r"a|b|c|([123456]*)"
  # test = r"(a|b)*abb\#"
  # test = r"[123]"
  # test = r"(a|b)*abb\#\123123"
  # test = r"[]"
  test = r"(a)\1*"
  tree.build(test).printTree()