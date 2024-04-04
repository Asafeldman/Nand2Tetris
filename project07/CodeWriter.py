"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

SEGMENT_SYMBOL_DICT = {"local": "@LCL", "argument": "@ARG", "this": "@THIS", "that": "@THAT"}

class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output = output_stream
        self.counter = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.filename = filename
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.
        Args:
            command (str): an arithmetic command.
        """
        self.output.write("// " + command + "\n")
        if command == "add":
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("D=D+M\n")
            self.output.write("M=D\n")
            self.output.write("@SP\n")
            self.output.write("M=M-1\n")

        elif command == "sub":
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("M=M-D\n")
            self.output.write("@SP\n")
            self.output.write("M=M-1\n")

        elif command == "neg":
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=-M\n")

        
        elif command in ["eq", "gt", "lt"]:
            self.output.write("@SP\n")
            self.output.write("M=M-1\n")
            self.output.write("A=M\n")
            self.output.write("D=M\n")
            self.output.write("@R13\n")
            self.output.write("M=D\n")
            self.output.write("@Y_NEG_{}\n".format(self.counter)) # jump to Y_NEG_i if y is negative
            self.output.write("D;JLT\n")
            self.output.write("@SP\n") # else check if x is negative
            self.output.write("M=M-1\n")
            self.output.write("A=M\n")
            self.output.write("D=M\n")
            self.output.write("@Y_POS_X_NEG_{}\n".format(self.counter)) # jump to Y_POS_X_NEG_i if x is negative
            self.output.write("D;JLT\n")
            self.output.write("@R13\n")
            self.output.write("D=D-M\n") 
            self.output.write("@END_{}\n".format(self.counter)) # jump to END_i if both are positive
            self.output.write("0;JMP\n")
            self.output.write("(Y_NEG_{})\n".format(self.counter)) 
            self.output.write("@SP\n")
            self.output.write("M=M-1\n")
            self.output.write("A=M\n")
            self.output.write("D=M\n")
            self.output.write("@Y_NEG_X_POS_{}\n".format(self.counter)) # jump to Y_NEG_X_POS_i if x is positive
            self.output.write("D;JGT\n")
            self.output.write("@R13\n")
            self.output.write("D=D-M\n")
            self.output.write("@END_{}\n".format(self.counter))
            self.output.write("0;JMP\n")
            self.output.write("(Y_POS_X_NEG_{})\n".format(self.counter))
            self.output.write("D=-1\n")
            self.output.write("@END_{}\n".format(self.counter))
            self.output.write("0;JMP\n")
            self.output.write("(Y_NEG_X_POS_{})\n".format(self.counter))
            self.output.write("D=1\n")
            self.output.write("@END_{}\n".format(self.counter))
            self.output.write("0;JMP\n")
            self.output.write("(END_{})\n".format(self.counter))
            self.output.write("@TRUE_{}\n".format(self.counter))
            self.output.write("D;J{}\n".format(command.upper()))
            self.output.write("D=0\n")
            self.output.write("@FINALIZE_{}\n".format(self.counter))
            self.output.write("0;JMP\n")
            self.output.write("(TRUE_{})\n".format(self.counter))
            self.output.write("D=-1\n")
            self.output.write("@FINALIZE_{}\n".format(self.counter))
            self.output.write("0;JMP\n")
            self.output.write("(FINALIZE_{})\n".format(self.counter))
            self.output.write("@SP\n")
            self.output.write("A=M\n")
            self.output.write("M=D\n")
            self.output.write("@SP\n")
            self.output.write("M=M+1\n") 

        elif command == "and":
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("M=M&D\n")
            self.output.write("@SP\n")
            self.output.write("M=M-1\n")

        elif command == "or":
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("M=M|D\n")
            self.output.write("@SP\n")
            self.output.write("M=M-1\n")

        elif command == "not":
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=!M\n")

        elif command == "shiftright":
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=>>M\n")

        elif command == "shiftleft":
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=<<M\n")
        
        self.counter += 1         

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        self.output.write("// " + str(command.lower()[2:]) + " " + str(segment) + " " + str(index) + "\n")
        if command == "C_PUSH":
            if segment == "constant":
                self.output.write("@{}\n".format(index))
                self.output.write("D=A\n")
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")

            elif segment in SEGMENT_SYMBOL_DICT: # = {"local": "@LCL", "argument": "@ARG", "this": "@THIS", "that": "@THAT"}
                self.output.write("@{}\n".format(index))
                self.output.write("D=A\n")
                self.output.write("{}\n".format(SEGMENT_SYMBOL_DICT[segment]))
                self.output.write("A=D+M\n")
                self.output.write("D=M\n")
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")
            
            elif segment == "pointer":
                self.output.write("@THIS\n") # add 0 or 1 to @THIS
                self.output.write("D=A\n")
                self.output.write("@{}\n".format(index))
                self.output.write("D=D+A\n")
                self.output.write("A=D\n")
                self.output.write("D=M\n")
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")

            elif segment == "temp":
                self.output.write("@5\n")
                self.output.write("D=A\n")
                self.output.write("@{}\n".format(index))
                self.output.write("D=D+A\n")
                self.output.write("A=D\n")
                self.output.write("D=M\n")
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")

            elif segment == "static":
                self.output.write("@{Xxx}.{i}\n".format(Xxx=self.filename.split(".")[0], i=index))
                self.output.write("D=M\n")
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")

        elif command == "C_POP":
            if segment in SEGMENT_SYMBOL_DICT: # = {"local": "@LCL", "argument": "@ARG", "this": "@THIS", "that": "@THAT"}
                self.output.write("@{}\n".format(index))
                self.output.write("D=A\n")
                self.output.write("{}\n".format(SEGMENT_SYMBOL_DICT[segment]))
                self.output.write("D=D+M\n")
                self.output.write("@R13\n") # temporary register to store the address
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("D=M\n")
                self.output.write("@R13\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
            
            elif segment == "pointer":
                self.output.write("@THIS\n") # add 0 or 1 to @THIS
                self.output.write("D=A\n")
                self.output.write("@{}\n".format(index))
                self.output.write("D=D+A\n")
                self.output.write("@R13\n") # temporary register to store the address
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("D=M\n")
                self.output.write("@R13\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")

            elif segment == "temp":
                self.output.write("@5\n")
                self.output.write("D=A\n")
                self.output.write("@{}\n".format(index))
                self.output.write("D=D+A\n")
                self.output.write("@R13\n") # temporary register to store the address
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("D=M\n")
                self.output.write("@R13\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
            
            elif segment == "static":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("D=M\n")
                self.output.write("@{Xxx}.{i}\n".format(Xxx=self.filename.split(".")[0], i=index))
                self.output.write("M=D\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass

    def close_file(self) -> None:
        self.output.close()

# my_code_writer = CodeWriter("/Users/asaffeldman/Downloads/nand2tetris/projects/07/MemoryAccess/PointerTest/PointerTest.asm")
# print(my_code_writer.filename)
