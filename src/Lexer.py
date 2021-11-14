import typing
from base import *


class Token(typing.NamedTuple):
  tag: str
  value: str


class Functors:
  _bracket_steck: list
  _sq_flag: bool

  def __init__(self):
    self._bracket_steck = []
    self._sq_flag = False

  def __brackets_check(self,s,k):
    if s == k:
      self._bracket_steck.append(k)
    else:
      if not self._bracket_steck:
        raise PatternError('Incorrect brackets sequence')
      t = self._bracket_steck.pop()
      if t != k:
        raise PatternError('Incorrect brackets sequence')

  def ogroup(self, i, s) -> typing.Dict[Token, int]:
    if self._sq_flag:
      raise PatternError('"[]" can\'t contains "()"')
    self.__brackets_check(s[i],'(')
    return (Token(GROUP_BRACKET, s[i]), i + 1)

  def osq(self, i, s) -> typing.Dict[Token, int]:
    if self._sq_flag and s[i] == '[':
      raise PatternError('"[]" can\'t contains "[]"')
    self.__brackets_check(s[i],'[')
    self._sq_flag = not self._sq_flag
    return (Token(SQ_BRACKET, s[i]), i + 1)

  def orepeat(self, i, s) -> typing.Dict[Token, int]:
    for j in range(i+1, len(s)-1):
      if s[j] == '}':
        if j-i == 1:
          raise PatternError('{} should contains numbers')
        return (Token(REPEATS, s[i+1: j]), j+1)
      elif not s[j] in '1234567890':
        raise PatternError('in {x} x must be a number sequence')
    raise PatternError('No "}" in {x} sequence')

  def oor(self, i, s) -> typing.Dict[Token, int]:
    return (Token(OR, '|'), i + 1)

  def oklini(self, i, s) -> typing.Dict[Token, int]:
    return (Token(KLINI, '*'), i + 1)

  def meta(self, i, s) -> typing.Dict[Token, int]:        #look forward 1
    return (Token(META, s[i:i+2]), i + 2)

  def ometanum(self, i, s) -> typing.Dict[Token, int]:    #look forward 1
    for j in range(i+1, len(s)):
      if not s[j] in '1234567890':
        return (Token(META_NUM, s[i+1: j]), j)
    raise PatternError('very strange pattern o_O')

  def ochar(self, i, s) -> typing.Dict[Token, int]:
    return (Token(CHAR, s[i]), i + 1)

  def oempty(self, i, s) -> typing.Dict[Token, int]:
    return (Token(EMPTY, '#'), i + 1)

class Lexer:
  _brackets_steck: list
  _specials: set
  __functor = Functors()
  _functors = dict
  
  meta = '\\'

  def __init__(self, specials=SPECIALS):
    self._specials = specials
    self._functors = {
      r'meta': self.__functor.meta,
      r'ometanum': self.__functor.ometanum,
      r'char': self.__functor.ochar,
      r'*': self.__functor.oklini,
      r'|': self.__functor.oor,
      r'{': self.__functor.orepeat,
      r'[': self.__functor.osq,
      r']': self.__functor.osq,
      r'(': self.__functor.ogroup,
      r')': self.__functor.ogroup,
      r'#': self.__functor.oempty,
    }
    self.clear()

  def clear(self):
    self._brackets_steck = []

  def check(self, i, s) -> typing.Dict[Token, int]:
    if s[i] == self.meta:
      if s[i+1] in '1234567890':
        return self._functors['ometanum'](i,s)
      elif s[i+1] in self._specials:
        return self._functors['meta'](i,s)
      else:
        raise PatternError('incorrect pattern')
    elif not s[i] in self._specials:
      return self._functors['char'](i,s)
    return self._functors[s[i]](i,s) 

  def lex(self, s: str) -> Token:
    i = 0
    s = '(' + s + ')'
    while i < len(s):
      token, i = self.check(i,s)
      yield token

if __name__ == '__main__':
  test = r"asd*(nad)|((cur\{))as[123]{6}[]\#"
  test = r"(nana)|((n*[a]){3})"
  lexer = Lexer()
  # print(*lexer.lex(test), sep='\n\n')
  for t in lexer.lex(test):
    print(t.tag, end=', ')
  print()
  for t in lexer.lex(test):
    print(t.value, end=', ')
  print()