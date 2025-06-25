from langchain_core.tools import tool
import math
import asyncio
import logging

@tool
async def add(x: float, y: float) -> float:
    """Add 'x' and 'y'."""
    return x + y

@tool
async def multiply(x: float, y: float) -> float:
    """Multiply 'x' and 'y'."""
    return x * y

@tool
async def exponentiate(x: float, y: float) -> float:
    """Raise 'x' to the power of 'y'."""
    return x ** y

@tool
async def subtract(x: float, y: float) -> float:
    """Subtract 'x' from 'y'."""
    return y - x

@tool
async def evaluate_expression(expr: str) -> float:
    """
    Given a user’s question containing a mathematical expression, pass the entire expression,
    exactly as written (including all parentheses and operators), to this tool.
    Do not remove or rearrange any part of the expression. For example,
    if the user asks what is (3 - 5) / 6 + 8, call this tool with expr="(3 - 5) / 6 + 8".
    """
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    allowed_names.update({"abs": abs, "round": round})

    def safe_eval():
        try:
            code = compile(expr, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    raise NameError(f"Use of '{name}' not allowed in math expressions.")
            result = eval(code, {"__builtins__": {}}, allowed_names)
            return float(result)
        except Exception as e:
            # Print for backend logs and return as string for LLM response
            logging.error(f"Error evaluating expression '{expr}': {e}")
            return f"Error: {e}"

    return await asyncio.get_event_loop().run_in_executor(None, safe_eval)
