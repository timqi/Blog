- tags: [python](/tags.md#python)
- date: 2014-08-28

# Python About Modules

## Excuting modules as scripts

```python
if __name__ == "__main__":

    import sys
        fib(int(sys.argv[1]))

```

If a module file contain the code above. The code that parses the command line only runs if the module is executed as the "main" file.

## The Module Search Path

When a module is imported, the interpreter first searches for a built-in module with that name. If not found, it then searches for a file named that in a list of directories given by the variable `sys.path`.

- The directory containg the input script (or the current directory when no file is specified).
- `PYTHONPATH` (a list of directory names, with the same syntax as the shell variable PATH).
- The installation-dependent default.

## "Compiled" Python files

To speed up loading modules, Python caches the compiled version of each module in the `__pycache__` directory under the name `module.version.pyc`, where the version encodes the format of the compiled file; it generally contains the Python version number. e.g.: in CPython release 3.3 the compiled version of `spam.py` would be cached as `__pycache__/spam.cpython-33.pyc`.

tips:

- You can use `-O` or `-OO` switches on the Python command to reduce the of a compiled module.
- A program doesn't run any faster when it is read from a .pyc or .pyo file than when if is read from a .py file; That's faster about .pyc or .pyo files is the speed with they are loaded.
- The module compileall can create .pyc files (or .pyo files when -O is used) for all modules in a directory.