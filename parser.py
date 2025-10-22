from enum import Enum, auto


# Token defining
class TokenType(Enum):
    NUMBER = auto()
    IDENTIFIER = auto()
    PLUS = auto()
    MINUS = auto()
    MULT = auto()
    EQUALS = auto()
    CONDITIONAL = auto()
    LAMBDA = auto()
    LET = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOI = auto()


class Token:
    def __init__(self, tokenValue):
        # Assign value to NUMBER and IDENTIFIER
        if tokenValue.isdigit():
            self.value = tokenValue
            self.type = TokenType.NUMBER
        elif isinstance(tokenValue, str) and self.typeOf(tokenValue) == None:
            self.value = tokenValue
            self.type = TokenType.IDENTIFIER
        else:
            self.value = -1
            self.type = self.typeOf(tokenValue)

    def typeOf(self, value):
        types = {
            "\u002b": TokenType.PLUS,
            "\u2212": TokenType.MINUS,
            "\u00d7": TokenType.MULT,
            "\u003d": TokenType.EQUALS,
            "\u003f": TokenType.CONDITIONAL,
            "\u03bb": TokenType.LAMBDA,
            "\u225c": TokenType.LET,
            "\u0028": TokenType.LPAREN,
            "\u0029": TokenType.RPAREN,
            "$": TokenType.EOI,
        }
        return types.get(value, None)

    def __str__(self):
        strings = {
            TokenType.NUMBER: str(self.value),
            TokenType.IDENTIFIER: str(self.value),
            TokenType.PLUS: "\u002b",
            TokenType.MINUS: "\u2212",
            TokenType.MULT: "\u00d7",
            TokenType.EQUALS: "\u003d",
            TokenType.CONDITIONAL: "\u003f",
            TokenType.LAMBDA: "\u03bb",
            TokenType.LET: "\u225c",
            TokenType.LPAREN: "\u0028",
            TokenType.RPAREN: "\u0029",
            TokenType.EOI: "$",
        }
        return strings.get(self.type, None)

    def __repr__(self):
        strings = {
            TokenType.NUMBER: str(self.value),
            TokenType.IDENTIFIER: str(self.value),
            TokenType.PLUS: "PLUS",
            TokenType.MINUS: "MINUS",
            TokenType.MULT: "MULT",
            TokenType.EQUALS: "EQUALS",
            TokenType.CONDITIONAL: "CONDITIONAL",
            TokenType.LAMBDA: "LAMBDA",
            TokenType.LET: "LET",
            TokenType.LPAREN: "LPAREN",
            TokenType.RPAREN: "RPAREN",
            TokenType.EOI: "$",
        }
        return strings.get(self.type, "None")


# Lexer that tokenizes input string where valid
class Lexer:
    def __init__(self):
        # Contains the tokens ready to be parsed
        self.tokens = []

    @classmethod
    def token_initialize(cls, inputString):
        return cls().token_process(inputString)

    # Add a space between lparen and the next char, between rparen and the previous char
    # Purpose to use whitespace as a delimiter to split and quick tokenize
    def token_process(self, inputString):
        modified = inputString.replace("\u0028", " \u0028 ").replace(
            "\u0029", " \u0029 "
        )
        string_list = modified.split()
        for i in string_list:
            self.tokens.append(self.tokenize(i))
        self.tokens.append(Token("$"))
        return self.tokens

    def tokenize(self, string):
        return Token(string)


