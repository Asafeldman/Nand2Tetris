"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

KEYWORDS = ['class', 'constructor', 'function', 'method', 'field',
               'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
               'false', 'null', 'this', 'let', 'do', 'if', 'else',
               'while', 'return']

KEYWORDS_DICT = {k: k.upper() for k in KEYWORDS}

SYMBOLS = ['{',  '}',  '(',  ')',  '[',  ']',  '.',  ',',  ';',  '+',  
              '-',  '*',  '/',  '&',  '|',  '<',  '>',  '=',  '~',  '^',  '#']

SYMBOLS_DICT = {symbol: '&lt;' if symbol == '<' 
                else '&gt;' if symbol == '>' 
                else '&amp;' if symbol == '&' 
                else symbol for symbol in SYMBOLS}


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_lines = input_stream.read().splitlines()
        self.tokens = self.fix_entire_input()
        self.cur_index = 0

    def remove_comments(self, line):
        """
        Removes comments from a single Jack code line. 
        This code handles all kinds of comments, and correctly handles strings as well. 
        This means that a comment symbol within a string will not be mistakenly interpreted as a string. 
        """
        fixed_line = ""
        inside_string = False 
        inside_comment = False
        multi_line_comment = False 

        for i, char in enumerate(line):
            if inside_string: # if we are inside a string, append the character and continue
                fixed_line += char
                if char == '"' or char == "'":
                    inside_string = False
                continue
            if inside_comment: # if we are inside a comment, we should not append the character, but we need to check if the comment ended
                if multi_line_comment:
                    if char == '/' and line[i - 1] == '*':
                        inside_comment = False
                        multi_line_comment = False
                else:
                    if char == '\n':
                        inside_comment = False
                continue
            if char == '"' or char == '"': # if we find a string starting sequence, set the inside_string flag
                inside_string = True
                fixed_line += char
                continue
            
            if char == '/' and i+1 < len(line) and line[i + 1] == '/': # if we find a single-line comment starting sequence, set the inside_comment flag
                inside_comment = True
                continue
            
            if char == '/' and i+1 < len(line) and line[i + 1] == '*': # if we find a multi-line comment starting sequence, set the inside_comment and multi_line_comment flags
                inside_comment = True
                multi_line_comment = True
                continue
            
            fixed_line += char # if none of the above conditions are met, append the character to the fixed_line string

        if fixed_line.lstrip() and fixed_line.lstrip()[0] == "*": # finally, removes sub comments within a multiline comment (as seen in SquareGame.jack)
            fixed_line = ""

        return fixed_line

    def tokenize_corrected_lines(self, corrected_lines):
        """
        Gets a list of corrected lines (a Jack code line that contains no comments, empty strings, tabs or double spaces) and returns
        this list split into single tokens.
        Should only be used for this specific case.
        """
        tokens = []
        for line in corrected_lines:
            current_word = "" 
            inside_string = False
            inside_symbol = False

            for i, char in enumerate(line):
                if inside_string: # if we're inside a string, add the current character to the word
                    current_word += char
                    if char == inside_string and line[i-1] != '//': # if the character is the same as the string delimiter and is not preceded by a backslash, do:
                        inside_string = False # set the flag to false
                        tokens.append(current_word) # add the current word to the list
                        current_word = "" # restart the current word
                    continue

                if inside_symbol: # if this is a symbol, add the current character to the word
                    current_word += char 
                    if char not in SYMBOLS: # if the char is not a symbol, do the same process as above
                        inside_symbol = False 
                        tokens.append(current_word)
                        current_word = ""
                    continue

                if char in ['\'', '"', "'"]:
                    current_word += char
                    inside_string = char
                    continue

                if char in SYMBOLS: 
                    if current_word:
                        tokens.append(current_word)
                        current_word = ""
                    tokens.append(char)
                    continue

                if char.isspace(): 
                    if current_word:
                        tokens.append(current_word)
                        current_word = ""
                    continue

                current_word += char

            if current_word:
                tokens.append(current_word)
                
        return tokens

    def fix_entire_input(self) -> list:
        """
        Removes comments, whitespace and empty strings from input_lines and returns a fixed list.
        """
        no_comments = [self.remove_comments(line) for line in self.input_lines] # removes comments from all lines
        no_empty = [line for line in no_comments if (line != "" or line != '')] # removes empty strings from all lines
        no_tabs = [line.replace("\t", "") for line in no_empty] # removes tabs from all lines
        no_double_spaces = [re.sub(' {2,}', ' ', line) for line in no_tabs] # removes double spaces from all lines
        return self.tokenize_corrected_lines(no_double_spaces) # splits the list without comments, empty strings, tabs and double spaces to single strings instead of lines

    def cur_token(self):
        """
        Returns the current token.
        """
        if self.token_type() == "KEYWORD":
            return self.keyword().lower()
        elif self.token_type() == "SYMBOL":
            return self.symbol()
        elif self.token_type() == "IDENTIFIER":
            return self.identifier()
        elif self.token_type() == "INT_CONST":
            return self.int_val()
        else:
            return self.tokens[self.cur_index]
        
    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.cur_index < len(self.tokens)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.cur_index += 1
    
    def check_n_ahead(self, n):
        """Returns the n'th next token if it exists. Note that the Jack language will only require L1 (1 look ahead).
        """
        i = 0
        for _ in range(n):
            if self.has_more_tokens():
                i += 1
                self.advance()
        n_token = self.cur_token()
        self.cur_index = self.cur_index - i
        return n_token

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        token = self.tokens[self.cur_index]
        if token in KEYWORDS:
            return "KEYWORD"
        elif token in SYMBOLS:
            return "SYMBOL"
        elif token.isnumeric() and 0 <= int(token) <= 32767:
            return "INT_CONST"
        elif len(token) and token[0] == '"':
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return KEYWORDS_DICT[self.tokens[self.cur_index]]
        

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return SYMBOLS_DICT[self.tokens[self.cur_index]]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.tokens[self.cur_index]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.tokens[self.cur_index])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.tokens[self.cur_index][1:-1]