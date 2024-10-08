#convert awatism to awatalk

import sys

inst = [
    'nop', 'prn', 'pr1', 'red', 'r3d',
    'blo', 'sbm', 'pop', 'dpl', 'srn',
    'mrg', '4dd', 'sub', 'mul', 'div', 'cnt',
    'lbl', 'jmp', 'eql', 'lss', 'gr8'
]
AWASCII = "AWawJELYHOSIUMjelyhosiumPCNTpcntBDFGRbdfgr0123456789 .,!'()~_/;\n"

def to_awawa(i, size=5):
    return f"{i:0{size}b}".replace('0',' awa').replace('1','wa')

def awatalk(op):
    res = to_awawa(op[0])
    if len(op)==2:
        if inst[op[0]]=='blo': #8bit
            res += to_awawa(op[1], 8)
        else: #5bit
            res += to_awawa(op[1], 5)
    return res


code = sys.stdin.read().split()

labels = {}

awa = []

#print(code)

for op in code:
    if op[-1]==':':
        lbl_idx = len(labels)
        labels[op[:-1]] = lbl_idx
        awa.append([inst.index('lbl'), lbl_idx])
    elif op.lower()=='trm':
        awa.append([0x1f])
    elif op.lower() in inst:
        awa.append([inst.index(op.lower())])
    elif op.lower()=='dup':
        awa.append([inst.index('dpl')])
    elif op.lower()=='add':
        awa.append([inst.index('4dd')])
    elif op[:3].lower() in ['blo','sbm','srn','jmp']:
        rest = op[3:].replace('\\s',' ').replace('\\n','\n')
        if len(rest)==0:
            raise ValueError(f"Instruction `{op}` missing argument."
            + " Make sure there is no whitespace, eg:"
            + "blo23  blo'A  blo\"Escaped\\sSpace\\n\"  sbm1  srn0  LBL:  jmpLBL")
        op = op[:3].lower()
        idx = inst.index(op)
        if op == 'jmp':
            awa.append([idx, rest]) #label name
        elif op=='blo' and rest[0]=="'":
            if len(rest)==1:
                awa.append([idx, AWASCII.index(' ')])
            elif rest[1] in AWASCII:
                awa.append([idx, AWASCII.index(rest[1])])
            else:
                raise ValueError(f"Invalid AWASCII for `blo'`: {rest[1]!r}")
        elif op=='blo' and rest[0]=='"':
            chars = rest[1:rest.find('"',1)]
            added = 0
            merges = 0
            for char in chars[::-1]:
                if char in AWASCII:
                    if added == 31: # max arg for single SRN
                        awa.append([inst.index('srn'), added])
                        added = 0
                        merges += 1
                    awa.append([idx, AWASCII.index(char)])
                    added += 1
                else:
                    raise ValueError(f"Invalid AWASCII for `blo\"`: {char!r}")
            awa.append([inst.index('srn'), added])
            # we may have multiple dbl-bubbles due to u5-bit SRN arg limit
            awa.extend([[inst.index('mrg')]]*merges)
        else:
            if rest.isdecimal():
                awa.append([idx, int(rest,10)])
            else:
                raise ValueError(f"Invalid number for `{op}`: {rest!r}")
    else:
        pass  # not an AWAtism - comment/ignore

#print(awa)

for i,op in enumerate(awa):
    if len(op)==2 and op[0]==inst.index('jmp'):
        if op[1] in labels:
            op[1] = labels[op[1]]
        else:
            raise ValueError(f"invalid jmp target {op[1]} at instruction #{i}")

print('awa')

for op in awa:
    print(awatalk(op))

