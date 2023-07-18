- tags: [python](/tags.md#python)
- date: 2014-08-25

# An Informal Introduction to Python

## Using Python as a Calculator

Division (/) always returns a float. To do division and get an integer result (discarding any fractional result) you can use `//` operator; To calculate the remainder you can use %:

```python
>>> 17 / 3  # classic division returns a float
5.666666666666667
>>>
>>> 17 // 3  # floor division discards the fractional part
5
>>> 17 % 3  # the % operator returns the remainder of the division
2
>>> 5 * 3 + 2  # result * divisor + remainder
17

```

With Python, it is possible to use the `**` operator to calculate powers:

```python
>>> 5 ** 2  # 5 squared
25
>>> 2 ** 7  # 2 to the power of 7
128

```

## Strings

Strings can be enclosed in single quotes ('...') or double quotes ("...") with the same result. `\\` can be used to escape quotes.

f you don’t want characters prefaced by \ to be interpreted as special characters, you can use raw strings by adding an `r` before the first quote:

```python
>>> print('C:\some\name')  # here \n means newline!
C:\some
ame
>>> print(r'C:\some\name')  # note the r before the quote
C:\some\name

```

Strings can be concatenated (glued together) with the `+` operator, and repeated with `*`:

```python
>>> # 3 times 'un', followed by 'ium'
>>> 3 * 'un' + 'ium'
'unununium'

```

Strings can be indexed (subscripted), with the first character having index 0. There is no seprate character type; a character is simply a string of size one:

```python
>>> word = 'Python'
>>> word[0]  # character in position 0
'P'
>>> word[5]  # character in position 5
'n'
>>> word[-1]  # last character
'n'
>>> word[-2]  # second-last character
'o'
>>> word[-6]
'P'
>>> word[0:2]  # characters from position 0 (included) to 2 (excluded)
'Py'
>>> word[2:5]  # characters from position 2 (included) to 5 (excluded)
'tho'
>>> word[:2] + word[2:]
'Python'
>>> word[:4] + word[4:]
'Python'
>>> word[:2]  # character from the beginning to position 2 (excluded)
'Py'
>>> word[4:]  # characters from position 4 (included) to the end
'on'
>>> word[-2:] # characters from the second-last (included) to the end
'on'

```

## Lists

Lists might contain items of different types, but usually the items all have the same type.

```python
>>> squares = [1, 4, 9, 16, 25]
>>> squares
[1, 4, 9, 16, 25]

```

Like strings (and all other built-in sequence type), lists can be indexed and sliced:

```python
>>> squares[0]  # indexing returns the item
1
>>> squares[-1]
25
>>> squares[-3:]  # slicing returns a new list
[9, 16, 25]

```