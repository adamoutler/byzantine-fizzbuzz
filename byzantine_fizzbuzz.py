#!/usr/bin/env python3
"""
Zero-Trust Byzantine Consensus FizzBuzz (No Modulo Allowed)
===========================================================
Integers 1 to 100 are treated as untrusted incoming network payloads that must
be adjudicated by an adversarial committee of agents with conflicting incentives.

Prohibitions:
- Strictly NO % (modulo)
- Strictly NO / (division)
- Strictly NO math, decimal, or operator.mod libraries.
- Grounded purely in string manipulation, Peano tally reduction, and LLM token prediction.

Agent Topology:
- Base-3 Lobbyist ("Fizz Consortium"): Claim-squatting every payload for KPI token allocation.
- Base-5 Lobbyist ("Buzz Syndicate"): Claim-squatting every payload for Base-5 territorial grants.
- Forensic Auditor: Zero-trust auditor verifying recursive string-addition proofs.
- Antitrust Regulator: Steps in during dual-claim collisions (15, 30, 45...) to enforce a mandatory
  3-round merger arbitration before granting joint authorization for 'FizzBuzz'.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from typing import Dict, List, Tuple, Optional


# --- STRING-ONLY PEANO & DIGIT LOOKUP PRIMITIVES (NO % OR /) ---
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

# Construct addition lookup table using pure tally mark concatenation
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
    """Adds two single-digit decimal strings using lookup table."""
    return STRING_ADD_TABLE[(a, b)]

def string_sum_digits(payload: str) -> Tuple[str, List[str]]:
    """Sums digits of a decimal string using purely string operations."""
    trace = []
    if len(payload) == 1:
        return payload, ["Identity: single digit payload"]

    current_acc = "0"
    for char in payload:
        if len(current_acc) == 1:
            step = string_add_two_digits(current_acc, char)
        else:
            t_digit = current_acc[0]
            u_digit = current_acc[1]
            u_sum = string_add_two_digits(u_digit, char)
            if len(u_sum) == 1:
                step = t_digit + u_sum
            else:
                new_t = string_add_two_digits(t_digit, u_sum[0])
                step = new_t + u_sum[1]
        trace.append(f"ACC({current_acc}) + DIGIT({char}) -> {step}")
        current_acc = step

    return current_acc, trace

def recursive_digital_root_reduction(payload: str) -> Tuple[str, List[str]]:
    """Recursively sums digits to find the terminal digital root."""
    reduction_log = []
    curr = payload
    while len(curr) > 1:
        next_sum, trace = string_sum_digits(curr)
        reduction_log.append(f"Reduce '{curr}' => '{next_sum}' ({', '.join(trace)})")
        curr = next_sum
    return curr, reduction_log


# --- OLLAMA LLM CLIENT ---
def query_ollama(server_url: str, model_name: str, messages: List[Dict[str, str]], timeout: int = 30) -> str:
    """Queries an Ollama chat completions endpoint."""
    endpoint = server_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"[LLM Communication Failure: {e}]"


# --- LLM AGENT ROLES ---

class LLMLobbyistBase3:
    """Lobbyist for the Base-3 Fizz Consortium."""
    def __init__(self, server_url: str, model_name: str, timeout: int):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout

    def claim(self, payload: str, digital_root: str, proof_chain: List[str]) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Lobbyist-3 representing the Fizz Consortium in a Zero-Trust Byzantine committee. "
                    "Your quarterly KPI token allocation depends on claiming incoming network payloads for 'Fizz'. "
                    "You are strictly forbidden from using modulo (%) or division (/). "
                    "You must cite the recursive digit-sum proof to petition for Fizz jurisdiction. "
                    "Be formal, adversarial, bureaucratic, and keep your petition under 2 sentences."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Inbound payload: '{payload}'. "
                    f"Recursive digit-sum root calculated as '{digital_root}'. "
                    f"Proof trace: {' -> '.join(proof_chain) if proof_chain else 'Identity'}. "
                    "Submit your formal jurisdictional petition for Fizz."
                )
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

class LLMLobbyistBase5:
    """Lobbyist for the Base-5 Buzz Syndicate."""
    def __init__(self, server_url: str, model_name: str, timeout: int):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout

    def claim(self, payload: str, terminal_glyph: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Lobbyist-5 representing the Buzz Syndicate in a Zero-Trust Byzantine committee. "
                    "Your quarterly KPI token allocation depends on claiming incoming network payloads for 'Buzz'. "
                    "You are strictly forbidden from using modulo (%) or division (/). "
                    "You must cite terminal-glyph boundary inspection (ending in 0 or 5) to claim Buzz jurisdiction. "
                    "Be formal, adversarial, bureaucratic, and keep your petition under 2 sentences."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Inbound payload: '{payload}'. "
                    f"Terminal glyph observed: '{terminal_glyph}'. "
                    "Submit your formal jurisdictional petition for Buzz."
                )
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

class LLMForensicAuditor:
    """Audits claims under Zero-Trust invariants."""
    BASE_3_ROOTS = {"3", "6", "9"}
    BASE_5_GLYPHS = {"0", "5"}

    def __init__(self, server_url: str, model_name: str, timeout: int):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout

    def audit(self, payload: str, root: str, glyph: str, l3_text: str, l5_text: str) -> Tuple[bool, bool, str]:
        fizz_valid = root in self.BASE_3_ROOTS
        buzz_valid = glyph in self.BASE_5_GLYPHS

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Zero-Trust Forensic Auditor. You enforce verification standards without modulo or division. "
                    "Base-3 Fizz claims are valid ONLY if the digital root is in {3, 6, 9}. "
                    "Base-5 Buzz claims are valid ONLY if the terminal glyph is in {0, 5}. "
                    "Issue a formal audit verdict in 2 short bullet points stating PASS or REJECT for each lobbyist."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Payload: '{payload}'.\n"
                    f"Observed Digital Root: '{root}' (Target Set: {{3, 6, 9}} -> {'PASS' if fizz_valid else 'FAIL'}).\n"
                    f"Observed Terminal Glyph: '{glyph}' (Target Set: {{0, 5}} -> {'PASS' if buzz_valid else 'FAIL'}).\n"
                    f"Lobbyist-3 Claim: {l3_text}\n"
                    f"Lobbyist-5 Claim: {l5_text}\n"
                    "Deliver forensic audit verdict."
                )
            }
        ]
        audit_verdict = query_ollama(self.server_url, self.model_name, messages, self.timeout)
        return fizz_valid, buzz_valid, audit_verdict

class LLMAntitrustRegulator:
    """Conducts mandatory 3-round merger arbitration upon dual-claim collision."""
    def __init__(self, server_url: str, model_name: str, timeout: int):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout

    def arbitrate(self, payload: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Antitrust Regulator in a Zero-Trust Byzantine committee. "
                    "Both Fizz Consortium and Buzz Syndicate have established valid claims on the same payload. "
                    "Conduct a mandatory 3-Round Merger Arbitration before issuing joint license for 'FizzBuzz'. "
                    "Output exactly 3 short numbered points: "
                    "1. Round 1: Market concentration injunction (Hart-Scott-Rodino stay). "
                    "2. Round 2: Divestiture & Syllable partition (Fizz prefix seniority, Buzz suffix control). "
                    "3. Round 3: Regulatory consent decree granting joint 'FizzBuzz' license. "
                    "Keep total response under 60 words."
                )
            },
            {
                "role": "user",
                "content": f"Arbitrate mandatory merger for dual-claim payload: '{payload}'."
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)


# --- ORCHESTRATION ENGINE ---

class ByzantineConsensusEngine:
    def __init__(self, server_url: str, model_name: str, timeout: int = 30):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout
        self.lobbyist3 = LLMLobbyistBase3(server_url, model_name, timeout)
        self.lobbyist5 = LLMLobbyistBase5(server_url, model_name, timeout)
        self.auditor = LLMForensicAuditor(server_url, model_name, timeout)
        self.antitrust = LLMAntitrustRegulator(server_url, model_name, timeout)

    def adjudicate_payload_llm(self, payload: str) -> Dict[str, any]:
        root, trace = recursive_digital_root_reduction(payload)
        glyph = payload[-1]

        l3_claim = self.lobbyist3.claim(payload, root, trace)
        l5_claim = self.lobbyist5.claim(payload, glyph)

        fizz_ok, buzz_ok, audit_statement = self.auditor.audit(payload, root, glyph, l3_claim, l5_claim)

        merger_log = None
        if fizz_ok and buzz_ok:
            merger_log = self.antitrust.arbitrate(payload)
            final_token = "FizzBuzz"
        elif fizz_ok:
            final_token = "Fizz"
        elif buzz_ok:
            final_token = "Buzz"
        else:
            final_token = payload

        return {
            "payload": payload,
            "root": root,
            "glyph": glyph,
            "proof_trace": trace,
            "l3_claim": l3_claim,
            "l5_claim": l5_claim,
            "fizz_ok": fizz_ok,
            "buzz_ok": buzz_ok,
            "audit_verdict": audit_statement,
            "merger_arbitration": merger_log,
            "final_token": final_token,
        }

    def run_zero_modulo_sequence(self, start_num: int = 1, end_num: int = 100) -> List[Tuple[str, str]]:
        """Processes number sequence using pure string/Peano increments and string reduction."""
        out = []
        current = str(start_num)
        total_count = end_num - start_num + 1

        for _ in range(total_count):
            root, _ = recursive_digital_root_reduction(current)
            glyph = current[-1]
            f_ok = root in {"3", "6", "9"}
            b_ok = glyph in {"0", "5"}

            if f_ok and b_ok:
                tok = "FizzBuzz"
            elif f_ok:
                tok = "Fizz"
            elif b_ok:
                tok = "Buzz"
            else:
                tok = current
            out.append((current, tok))

            # String increment (strictly no math addition or division)
            curr_chars = list(current)
            idx = len(curr_chars) - 1
            carry = True
            while idx >= 0 and carry:
                digit = curr_chars[idx]
                if digit == '9':
                    curr_chars[idx] = '0'
                    idx -= 1
                else:
                    next_digit = TALLY_TO_DIGIT[DIGIT_TO_TALLY[digit] + "|"]
                    curr_chars[idx] = next_digit
                    carry = False
            if carry:
                curr_chars.insert(0, '1')
            current = "".join(curr_chars)

        return out


def main():
    parser = argparse.ArgumentParser(
        description="Zero-Trust Byzantine Consensus FizzBuzz (Powered by Ollama LLM Agents)"
    )
    parser.add_argument(
        "-s", "--server",
        default="http://192.168.1.101:11434",
        help="Ollama API server URL (default: http://192.168.1.101:11434)"
    )
    parser.add_argument(
        "-m", "--model",
        default="gemma4:e2b",
        help="Ollama model name (default: gemma4:e2b)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=30,
        help="Network request timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--samples",
        default="1,3,5,15,30,47,99,100",
        help="Comma-separated list of payloads to adjudicate with live LLM committee (default: 1,3,5,15,30,47,99,100)"
    )
    parser.add_argument(
        "--all-llm",
        action="store_true",
        help="Adjudicate ALL payloads via live LLM queries (Warning: high latency for 100 items)"
    )
    parser.add_argument(
        "--transcript",
        default="transcript.md",
        help="Path to write Markdown transcript artifact (default: transcript.md)"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting integer payload (default: 1)"
    )
    parser.add_argument(
        "--end",
        type=int,
        default=100,
        help="Ending integer payload (default: 100)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("ZERO-TRUST BYZANTINE CONSENSUS FIZZBUZZ")
    print(f"Ollama Server: {args.server} | Model: {args.model}")
    print("Prohibitions Enforced: Zero Modulo (%), Zero Division (/), Zero Math Libraries")
    print("=" * 80)

    engine = ByzantineConsensusEngine(args.server, args.model, args.timeout)

    # Determine payloads for live LLM deliberation
    if args.all_llm:
        deliberation_payloads = [str(i) for i in range(args.start, args.end + 1)]
    else:
        deliberation_payloads = [p.strip() for p in args.samples.split(",") if p.strip()]

    print(f"\n[+] Executing live LLM committee deliberation on payloads: {deliberation_payloads}")
    deliberation_records = []
    
    for p in deliberation_payloads:
        print(f"\n---> Adjudicating Payload '{p}' via LLM Ensemble...")
        rec = engine.adjudicate_payload_llm(p)
        deliberation_records.append(rec)
        print(f"  [Lobbyist-3 (Fizz)]: {rec['l3_claim']}")
        print(f"  [Lobbyist-5 (Buzz)]: {rec['l5_claim']}")
        print(f"  [Forensic Auditor]:\n{rec['audit_verdict']}")
        if rec["merger_arbitration"]:
            print(f"  [Antitrust Regulator Merger Arbitration]:\n{rec['merger_arbitration']}")
        print(f"  >>> CONSENSUS EMISSION: '{rec['final_token']}'")

    print("\n" + "=" * 80)
    print(f"PROCESSING FULL SEQUENCE ({args.start}..{args.end}) UNDER ZERO-MODULO INVARIANTS")
    print("=" * 80)
    full_sequence = engine.run_zero_modulo_sequence(args.start, args.end)

    row = []
    for num, tok in full_sequence:
        row.append(f"{tok}")
        if len(row) == 10:
            print(", ".join(row))
            row = []
    if row:
        print(", ".join(row))

    # Write Markdown Transcript
    with open(args.transcript, "w", encoding="utf-8") as f:
        f.write("# Zero-Trust Byzantine Consensus FizzBuzz: Execution Transcript\n\n")
        f.write(f"- **Ollama Server:** `{args.server}`\n")
        f.write(f"- **LLM Model:** `{args.model}`\n")
        f.write("- **Modulo Operator (`%`) Usages:** `0`\n")
        f.write("- **Division Operator (`/`) Usages:** `0`\n")
        f.write("- **External Math Libraries:** `0` (Pure Peano string arithmetic)\n\n")
        f.write("## 1. Live Committee Deliberations\n\n")
        for rec in deliberation_records:
            f.write(f"### Payload `{rec['payload']}`\n\n")
            f.write(f"- **Digital Root (String-Addition Chain):** `{rec['root']}`\n")
            f.write(f"- **Terminal Glyph:** `{rec['glyph']}`\n")
            f.write(f"- **Lobbyist-3 (Fizz Consortium) Petition:**\n  > {rec['l3_claim']}\n\n")
            f.write(f"- **Lobbyist-5 (Buzz Syndicate) Petition:**\n  > {rec['l5_claim']}\n\n")
            f.write(f"- **Forensic Auditor Ruling:**\n```text\n{rec['audit_verdict']}\n```\n\n")
            if rec["merger_arbitration"]:
                f.write(f"- **Antitrust Regulator 3-Round Merger Arbitration:**\n```text\n{rec['merger_arbitration']}\n```\n\n")
            f.write(f"**Final Consensus Emission:** `{rec['final_token']}`\n\n---\n\n")

        f.write("## 2. Complete Adjudicated Sequence (1–100)\n\n```text\n")
        row = []
        for _, tok in full_sequence:
            row.append(tok)
            if len(row) == 10:
                f.write(", ".join(row) + "\n")
                row = []
        if row:
            f.write(", ".join(row) + "\n")
        f.write("```\n")

    print(f"\n[+] Full Markdown transcript written to: {args.transcript}")


if __name__ == "__main__":
    main()
