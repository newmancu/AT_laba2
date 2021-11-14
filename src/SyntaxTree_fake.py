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

  def __str__(self) -> str:
    return f"(lvl={self.lvl}  id={id(self)}  p={id(self.root) if self.root else self.root}  v={self.value})"

class Functor:
  
  def __init__(self):
    pass

  def o_group(self, root: typing.List[Node], t: Token, *args):
    if t.value == '(':
      node = root[-1].add(t)
      root.append(node)
    else:
      root.pop()
    return 2

  def o_sq(self, root: typing.List[Node], t: Token, *args):
    if t.value == '[':
      node = root[-1].add(t)
      root.append(node)
    else:
      root.pop()
    return 2

  def o_repeats(self, root: typing.List[Node], t: Token, *args):
    head = root[-1].pop()
    tmp = root[-1].add(t)
    tmp.add_node(head)
    return 0

  def o_or(self, root: typing.List[Node], t: Token, *args):
    left = root[-1].pop()
    tmp = root[-1].add(t)
    tmp.add_node(left)
    root.append(tmp)
    return 1

  def o_klini(self, root: typing.List[Node], t: Token, *args):
    head = root[-1].pop()
    tmp = root[-1].add(t)
    tmp.add_node(head)
    return 0

  def o_meta(self, root: typing.List[Node], t: Token, *args):
    root[-1].add(t)
    return 0

  def o_meta_num(self, root: typing.List[Node], t: Token, *args):
    head = root[-1].pop()
    tmp = root[-1].add(t)
    tmp.add_node(head)
    return 0

  def o_char(self, root: typing.List[Node], t: Token, *args):
    root[-1].add(t)
    return 0


class SyntaxTree:
  root_steck: typing.List[Node]
  lexer: Lexer
  _functors = dict
  _functor: Functor

  def __init__(self):
    self.lexer = Lexer()
    self._functor = Functor()
    self._functors = {
      GROUP_BRACKET: self._functor.o_group,
      SQ_BRACKET: self._functor.o_sq,
      REPEATS: self._functor.o_repeats,
      OR: self._functor.o_or,
      KLINI: self._functor.o_klini,
      META: self._functor.o_meta,
      META_NUM: self._functor.o_meta_num,
      CHAR: self._functor.o_char
    }
    self.clear()

  def clear(self):
    self.root_steck = [Node()]
    self.lexer.clear()

  def build(self, s: str):
    gen = self.lexer.lex(s)
    skip = 0
    for t in gen:
      prev_skip = skip
      skip = self._functors[t.tag](self.root_steck, t)
      if prev_skip == 1:
        if skip:
          self.root_steck.pop(-2)
        else:
          self.root_steck.pop()

    if len(self.root_steck) > 1:
      raise PatternError("syntax tree")
    return self.root_steck[0]

if __name__ == '__main__':
  tree = SyntaxTree()
  test = r"asd*((geg)([123\{\]]*)){3}"
  test = r"(12)|b"
  test = r"(nana)|((n*[a]){3})"
  test = r"asd*(nad)|((cur\{))as[123]{6}[]\#"
  test = r"a|b|c|([123]*)"
  test = r"(a|b)*abb\#\123123"
  tree.build(test).printTree()