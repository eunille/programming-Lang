"""
<program> ::= <expression> | <if_expr>

<if_expr> ::= "IF" <logical_expr> "THEN" <expression> "ELSE" <expression>

<logical_expr> ::= <comparison> { ("AND" | "OR") <comparison> }

<comparison> ::= <expression> { ("==" | "!=" | "<" | ">" | "<=" | ">=") <expression> }

<expression> ::= <term> { ("+" | "-") <term> }

<term> ::= <factor> { ("*" | "/" | "%") <factor> }

<factor> ::= ("+" | "-") <factor> | <exponentiation>

<exponentiation> ::= <atom> { "^" <factor> }

<atom> ::= <number> | "(" <expression> ")"

<number> ::= <digit> { <digit> } [ "." <digit> { <digit> } ]

<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"


sample test case for exponentiation
2 ^ 3 + 4 * 5 - 6
10 / 2 + 3 ^ 2
5 + 2 ^ 3 ^ 2 - 1
"""
from enum import Enum
from typing import Any, List, Optional
import math

# Token types for our language
class TokenType(Enum):
    # Keywords
    IF = 'IF'
    THEN = 'THEN'
    ELSE = 'ELSE'
    
    # Operators
    PLUS = 'PLUS'           # +
    MINUS = 'MINUS'         # -
    MULTIPLY = 'MULTIPLY'   # *
    DIVIDE = 'DIVIDE'       # /
    EXPONENTIATION = 'EXPONENTIATION'         # ^
    MODULUS = 'MODULUS'     # %
    
    # Bitwise operators
    BITWISE_AND = 'BITWISE_AND' # &
    BITWISE_OR = 'BITWISE_OR'   # |
    
    # Logical operators
    AND = 'AND'            # AND
    OR = 'OR'             # OR
    NOT = 'NOT'           # NOT
    
    # Comparison operators
    EQUAL = 'EQUAL'       # ==
    NOT_EQUAL = 'NOT_EQUAL' # !=
    LESS = 'LESS'         # <
    GREATER = 'GREATER'   # >
    LESS_EQUAL = 'LESS_EQUAL' # <=
    GREATER_EQUAL = 'GREATER_EQUAL' # >=
    
    # Other tokens
    NUMBER = 'NUMBER'
    LPAREN = 'LPAREN'     # (
    RPAREN = 'RPAREN'     # )
    EOF = 'EOF'

