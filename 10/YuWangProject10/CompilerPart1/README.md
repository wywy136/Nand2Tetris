# README

### How to run

The program accepts a path of a specific `.jack` file or a directory containing multiple `.jack` files. Pass the path to the program. There is no need to compile the python programs.

```
python src/main <path to a jack file or to a directory containing jack files>
```

The path could be either relative path or absolute path.

The program will produce 2 `.xml` files in the same directory of the `.jack` files.

- One is **tokenization** result, named `<filename>T.xml`
- One is **parsing** result, named `<filename>.xml`

### Implementation

There are 4 python scripts under `src/`

- `main.py` - accepts the arguments, handling I/O and call tokenizer and parser
- `references.py` - stores some constant elements for tokenizer and parser
- `tokenizer.py` - tokenizes the original `.jack` file and output a `...T.xml` file
- `parser.py` - based on the tokenization, generates parsed XML file by calling subroutines recursively. This is most complex part for this project and please refer to comments in this script.