# Define Non terminals
class NonTerminal(Enum):
    PROGRAM = auto()
    EXPR = auto()
    PAREN_EXPR = auto()


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, parseTree=False):
        # Build the parse table based on the one built in the report
        self.parse_table = self.build_table()
        # Initialize the stack
        self.stack = []
        # Storing the input tokens
        self.tokens = []
        # Keep track of position when parsing
        self.position = 0
        # Option to enable printing parse tree
        self.parseTree = parseTree

    # Build the table.
    # Use a dictionary with the key is a tuple of (Terminal, Non-terminal) and the value is the production
    def build_table(self):
        parse_table = {}
        for i in [TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.LPAREN]:
            parse_table[(NonTerminal.PROGRAM, i)] = NonTerminal.EXPR

        parse_table[(NonTerminal.EXPR, TokenType.NUMBER)] = TokenType.NUMBER
        parse_table[(NonTerminal.EXPR, TokenType.IDENTIFIER)] = TokenType.IDENTIFIER
        parse_table[(NonTerminal.EXPR, TokenType.LPAREN)] = [
            TokenType.LPAREN,
            NonTerminal.PAREN_EXPR,
            TokenType.RPAREN,
        ]

        for i in [TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.LPAREN]:
            parse_table[(NonTerminal.PAREN_EXPR, i)] = [NonTerminal.EXPR, "EXPR*"]
        parse_table[(NonTerminal.PAREN_EXPR, TokenType.PLUS)] = [
            TokenType.PLUS,
            NonTerminal.EXPR,
            NonTerminal.EXPR,
        ]
        parse_table[(NonTerminal.PAREN_EXPR, TokenType.MULT)] = [
            TokenType.MULT,
            NonTerminal.EXPR,
            NonTerminal.EXPR,
        ]
        parse_table[(NonTerminal.PAREN_EXPR, TokenType.EQUALS)] = [
            TokenType.EQUALS,
            NonTerminal.EXPR,
            NonTerminal.EXPR,
        ]
        parse_table[(NonTerminal.PAREN_EXPR, TokenType.MINUS)] = [
            TokenType.MINUS,
            NonTerminal.EXPR,
            NonTerminal.EXPR,
        ]
        parse_table[(NonTerminal.PAREN_EXPR, TokenType.CONDITIONAL)] = [
            TokenType.CONDITIONAL,
            NonTerminal.EXPR,
            NonTerminal.EXPR,
            NonTerminal.EXPR,
        ]
        parse_table[(NonTerminal.PAREN_EXPR, TokenType.LAMBDA)] = [
            TokenType.LAMBDA,
            TokenType.IDENTIFIER,
            NonTerminal.EXPR,
        ]
        parse_table[(NonTerminal.PAREN_EXPR, TokenType.LET)] = [
            TokenType.LET,
            TokenType.IDENTIFIER,
            NonTerminal.EXPR,
            NonTerminal.EXPR,
        ]
        return parse_table

    # Get the current token when parsing
    def current_token(self):
        if self.position >= len(self.tokens):
            raise ParserError("End of input")
        return self.tokens[self.position]

    # Move to the next token
    def advance(self):
        self.position += 1

    @classmethod
    def parseProcess(cls, input, parseTree=False):
        return cls(parseTree=parseTree).parse(input)

    def parse(self, input):
        # Initiate input token and position at 0.
        self.tokens = Lexer.token_initialize(input)
        self.position = 0

        # If print parse tree option is on
        # (Since I cannot find a way to print a parse tree effectively with the normal approach (else clause))
        # So for the print parse tree I do it manually with every cases.
        if self.parseTree:
            self.position = 0
            # A program always start with <expr> so we can start by trying to parse an <expr>
            tree = self.parseEXPR()
            # Check if we reach the end then print the parse tree
            if self.current_token().type == TokenType.EOI:
                self.printFormatTree(input, tree)
            else:
                raise ParserError("Unexpected error occurs")
        else:
            # Normal approach using stack and parse table
            try:
                # Initiate the stack with an $ and <program>
                self.stack = [TokenType.EOI, NonTerminal.PROGRAM]
                # Loop until stack empty
                while self.stack:
                    # Take the token on top of the stack an current token
                    top_stack = self.stack[-1]
                    current_token = self.current_token()

                    # Check is the top token is non terminal
                    if isinstance(top_stack, NonTerminal):
                        key = (top_stack, current_token.type)
                        if key not in self.parse_table:
                            raise ParserError(
                                f"No production rule found for {top_stack}->{current_token.type}"
                            )
                        production = self.parse_table[key]
                        # Pop the top token from the stack to add in the production
                        self.stack.pop()
                        if isinstance(production, list):
                            for i in reversed(production):
                                self.stack.append(i)
                        elif isinstance(production, NonTerminal) or isinstance(
                            production, TokenType
                        ):
                            self.stack.append(production)
                    # Check if the top token of the stack is a terminal,
                    # if true then compare with the current input token,
                    # if they are the same and move to the next position
                    elif isinstance(top_stack, TokenType):
                        if top_stack == current_token.type:
                            self.stack.pop()
                            self.advance()
                        else:
                            raise ParserError(
                                f"Unexpected token {current_token} at position {self.position}, expected {top_stack}"
                            )
                    # Handle <expr>*
                    elif top_stack == "EXPR*":
                        # Pop the <expr>*
                        self.stack.pop()
                        # Check if we can parse another <expr>
                        if current_token.type in [
                            TokenType.NUMBER,
                            TokenType.IDENTIFIER,
                            TokenType.LPAREN,
                        ]:
                            # If yes then add another <expr> followed by <expr>*
                            self.stack.append("EXPR*")
                            self.stack.append(NonTerminal.EXPR)
                    else:
                        raise ParserError(f"Invalid symbol on stack: {top_stack}")
                # Check if we pop the $ or not
                if not self.stack:
                    print("Parse successful")
                    return True
                else:
                    raise ParserError(f"Unexpected tokens remaining: {self.tokens}")
            except ParserError as e:
                print("Parse failed: ", e)
                return False

    # Parse <expr> manually for parse table use case
    def parseEXPR(self):
        token = self.current_token()
        if token.type == TokenType.NUMBER:
            self.advance()
            return token.value
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return token.value
        elif token.type == TokenType.LPAREN:
            self.advance()
            tree = self.parsePAREN()
            if self.current_token().type != TokenType.RPAREN:
                raise ParserError("Expected ')'")
            self.advance()
            return tree
        elif token.type == TokenType.RPAREN:
            raise ParserError("Unmatched paren")
        else:
            raise ParserError(f"Unexpected token {token}, expect an <expr>")

    # Parse <paren-expr> manually for parse table use case
    def parsePAREN(self):
        token = self.current_token()

        if token.type in [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MULT,
            TokenType.EQUALS,
            TokenType.CONDITIONAL,
        ]:
            op = str(token.type.name)
            self.advance()

            if token.type in [
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.MULT,
                TokenType.EQUALS,
            ]:
                f_expr = self.parseEXPR()
                s_expr = self.parseEXPR()
                if self.current_token().type != TokenType.RPAREN:
                    raise ParserError(f"Wrong number of arguments")
                return [op, f_expr, s_expr]

            elif token.type == TokenType.CONDITIONAL:
                f_expr = self.parseEXPR()
                s_expr = self.parseEXPR()
                t_expr = self.parseEXPR()
                if self.current_token().type != TokenType.RPAREN:
                    raise ParserError(f"Wrong number of arguments")
                return [op, f_expr, s_expr, t_expr]
        elif token.type == TokenType.LAMBDA:
            self.advance()
            if self.current_token().type != TokenType.IDENTIFIER:
                raise ParserError("LAMBDA followed by identifier argument")
            id = self.current_token().value
            self.advance()
            expr = self.parseEXPR()
            if self.current_token().type != TokenType.RPAREN:
                raise ParserError(f"Wrong number of arguments")
            return ["LAMBDA", id, expr]

        elif token.type == TokenType.LET:
            self.advance()
            if self.current_token().type != TokenType.IDENTIFIER:
                raise ParserError("LET followed by identifier argument")
            id = self.current_token().value
            self.advance()
            f_expr = self.parseEXPR()
            s_expr = self.parseEXPR()
            if self.current_token().type != TokenType.RPAREN:
                raise ParserError(f"Wrong number of arguments")
            return ["LET", id, f_expr, s_expr]
        else:
            func = self.parseEXPR()
            args = []
            while self.current_token().type in [
                TokenType.NUMBER,
                TokenType.IDENTIFIER,
                TokenType.LPAREN,
            ]:
                args.append(self.parseEXPR())

            if args:
                return [func] + args
            else:
                return func

    # Print like the demo
    def printFormatTree(self, input, tree):
        print(f"Input: {input}")
        print(f"Output: {tree}")


def main():
    inp = input("Enter string: ")
    tree = Parser.parseProcess(inp, parseTree=True)


if __name__ == "__main__":
    main()
