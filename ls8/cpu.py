"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # Bytes of memory
        self.reg = [0] * 8 # Registers
        self.pc = 0 # Program Counter
        self.sp = self.reg[7] # Stack pointer.
        self.reg[7] = 0xF4
        self.running = True
        # self.HLT = '1'
        # self.LDI = '10000010'
        # self.PRN = '1000111'
        # self.MUL = '10100010'
        # self.PUSH = '01000101'
        # self.POP = '01000110'
        # self.ADD = '10100000'
        self.operand_a = 0
        self.operand_b = 0
        # self.CALL = '01010000'
        # self.RET = '00010001'

        self.branch_table = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100000: self.ADD,
        }

    def HLT(self):
        self.running = False
    
    def LDI(self):
        '''
        Set the value of a register to an integer.
        '''
        self.reg[self.operand_a] = self.operand_b
        self.pc += 3

    def PRN(self):
        '''
        Print numeric value stored in the given register.
        Print to the console the decimal integer value that is stored in the given
        register.
        '''
        print(self.reg[self.operand_a])
        self.pc += 2

    def MUL(self):
        '''
        Multiply the values in two registers together and store the result in registerA.
        '''
        self.alu("MUL", self.operand_a, self.operand_b)
        self.pc += 3

    def ADD(self):
        '''
        *This is an instruction handled by the ALU.*
        `ADD registerA registerB`
        Add the value in two registers and store the result in registerA.
        '''
        self.alu("ADD", self.operand_a, self.operand_b)
        self.pc += 3

    def PUSH(self):
        '''
        Push the value in the given register on the stack.
        1. Decrement the stack.
        2. Copy the value in the given register to the address pointed to by
        stack.
        '''
        self.sp -= 1  #decrement stack pointer

        # Push the value in the given register on the stack.
        # First operand is address of register holding value 
        value = self.reg[self.operand_a]
        # #put in memory
        self.ram[self.sp] = value
        self.pc += 2
       
    def POP(self):
        '''
        Pop the value at the top of the stack into the given register.
        1. Copy the value from the address pointed to by `SP` to the given register.
        2. Increment Stack.
        '''
        value = self.ram[self.sp]

        self.reg[self.operand_a] = value
        self.sp += 1
        self.pc += 2

    def RET(self):
        #pop from stack
        value = self.ram[self.sp]
        #set pc to value popped from the stack 
        self.sp += 1
        self.pc = value

    
    def CALL(self):
        # Get address to the instruction directly after CALL
        value = self.pc + 2

        # Push to stack #decrement the SP 
        self.sp -= 1
        self.ram[self.sp] = value
        
        # PC is set to the address stored in the given register
        self.pc = self.reg[self.operand_a]

    def load(self):
        """Load a program into memory."""

        address = 0

        #For now, we've just hardcoded a program:
        try: 
            with open(sys.argv[1]) as file: 
                for line in file: 
                    comment_split = line.split('#')

                    possible_num = comment_split[0]

                    if possible_num == '':
                        continue 
                    
                    if possible_num[0] == '1' or possible_num[0] == '0':
                        num = possible_num[:8]

                    #print(f'{num}: {int(num,2)}')

                    self.ram[address] = int(num, 2)
                    address += 1

        except FileNotFoundError: 
            print(f'{sys.argv[0]}: {sys.argv[1]} not found')
        
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")
    

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

    def ram_read(self, MAR):
        # MAR: Memory Address Register contains the address that is being read or written to
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        # MDR: Memory Data Register contains the data that was read or the data to write
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        # HLT = self.HLT
        # LDI = self.LDI
        # PRN = self.PRN
        # MUL = self.MUL

        self.running = True

        while self.running:
            #command = bin(self.ram_read(self.pc))[2:] 
            ir = self.ram[self.pc]
            self.operand_a = self.ram_read(self.pc + 1) 
            self.operand_b = self.ram_read(self.pc + 2) 
            
            #update program counter

            self.branch_table[ir]()
            
            # add_counter = (int(command, 2) >> 6) + 1
           
            # if command == LDI:
            #     self.reg[operand_a] = operand_b
            
            # elif command == MUL:
            #     self.alu("MUL", operand_a, operand_b)

            # elif command == PRN:
            #     print(self.reg[operand_a])

            # elif command == HLT:
            #     self.running = False

            # self.pc += add_counter  

   