from enum import Enum
from functools import partial


class AddressType(Enum):
    """Address type used in the operation"""
    NONE = 0
    ADDRESS = 1
    IMMEDIATE = 2
    INDIRECT = 3

    def __str__(self) -> str:
        if self.value < 2:
            return ''
        elif self.value == 2:
            return '#'
        else:
            return '@'

    def __repr__(self) -> str:
        return self.__str__()


class Op(Enum):
    """Supported Three-Address Operations"""
    ADD = 0
    MULT = 1
    SUB = 2
    EQ = 3
    LT = 4
    ASSIGN = 5
    JPF = 6
    JP = 7
    PRINT = 8


class Address:
    """Helper class for addresses"""

    def __init__(self, type: AddressType, value: int = 0) -> None:
        self.value = value
        self.type = type

    def __str__(self) -> str:
        if self.type == AddressType.NONE:
            return str(self.type)
        return str(self.type) + str(self.value)

    def __repr__(self) -> str:
        return self.__str__()


class Instruction:
    """Helper class to save instructions"""

    def __init__(self, op: Op, a: Address, b: Address, c: Address) -> None:
        self.op = op
        self.a = a
        self.b = b
        self.c = c

    def __str__(self) -> str:
        return f'({self.op.name}, {self.a}, {self.b}, {self.c})'

    def __repr__(self) -> str:
        return self.__str__()


def generate_address(addr: str):
    """Create address object from strings like 500, @500 and #500"""
    if addr == None:
        return Address(AddressType.NONE)
    if addr[0] == '@':
        return Address(AddressType.INDIRECT, int(addr[1:]))
    elif addr[0] == '#':
        return Address(AddressType.IMMEDIATE, int(addr[1:]))
    else:
        return Address(AddressType.ADDRESS, int(addr))


def generate_instruction(op, a, b, c):
    return Instruction(op,
                       generate_address(a),
                       generate_address(b),
                       generate_address(c))


# Instruction functions
ADD = partial(generate_instruction, Op.ADD)
MUL = partial(generate_instruction, Op.MULT)
SUB = partial(generate_instruction, Op.SUB)
EQ = partial(generate_instruction, Op.EQ)
LT = partial(generate_instruction, Op.LT)
ASSIGN = partial(generate_instruction, Op.ASSIGN, c=None)
JPF = partial(generate_instruction, Op.JPF, c=None)
JP = partial(generate_instruction, Op.JP, b=None, c=None)
PRINT = partial(generate_instruction, Op.PRINT, b=None, c=None)

operation = {
    '+': ADD,
    '*': MUL,
    '-': SUB,
    '==': EQ,
    '<': LT
}
