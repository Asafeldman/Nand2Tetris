"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import *
from SymbolTable import *
from VMWriter import *

TYPE_DICT = {"KEYWORD": "keyword", 
            "SYMBOL": "symbol", 
            "IDENTIFIER": "identifier", 
            "INT_CONST": "integerConstant", 
            "STRING_CONST": "stringConstant"}

CONVERT_DICT = {"ARG": "ARG", 
                "STATIC": "STATIC", 
                "VAR": "LOCAL", 
                "FIELD": "THIS"}

UNARY_DICT = {"-": "NEG", 
              "~": "NOT", 
              '^': "SHIFTLEFT", 
              "#": "SHIFTRIGHT"}




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
        self.output = output_stream
        self.tokenizer = input_stream
        self.symbol_table = SymbolTable()
        self.vmwriter = VMWriter(output_stream)
        self.class_name = None
        self.while_counter = 0
        self.if_counter = 0
        self.keyword_constant_dct = {'true': ['CONST', 0],
                                     'false': ['CONST', 0],
                                     'null': ['CONST', 0],
                                     'this': ['POINTER', 0]}
        self.unary_op_vm = {'-': 'NEG', '~': 'NOT', '^': 'SHIFTLEFT',
                            '#': 'SHIFRIGHT'}
    
    # def compile_single_token(self) -> None:
    #     """Compiles a single token and advances."""
    #     type = TYPE_DICT[self.tokenizer.token_type()]
    #     token = self.tokenizer.cur_token()
    #     if self.tokenizer.token_type() == "STRING_CONST":
    #         token = self.tokenizer.string_val()
    #     self.output.write(f"<{type}> {token} </{type}>\n")
    #     self.tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output.write("// start class compilation\n")

        self.tokenizer.advance() # class
        self.class_name = self.tokenizer.cur_token() # save the class's name for the subroutines
        self.tokenizer.advance() # className
        self.tokenizer.advance() # {
        while self.tokenizer.cur_token() in ["static", "field"]: # classVarDec*
            self.compile_class_var_dec()
        while self.tokenizer.cur_token() in ["constructor", "method", "function"]: # classSubroutineDec
            self.compile_subroutine() 
        self.tokenizer.advance() # }

        self.output.write("// end class compilation\n")
        
    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""

        self.output.write("// start class variable declaration\n")

        kind = self.tokenizer.cur_token().upper()
        self.tokenizer.advance()
        type = self.tokenizer.cur_token()
        self.tokenizer.advance()
        name = self.tokenizer.cur_token()
        self.tokenizer.advance()
        self.symbol_table.define(name, type, kind) # add class variable to the symbol table
        while self.tokenizer.cur_token() == ",":
            self.tokenizer.advance() # ,
            name = self.tokenizer.cur_token()
            self.symbol_table.define(name, type, kind) # add new class variable to the symbol table
            self.tokenizer.advance() 
        self.tokenizer.advance() # ;

        self.output.write("// end class variable declaration\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """

        self.output.write("// start subroutine compilation\n")

        self.symbol_table.start_subroutine() # set new symbol table
        kind = self.tokenizer.cur_token() # save the subroutine's kind (constructor, function or method)
        self.tokenizer.advance() # constructor, function or method
        self.tokenizer.advance() # void or typed subroutine
        subroutine_name = self.tokenizer.cur_token() # save the subroutine's name
        if kind == "method": # add 'this | className | argument | 0' to the symbol table
            self.symbol_table.define("this", self.class_name, "ARG")   
        function_name = self.class_name + "." + subroutine_name # Main.foo for example
        self.tokenizer.advance() # subroutineName
        self.tokenizer.advance() # (
        self.compile_parameter_list()
        self.tokenizer.advance() # )

        self.output.write("// start subroutine body compilation\n")
        self.tokenizer.advance() # {
        while self.tokenizer.cur_token() == "var": # varDec*
            self.compile_var_dec() 
        n_locals = self.symbol_table.var_count("VAR")
        self.vmwriter.write_function(function_name, n_locals) 

        if kind == "constructor":
            n_fields = self.symbol_table.var_count("FIELD")
            self.vmwriter.write_push("CONST", n_fields) # push (number of field variables in the class)
            self.vmwriter.write_call("Memory.alloc", 1) # Memory.alloc(number of arguments)
            self.vmwriter.write_pop("POINTER", 0) # anchor this at the base address
        elif kind == "method":
            self.vmwriter.write_push("ARG", 0)
            self.vmwriter.write_pop("POINTER", 0)
        self.compile_statements()
        self.tokenizer.advance() # }
        self.output.write("// end subroutine body compilation\n")

        self.output.write("// end subroutine compilation\n")

    def compile_subroutine_call(self) -> None:
        """
        Compiles a subroutine call, not including the enclosing "().
        """

        self.output.write("// start subroutine call compilation\n")
        n_args = 0
        identifier = self.tokenizer.cur_token()
        function_name = identifier

        self.tokenizer.advance() # functionName

        if self.tokenizer.cur_token() == ".":
            self.tokenizer.advance() # .
            subroutine_name = self.tokenizer.cur_token()
            self.tokenizer.advance() # subroutineName
            type = self.symbol_table.type_of(identifier)
            if type: # typed subroutine
                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)
                self.vmwriter.write_push(CONVERT_DICT[kind], index)
                function_name = type + "." + subroutine_name
                n_args += 1
            else:
                function_name = identifier + "." + subroutine_name
        else:
            self.vmwriter.write_push("POINTER", 0)
            function_name = self.class_name + "." + identifier
            n_args += 1
        self.tokenizer.advance() # (
        n_args += self.compile_expression_list() # compile the expression list and add its number of arguments to n_args
        self.tokenizer.advance() # )
        self.vmwriter.write_call(function_name, n_args)

        self.output.write("// end subroutine call compilation\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """

        self.output.write("// start parameter list compilation\n")
        
        if self.tokenizer.cur_token() != ")":
            type = self.tokenizer.cur_token() 
            self.tokenizer.advance() # type
            name = self.tokenizer.cur_token()
            self.tokenizer.advance() # name
            self.symbol_table.define(name, type, "ARG")
        
        while self.tokenizer.cur_token() != ")":
            self.tokenizer.advance() # ,
            type = self.tokenizer.cur_token()
            self.tokenizer.advance() # type
            name = self.tokenizer.cur_token() 
            self.tokenizer.advance() # name            
            self.symbol_table.define(name, type, "ARG")
        
        self.output.write("// end parameter list compilation\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""

        self.output.write("// start variable declaration compilation\n")
        self.tokenizer.advance() # var
        type = self.tokenizer.cur_token() 
        self.tokenizer.advance() # type
        name = self.tokenizer.cur_token() 
        self.tokenizer.advance() # varName
        self.symbol_table.define(name, type, "VAR")

        while self.tokenizer.cur_token() != ";":
            self.tokenizer.advance() # ,
            name = self.tokenizer.cur_token()
            self.tokenizer.advance() # varName
            self.symbol_table.define(name, type, "VAR")
        self.tokenizer.advance() # ;

        self.output.write("// end variable declaration compilation\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """

        self.output.write("// start statements compilation\n")

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
        
        self.output.write("// end statements compilation\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        
        self.output.write("// start do compilation\n")

        self.tokenizer.advance() # do
        self.compile_subroutine_call()
        self.vmwriter.write_pop("TEMP", 0) # we've got to return some value; store the dummy value at temp 0
        self.tokenizer.advance() # ;

        self.output.write("// end do compilation\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""

        self.output.write("// start let compilation\n")
        
        self.tokenizer.advance() # let
        name = self.tokenizer.cur_token()
        kind = self.symbol_table.kind_of(name)
        index = self.symbol_table.index_of(name)
        self.tokenizer.advance() # varName

        if self.tokenizer.cur_token() == "[": # array item assingment
            self.tokenizer.advance() # [
            self.compile_expression() # expression
            self.tokenizer.advance() # ]

            self.vmwriter.write_push(CONVERT_DICT[kind], index)
            self.vmwriter.write_arithmetic("ADD")
            self.vmwriter.write_pop("TEMP", 0)
        
            self.tokenizer.advance() # =
            self.compile_expression() # expression
            self.tokenizer.advance() # ;

            self.vmwriter.write_push("TEMP", 0)
            self.vmwriter.write_pop("POINTER", 1)
            self.vmwriter.write_pop("THAT", 0)

        else: # regular assignment
            self.tokenizer.advance() # =
            self.compile_expression() # expression
            self.tokenizer.advance() # ;
            self.vmwriter.write_pop(CONVERT_DICT[kind],index)

        self.output.write("// end let compilation\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output.write("// start while statement compilation\n")
    
        self.while_counter += 1 # we've entered a new while loop

        self.vmwriter.write_label(f"WHILE_START_{self.while_counter}") # insert "L1" - the starting while label, as Shimon showed in the lecture
        self.tokenizer.advance() # while
        self.tokenizer.advance() # (
        self.compile_expression()
        self.vmwriter.write_arithmetic("NOT") # negate the expression
        self.tokenizer.advance() # )
        self.tokenizer.advance() # {
        self.vmwriter.write_if(f"WHILE_END_{self.while_counter}") # if the negated expression is true - the expression is false, exit the loop
        self.compile_statements() # if the negated expression is false - the expression is true, compile the statements
        self.vmwriter.write_goto(f"WHILE_START_{self.while_counter}")
        self.vmwriter.write_label(f"WHILE_END_{self.while_counter}")
        self.tokenizer.advance() # }

        self.output.write("// end while statement compilation\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        
        self.output.write("// start return statement compilation\n")

        self.tokenizer.advance() # return
        if self.tokenizer.cur_token() != ";":
            while self.tokenizer.cur_token() != ";":
                self.compile_expression()
        else:
            self.vmwriter.write_push("CONST", 0) # there is no expression to return - return 0 as a dummy value
        self.tokenizer.advance() # ;
        self.vmwriter.write_return()

        self.output.write("// end return statement compilation\n")
        
    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # https://www.youtube.com/watch?v=N0BbhTk4Lu0&list=PLuHmgt1HXB7BEasFuIjh4mRKs8IDbjPE1&index=4 @ 5:14 - Shimon's lecture
        self.output.write("// start if statement compilation\n")

        self.if_counter += 1

        self.tokenizer.advance() # if
        self.tokenizer.advance() # (
        self.compile_expression() # expression
        self.tokenizer.advance() # )

        self.vmwriter.write_if(f"IF_TRUE_{self.if_counter}") # if-goto L1
        self.vmwriter.write_goto(f"IF_FALSE_{self.if_counter}") # goto L2
        self.vmwriter.write_label(f"IF_TRUE_{self.if_counter}")
        self.tokenizer.advance() # {
        self.compile_statements() # compiled statements1
        self.tokenizer.advance() # }

        if self.tokenizer.cur_token() == "else":
            self.vmwriter.write_goto(f"IF_END_{self.if_counter}") 
            self.vmwriter.write_label(f"IF_FALSE_{self.if_counter}")
            self.tokenizer.advance() # else
            self.tokenizer.advance() # {
            self.compile_statements()
            self.tokenizer.advance() # }
            self.vmwriter.write_label(f"IF_END_{self.if_counter}") # goto L2
        
        else:
            print(f"if_false_{self.if_counter}")
            self.vmwriter.write_label(f"IF_FALSE_{self.if_counter}")

        self.output.write("// end if statement compilation\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""

        self.output.write("// start expression compilation\n")

        self.compile_term() # term
        while self.tokenizer.cur_token() in ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']:
            cur_operator = self.tokenizer.cur_token()
            self.tokenizer.advance() # op
            self.compile_term() # term

            if cur_operator == "*": # multiplication is an os built-in function
                self.vmwriter.write_call("Math.multiply", 2)
            elif cur_operator == "/": # division is an os built-in function
                self.vmwriter.write_call("Math.divide", 2)
            else:
                self.vmwriter.write_arithmetic(ARITHMETIC_DICT[cur_operator])
            
        self.output.write("// end expression compilation\n")

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
        self.output.write("// start term compilation\n")

        if self.tokenizer.token_type() == "INT_CONST":
            self.vmwriter.write_push("CONST", self.tokenizer.cur_token())
            self.tokenizer.advance() # integerConstant

        elif self.tokenizer.cur_token() == "(":
            self.tokenizer.advance() # (
            self.compile_expression() # expression
            self.tokenizer.advance() # )
      
        elif self.tokenizer.cur_token() in UNARY_DICT:
            operator = self.tokenizer.cur_token()
            self.tokenizer.advance() # operator
            self.compile_expression()
            self.vmwriter.write_arithmetic(UNARY_DICT[operator])
        
        elif self.tokenizer.check_n_ahead(1) == "(" or self.tokenizer.check_n_ahead(1) == ".":
            self.compile_subroutine_call()

        elif self.tokenizer.token_type() == "STRING_CONST":
            str = self.tokenizer.cur_token()
            length = len(str)
            self.vmwriter.write_push("CONST", length)
            self.vmwriter.write_call("String.new", 1)
            for c in str: 
                self.vmwriter.write_push("CONST", ord(c)), self.vmwriter.write_call("String.appendChar", 2)
            self.tokenizer.advance() # stringConstant

        elif self.tokenizer.token_type() == "KEYWORD":
            keyword = self.tokenizer.cur_token()
            if keyword in ["true", "false", "null"]:
                self.vmwriter.write_push("CONST", 0)
                if keyword == "true":
                    self.vmwriter.write_arithmetic("NOT")
            else:
                self.vmwriter.write_push("POINTER", 0)
            self.tokenizer.advance() # keyword
        
        elif self.tokenizer.token_type() == "IDENTIFIER":
            identifier = self.tokenizer.cur_token()
            self.tokenizer.advance() # identifier
            if self.tokenizer.cur_token() == "[":
                self.tokenizer.advance() # [
                self.compile_expression() # expression
                self.tokenizer.advance() # ]
                arr_index, arr_kind = self.symbol_table.index_of(identifier), self.symbol_table.kind_of(identifier)
                self.vmwriter.write_push(CONVERT_DICT[arr_kind], arr_index)
                self.vmwriter.write_arithmetic("ADD")
                self.vmwriter.write_pop("POINTER", 1)
                self.vmwriter.write_push("THAT", 0)
 
            else:
                var_index, var_kind = self.symbol_table.index_of(identifier), CONVERT_DICT[self.symbol_table.kind_of(identifier)]
                self.vmwriter.write_push(var_kind, var_index)
  
        self.output.write("// end term compilation\n")


    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""

        self.output.write("// start expression list compilation\n")
        
        n_args = 0
        if self.tokenizer.cur_token() != ")":
            n_args += 1
            self.compile_expression()
            
        while self.tokenizer.cur_token() != ")":
            self.tokenizer.advance() # ,
            n_args += 1
            self.compile_expression()

        self.output.write("// end expression list compilation\n")
        return n_args
