"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

C_ARITHMETIC = ["add", "sub", "neg", "and", "or", "not", "shiftleft", "shiftright", "eq", "gt", "lt"]

def remove_newline(list_strings: list[str]) -> list:
        """Removes newline characters from a list of strings"""
        no_newline = []
        for line in list_strings:
            if "\n" not in line:
                no_newline.append(line)
            else:
                line_fixed = line.replace("\n", "")
                no_newline.append(line_fixed)
        return no_newline

def remove_comments(list_strings: list[str]) -> list:
    no_comments = []
    for line in list_strings:
        if "/" not in line:
            no_comments.append(line)
        else:
            no_comments.append(line.split("/", 1)[0])
    return no_comments

def remove_empty_strings(list_strings: list[str]) -> list:
    return [line for line in list_strings if line != ""]

def fix_input(list_strings: list[str]) -> list:
    return remove_empty_strings(remove_comments((remove_newline(list_strings))))

class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = fix_input(input_file.read().splitlines())
        self.length = len(self.input_lines)
        self.index = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.index < self.length

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        command = self.input_lines[self.index].split(" ")[0]
        if command in C_ARITHMETIC:
            return "C_ARITHMETIC"
        elif command == "push":
            return "C_PUSH"
        elif command == "pop":
            return "C_POP"
        elif command == "label":
            return "C_LABEL"
        elif command == "goto":
            return "C_GOTO"
        elif command == "if-goto":
            return "C_IF"
        elif command == "function":
            return "C_FUNCTION"
        elif command == "call":
            return "C_CALL"
        return "C_RETURN"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == "C_ARITHMETIC":
            return self.input_lines[self.index].split(" ")[0]
        elif self.command_type() in ["C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION", "C_CALL"]:
            return self.input_lines[self.index].split(" ")[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        if self.command_type() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            return self.input_lines[self.index].split(" ")[2]