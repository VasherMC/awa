
"""
AWA5.0 Interpreter
Usage:
    python awa.py file.awa

For a description of the AWA5.0 language, see:
https://github.com/TempTempai/AWA5.0

Intended to be compatible with TempTempai's (javascript) interpreter
at https://temptempai.github.io/AWA5.0/
"""

from copy import deepcopy
import operator

orig_print = print
def print(*args,**kwargs):
    """workaround for https://github.com/python/cpython/issues/79935"""
    try:
        orig_print(*args,**kwargs)
    except (OSError, BrokenPipeError):
        sys.stderr.close()
        sys.exit()

"""See table of opcodes below"""
Opcode = int
Instruction = list[Opcode, int]
AwaProgram = list[Instruction]

ALL_OPS = (
 NOP, PRN, PR1, RED, R3D, BLO, SBM, POP,
 DPL, SRN, MRG, ADD, SUB, MUL, DIV, CNT,
 LBL, JMP, EQL, LSS, GR8) = range(0x15)
TRM = 0x1F
ALL_OPS = (*ALL_OPS, TRM)

def parse(txt: str) -> AwaProgram:
    """
    Parse .awa text into instructions.
    Each `awa` or `wa` corresponds to a 0/1 bit.
    Instructions are 5 bits and arguments are 5 bits (except BLO).
    """
    instrs = []
    txt = txt.lower()
    # All programs begin with initial 'awa'
    i = txt.find('awa') + 3
    cur = sz = 0
    ins = []
    while i<len(txt):
        #parse bit
        if txt[i:i+3]=="awa": #don't require the space before (' awa')
            cur <<= 1
            sz += 1
            i += 3
        elif txt[i:i+2]=="wa":
            cur = (cur<<1)|1
            sz += 1
            i+=2
        else:
            i+=1
        #check if we have a complete instruction
        if BLO in ins:
            if sz==8:  # blo takes an i8 argument
                ins.append(cur)
                cur = sz = 0
                instrs.append(ins)
                ins = []
        elif sz==5:
            if len(ins)==0 and cur not in ALL_OPS:
                print(f"WARNING: Invalid opcode 0x{cur:02x} ending at position {i}")
            ins.append(cur)
            cur = sz = 0
            if len(ins)==2 or ins[0] not in [JMP,LBL,BLO,SRN,SBM]:
                instrs.append(ins)
                ins = []
    if sz!=0:
        print("WARNING: partial instruction at end")
    return instrs

AWASCII = "AWawJELYHOSIUMjelyhosiumPCNTpcntBDFGRbdfgr0123456789 .,!'()~_/;\n"
AWATISM = {i:s for i,s in enumerate([
    'nop', 'prn', 'pr1', 'red', 'r3d',
    'blo', 'sbm', 'pop', 'dpl', 'srn',
    'mrg', '4dd', 'sub', 'mul', 'div', 'cnt',
    'lbl', 'jmp', 'eql', 'lss', 'gr8'
])} | {0x1f:'trm'}

def awatism_ins(ins: Instruction) -> str:
    return AWATISM.get(ins[0],'INVALID') + (f" {ins[1]:>3d}"if len(ins)==2 else "    ")
def awatism(code: AwaProgram) -> str:
    """Convert program to more readable, assembly-like "awatism" representation"""
    return "\n".join(map(awatism_ins, code))

# Begin interpreter implementation
op_table = {
        EQL: operator.eq,
        LSS: operator.lt,
        GR8: operator.gt,
        ADD: operator.add,
        SUB: operator.sub,
        MUL: operator.mul,
        DIV: lambda a,b: list(divmod(a,b)),
}
#recursive
def binary_op(inst, top, nx):
    if type(top) is type(nx) is int:
        return op_table[inst](top, nx)
    if type(top) is int:
        top = [top]*len(nx)
    if type(nx) is int:
        nx = [nx]*len(top)
    return [binary_op(inst, a,b) for a,b in zip(top,nx)]

#recursive
def str_PR(val, inst):
    return ((str(val)if inst==PR1 else AWASCII[val&0x3f])if type(val) is int
    else (' '*(inst==PR1)).join(str_PR(v,inst)for v in val[::-1]))

