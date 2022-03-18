# README

### How to run

The program accepts a path of a specific `.jack` file or a directory containing multiple `.jack` files. Pass the path to the program. There is no need to compile the python programs.

```
python src/main <path to a jack file or to a directory containing jack files>
```

The path could be either relative path or absolute path.

The program will produce `.vm` files in the same directory of the `.jack` files.

### Implementation

There are 5 python scripts under `src/`

- `main.py` - accepts the arguments, handling I/O and call tokenizer and code generator
- `references.py` - stores some constant elements for tokenizer and parser
- `tokenizer.py` - tokenizes the original `.jack` file
- `codegenerator.py` - based on the tokenization, generates the VM codes. This class is composed of a series of functions, each for compiling a segments of jack code. This is the most intricate part of this project, and please refer to the comments in each function
- `vmwriter.py` - generate different types of VM code, with meaning expressed by function names