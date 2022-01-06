---
title: Python Interpreter
category: python
---

## 1. Invoking the Interprer

The Python Interpreter is usually installed as `/usr/local/bin/python3.4` on those machines where it is available.
<!--more-->

Typing an end-of-file character (`C-d` on Unix, `C-z` on windows) at the primary prompt causes the interpreter to exit with a zero exit status. if thar doesn't work, you can exit the interpreter by typing the following command: `quit()`.

### 1.1 Argument Passing

Arguments will assigned to the `argv` variable in the `sys` modules. You can access arguments list by executing `import sys`. The length of the list is at least one. Here list some cases about this:

- no script and no arguments: sys.argv[0] is an empty string
- script name '-'(meaning standard input): sys.argv[0] is set to '-'
- `-c` command is used: sys.argv[0] is set to '-c'
- `-m` command is used: sys.argv[0] is set to full name of the loacated modules

### 1.2 Interactive Mode

## 2. The Interpreter and Its Environment

### 2.1 Error Handling

When an error occurs, the interpreter prints an error message and a stack trace. Exceptions handled by an except clause in a try statement are not errors in this context.

### 2.2 Excutable Python Scripts

On Unix like systems, Python script can be made derectly executable, like the shell script, by putting the line:

``` python
#! /usr/bin/env python3.4
```

The script can be a executable mode, or permission, using the **chmod** command:

``` bash
chmod +x myscript.py
```

### 2.3 Source Code Encoding

It is possible to specify a different encoding for source file. In order to do this, put one more special comment line right after the #! line to define the source file encoding：

``` python
# -*- coding: encoding -*-
```

### 2.4 The Interactive Startup File

You can do this by setting an variable named `PYTHONSTARTUP` to the name of a file containing your start-up command. This is similar to the .profile feature of the unix shells.

If you want to read an additional start-up file frome the current directory, you can program this in the global start-up file using code like this:

``` python
import os
filename = os.environ.get('PYTHONSTARTUP')
if filename and os.path.isfile(filename)
    exec(open(filename).read())
```

### 2.5 The Customization Modules

Python provides two hooks to let you customize it: sitecustomize and user customize. To see how it works, you need first to find the location of your site-packages directory. Start python and run this code:

``` python
>>> import site
>>> site.getusersitepackages()
```

sitecustomize works in the same way, but is typically created by an administrator of the computer in the global site-packages directory.