class Token:
    def __init__(self, type: TokenType, value: Any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f'Token({self.type}, {self.value}, pos={self.line}:{self.column})'

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1
        
        # Define keywords
        self.keywords = {
            'IF': TokenType.IF,
            'THEN': TokenType.THEN,
            'ELSE': TokenType.ELSE,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT
        }

    def error(self):
        raise Exception(f'Invalid character at line {self.line}, column {self.column}')

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        self.pos += 1
        self.column += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char and self.current_char != '\n':
            self.advance()
        self.advance()

    def number(self) -> Token:
        result = ''
        decimal_point_count = 0
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                decimal_point_count += 1
                if decimal_point_count > 1:
                    self.error()
            result += self.current_char
            self.advance()
            
        if result.startswith('.'):
            result = '0' + result
        if result.endswith('.'):
            result += '0'
            
        return Token(
            TokenType.NUMBER,
            float(result),
            self.line,
            self.column - len(result)
        )

    def _id(self) -> Token:
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
            
        token_type = self.keywords.get(result.upper())
        if token_type:
            return Token(token_type, result.upper(), self.line, self.column - len(result))
        self.error()  # Unknown identifier

    def get_next_token(self) -> Token:
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.skip_comment()
                continue

            if self.current_char.isdigit() or self.current_char == '.':
                return self.number()

            if self.current_char.isalpha():
                return self._id()

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.line, self.column - 1)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.line, self.column - 1)

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', self.line, self.column - 1)

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', self.line, self.column - 1)

            if self.current_char == '^':
                self.advance()
                return Token(TokenType.EXPONENTIATION, '^', self.line, self.column - 1)

            if self.current_char == '%':
                self.advance()
                return Token(TokenType.MODULUS, '%', self.line, self.column - 1)

            if self.current_char == '&':
                self.advance()
                return Token(TokenType.BITWISE_AND, '&', self.line, self.column - 1)

            if self.current_char == '|':
                self.advance()
                return Token(TokenType.BITWISE_OR, '|', self.line, self.column - 1)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, self.column - 1)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, self.column - 1)

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', self.line, self.column - 2)
                self.error()

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', self.line, self.column - 2)
                self.error()

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', self.line, self.column - 2)
                return Token(TokenType.LESS, '<', self.line, self.column - 1)

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column - 2)
                return Token(TokenType.GREATER, '>', self.line, self.column - 1)

            self.error()

        return Token(TokenType.EOF, None, self.line, self.column)

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1
        
        # Define keywords
        self.keywords = {
            'IF': TokenType.IF,
            'THEN': TokenType.THEN,
            'ELSE': TokenType.ELSE,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT
        }

    def error(self):
        raise Exception(f'Invalid character at line {self.line}, column {self.column}')

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        self.pos += 1
        self.column += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char and self.current_char != '\n':
            self.advance()
        self.advance()

    def number(self) -> Token:
        result = ''
        decimal_point_count = 0
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                decimal_point_count += 1
                if decimal_point_count > 1:
                    self.error()
            result += self.current_char
            self.advance()
            
        if result.startswith('.'):
            result = '0' + result
        if result.endswith('.'):
            result += '0'
            
        return Token(
            TokenType.NUMBER,
            float(result),
            self.line,
            self.column - len(result)
        )

    def _id(self) -> Token:
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
            
        token_type = self.keywords.get(result.upper())
        if token_type:
            return Token(token_type, result.upper(), self.line, self.column - len(result))
        self.error()  # Unknown identifier

    def get_next_token(self) -> Token:
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.skip_comment()
                continue

            if self.current_char.isdigit() or self.current_char == '.':
                return self.number()

            if self.current_char.isalpha():
                return self._id()

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.line, self.column - 1)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.line, self.column - 1)

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', self.line, self.column - 1)

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', self.line, self.column - 1)

            if self.current_char == '^':
                self.advance()
                return Token(TokenType.EXPONENTIATION, '^', self.line, self.column - 1)

            if self.current_char == '%':
                self.advance()
                return Token(TokenType.MODULUS, '%', self.line, self.column - 1)

            if self.current_char == '&':
                self.advance()
                return Token(TokenType.BITWISE_AND, '&', self.line, self.column - 1)

            if self.current_char == '|':
                self.advance()
                return Token(TokenType.BITWISE_OR, '|', self.line, self.column - 1)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, self.column - 1)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, self.column - 1)

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', self.line, self.column - 2)
                self.error()

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', self.line, self.column - 2)
                self.error()

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', self.line, self.column - 2)
                return Token(TokenType.LESS, '<', self.line, self.column - 1)

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column - 2)
                return Token(TokenType.GREATER, '>', self.line, self.column - 1)

            self.error()

        return Token(TokenType.EOF, None, self.line, self.column)

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def atom(self) -> float:
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return token.value
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.expression()
            self.eat(TokenType.RPAREN)
            return result
        self.error()

    def factor(self) -> float:
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return self.factor()
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return -self.factor()
        return self.exponentiation()

    def exponentiation(self) -> float:
        result = self.atom()
        
        while self.current_token.type == TokenType.EXPONENTIATION:
            self.eat(TokenType.EXPONENTIATION)
            result = math.pow(result, self.factor())
            
        return result

    def term(self) -> float:
        result = self.factor()
        
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULUS):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
                result *= self.factor()
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
                divisor = self.factor()
                if divisor == 0:
                    raise Exception('Division by zero')
                result /= divisor
            elif token.type == TokenType.MODULUS:
                self.eat(TokenType.MODULUS)
                result %= self.factor()
                
        return result

    def expression(self) -> float:
        result = self.term()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                result += self.term()
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                result -= self.term()
                
        return result

    def comparison(self) -> bool:
        result = self.expression()
        
        while self.current_token.type in (TokenType.EQUAL, TokenType.NOT_EQUAL, 
                                        TokenType.LESS, TokenType.GREATER,
                                        TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            token = self.current_token
            if token.type == TokenType.EQUAL:
                self.eat(TokenType.EQUAL)
                result = result == self.expression()
            elif token.type == TokenType.NOT_EQUAL:
                self.eat(TokenType.NOT_EQUAL)
                result = result != self.expression()
            elif token.type == TokenType.LESS:
                self.eat(TokenType.LESS)
                result = result < self.expression()
            elif token.type == TokenType.GREATER:
                self.eat(TokenType.GREATER)
                result = result > self.expression()
            elif token.type == TokenType.LESS_EQUAL:
                self.eat(TokenType.LESS_EQUAL)
                result = result <= self.expression()
            elif token.type == TokenType.GREATER_EQUAL:
                self.eat(TokenType.GREATER_EQUAL)
                result = result >= self.expression()
                
        return result

    def logical_expr(self) -> bool:
        result = self.comparison()
        
        while self.current_token.type in (TokenType.AND, TokenType.OR):
            token = self.current_token
            if token.type == TokenType.AND:
                self.eat(TokenType.AND)
                result = result and self.comparison()
            elif token.type == TokenType.OR:
                self.eat(TokenType.OR)
                result = result or self.comparison()
                
        return result

    def if_expr(self) -> float:
        self.eat(TokenType.IF)
        condition = self.logical_expr()
        self.eat(TokenType.THEN)
        true_value = self.expression()
        self.eat(TokenType.ELSE)
        false_value = self.expression()
        
        return true_value if condition else false_value

    def parse(self):
        if self.current_token.type == TokenType.IF:
            return self.if_expr()
        return self.logical_expr()

def evaluate(text: str) -> Any:
    lexer = Lexer(text)
    parser = Parser(lexer)
    return parser.parse()

def interactive_test():
    print("hello world")
    print("Expression Parser Test Interface")
    print("===============================")
    print("Supported operations:")
    print("1. Arithmetic: +, -, *, /, ^, %")
    print("2. Bitwise: &, |")
    print("3. Logical: AND, OR, NOT")
    print("4. Comparison: ==, !=, <, >, <=, >=")
    print("5. IF-THEN-ELSE statements")
    print("6. Enter 'quit' to exit")
    print("\nExample expressions:")
    print("- 3 + 4 * 2")
    print("- (3 + 4) * 2")
    print("- 2 ^ 3")
    print("- 5 % 2")
    print("- 5 & 3")
    print("- 5 > 3 AND 2 < 4")
    print("- IF 5 > 3 THEN 1 ELSE 0")
    print("\nEnter your expression:")

    while True:
        try:
            expr = input("\n> ")
            if expr.lower() == 'quit':
                print("Goodbye!")
                break
            
            if not expr.strip():
                continue
                
            result = evaluate(expr)
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    interactive_test()