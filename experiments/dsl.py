from enum import Enum, auto
from string import ascii_letters, digits, whitespace
import re
import unicodedata
import random

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



TYPE = list(Type)
CASE = list(Case)
BOUNDRY = list(Boundry)
POSITION = list(range(-100, 101))
INDEX = list(range(-5, 5))
DELIMITER_NAMES = ["AMPERSAND", "COMMA", "FULL STOP", "QUESTION MARK", "EXCLAMATION MARK",
                   "COMMERCIAL AT", "LEFT PARENTHESIS", "RIGHT PARENTHESIS", "LEFT SQUARE BRACKET",
                   "RIGHT SQUARE BRACKET", "PERCENT SIGN", "LEFT CURLY BRACKET",
                   "RIGHT CURLY BRACKET", "SOLIDUS", "COLON", "SEMICOLON", "DOLLAR SIGN",
                   "NUMBER SIGN", "REVERSE SOLIDUS", "RIGHT DOUBLE QUOTATION MARK", "APOSTROPHE",
                   "SPACE", "HORIZONTAL TABULATION", "LINE FEED", "CARRIAGE RETURN"]
DELIMITER = [unicodedata.lookup(name) for name in DELIMITER_NAMES]
CHARACTER = list(ascii_letters) + list(digits) + DELIMITER
REGEX = DELIMITER + TYPE

class Expression:
    def __init__(self):
        pass

    def __call__(self, *args, **kwds):
        raise NotImplemented


class Concat(Expression):
    @staticmethod
    def self_initialize():
        expressions = []
        for _ in range(random.randint(0, 10)):
            expressions.append(random.choice(EXPRESSIONS).self_initialize())
        return Concat(expressions)

    def __init__(self, *expressions):
        self.experssions = expressions

    def __call__(self, v):
        return "".join([expression(v) for expression in self.experssions])


class ConstStr(Expression):
    @staticmethod
    def self_initialize():
        return ConstStr(random.choice(CHARACTER))
    
    def __init__(self, c):
        self.c = c

    def __call__(self, v):
        return self.c


class SubString(Expression):
    @staticmethod
    def self_initialize():
        while True:
            try:
                return SubString(random.choice(POSITION), random.choice(POSITION))
            except AssertionError:
                pass

    def __init__(self, k1, k2):
        self.k1 = k1
        self.k2 = k2
        assert k1 < k2

    def __call__(self, v):
        return v[self.k1: self.k2]


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
            regex_str = re.escape(t)

        self.regex_matcher = re.compile(regex_str)

    def __call__(self, v):
        return list(self.regex_matcher.finditer(v))

    
class GetSpan(Expression):
    @staticmethod
    def self_initialize():
        return GetSpan(random.choice(REGEX), random.choice(INDEX), random.choice(BOUNDRY),
                       random.choice(REGEX), random.choice(INDEX), random.choice(BOUNDRY))
    
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
    @staticmethod
    def self_initialize():
        return Nesting(random.choice(NESTING_EXPRESSIONS).self_initialize(),
                       random.choice(NESTING_EXPRESSIONS + SUBSTRING_EXPRESSIONS).self_initialize())

    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

    def __call__(self, v):
        return self.parent(self.child(v))
    
    
class GetToken(Expression):
    @staticmethod
    def self_initialize():
        return GetToken(random.choice(TYPE), random.choice(INDEX))

    def __init__(self, t, i):
        self.matcher = _GetTypeMatches(t)
        self.i = i

    def __call__(self, v):
        match_result = self.matcher(v)[self.i]
        return v[match_result.start():match_result.end()]


class ToCase(Expression):
    @staticmethod
    def self_initialize():
        return ToCase(random.choice(CASE))

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
    @staticmethod
    def self_initialize():
        return Replace(random.choice(DELIMITER), random.choice(DELIMITER))

    def __init__(self, f, t):
        self.f = f
        self.t = t

    def __call__(self, v):
        return v.replace(self.f, self.t)


class Trim(Expression):
    @staticmethod
    def self_initialize():
        return Trim()

    def __call__(self, v):
        return v.strip()


