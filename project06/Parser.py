"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

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
            
def remove_whitespace(list_strings: list[str]) -> list:
    no_whitespace = []
    for line in list_strings:
        no_whitespace.append(line.replace(" ", ""))
    return no_whitespace

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
    return remove_empty_strings(remove_comments(remove_whitespace(remove_newline(list_strings))))

class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """
    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = fix_input(input_file.read().splitlines())
        self.num_commands = len(self.input_lines)
        self.command_counter = 0
        self.cur_com = self.input_lines[self.command_counter]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.command_counter < self.num_commands-1

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.command_counter += 1
            self.cur_com = self.input_lines[self.command_counter]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if "@" in self.cur_com:
            return "A_COMMAND"
        elif "(" in self.cur_com:
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == "A_COMMAND":
            return self.cur_com[1:]
        elif self.command_type() == "L_COMMAND":
            return self.cur_com[1:len(self.cur_com)-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == "C_COMMAND":
            if "=" in self.cur_com:
                eq_i = self.cur_com.find("=")
                return self.cur_com[:eq_i]
            return ""

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == "C_COMMAND":
            if "=" in self.cur_com and not ";" in self.cur_com:
                after_eq_i = self.cur_com.find("=")+1
                return self.cur_com[after_eq_i:]
            elif ";" in self.cur_com and not "=" in self.cur_com:
                jump_i = self.cur_com.find(";")
                return self.cur_com[:jump_i]
            elif "=" in self.cur_com and ";" in self.cur_com:
                after_eq_i = self.cur_com.find("=")+1
                jump_i = self.cur_com.find(";")
                return self.cur_com[after_eq_i:jump_i]
        
    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == "C_COMMAND":
            if ";" in self.cur_com:
                after_jump_i = self.cur_com.find(";") + 1
                return self.cur_com[after_jump_i:]
            return ""
