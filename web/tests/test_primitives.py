import ast
import inspect
import pytest
from app.engine import primitives

def test_ast_prohibitions():
    """Verify that neither % nor / appear in primitives.py."""
    source = inspect.getsource(primitives)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            assert not isinstance(node.op, ast.Mod), "Prohibited Modulo (%) operator found!"
            assert not isinstance(node.op, ast.Div), "Prohibited Division (/) operator found!"
            assert not isinstance(node.op, ast.FloorDiv), "Prohibited Floor Division (//) operator found!"

def test_string_add_arbitrary():
    assert primitives.string_add_arbitrary("0", "0") == "0"
    assert primitives.string_add_arbitrary("5", "7") == "12"
    assert primitives.string_add_arbitrary("99", "1") == "100"
    assert primitives.string_add_arbitrary("999999999999", "1") == "1000000000000"
    assert primitives.string_add_arbitrary("12345678901234567890", "98765432109876543210") == "111111111011111111100"

def test_recursive_digital_root_reduction():
    root, trace = primitives.recursive_digital_root_reduction("15")
    assert root == "6"
    
    root, trace = primitives.recursive_digital_root_reduction("30")
    assert root == "3"

    root, trace = primitives.recursive_digital_root_reduction("99")
    assert root == "9"

    # Large number: 1000 -> root 1
    root, trace = primitives.recursive_digital_root_reduction("1000")
    assert root == "1"

def test_fizz_buzz_invariants():
    # 15 -> FizzBuzz
    f_ok, b_ok, root, glyph, _ = primitives.verify_fizz_buzz_invariants("15")
    assert f_ok and b_ok
    assert glyph == "5"

    # 3 -> Fizz
    f_ok, b_ok, root, glyph, _ = primitives.verify_fizz_buzz_invariants("3")
    assert f_ok and not b_ok

    # 5 -> Buzz
    f_ok, b_ok, root, glyph, _ = primitives.verify_fizz_buzz_invariants("5")
    assert not f_ok and b_ok

    # 7 -> Raw
    f_ok, b_ok, root, glyph, _ = primitives.verify_fizz_buzz_invariants("7")
    assert not f_ok and not b_ok
