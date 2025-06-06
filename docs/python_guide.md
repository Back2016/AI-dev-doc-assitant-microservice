# Python Basics Guide

Python is a high-level, interpreted programming language known for its clear syntax and readability.
It supports multiple programming paradigms, including procedural, object-oriented, and functional programming.

## Variables and Data Types

In Python, you can create a variable by simply assigning a value:

```python
x = 5          # integer
name = "Alice" # string
pi = 3.14159   # float
```

Common built-in data types include:
- **Integers** (`int`)
- **Floating-point numbers** (`float`)
- **Strings** (`str`)
- **Booleans** (`bool`)
- **Lists** (`list`)
- **Tuples** (`tuple`)
- **Dictionaries** (`dict`)
- **Sets** (`set`)

### Python Lists

A **list** is an ordered, mutable collection of items. You create a list using square brackets `[]`:

```python
fruits = ["apple", "banana", "cherry"]
print(fruits[1])  # Output: banana
fruits.append("date")
```

Lists can contain mixed types:

```python
mixed = [1, "two", 3.0, True]
```

You can slice, iterate, and perform common operations like `append`, `insert`, `remove`, `pop`, and more.

## Functions

Functions in Python are defined using the `def` keyword:

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))  # Output: Hello, Alice!
```

- **Parameters** are variables listed inside the parentheses.
- **Return values** are specified with the `return` statement.

You can also write **anonymous (lambda) functions**:

```python
add = lambda a, b: a + b
print(add(3, 5))  # Output: 8
```

## Control Flow

### If/Else

```python
x = 10
if x > 0:
    print("Positive")
elif x == 0:
    print("Zero")
else:
    print("Negative")
```

### For Loops

```python
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4
```

### While Loops

```python
count = 0
while count < 3:
    print(count)
    count += 1  # Prints 0, 1, 2
```

## Classes and Objects

Python is object-oriented. A simple class looks like:

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} says woof!"

my_dog = Dog("Rex")
print(my_dog.bark())  # Output: Rex says woof!
```

- `__init__` is the constructor that initializes instance attributes.
- Methods are functions defined inside a class (they automatically receive `self` as the first argument).

## Modules and Packages

You can group related code into modules (single `.py` files) and packages (directories with an `__init__.py`):

```python
# In file math_utils.py
def add(a, b):
    return a + b

# In another file
from math_utils import add
print(add(2, 3))  # Output: 5
```

To install third-party packages, use `pip`:

```bash
pip install requests
```

Then import in your code:

```python
import requests
response = requests.get("https://api.example.com")
print(response.status_code)
```

## File I/O

Reading from and writing to files is straightforward using Python’s built-in `open` function:

```python
# Write to a file
with open("example.txt", "w") as f:
    f.write("Hello, world!\n")

# Read from a file
with open("example.txt", "r") as f:
    content = f.read()
    print(content)  # Output: Hello, world!
```

Using `with` ensures the file is automatically closed when the block ends.

## List Comprehensions

Python supports concise list construction using list comprehensions:

```python
# Create a list of squares from 0 to 9
squares = [x**2 for x in range(10)]
print(squares)  # Output: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

You can also include conditional filtering:

```python
even_squares = [x**2 for x in range(10) if x % 2 == 0]
print(even_squares)  # Output: [0, 4, 16, 36, 64]
```

## Exception Handling

Handle errors using `try`/`except` blocks:

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
finally:
    print("This block always runs.")
```

- **`try`**: Code that might raise an exception.
- **`except`**: Catches and handles specific exceptions.
- **`finally`**: Runs whether or not an exception occurred.

## Working with JSON

Python’s `json` module makes it easy to work with JSON data:

```python
import json

data = {"name": "Alice", "age": 30, "city": "New York"}

# Convert to JSON string
json_str = json.dumps(data)
print(json_str)  # Output: {"name": "Alice", "age": 30, "city": "New York"}

# Parse JSON string back to Python dictionary
parsed = json.loads(json_str)
print(parsed["city"])  # Output: New York
```

# End of Python Basics Guide
