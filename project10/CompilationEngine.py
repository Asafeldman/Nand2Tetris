"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer

TYPE_DICT = {"KEYWORD": "keyword", 
            "SYMBOL": "symbol", 
            "IDENTIFIER": "identifier", 
            "INT_CONST": "integerConstant", 
            "STRING_CONST": "stringConstant"}

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output = output_stream
    
    def compile_single_token(self) -> None:
        """Compiles a single token and advances."""
        type = TYPE_DICT[self.tokenizer.token_type()]
        token = self.tokenizer.cur_token()
        if self.tokenizer.token_type() == "STRING_CONST":
            token= self.tokenizer.string_val()
        self.output.write(f"<{type}> {token} </{type}>\n")
        self.tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output.write("<class>\n")
        self.compile_single_token() # class
        self.compile_single_token() # className
        self.compile_single_token() # {
        while self.tokenizer.cur_token() in ["static", "field"] and self.tokenizer.has_more_tokens(): # classVarDec*
            self.compile_class_var_dec()
        while self.tokenizer.cur_token() in ["constructor", "function", "method"] and self.tokenizer.has_more_tokens(): # subroutineDec*
            self.compile_subroutine()
        self.compile_single_token() # }
        self.output.write("</class>\n")
        
    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output.write("<classVarDec>\n")
        self.compile_single_token() # static or field
        self.compile_single_token() # type
        self.compile_single_token() # varName
        while self.tokenizer.cur_token() == ",":
            self.compile_single_token() # ,
            self.compile_single_token() # varName
        self.compile_single_token() # ;
        self.output.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output.write("<subroutineDec>\n")
        self.compile_single_token() # constructor, function or method
        self.compile_single_token() # void or type
        # subroutineName
        self.compile_single_token() # subroutineName
        self.compile_single_token() # (
        self.compile_parameter_list()
        self.compile_single_token() # )
        self.output.write("<subroutineBody>\n")
        # subroutineBody
        self.compile_single_token() # {
        while self.tokenizer.cur_token() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.compile_single_token() # }
        self.output.write("</subroutineBody>\n")
        self.output.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output.write("<parameterList>\n")
        while self.tokenizer.cur_token() != ")": # if we haven't reached a closing parantheses, keep advancing tokens
            self.compile_single_token()
        self.output.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output.write("<varDec>\n")
        self.compile_single_token() # var
        self.compile_single_token() # type
        self.compile_single_token() # varName
        while self.tokenizer.cur_token() == ",":
            self.compile_single_token() # ,
            self.compile_single_token() # varName
        self.compile_single_token() # ;
        self.output.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output.write("<statements>\n")
        while self.tokenizer.cur_token() in ["let", "if", "while", "do", "return"]:
            if self.tokenizer.cur_token() == "let":
                self.compile_let()
            elif self.tokenizer.cur_token() == "if":
                self.compile_if()
            elif self.tokenizer.cur_token() == "while":
                self.compile_while()
            elif self.tokenizer.cur_token() == "do":
                self.compile_do()
            elif self.tokenizer.cur_token() == "return":
                self.compile_return()
        self.output.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output.write("<doStatement>\n")
        self.compile_single_token() # do
        self.compile_single_token() # subroutineName
        if self.tokenizer.cur_token() == ".":
            self.compile_single_token() # .
            self.compile_single_token() # methodName
        self.compile_single_token() # (
        self.compile_expression_list() # expressionList
        self.compile_single_token() # )
        self.compile_single_token() # ;
        self.output.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output.write("<letStatement>\n")
        self.compile_single_token() # let
        self.compile_single_token() # varName
        if self.tokenizer.cur_token() == "[":
            self.compile_single_token() # [
            self.compile_expression() # expression
            self.compile_single_token() # ]
        self.compile_single_token() # =
        self.compile_expression() # expression
        self.compile_single_token() # ;
        self.output.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output.write("<whileStatement>\n")
        self.compile_single_token() # while
        self.compile_single_token() # (
        self.compile_expression() # expression
        self.compile_single_token() # )
        self.compile_single_token() # {
        self.compile_statements() # statements
        self.compile_single_token() # }
        self.output.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output.write("<returnStatement>\n")
        self.compile_single_token() # return
        if self.tokenizer.cur_token() != ";":
            self.compile_expression() # expression
        self.compile_single_token() # ;
        self.output.write("</returnStatement>\n")
        
    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output.write("<ifStatement>\n")
        self.compile_single_token() # if
        self.compile_single_token() # (
        self.compile_expression() # expression
        self.compile_single_token() # )
        self.compile_single_token() # {
        self.compile_statements() # statements
        self.compile_single_token() # }
        if self.tokenizer.cur_token() == "else":
            self.compile_single_token() # else
            self.compile_single_token() # {
            self.compile_statements() # statements
            self.compile_single_token() # }

        self.output.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output.write("<expression>\n")
        self.compile_term() # term
        while self.tokenizer.cur_token() in ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']:
            self.compile_single_token() # operation
            self.compile_term() # term
        self.output.write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.output.write("<term>\n")

        if self.tokenizer.token_type() in ["INT_CONST", 'STRING_CONST', "KEYWORD"]:
            self.compile_single_token() # integerConstant, stringConstant or keyword

        elif self.tokenizer.token_type() == "IDENTIFIER":
            self.compile_single_token() # varName
            if self.tokenizer.cur_token() == "[": # varName [expression]
                self.compile_single_token() # [
                self.compile_expression() # expression
                self.compile_single_token() # ]
            elif self.tokenizer.cur_token() == "(":
                self.compile_single_token() # (
                self.compile_expression() # expression
                self.compile_single_token() # )
            elif self.tokenizer.cur_token() == ".":
                self.compile_single_token() # .
                self.compile_single_token() # subroutineName
                self.compile_single_token() # (
                self.compile_expression_list() # expressionList
                self.compile_single_token() # )

        elif self.tokenizer.cur_token() == "(":
            self.compile_single_token() # (
            self.compile_expression() # expression
            self.compile_single_token() # )

        elif self.tokenizer.cur_token() in ['-', '~', '^', '#']:
            self.compile_single_token() # unary op
            self.compile_term() # term

        self.output.write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output.write("<expressionList>\n")
        if self.tokenizer.cur_token() != ")":
            self.compile_expression() # expression
            while self.tokenizer.cur_token() == ",":
                self.compile_single_token() # ,
                self.compile_expression() # expression
        self.output.write("</expressionList>\n")
