import sys

class CPU:

    def __init__(self):
        self.ram = [0]*256
        self.pc = 0
        self.register = [0]*8
        self.running = True
        self.register[7] = 0xf4
        self.sp = self.register[7]
        self.fl = 0b00000000
        self.branches = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b00000001: self.HLT,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE,
            0b10101000: self.AND,
            0b10101010: self.OR,
            0b10101011: self.XOR,
            0b01101001: self.NOT,
            0b10101100: self.SHL,
            0b10101101: self.SHR,
            0b10100100: self.MOD,
        }

    """ READ, WRITE, LOAD METHODS """

    def ram_read(self, address):
        # look in the RAM at the address passed through 
        return self.ram[address]

    def ram_write(self, value, address):
        # takes the address and updates the value at that address
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        address = 0
        filename = sys.argv[1]
        with open(filename) as f:
            for line in f:
                line = line.split('#')[0].strip()
                # new_line = line[0].strip()
                try:
                    v = int(line, 2)
                except ValueError:
                    continue
                # print(f"{v:08b}: {v:d}")
                self.ram[address] = v
                # print(address, v)
                address+=1
        # print(self.ram[:15])

    """ MAIN METHODS """

    def LDI(self):
        address = self.ram_read(self.pc+1)
        value = self.ram_read(self.pc+2)
        self.register[address] = value

    def PRN(self):
        address = self.ram_read(self.pc+1)
        value = self.register[address]
        print(value)

    def HLT(self):
        self.running = False

    def PUSH(self):
        self.sp -= 1
        address = self.ram[self.pc+1]
        value = self.register[address]
        self.ram[self.sp] = value

    def POP(self):
        address = self.ram[self.pc+1]
        value = self.ram[self.sp]
        self.register[address] = value
        self.sp += 1

    def CALL(self):
        self.sp-=1
        return_address = self.pc+2
        self.ram[self.sp] = return_address
        register_index = self.ram[self.pc+1]
        self.pc = self.register[register_index]

    def RET(self):
        return_address = self.ram[self.sp]
        self.pc = return_address
        self.sp+=1

    def JMP(self):
        register_address = self.ram_read(self.pc+1)
        jump_address = self.register[register_address]
        self.pc = jump_address
    
    def JEQ(self):
        register_address = self.ram_read(self.pc+1)
        address = self.register[register_address]
        if self.fl == 0b00000001:
            self.pc = address
        else:
            self.pc+=2

    def JNE(self):
        register_address = self.ram_read(self.pc+1)
        address = self.register[register_address]
        if self.fl != 0b00000001:
            self.pc = address
        else:
            self.pc+=2

    """ ALU METHODS """

    def ADD(self):
        num1 = self.ram_read(self.pc+1)
        num2 = self.ram_read(self.pc+2)
        self.alu('ADD', num1, num2)

    def AND(self):
        reg1 = self.ram_read(self.pc+1)
        reg2 = self.ram_read(self.pc+2)
        self.alu('AND', reg1, reg2)

    def CMP(self):
        reg1 = self.ram_read(self.pc+1)
        reg2 = self.ram_read(self.pc+2)
        self.alu('CMP', reg1, reg2)

    def MOD(self):
        reg1 = self.ram_read(self.pc+1)
        reg2 = self.ram_read(self.pc+2)
        self.alu('MOD', reg1, reg2)

    def MUL(self):
        num1 = self.ram_read(self.pc+1)
        num2 = self.ram_read(self.pc+2)
        self.alu('MUL', num1, num2)

    def NOT(self):
        reg1 = self.ram_read(self.pc+1)
        self.alu('NOT', reg1, None)

    def OR(self):
        reg1 = self.ram_read(self.pc+1)
        reg2 = self.ram_read(self.pc+2)
        self.alu('OR', reg1, reg2)

    def SHL(self):
        reg1 = self.ram_read(self.pc+1)
        reg2 = self.ram_read(self.pc+2)
        self.alu('SHL', reg1, reg2)

    def SHR(self):
        reg1 = self.ram_read(self.pc+1)
        reg2 = self.ram_read(self.pc+2)
        self.alu('SHR', reg1, reg2)

    def XOR(self):
        reg1 = self.ram_read(self.pc+1)
        reg2 = self.ram_read(self.pc+2)
        self.alu('XOR', reg1, reg2)

    """ ALU """

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == 'ADD':
            self.register[reg_a] += self.register[reg_b]
        elif op == 'AND':
            result = self.register[reg_a] & self.register[reg_b]
            self.register[reg_a] = result
        elif op == 'CMP':
            if self.register[reg_a] < self.register[reg_b]:
                self.fl = 0b00000100
            elif self.register[reg_a] > self.register[reg_b]:
                self.fl = 0b00000010
            elif self.register[reg_a] == self.register[reg_b]:
                self.fl = 0b00000001
        elif op == 'MOD':
            if self.register[reg_b] == 0:
                print(f"Can't divide by 0!")
                self.HLT()
            else:
                result = self.register[reg_a] % self.register[reg_b]
                self.register[reg_a] = result
        elif op == 'MUL':
            self.register[reg_a] *= self.register[reg_b]
        elif op == 'NOT':
            self.register[reg_a] = ~self.register[reg_a]
        elif op == 'OR':
            result = self.register[reg_a] | self.register[reg_b]
            self.register[reg_a] = result
        elif op == 'SHL':
            result = self.register[reg_a] << self.register[reg_b]
            self.register[reg_a] = result
        elif op == 'SHR':
            result = self.register[reg_a] >> self.register[reg_b]
            self.register[reg_a] = result
        elif op == 'SUB':
            self.register[reg_a] -= self.register[reg_b]
        elif op == 'XOR':
            result = self.register[reg_a] ^ self.register[reg_b]
            self.register[reg_a] = result
        else:
            raise Exception("Unsupported ALU operation")

    """ TRACE """

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    """RUN THE CPU"""

    def run(self):
        while self.running:

            IR = self.ram_read(self.pc)

            if IR in self.branches:
                self.branches[IR]()
                operands = (IR & 0b11000000) >> 6

                params = (IR & 0b00010000) >> 4

                if not params:
                    self.pc += operands + 1
            else:
                print(f'{IR} not found in self.branches. Try again!')
                sys.exit(1)