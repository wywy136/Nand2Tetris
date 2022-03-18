# README

### How to run

There is no need to compile the python program.

```
python src/main <absolute path to the directory containing the vm files>
```

The program will generate a single file with same name of the directory postfixed by `.asm`.

### Important Notes

- The path passed to the program should be an **absolute** path;

- The path should stop at the directory level and should not indicate the specific `.vm` file, since there may be multiple `.vm` files to be handled. The program will detect all the `.vm` files under the directory and generate a unified `.asm` file under the same directory.

  For example, if the directory looks like

  ```
  --FunctionCalls
  	-- FibonacciElement
  		-- Main.vm
  		-- Sys.vm
  ```

  The command should be 

  ```
  python src/main /Users/.../FunctionCalls/FibonacciElement
  ```

  And you will find `FibonacciElement.asm` file under the directory after the program is run.

  ```
  -- FunctionCalls
  	-- FibonacciElement
  		-- Main.vm
  		-- Sys.vm
  		-- FibonacciElement.asm  <- Generated
  ```

  