def do_PR(inst, val):
    """run PRN or PR1 instruction (output)"""
    print(str_PR(val,inst),end='')

def do_RD(inst):
    """Read input. Note only one line can be input at a time,
    and the trailing newline is not included."""
    x = input('>')
    if inst==RED:
        return [AWASCII.find(c)for c in x if c in AWASCII][::-1]
    else:
        return int(x.replace('~','-'),10)

def run(instrs: AwaProgram, dbg=0):
    ip = 0
    timestep = 0
    abyss = []
    label_table = {inst[1]:i for i,inst in enumerate(instrs) if inst[0]==LBL}
    running = True
    while running and ip<len(instrs):
        timestep+=1
        if dbg:
            print(f"{ip:>4d}", awatism_ins(instrs[ip]),"  ", str(abyss).replace(' ',''))
            if timestep%100==0:
                if input("continue? ").lower()[:1] in ["n","q"]:
                    running = False
        inst: Opcode = instrs[ip][0]
        arg = instrs[ip][1] if len(instrs[ip])>1 else None
        # LBL, NOP: ignore
        if inst in (PRN, PR1): # ------------- I/O
            if len(abyss)>0:
                do_PR(inst, abyss.pop())
            else:
                "Undefined behaviour"
        elif inst in (RED, R3D):
            abyss.append(do_RD(inst))
        elif inst == DPL: # --------------- STACK MANIP
            if len(abyss)>0:
                abyss.append(deepcopy(abyss[-1]))
            else:
                "Undefined behavior"
                pass
        elif inst == BLO:
            abyss.append(arg)
        elif inst == SBM:
            if len(abyss)>1:
                if arg==0:
                    abyss.insert(0, abyss.pop())
                else:
                    abyss.insert(-arg, abyss.pop())
            else:
                "Undefined behaviour (nothing to submerge)"
                pass
        elif inst == POP:
            if len(abyss)>0:
                top = abyss.pop()
                if isinstance(top, list):
                    abyss.extend(top)
            else:
                "Undefined behaviour (nothing to pop)"
                pass
        elif inst == SRN:
            if arg==0:
                abyss.append([])
            else:
                if arg > len(abyss):
                    "Undefined behaviour (ignore)"
                abyss = abyss[:-arg] + [abyss[-arg:]]
        elif inst == MRG:
            if len(abyss)>1:
                top = abyss.pop()
                if type(top) is type(abyss[-1]):
                    abyss[-1] = abyss[-1] + top
                elif type(top) is int:
                    abyss[-1].append(top)
                else:
                    top.insert(0,abyss.pop())
                    abyss.append(top)
            else:
                "Undefined behaviour"
                pass
        elif inst == CNT: # ----------------- ARITH
            if len(abyss)>0:
                abyss.append(len(abyss[-1]) if isinstance(abyss[-1], list) else 0)
            else:
                "Undefined behaviour (?)"
                "push 0 for conformance w/ javascript version"
                abyss.append(0)
        elif inst in (ADD, SUB, MUL, DIV):
            if len(abyss) >= 2:
                top, nx = abyss.pop(), abyss.pop()
                abyss.append(binary_op(inst, top, nx))
            else:
                "Undefined behaviour"
                pass
        elif inst == JMP: #------------CONTROL FLOW
            if arg in label_table:
                ip = label_table[arg] - 1
            else:
                print(f"ERROR: invalid jump target {arg}")
                running = False
        elif inst in (EQL, LSS, GR8):
            if len(abyss) >= 2:
                b, top = abyss[-2:]
                #if not op_table[inst](top, b):
                if not (top==b if inst==EQL else top<b if inst==LSS else top>b):
                    ip += 1 #skip if false
            else:
                "Undefined behaviour"
                pass
        elif inst == TRM:
            running = False
        ip += 1

debug = 0
if __name__ == "__main__":
    import sys
    if len(sys.argv)>1:
        fname = sys.argv[1]
        with open(fname) as f:
            r = f.read()
        code: AwaProgram = parse(r)
        if debug:
            print(awatism(code))
            input("press enter to run...")
        run(code, debug)


