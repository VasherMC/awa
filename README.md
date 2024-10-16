# AWA5.0 Interpreter

Interpreter for the AWA5.0 esolang, written in python. Comes with Awatism->Awa transpiler.
Also includes a cyclic tag implementation in AWA5.0, proving the language is Turing Complete.

See the [language specs](https://github.com/TempTempai/AWA5.0/blob/main/Documentation/AWA5.0%20Specification.pdf)
and reference implementation for AWA5.0 at [https://github.com/TempTempai/AWA5.0](https://github.com/TempTempai/AWA5.0)

### Implementation Differences

#### red
Due to taking input via STDIN/terminal, `red` operations will only read a single line (not including the terminating newline).
This means that a newline cannot be received as part of `red` input.

#### Undefined Behavior
Most cases of undefined behaviour involve operations accessing more bubbles from the ~~stack~~ abyss than are actually present.
The Javascript implementation at uses Javascript's default behaviour, usually resulting in `undefined` elements.
This implementation will instead usually do nothing, as if the instruction was a `nop`,
except in the following cases:
- `srn` of more bubbles than are present: only the bubbles present will be surrounded
- `cnt` when there are no bubbles: 0 will be blown (same as the Javascript implementation)
- `jmp` to an invalid label: an error is raised and the program terminates

## Usage

Run the included 'cat.awa' program:
```sh
python awa.py awa/cat.awa
```

Transpile the included `cyclic_tag.awatism` program to `cylic_tag.awa`:
```sh
python awatism.py <awa/cyclic_tag.awatism >awa/cyclic_tag.awa
```

Run the Collatz cyclic tag program, simulating a variant of the Collatz sequence
```sh
# full output:
python awa.py awa/cyclic_tag.awa <collatz.cyclic_tag
```
```sh
# only the lines corresponding to the collatz sequence:
python awa.py awa/cyclic_tag.awa <collatz.cyclic_tag   | split -n r/5/6 | egrep "^(100)+$"
```

## Awatism Transpiler Features

Awatism operations taking arguments should be concatenated with those arguments, not separated by spaces:
> `blo1 srn0 sbm1 jmpLABEL`
> instead of
> `blo 1 srn 0 sbm 1 jmp LABEL`

Labels are named instead of numbered, and written `LABEL:` with a following colon rather than using the `lbl N` op.

The transpiler implements the following syntactic sugar for the `blo` operation:
- Default: `blo1` blows the integer value 1 as usual
- Single Quote: `blo'1` blows the AWASCII encoding of '1' (ie, integer value 43)
- Double Quote: `blo"123"` blows the string "123", i.e. a double bubble containing AWASCII encoding of each character,
    with '1' at the top, such that `prn` will output the same string. Spaces and newlines must be escaped with `\s` and `\n`.

