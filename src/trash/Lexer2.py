from os import error
import typing


class Token(typing.NamedTuple):
  tag: str
  value: str


class PatternError(Exception):
  pass


class Lexer:
  _brackets_steck: list
  _specials: set

  orepeat = (r'{}', 'REPEAT')
  ogroup = (r'()', 'GROUP')
  osq = (r'[]', 'SQUARE')
  oor = r'|'
  oklini = r'*'
  meta = r'\\'
  empty = r'#'

  def __init__(self):
    self._specials = set(self.orepeat[0] + self.ogroup[0] + self.osq[0] + self.oor + self.oklini + self.meta + self.empty)
    self.clear()

  def clear(self):
    self._brackets_steck = []

  def __addStr(self, i, start, s):
    if i-start > 0:
      return Token('STR', s[start:i])
    return Token('EMPTY', self.empty)

  def __addBrackets(self, i, start, s, group):
    token1 = self.__addStr(i,start,s)
    token2 = Token(group[1],s[i])
    if s[i] == group[0][1]:
      t = self._brackets_steck.pop()
      if t != group[0][0]:
        raise PatternError(f"Incorrect brackets sequence for '{group[0][0]}'")
    else:
      self._brackets_steck.append(s[i])
    return token1, token2

  def lex(self, s: str):
    # TODO: make this code clearer. Use dict or Functors instead
    # TODO: sq brackets not work
    self.clear()
    i = 0
    start = 0
    s = '(' + s + ')'
    while i < len(s)-1:
      if s[i] in self.ogroup[0]:
        for t in self.__addBrackets(i,start,s,self.ogroup):
          yield t
        start = i + 1
      elif s[i] in self.osq[0]:
        for t in self.__addBrackets(i,start,s,self.osq):
          yield t
        start = i + 1
      elif s[i] in self.oor:
        yield self.__addStr(i,start,s)
        start = i + 1 
        yield Token(s[i], s[i])       
      elif s[i] in self.meta:
        if not s[i+1] in self._specials:
          raise PatternError(f"Incorrect meta symbol '{s[i:i+2]}'")
        yield self.__addStr(i,start,s)
        i += 1
        start = i+1
        sp = 1
        yield Token(self.meta, s[i])
      if s[i+1] == self.orepeat[0][0]:
        if not sp:
          yield self.__addStr(i,start,s)
          yield self.__addStr(i+1, i, s)
        yield Token(self.orepeat[0][0], self.orepeat[0][0])
        for j in range(i+2, len(s)-1):
          if s[j] == self.orepeat[0][1]:
            yield Token('STR', s[i+2:j])
            yield Token(self.orepeat[0][1], self.orepeat[0][1])
            i = j
            start = j
            break
          elif not s[j] in '1234567890':
            raise PatternError(f"Repeat number should be integer not '{s[i+1:j]}'")
      elif s[i+1] in self.oklini:
        if not sp:
          yield self.__addStr(i,start,s)
          start = i + 2
          yield self.__addStr(i+1, i, s)
        i += 1
        yield Token(s[i], s[i]) 
      i += 1
      sp = 0
    for t in self.__addBrackets(i,start,s,self.ogroup):
      yield t
    if self._brackets_steck:
      raise PatternError(f"Incorrect brackets sequence")

if __name__ == '__main__':
  test = r"asd*(nad)|((cur\{}))as[123]{6}"
  lexer = Lexer()
  # print(*lexer.lex(test), sep='\n\n')
  for t in lexer.lex(test):
    print(t.value, end=', ')
  print()