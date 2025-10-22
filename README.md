# Simple Lexer and Parser for a Functional Language Subset

## Overview

This repository contains a simple **Lexer** and a **Parser** implemented in Python. These components are designed to process a string input written in a functional language subset that uses a Lisp-style prefix notation (e.g., `(OP arg1 arg2)`).

The **Lexer** (`Lexer` class) is responsible for taking the raw input string and converting it into a sequence of meaningful **Tokens**.
The **Parser** (`Parser` class) then takes these tokens and attempts to validate the syntax based on a defined grammar using a **Predictive Parsing** approach with an explicit parse table (Non-Terminal/Terminal pairs).

## Features

* **Tokenization:** Converts the input string into a list of `Token` objects.
* **Symbol Support:** Recognizes numbers, identifiers, and special unicode symbols for operators and keywords:
    * Addition: `+` ($\u002b$)
    * Subtraction: `−` ($\u2212$)
    * Multiplication: `×` ($\u00d7$)
    * Equality: `=` ($\u003d$)
    * Conditional (If-Else): `?` ($\u003f$)
    * Lambda Function: `λ` ($\u03bb$)
    * Local Variable Binding (Let): `≜` ($\u225c$)
    * Parentheses: `(` and `)`
* **Parsing:** Implements a top-down predictive parser that uses an explicit lookup **parse table** for syntax analysis.
* **Syntax Checking:** Reports parsing errors for incorrect syntax, unexpected tokens, and wrong number of arguments for operations.
* **Parse Tree Output:** Supports an optional mode (`parseTree=True`) to manually generate and print the resulting abstract syntax structure (in a list/nested list format) upon successful parsing.

---

## Language Grammar (Implied)

The parser is built to recognize expressions following this general structure (similar to Lisp or Scheme):

| Non-Terminal | Production Rules | Description |
| :--- | :--- | :--- |
| **`PROGRAM`** | $\rightarrow$ `EXPR` | A program is a single expression. |
| **`EXPR`** | $\rightarrow$ `NUMBER` | A numeric literal. |
| | $\rightarrow$ `IDENTIFIER` | A variable name. |
| | $\rightarrow$ `( PAREN_EXPR )` | A parenthesized expression (function call or special form). |
| **`PAREN_EXPR`**| $\rightarrow$ `OP EXPR EXPR` | Binary operations (`+`, `−`, `×`, `=`). |
| | $\rightarrow$ `? EXPR EXPR EXPR` | Conditional form. |
| | $\rightarrow$ `λ IDENTIFIER EXPR` | Lambda function definition. |
| | $\rightarrow$ `≜ IDENTIFIER EXPR EXPR` | Let binding. |
| | $\rightarrow$ `EXPR EXPR*` | Function application/call (function followed by arguments). |
| | $\rightarrow$ `EXPR*` | Zero or more expressions (for function applications). |

---

## Usage

### Prerequisites

You need **Python 3.x** to run this script.

### Running the Parser

The file contains a `main` function that prompts the user for input and attempts to parse it.

1.  Save the code as a Python file (e.g., `parser.py`).
2.  Run the script from your terminal:

```bash
python parser.py
