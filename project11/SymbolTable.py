"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.cur_scope = "CLASS" # we start at the class scope - this will be changed to "SUBROUTINE" if we are in a subroutine
        self.class_symbol_table = {} # {name: [type, kind, count]}
        self.subroutine_symbol_table = {} # {name: [type, kind, count]}
        self.counter_dict = {"STATIC": 0, "FIELD": 0,  # class scope
                            "ARG": 0, "VAR": 0} # subroutine scope

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.cur_scope = "SUBROUTINE" # if we start a new subroutine, we are in the subroutine scope 
        self.subroutine_symbol_table = {}
        self.counter_dict["ARG"] = 0
        self.counter_dict["VAR"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in ["STATIC", "FIELD"]: # class scope
            self.class_symbol_table[name] = [type, kind, self.counter_dict[kind]]
            self.counter_dict[kind] += 1
        else: # subroutine scope
            self.subroutine_symbol_table[name] = [type, kind, self.counter_dict[kind]]
            self.counter_dict[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.counter_dict[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if self.cur_scope == "CLASS":
            if name in self.class_symbol_table:
                return self.class_symbol_table[name][1]
        elif self.cur_scope == "SUBROUTINE":
            if name in self.subroutine_symbol_table:
                return self.subroutine_symbol_table[name][1]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if self.cur_scope == "CLASS":
            if name in self.class_symbol_table:
                return self.class_symbol_table[name][0]
        elif self.cur_scope == "SUBROUTINE":
            if name in self.subroutine_symbol_table:
                return self.subroutine_symbol_table[name][0]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if self.cur_scope == "CLASS":
            if name in self.class_symbol_table:
                return self.class_symbol_table[name][2]
        elif self.cur_scope == "SUBROUTINE":
            if name in self.subroutine_symbol_table:
                return self.subroutine_symbol_table[name][2]
