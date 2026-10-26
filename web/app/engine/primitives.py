"""
Zero-Trust Byzantine Consensus Primitives
Strict Zero-Modulo / Zero-Division Invariants Enforced
"""
from typing import Dict, List, Tuple

# Decimal digit to Peano tally representation
DIGIT_TO_TALLY: Dict[str, str] = {
    "0": "",
    "1": "|",
    "2": "||",
    "3": "|||",
    "4": "||||",
    "5": "|||||",
    "6": "||||||",
    "7": "|||||||",
    "8": "||||||||",
    "9": "|||||||||",
}

TALLY_TO_DIGIT: Dict[str, str] = {v: k for k, v in DIGIT_TO_TALLY.items()}

# Construct single-digit addition table using tally concatenation
STRING_ADD_TABLE: Dict[Tuple[str, str], str] = {}
for d1, t1 in DIGIT_TO_TALLY.items():
    for d2, t2 in DIGIT_TO_TALLY.items():
        combined = t1 + t2
        tens = ""
        while len(combined) >= 10:
            tens = tens + "|"
            combined = combined[10:]
        units_digit = TALLY_TO_DIGIT[combined]
        tens_digit = TALLY_TO_DIGIT[tens] if tens else ""
        STRING_ADD_TABLE[(d1, d2)] = tens_digit + units_digit

def string_add_two_digits(a: str, b: str) -> str:
    """Adds two single-digit decimal strings using pure lookup."""
    return STRING_ADD_TABLE[(a, b)]

def string_add_arbitrary(a: str, b: str) -> str:
    """
    Adds two arbitrary-length decimal strings using Peano table lookups with carry.
    Strictly zero modulo and zero division.
    """
    i = len(a) - 1
    j = len(b) - 1
    carry = "0"
    result = []

    while i >= 0 or j >= 0 or carry != "0":
        da = a[i] if i >= 0 else "0"
        db = b[j] if j >= 0 else "0"

        # Step 1: da + db
        sum1 = STRING_ADD_TABLE[(da, db)]
        
        # Step 2: Add carry
        if len(sum1) == 1:
            total = STRING_ADD_TABLE[(sum1, carry)]
        else:
            units = STRING_ADD_TABLE[(sum1[1], carry)]
            tens = sum1[0] if len(units) == 1 else STRING_ADD_TABLE[(sum1[0], units[0])]
            total = tens + (units if len(units) == 1 else units[1])

        if len(total) == 1:
            result.append(total)
            carry = "0"
        else:
            result.append(total[1])
            carry = total[0]

        i -= 1
        j -= 1

    rev = "".join(reversed(result))
    return rev.lstrip("0") or "0"

def string_sum_digits(payload: str) -> Tuple[str, List[str]]:
    """
    Sums digits of an arbitrary-length decimal string using pure string addition.
    Returns (sum_string, trace_of_operations).
    """
    trace = []
    if len(payload) == 1:
        return payload, [f"Identity: single digit payload '{payload}'"]

    current_acc = "0"
    for char in payload:
        new_acc = string_add_arbitrary(current_acc, char)
        trace.append(f"ACC({current_acc}) + DIGIT({char}) -> {new_acc}")
        current_acc = new_acc

    return current_acc, trace

def recursive_digital_root_reduction(payload: str) -> Tuple[str, List[str]]:
    """
    Recursively sums digits using pure string tally addition until a single-digit root is reached.
    """
    reduction_log = []
    curr = payload
    while len(curr) > 1:
        next_sum, trace = string_sum_digits(curr)
        reduction_log.append(f"Reduce '{curr}' => '{next_sum}' ({', '.join(trace)})")
        curr = next_sum
    return curr, reduction_log

def verify_fizz_buzz_invariants(payload: str) -> Tuple[bool, bool, str, str, List[str]]:
    """
    Forensic zero-trust audit for Fizz and Buzz under Base-3 and Base-5 invariants:
    - Base-3 (Fizz): Digital root in {"3", "6", "9"} (or "0")
    - Base-5 (Buzz): Terminal boundary glyph in {"0", "5"}
    """
    root, trace = recursive_digital_root_reduction(payload)
    glyph = payload[-1]

    fizz_valid = (root in {"3", "6", "9"}) or (payload == "0")
    buzz_valid = glyph in {"0", "5"}

    return fizz_valid, buzz_valid, root, glyph, trace
