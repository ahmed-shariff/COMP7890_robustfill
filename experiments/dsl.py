from enum import Enum, auto
from string import ascii_letters, digits, whitespace
import re
import unicodedata

# Defning the base parameter values that can be passed to an expression
class Boundry(Enum):
    START = auto()
    END = auto()


class Case(Enum):
    PROPER = auto()
    ALL_CAPS = auto()
    LOWER = auto()


class Type(Enum):
    NUMBER = auto()
    WORD = auto()
    ALPHANUM = auto()
    ALL_CAPS = auto()
    PROP_CASE = auto()
    LOWER = auto()
    DIGIT = auto()
    CHAR = auto()


Position = list(range(-100, 101))
Index = list(range(-5, 5))
Delimiter_names = ["AMPERSAND", "COMMA", "FULL STOP", "QUESTION MARK", "EXCLAMATION MARK",
                   "COMMERCIAL AT", "LEFT PARENTHESIS", "RIGHT PARENTHESIS", "LEFT SQUARE BRACKET",
                   "RIGHT SQUARE BRACKET", "PERCENT SIGN", "LEFT CURLY BRACKET",
                   "RIGHT CURLY BRACKET", "SOLIDUS", "COLON", "SEMICOLON", "DOLLAR SIGN",
                   "NUMBER SIGN", "REVERSE SOLIDUS", "RIGHT DOUBLE QUOTATION MARK", "APOSTROPHE",
                   "SPACE", "HORIZONTAL TABULATION", "LINE FEED", "CARRIAGE RETURN"]
Delimiter = [unicodedata.lookup(name) for name in Delimiter_names]
Character = list(ascii_letters) + list(digits) + Delimiter

class Expression:
    def __init__(self):
        pass

    def __call__(self, *args, **kwds):
        raise NotImplemented


class Concat(Expression):
    def __init__(self, *expressions):
        self.experssions = expressions

    def __call__(self, v):
        return "".join([expression(v) for expression in self.experssions])


class ConstStr(Expression):
    def __init__(self, c):
        self.c = c

    def __call__(self, v):
        return self.c


class SubString(Expression):
    def __init__(self, k1, k2):
        self.k1 = k1
        self.k2 = k2

    def __call__(self, v):
        return v[k1:k2]


class _GetTypeMatches(Expression):
    def __init__(self, t):
        if t == Type.NUMBER:
            regex_str = '[0-9]+'
        elif t == Type.WORD:
            regex_str = '[A-Za-z]+'
        elif t == Type.ALPHANUM:
            regex_str = '[A-Za-z0-9]+'
        elif t == Type.ALL_CAPS:
            regex_str = '[A-Z]+'
        elif t == Type.PROP_CASE:
            regex_str = '[A-Z][a-z]+'
        elif t == Type.LOWER:
            regex_str = '[a-z]+'
        elif t == Type.DIGIT:
            regex_str = '[0-9]'
        elif t == Type.CHAR:
            regex_str = '[A-Za-z0-9]'
        elif isinstance(t, str):
            regex_str = t

        self.regex_matcher = re.compile(regex_str)

    def __call__(self, v):
        return list(self.regex_matcher.finditer(v))

    
class GetSpan(Expression):
    def __init__(self, r1, i1, y1, r2, i2, y2):
        self.matcher1 = _GetTypeMatches(r1)
        self.i1 = i1
        self.y1 = y1
        self.matcher2 = _GetTypeMatches(r2)
        self.i2 = i2
        self.y2 = y2

    def __call__(self, v):
        match_result1 = self.matcher1(v)[self.i1]
        match_result2 = self.matcher2(v)[self.i2]
        if self.y1 == Boundry.START:
            start = match_result1.start()
        elif self.y1 == Boundry.END:
            start = match_result1.end()

        if self.y2 == Boundry.START:
            end = match_result2.start()
        elif self.y2 == Boundry.END:
            end = match_result2.end()

        return v[start:end]
        
    
class Nesting(Expression):
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

    def __call__(self, v):
        return self.parent(self.child(v))
    
    
class GetToken(Expression):
    def __init__(self, t, i):
        self.matcher = _GetTypeMatches(t)
        self.i = i

    def __call__(self, v):
        match_result = self.matcher(v)[self.i]
        return v[match_result.start():match_result.end()]


class ToCase(Expression):
    def __init__(self, case):
        self.case = case

    def __call__(self, v):
        if self.case == Case.ALL_CAPS:
            return v.upper()
        elif self.case == Case.LOWER:
            return v.lower()
        elif self.case == Case.PROPER:
            return v.capitalize()
        else:
            raise ValueError("Invalid value for case")


class Replace(Expression):
    def __init__(self, f, t):
        self.f = f
        self.t = t

    def __call__(self, v):
        return v.replace(self.f, self.t)


class Trim(Expression):
    def __call__(self, v):
        return v.strip()


class GetUpTo(Expression):
    def __init__(self, r, i):
        self.matcher = _GetTypeMatches(r)
        self.i = i        

    def __call__(self, v):
        match_result = self.matcher(v)[self.i]
        return v[:match_result.end()]


# GetFrom(r)| GetFirst(t, i) | GetAll(t)
class GetFrom(Expression):
    def __init__(self, r, i):
        self.matcher = _GetTypeMatches(r)
        self.i = i        

    def __call__(self, v):
        match_result = self.matcher(v)[self.i]
        return v[match_result.end():]


class GetFirst(Expression):
    def __init__(self, r, i):
        self.matcher = _GetTypeMatches(r)
        self.i = i        

    def __call__(self, v):
        match_results = self.matcher(v)[:self.i]
        return "".join([v[match_result.start(): match_result.end()] for match_result in match_results])


class GetAll(Expression):
    def __init__(self, r):
        self.matcher = _GetTypeMatches(r)

    def __call__(self, v):
        match_results = self.matcher(v)
        return "".join([v[match_result.start(): match_result.end()] for match_result in match_results])

    
if __name__=="__main__":
    print(list(Boundry))
    print(list(Case))
    print(list(Position))
    print(list(Index))
    print(list(Delimiter))
    print(list(Character))
    print(len(list(Boundry) +
              list(Case)   +
              list(Position) +
              list(Index) +
              list(Delimiter)+
              list(Character)))
    print(_GetTypeMatches(Type.CHAR)(" asdf ks 12 44 ; sdf"))
    print(_GetTypeMatches(";")(" asdf ks 12 44 ; sdf"))
    print(GetToken(Type.WORD, 2)(" asdf ks 12 44 ; sdf"))
    print(Replace(";", " ")(" asdf ks 12 44 ; sdf"))
    print(GetUpTo(Type.DIGIT, 3)(" asdf ks 12 44 ; sdf"))
    print(GetFrom(Type.DIGIT, 3)(" asdf ks 12 44 ; sdf"))
    print(GetFirst(Type.WORD, 2)(" asdf ks 12 44 ; sdf"))
    print(GetToken(Type.WORD, 2).__dict__)
