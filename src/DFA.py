import typing
from base import *
from SyntaxTree import SyntaxTree


class DFANode:
  pass


class DFATransition:
  _from: DFANode
  _to: DFANode

  def __init__(self, _from: DFANode, _to: DFANode):
    self._from = _from
    self._to = _to

  @property
  def go(self):
    return self._to


class DFANode:
  nodes: typing.Dict[DFATransition]

  def __init__(self):
    self.nodes = dict()

  def go(self, s: str):
    if s in self.nodes:
      return self.nodes[s].go
    return None


class DFA:
  graph: typing.List[DFANode]
  head: DFANode

  def __init__(self):
    self.clear()

  def clear(self):
    self.graph = []
    self.head = None

  def build(self, tree: SyntaxTree):
    pass