class GetUpTo(Expression):
    @staticmethod
    def self_initialize():
        return GetUpTo(random.choice(REGEX), random.choice(INDEX))

    def __init__(self, r, i):
        self.matcher = _GetTypeMatches(r)
        self.i = i        

    def __call__(self, v):
        print(v, self.i, self.matcher.regex_matcher)
        match_result = self.matcher(v)[self.i]
        return v[:match_result.end()]


class GetFrom(Expression):
    @staticmethod
    def self_initialize():
        return GetFrom(random.choice(REGEX), random.choice(INDEX))

    def __init__(self, r, i):
        self.matcher = _GetTypeMatches(r)
        self.i = i        

    def __call__(self, v):
        match_result = self.matcher(v)[self.i]
        return v[match_result.end():]


class GetFirst(Expression):
    @staticmethod
    def self_initialize():
        return GetFirst(random.choice(REGEX), random.choice(INDEX))

    def __init__(self, r, i):
        self.matcher = _GetTypeMatches(r)
        self.i = i        

    def __call__(self, v):
        match_results = self.matcher(v)[:self.i]
        return "".join([v[match_result.start(): match_result.end()] for match_result in match_results])


class GetAll(Expression):
    @staticmethod
    def self_initialize():
        return GetAll(random.choice(REGEX))

    def __init__(self, r):
        self.matcher = _GetTypeMatches(r)

    def __call__(self, v):
        match_results = self.matcher(v)
        return "".join([v[match_result.start(): match_result.end()] for match_result in match_results])


EXPRESSIONS = [ConstStr,
               SubString,
               GetSpan,
               Nesting,
               GetToken,
               ToCase,
               Replace,
               Trim,
               GetUpTo,
               GetFrom,
               GetFirst,
               GetAll]

NESTING_EXPRESSIONS = [GetToken,
                       ToCase,
                       Replace,
                       Trim,
                       GetUpTo,
                       GetFrom,
                       GetFirst,
                       GetAll]

SUBSTRING_EXPRESSIONS = [SubString,
                         GetSpan]
    
    
if __name__=="__main__":
    print(list(BOUNDRY))
    print(list(CASE))
    print(list(POSITION))
    print(list(INDEX))
    print(list(DELIMITER))
    print(list(CHARACTER))
    print(len(list(BOUNDRY) +
              list(CASE)   +
              list(POSITION) +
              list(INDEX) +
              list(DELIMITER)+
              list(CHARACTER)))
    print(_GetTypeMatches(Type.CHAR)(" asdf ks 12 44 ; sdf"))
    print(_GetTypeMatches(";")(" asdf ks 12 44 ; sdf"))
    print(GetToken(Type.WORD, 2)(" asdf ks 12 44 ; sdf"))
    print(Replace(";", " ")(" asdf ks 12 44 ; sdf"))
    print(GetUpTo(Type.DIGIT, 3)(" asdf ks 12 44 ; sdf"))
    print(GetFrom(Type.DIGIT, 3)(" asdf ks 12 44 ; sdf"))
    print(GetFirst(Type.WORD, 2)(" asdf ks 12 44 ; sdf"))
    print(GetToken(Type.WORD, 2).__dict__)
    print(ConstStr.self_initialize()(" asdf ks 12 44 ; sdf"))
    print(SubString.self_initialize()(" asdf ks 12 44 ; sdf"))
    try:
        print(GetSpan.self_initialize()(" asdf ks 12 44 ; sdf asdf ks 12 44 ; sdf asdf ks 12 44 ; sdf asdf ks 12 44 ; sdf asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    try:
        print(GetToken.self_initialize()(" asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    try:
        print(ToCase.self_initialize()(" asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    try:
        print(Replace.self_initialize()(" asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    try:
        print(GetUpTo.self_initialize()(" asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    try:
        print(GetFrom.self_initialize()(" asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    try:
        print(GetFirst.self_initialize()(" asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    try:
        print(GetAll.self_initialize()(" asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    try:
        print(Nesting.self_initialize()(" asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf  asdf ks 12 44 ; sdf"))
    except IndexError as e:
        print(e)
    

    print(Concat.self_initialize().experssions)
