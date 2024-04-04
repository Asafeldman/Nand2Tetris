"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

def get_binary(num: int) -> str:
    return format(num, 'b').zfill(16)

def pad_with_zeros(binary_num):
    if len(binary_num) < 15:
        more_zeros = 15 - len(binary_num)
        return "0" + ("0" * more_zeros) + binary_num

def translate_a_command(parser_obj: Parser, table_obj: SymbolTable) -> str:
    symbol = parser_obj.symbol()
    address = table_obj.get_address(symbol)
    return get_binary(int(address))

def translate_c_command(parser_obj: Parser, code: Code) -> str:
    return "111" + str(code.comp(parser_obj.comp())) + str(code.dest(parser_obj.dest())) + str(code.jump(parser_obj.jump()))

def translate_l_command(parser_obj: Parser, table_obj: SymbolTable) -> str:
    return translate_a_command(parser_obj, table_obj)

def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """

    # Initializing
    parser = Parser(input_file)
    table = SymbolTable()
    code = Code()

    # Add L command symbols to the table first
    i = 0
    while parser.has_more_commands():
        if parser.command_type() == "L_COMMAND":
            if i == 0:
                table.add_entry(parser.symbol(), i+1)
                i += 1
                parser.advance()
                continue
            table.add_entry(parser.symbol(), i)
            parser.advance()
            continue
        i += 1
        parser.advance()
        continue

    # Add A command symbols to the table and translate all lines
    i = 16
    parser.command_counter = 0
    parser.cur_com = parser.input_lines[0]

    while parser.has_more_commands():
        if parser.command_type() == "A_COMMAND":
            if parser.symbol().isnumeric():
                output_file.write(get_binary(int(parser.symbol())) + "\n")
                parser.advance()
                continue
            else:
                if not table.contains(parser.symbol()):
                    table.add_entry(parser.symbol(), i)
                    output_file.write(translate_a_command(parser, table) + "\n")
                    i += 1
                    parser.advance()
                    continue
                else:
                    output_file.write(translate_a_command(parser, table) + "\n")
                    parser.advance()
                    continue

        elif parser.command_type() == "C_COMMAND":
            output_file.write(translate_c_command(parser, code) + "\n")
            parser.advance()
            continue

        else:
            parser.advance()
            continue
    
    # We've completed the loop but still need to check the last command
    if parser.command_type() == "A_COMMAND":
        if parser.symbol().isnumeric():
            output_file.write(get_binary(int(parser.symbol())))
        else:

            if not table.contains(parser.symbol()):
                table.add_entry(parser.symbol(), i)
                output_file.write(translate_a_command(parser, table) + "\n")
            else:
                output_file.write(translate_a_command(parser, table) + "\n")
    else:
        if parser.command_type() == "C_COMMAND":
            output_file.write(translate_c_command(parser, code) + "\n")

    
if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)