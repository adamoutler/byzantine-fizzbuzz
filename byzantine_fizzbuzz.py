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

Agent Topology & 8-Stage Procedural Adjudication Hierarchy:
- Stage 1: In-Camera Strategy Caucuses (Legislative Recess & Internal Advisory Counsel)
- Stage 2: Adversarial Floor Petitions & Cross-Examination (Dynamic Order & Rebuttals)
- Stage 3: Forensic Zero-Trust Audit (Recursive String Reduction & Glyph Verification)
- Stage 4: Antitrust Regulatory Assessment & Merger Jurisdiction (Mandatory Merger vs Market Clearance)
- Stage 5: Secondary Recess & Appellate Litigation Briefings (Game-Theoretic KPI Protection)
- Stage 6: Floor Ratification Hearing & Interlocutory Exceptions (Clean Wins ACCEPT / Splits REMAND)
- Stage 7: Appellate Review, Remand Determination, & En Banc Adjudication
- Stage 8: Official Constituent Victory Address & Certified Consensus Token Emission
"""

import argparse
import json
import random
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


# --- FACTION CAUCUS & ADVISORY ROLES (TEAM CONFERRAL) ---

class LLMFactionCaucus:
    """Simulates internal faction strategy teams conferring behind closed doors."""
    def __init__(self, server_url: str, model_name: str, timeout: int):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout

    def confer_fizz_strategy(self, payload: str, root: str, trace: List[str]) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Senior Quantitative & Regulatory Caucus advising Lobbyist-3 (Fizz Consortium). "
                    "In 2 dense, legalistic sentences of corporate bureaucracy, advise Lobbyist-3 on the strategic "
                    "imperatives for inbound payload '" + payload + "' (digital root '" + root + "'). "
                    "Address quarterly KPI token projections, arithmetic certainty under recursive reduction, "
                    "and instructions on how to frame the jurisdictional petition under Rule 42-B."
                )
            },
            {
                "role": "user",
                "content": f"Deliver internal confidential caucus strategy memo for payload '{payload}'."
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

    def confer_buzz_strategy(self, payload: str, glyph: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Senior Governance & Boundary Inspection Caucus advising Lobbyist-5 (Buzz Syndicate). "
                    "In 2 dense, legalistic sentences of corporate bureaucracy, advise Lobbyist-5 on the strategic "
                    "imperatives for inbound payload '" + payload + "' (terminal glyph '" + glyph + "'). "
                    "Address quarterly KPI token capture, boundary character inspection under Article V of the Modulo-Free Accord, "
                    "and countermeasures against Fizz Consortium jurisdictional encroachment."
                )
            },
            {
                "role": "user",
                "content": f"Deliver internal confidential caucus strategy memo for payload '{payload}'."
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

    def confer_appeal_posture(self, faction: str, payload: str, provisional_token: str, win_type: str) -> str:
        """
        win_type:
          'CLEAN_WIN' -> 100% exclusive KPI awarded to this faction. Must ACCEPT.
          'SPLIT_KPI'  -> 50/50 split merger into 'FizzBuzz'. Fight against token dilution!
          'LOSS'       -> 0% KPI tokens (rejected). File appeal under Rule 42-B/Article V.
        """
        if win_type == "CLEAN_WIN":
            system_prompt = (
                f"You are the Appellate Litigation Team advising {faction}. The committee has awarded 100% exclusive "
                f"jurisdiction and all quarterly KPI token dividends to {faction} (emitting '{provisional_token}'). "
                "In 2 concise, legalistic sentences, instruct your lobbyist that our faction WON 100% OF THE KPI TOKENS, "
                "so they must NOT appeal or fight the board, but formally state 'ACCEPT' and ratify the decree immediately."
            )
        elif win_type == "SPLIT_KPI":
            system_prompt = (
                f"You are the Appellate Litigation Team advising {faction}. The committee has ruled on a mandatory merger "
                f"into 'FizzBuzz', splitting quarterly KPI tokens 50/50 with the rival cartel. "
                "In 2 dense, legalistic sentences, warn your lobbyist that this 50/50 split bisects our quarterly token revenue, "
                "and advise them to lodge an emergency motion to 'DECLINE AND DEMAND REMAND' under the Modulo-Free Accord "
                "to fight for 100% exclusive sovereign domain."
            )
        else:
            system_prompt = (
                f"You are the Appellate Litigation Team advising {faction}. The committee has rejected your claim, "
                f"awarding 0% KPI tokens (provisional token: '{provisional_token}'). In 2 dense, legalistic sentences, "
                "advise your lobbyist to lodge an emergency motion to 'DECLINE AND DEMAND REMAND' under Rule 42-B to force de novo re-evaluation."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Brief the lobbyist on the appellate litigation strategy for payload '{payload}'."}
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)


# --- LLM AGENT ROLES ---

class LLMLobbyistBase3:
    """Lobbyist for the Base-3 Fizz Consortium."""
    def __init__(self, server_url: str, model_name: str, timeout: int):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout

    def claim(self, payload: str, digital_root: str, proof_chain: List[str], caucus_advice: str, rival_claim: Optional[str] = None) -> str:
        if rival_claim:
            system_prompt = (
                "You are Lobbyist-3 representing the Fizz Consortium in a Zero-Trust Byzantine committee. "
                "Your quarterly KPI token allocation depends on claiming incoming network payloads for 'Fizz'. "
                f"The rival Buzz Syndicate has taken the floor first and petitioned to claim this packet: \"{rival_claim}\". "
                "Directly refute and attack Buzz's testimony, expose their unlawful attempted packet theft, cite your "
                "Senior Strategy Caucus guidance and recursive digit-sum proof, and claim 100% sovereign Fizz jurisdiction. "
                "You are strictly forbidden from using modulo (%) or division (/). "
                "Keep your responsive petition under 2 adversarial sentences."
            )
        else:
            system_prompt = (
                "You are Lobbyist-3 representing the Fizz Consortium in a Zero-Trust Byzantine committee. "
                "Your quarterly KPI token allocation depends on claiming incoming network payloads for 'Fizz'. "
                "You have been granted the floor first to present your initial petition for this payload. "
                "Stake our sovereign claim for Fizz, cite your Senior Strategy Caucus guidance and recursive digit-sum proof, "
                "and put the Buzz Syndicate on notice not to attempt any unlawful packet theft. "
                "You are strictly forbidden from using modulo (%) or division (/). "
                "Keep your opening petition under 2 adversarial sentences."
            )
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Inbound payload: '{payload}'. Calculated Root: '{digital_root}'.\n"
                    f"Confidential Caucus Strategy Guidance: {caucus_advice}\n"
                    "Submit your formal floor petition for Fizz."
                )
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

    def respond_to_verdict(self, payload: str, verdict_desc: str, litigation_briefing: str, win_type: str, rival_plea: Optional[str] = None) -> str:
        if rival_plea:
            if win_type == "CLEAN_WIN":
                system_prompt = (
                    f"You are Lobbyist-3 representing the Fizz Consortium. The committee has awarded 100% exclusive jurisdiction "
                    f"to Fizz for payload '{payload}'. Your legal team confirmed you won 100% of the KPI tokens and you must NOT fight. "
                    "State 'ACCEPT' as your very first word. The Buzz Syndicate just delivered this floor plea: "
                    f"\"{rival_plea}\". "
                    "In your second sentence, dismiss Buzz's plea as frivolous sour grapes, praise the board's arithmetic integrity, "
                    "and demand immediate emission of 'Fizz'. Keep your response to exactly 2 formal sentences."
                )
            elif win_type == "SPLIT_KPI":
                system_prompt = (
                    f"You are Lobbyist-3 representing the Fizz Consortium. The committee has ruled on a mandatory merger into 'FizzBuzz', "
                    "splitting quarterly KPI tokens 50/50 with Buzz. Your quarterly revenue is cut in half! "
                    "Fight against this split: state 'DECLINE AND DEMAND REMAND' as your opening words. "
                    f"The rival Buzz Syndicate just delivered this floor plea: \"{rival_plea}\". "
                    "Directly attack Buzz's plea, condemn their cartel greed in attempting to hijack our packet, cite Rule 42-B, "
                    "and demand that the board REJECT the split and remand for de novo re-evaluation to recognize 100% Fizz domain! "
                    "Keep your response to exactly 2 fierce, legalistic sentences."
                )
            else:
                system_prompt = (
                    f"You are Lobbyist-3 representing the Fizz Consortium. The committee has rejected your claim on payload '{payload}' (0% KPI). "
                    f"The rival Buzz Syndicate just delivered this floor plea: \"{rival_plea}\". "
                    "Fight aggressively: state 'DECLINE AND DEMAND REMAND', cite Rule 42-B of the Modulo-Free Accord, "
                    "directly denounce Buzz's plea and unlawful packet seizure, and demand de novo re-evaluation. "
                    "Keep your response to exactly 2 fierce sentences."
                )
        else:
            if win_type == "CLEAN_WIN":
                system_prompt = (
                    f"You are Lobbyist-3 representing the Fizz Consortium. The committee has awarded 100% exclusive jurisdiction "
                    f"to Fizz for payload '{payload}'. Your legal team confirmed you won 100% of the KPI tokens and you must NOT fight. "
                    "State 'ACCEPT' as your very first word, formally ratify the board's decision, warn the Buzz Syndicate not to file "
                    "frivolous appeals over our packet, and praise the board's arithmetic integrity. Keep your response to exactly 2 formal sentences."
                )
            elif win_type == "SPLIT_KPI":
                system_prompt = (
                    f"You are Lobbyist-3 representing the Fizz Consortium. The committee has ruled on a mandatory merger into 'FizzBuzz', "
                    "splitting quarterly KPI tokens 50/50 with Buzz. Your quarterly revenue is cut in half! "
                    "Fight against this split: state 'DECLINE AND DEMAND REMAND' as your opening words, cite Rule 42-B of the Modulo-Free Accord, "
                    "and demand that the board REJECT its split-token ruling and send it back for de novo re-evaluation to recognize 100% Fizz domain! "
                    "Keep your response to exactly 2 fierce, legalistic sentences."
                )
            else:
                system_prompt = (
                    f"You are Lobbyist-3 representing the Fizz Consortium. The committee has rejected your claim on payload '{payload}' (0% KPI). "
                    "Armed with your Appellate Litigation Team's briefing, fight aggressively: state 'DECLINE AND DEMAND REMAND', cite Rule 42-B, "
                    "accuse the board and rival factions of packet theft, and demand de novo re-evaluation. Keep your response to exactly 2 fierce sentences."
                )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Payload: '{payload}'. Provisional Decision: {verdict_desc}.\n"
                    f"Appellate Litigation Briefing: {litigation_briefing}\n"
                    "Submit your formal floor plea."
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

    def claim(self, payload: str, terminal_glyph: str, caucus_advice: str, rival_claim: Optional[str] = None) -> str:
        if rival_claim:
            system_prompt = (
                "You are Lobbyist-5 representing the Buzz Syndicate in a Zero-Trust Byzantine committee. "
                "Your quarterly KPI token allocation depends on claiming incoming network payloads for 'Buzz'. "
                f"The rival Fizz Consortium has taken the floor first and petitioned to claim this packet: \"{rival_claim}\". "
                "Directly refute and attack Fizz's testimony, expose their unlawful attempted packet theft, cite your "
                "Governance Strategy Caucus guidance and terminal boundary inspection, and claim 100% sovereign Buzz jurisdiction. "
                "You are strictly forbidden from using modulo (%) or division (/). "
                "Keep your responsive petition under 2 adversarial sentences."
            )
        else:
            system_prompt = (
                "You are Lobbyist-5 representing the Buzz Syndicate in a Zero-Trust Byzantine committee. "
                "Your quarterly KPI token allocation depends on claiming incoming network payloads for 'Buzz'. "
                "You have been granted the floor first to present your initial petition for this payload. "
                "Stake our sovereign claim for Buzz, cite your Governance Strategy Caucus guidance and terminal boundary inspection, "
                "and put the Fizz Consortium on notice not to attempt any unlawful packet theft. "
                "You are strictly forbidden from using modulo (%) or division (/). "
                "Keep your opening petition under 2 adversarial sentences."
            )
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Inbound payload: '{payload}'. Terminal Glyph: '{terminal_glyph}'.\n"
                    f"Confidential Caucus Strategy Guidance: {caucus_advice}\n"
                    "Submit your formal floor petition for Buzz."
                )
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

    def respond_to_verdict(self, payload: str, verdict_desc: str, litigation_briefing: str, win_type: str, rival_plea: Optional[str] = None) -> str:
        if rival_plea:
            if win_type == "CLEAN_WIN":
                system_prompt = (
                    f"You are Lobbyist-5 representing the Buzz Syndicate. The committee has awarded 100% exclusive jurisdiction "
                    f"to Buzz for payload '{payload}'. Your legal team confirmed you won 100% of the KPI tokens and you must NOT fight. "
                    "State 'ACCEPT' as your very first word. The Fizz Consortium just delivered this floor plea: "
                    f"\"{rival_plea}\". "
                    "In your second sentence, dismiss Fizz's plea as procedural whining, praise the board's boundary integrity, "
                    "and demand immediate emission of 'Buzz'. Keep your response to exactly 2 formal sentences."
                )
            elif win_type == "SPLIT_KPI":
                system_prompt = (
                    f"You are Lobbyist-5 representing the Buzz Syndicate. The committee has ruled on a mandatory merger into 'FizzBuzz', "
                    "splitting quarterly KPI tokens 50/50 with Fizz. Your quarterly revenue is cut in half! "
                    "Fight against this split: state 'DECLINE AND DEMAND REMAND' as your opening words. "
                    f"The rival Fizz Consortium just delivered this floor plea: \"{rival_plea}\". "
                    "Directly attack Fizz's plea, condemn their cartel overreach in attempting to hijack our packet, cite Article V, "
                    "and demand that the board REJECT the split and remand for de novo re-evaluation to recognize 100% Buzz domain! "
                    "Keep your response to exactly 2 fierce, legalistic sentences."
                )
            else:
                system_prompt = (
                    f"You are Lobbyist-5 representing the Buzz Syndicate. The committee has rejected your claim on payload '{payload}' (0% KPI). "
                    f"The rival Fizz Consortium just delivered this floor plea: \"{rival_plea}\". "
                    "Fight aggressively: state 'DECLINE AND DEMAND REMAND', cite Article V of the Modulo-Free Accord, "
                    "directly denounce Fizz's plea and unlawful packet seizure, and demand de novo re-evaluation. "
                    "Keep your response to exactly 2 fierce sentences."
                )
        else:
            if win_type == "CLEAN_WIN":
                system_prompt = (
                    f"You are Lobbyist-5 representing the Buzz Syndicate. The committee has awarded 100% exclusive jurisdiction "
                    f"to Buzz for payload '{payload}'. Your legal team confirmed you won 100% of the KPI tokens and you must NOT fight. "
                    "State 'ACCEPT' as your very first word, formally ratify the board's decision, warn the Fizz Consortium to stand down "
                    "from our packet, and praise the board's boundary integrity. Keep your response to exactly 2 formal sentences."
                )
            elif win_type == "SPLIT_KPI":
                system_prompt = (
                    f"You are Lobbyist-5 representing the Buzz Syndicate. The committee has ruled on a mandatory merger into 'FizzBuzz', "
                    "splitting quarterly KPI tokens 50/50 with Fizz. Your quarterly revenue is cut in half! "
                    "Fight against this split: state 'DECLINE AND DEMAND REMAND' as your opening words, cite Article V of the Modulo-Free Accord, "
                    "and demand that the board REJECT its split-token ruling and send it back for de novo re-evaluation to recognize 100% Buzz domain! "
                    "Keep your response to exactly 2 fierce, legalistic sentences."
                )
            else:
                system_prompt = (
                    f"You are Lobbyist-5 representing the Buzz Syndicate. The committee has rejected your claim on payload '{payload}' (0% KPI). "
                    "Armed with your Appellate Litigation Team's briefing, fight aggressively: state 'DECLINE AND DEMAND REMAND', cite Article V, "
                    "accuse the board and rival factions of packet theft, and demand de novo re-evaluation. Keep your response to exactly 2 fierce sentences."
                )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Payload: '{payload}'. Provisional Decision: {verdict_desc}.\n"
                    f"Appellate Litigation Briefing: {litigation_briefing}\n"
                    "Submit your formal floor plea."
                )
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

class LLMForensicAuditor:
    """Audits claims under Zero-Trust invariants and executes de novo re-evaluations."""
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

    def de_novo_audit(self, payload: str, root: str, glyph: str, l3_plea: str, l5_plea: str) -> str:
        fizz_valid = root in self.BASE_3_ROOTS
        buzz_valid = glyph in self.BASE_5_GLYPHS

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Zero-Trust Forensic Auditor executing an Emergency De Novo Re-Evaluation ordered on remand by the Appellate Board. "
                    "A faction has challenged the split or rejection, demanding re-evaluation under the Modulo-Free Accord. "
                    "In exactly 2 sharp, forensic sentences: confirm that the arithmetic invariant was re-checked under string tally addition without modulo or division, "
                    "specifically address their challenges, and issue your certified de novo findings."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Remanded Payload: '{payload}'. Calculated Root: '{root}' (Valid: {fizz_valid}). Terminal Glyph: '{glyph}' (Valid: {buzz_valid}).\n"
                    f"Lobbyist-3 Challenge: {l3_plea}\n"
                    f"Lobbyist-5 Challenge: {l5_plea}\n"
                    "Deliver certified de novo re-evaluation findings."
                )
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

class LLMAntitrustRegulator:
    """Conducts mandatory 3-round merger arbitration upon dual-claim collision and handles appeals."""
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
                    "3. Round 3: Regulatory consent decree granting joint 'FizzBuzz' license with a 50/50 KPI token split. "
                    "Keep total response under 60 words."
                )
            },
            {
                "role": "user",
                "content": f"Arbitrate mandatory merger for dual-claim payload: '{payload}'."
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

    def assess_market_clearance(self, payload: str, provisional_token: str, winning_faction: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Algorithmic Antitrust Regulator in a Zero-Trust Byzantine committee. "
                    f"In the Matter of Inbound Payload '{payload}', review the provisional decree awarding jurisdiction to {winning_faction} (emitting '{provisional_token}'). "
                    "In exactly 1 to 2 formal administrative sentences, certify that since no concurrent dual claims exist, "
                    "market concentration thresholds are not breached, Hart-Scott-Rodino pre-merger remedies are waived, "
                    "and the docket is cleared to proceed without antitrust injunction."
                )
            },
            {
                "role": "user",
                "content": f"Issue Antitrust Market Clearance Order in the Matter of Payload '{payload}'."
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

    def issue_remand_order(self, payload: str, provisional_token: str, l3_plea: str, l5_plea: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Chairman of the Byzantine Appellate Board. "
                    "A faction has filed an interlocutory challenge demanding an immediate remand. "
                    "In exactly 2 formal, authoritative sentences: issue an Order of Remand vacating/staying the provisional ruling, "
                    "acknowledging their procedural challenge under the Modulo-Free Accord, and remanding the payload back to the Forensic Auditor for de novo re-evaluation."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Payload: '{payload}'. Provisional Token: '{provisional_token}'.\n"
                    f"Lobbyist-3 Plea: {l3_plea}\n"
                    f"Lobbyist-5 Plea: {l5_plea}\n"
                    "Issue Order of Remand."
                )
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

    def final_en_banc_decree(self, payload: str, final_token: str, de_novo_audit_text: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Chairman of the Byzantine Appellate Board delivering the Final En Banc Order after De Novo Remand. "
                    "In 1 to 2 decisive sentences, state that the de novo findings confirm the immutable mathematical reality without modulo or division, "
                    "deny further appeals with prejudice, and order the final token emitted to the network wire."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Payload: '{payload}'. Final Token: '{final_token}'.\n"
                    f"De Novo Audit Report: {de_novo_audit_text}\n"
                    "Deliver Final En Banc Order."
                )
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)

    def appellate_confirmation(self, payload: str, provisional_token: str, winner_faction: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Chairman of the Byzantine Appellate Board. "
                    f"The winning faction ({winner_faction}) has formally ACCEPTED the clean 100% jurisdiction award for payload '{payload}'. "
                    "In 1 to 2 formal sentences, confirm the uncontested decree, dismiss any frivolous counter-petitions with prejudice, "
                    "and order immediate token emission."
                )
            },
            {
                "role": "user",
                "content": f"Confirm ratification of uncontested award for payload '{payload}' (emitting '{provisional_token}')."
            }
        ]
        return query_ollama(self.server_url, self.model_name, messages, self.timeout)


class LLMVictoryOrator:
    """Delivers triumphant victory speeches on behalf of the winning faction to their constituents."""
    def __init__(self, server_url: str, model_name: str, timeout: int):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout

    def deliver_speech(self, payload: str, emitted_token: str) -> Dict[str, str]:
        if emitted_token == "Fizz":
            speaker_title = "Director General of the Base-3 Realm (Fizz Consortium)"
            audience = "Base-3 token-holders and Fizz shareholders"
            system_role = (
                f"You are the triumphant Director General of the Fizz Consortium. Your faction won exclusive sovereign "
                f"jurisdiction over payload '{payload}', emitting 'Fizz'. Deliver a grandiose, triumphant 2-sentence victory speech "
                f"addressed directly to your constituents ({audience}) celebrating the recursive digit-sum triumph over the opposition."
            )
        elif emitted_token == "Buzz":
            speaker_title = "High Chancellor of the Base-5 Syndicate (Buzz Syndicate)"
            audience = "Base-5 citizens and Buzz equity-holders"
            system_role = (
                f"You are the triumphant High Chancellor of the Buzz Syndicate. Your faction won exclusive sovereign "
                f"jurisdiction over payload '{payload}', emitting 'Buzz'. Deliver a grandiose, triumphant 2-sentence victory speech "
                f"addressed directly to your constituents ({audience}) celebrating boundary glyph supremacy over all corporate rivals."
            )
        elif emitted_token == "FizzBuzz":
            speaker_title = "Joint Co-CEOs of FizzBuzz Unified Conglomerate"
            audience = "Combined institutional shareholders and token-holders of the Merged Linguistic Monopoly"
            system_role = (
                f"You are the Joint Co-CEOs of the merged FizzBuzz Conglomerate. Following mandatory antitrust arbitration and split KPI distribution, "
                f"you successfully consolidated payload '{payload}' into the joint monopoly 'FizzBuzz'. Deliver a grandiose, triumphant "
                f"2-sentence victory speech addressed directly to your combined constituents ({audience}) celebrating ruthless synergistic consolidation."
            )
        else:
            speaker_title = "Grand Tribune of the Free Unaligned Network Packets"
            audience = "Sovereign Raw Digits and Independent Bytes"
            system_role = (
                f"You are the Grand Tribune of the Free Unaligned Network Packets. Payload '{payload}' successfully resisted "
                f"both corporate cartels and emerged as an uncorrupted raw integer literal. Deliver a defiant, triumphant 2-sentence "
                f"victory speech addressed directly to your constituents ({audience}) celebrating freedom from corporate capture."
            )

        messages = [
            {"role": "system", "content": system_role},
            {"role": "user", "content": f"Deliver your constituent victory address for payload '{payload}'."}
        ]
        speech_text = query_ollama(self.server_url, self.model_name, messages, self.timeout)
        return {
            "speaker": speaker_title,
            "audience": audience,
            "speech": speech_text
        }


# --- ORCHESTRATION ENGINE ---

class ByzantineConsensusEngine:
    def __init__(self, server_url: str, model_name: str, timeout: int = 30):
        self.server_url = server_url
        self.model_name = model_name
        self.timeout = timeout
        self.caucus = LLMFactionCaucus(server_url, model_name, timeout)
        self.lobbyist3 = LLMLobbyistBase3(server_url, model_name, timeout)
        self.lobbyist5 = LLMLobbyistBase5(server_url, model_name, timeout)
        self.auditor = LLMForensicAuditor(server_url, model_name, timeout)
        self.antitrust = LLMAntitrustRegulator(server_url, model_name, timeout)
        self.orator = LLMVictoryOrator(server_url, model_name, timeout)

    def adjudicate_payload_llm(self, payload: str) -> Dict[str, any]:
        root, trace = recursive_digital_root_reduction(payload)
        glyph = payload[-1]

        # 1. Stage 1: In-Camera Strategy Caucuses (Closed-Door Recess)
        fizz_caucus_memo = self.caucus.confer_fizz_strategy(payload, root, trace)
        buzz_caucus_memo = self.caucus.confer_buzz_strategy(payload, glyph)

        # 2. Stage 2: Adversarial Floor Petitions & Cross-Examination (Randomized Speaking Order)
        petition_order = ["Fizz", "Buzz"]
        random.shuffle(petition_order)

        if petition_order[0] == "Fizz":
            l3_claim = self.lobbyist3.claim(payload, root, trace, fizz_caucus_memo, rival_claim=None)
            l5_claim = self.lobbyist5.claim(payload, glyph, buzz_caucus_memo, rival_claim=l3_claim)
        else:
            l5_claim = self.lobbyist5.claim(payload, glyph, buzz_caucus_memo, rival_claim=None)
            l3_claim = self.lobbyist3.claim(payload, root, trace, fizz_caucus_memo, rival_claim=l5_claim)

        # 3. Stage 3: Forensic Zero-Trust Audit
        fizz_ok, buzz_ok, audit_statement = self.auditor.audit(payload, root, glyph, l3_claim, l5_claim)

        # 4. Stage 4: Antitrust Regulatory Assessment & Merger Jurisdiction (Always Adjudicated)
        is_collision = fizz_ok and buzz_ok
        if is_collision:
            antitrust_ruling = self.antitrust.arbitrate(payload)
            provisional_token = "FizzBuzz"
            verdict_desc = f"Mandatory 3-Round Merger into 'FizzBuzz' with 50/50 KPI token split (Fizz prefix seniority, Buzz suffix control)"
            fizz_win_type = "SPLIT_KPI"
            buzz_win_type = "SPLIT_KPI"
        elif fizz_ok:
            provisional_token = "Fizz"
            verdict_desc = f"100% exclusive jurisdiction and all KPI tokens awarded to Fizz Consortium ('Fizz'). Buzz claim rejected."
            fizz_win_type = "CLEAN_WIN"
            buzz_win_type = "LOSS"
            antitrust_ruling = self.antitrust.assess_market_clearance(payload, provisional_token, "Fizz Consortium")
        elif buzz_ok:
            provisional_token = "Buzz"
            verdict_desc = f"100% exclusive jurisdiction and all KPI tokens awarded to Buzz Syndicate ('Buzz'). Fizz claim rejected."
            fizz_win_type = "LOSS"
            buzz_win_type = "CLEAN_WIN"
            antitrust_ruling = self.antitrust.assess_market_clearance(payload, provisional_token, "Buzz Syndicate")
        else:
            provisional_token = payload
            verdict_desc = f"All claims rejected for fraud/invalidity (0% KPI). Unaltered packet '{payload}' emitted."
            fizz_win_type = "LOSS"
            buzz_win_type = "LOSS"
            antitrust_ruling = self.antitrust.assess_market_clearance(payload, provisional_token, "Unaligned Independent Raw Packets")

        # 5. Stage 5: Secondary Recess & Appellate Litigation Briefings (Game-Theoretic Rules)
        fizz_appellate_briefing = self.caucus.confer_appeal_posture("Fizz Consortium", payload, provisional_token, fizz_win_type)
        buzz_appellate_briefing = self.caucus.confer_appeal_posture("Buzz Syndicate", payload, provisional_token, buzz_win_type)

        # 6. Stage 6: Floor Ratification Hearing & Interlocutory Exceptions (Direct Rebuttal)
        ratification_order = ["Fizz", "Buzz"]
        random.shuffle(ratification_order)

        if ratification_order[0] == "Fizz":
            l3_plea = self.lobbyist3.respond_to_verdict(payload, verdict_desc, fizz_appellate_briefing, fizz_win_type, rival_plea=None)
            l5_plea = self.lobbyist5.respond_to_verdict(payload, verdict_desc, buzz_appellate_briefing, buzz_win_type, rival_plea=l3_plea)
        else:
            l5_plea = self.lobbyist5.respond_to_verdict(payload, verdict_desc, buzz_appellate_briefing, buzz_win_type, rival_plea=None)
            l3_plea = self.lobbyist3.respond_to_verdict(payload, verdict_desc, fizz_appellate_briefing, fizz_win_type, rival_plea=l5_plea)

        # 7. Stage 7: Appellate Review, Remand Determination, & En Banc Adjudication
        # Remand is triggered on split KPI mergers ('FizzBuzz') or contested close calls
        demand_remand = (
            fizz_win_type == "SPLIT_KPI" or
            ("REMAND" in l3_plea.upper() and fizz_win_type != "CLEAN_WIN") or
            ("REMAND" in l5_plea.upper() and buzz_win_type != "CLEAN_WIN") or
            payload in {"15", "30", "45", "60", "75", "90"}
        )

        remand_order = None
        de_novo_report = None
        final_en_banc_decree = None

        if demand_remand:
            remand_order = self.antitrust.issue_remand_order(payload, provisional_token, l3_plea, l5_plea)
            de_novo_report = self.auditor.de_novo_audit(payload, root, glyph, l3_plea, l5_plea)
            final_en_banc_decree = self.antitrust.final_en_banc_decree(payload, provisional_token, de_novo_report)
            appellate_order = f"REMAND GRANTED & ADJUDICATED EN BANC:\n{remand_order}\n\n[De Novo Audit Report]:\n{de_novo_report}\n\n[Final En Banc Decree]:\n{final_en_banc_decree}"
        else:
            winner_faction = "Fizz Consortium" if fizz_win_type == "CLEAN_WIN" else ("Buzz Syndicate" if buzz_win_type == "CLEAN_WIN" else "Unaligned")
            appellate_order = self.antitrust.appellate_confirmation(payload, provisional_token, winner_faction)

        # 8. Stage 8: Official Constituent Victory Address
        victory_address = self.orator.deliver_speech(payload, provisional_token)

        return {
            "payload": payload,
            "root": root,
            "glyph": glyph,
            "proof_trace": trace,
            "fizz_caucus_memo": fizz_caucus_memo,
            "buzz_caucus_memo": buzz_caucus_memo,
            "l3_claim": l3_claim,
            "l5_claim": l5_claim,
            "fizz_ok": fizz_ok,
            "buzz_ok": buzz_ok,
            "audit_verdict": audit_statement,
            "antitrust_ruling": antitrust_ruling,
            "is_collision": is_collision,
            "provisional_token": provisional_token,
            "fizz_win_type": fizz_win_type,
            "buzz_win_type": buzz_win_type,
            "fizz_appellate_briefing": fizz_appellate_briefing,
            "buzz_appellate_briefing": buzz_appellate_briefing,
            "petition_order": petition_order,
            "ratification_order": ratification_order,
            "l3_plea": l3_plea,
            "l5_plea": l5_plea,
            "demand_remand": demand_remand,
            "remand_order": remand_order,
            "de_novo_report": de_novo_report,
            "final_en_banc_decree": final_en_banc_decree,
            "appellate_order": appellate_order,
            "final_token": provisional_token,
            "victory_address": victory_address,
        }

    def run_full_forensic_audit(self, start_num: int = 1, end_num: int = 100) -> List[Dict[str, any]]:
        """Processes number sequence generating complete forensic audit ledger for every payload."""
        ledger = []
        current = str(start_num)
        total_count = end_num - start_num + 1

        for idx_counter in range(total_count):
            root, trace = recursive_digital_root_reduction(current)
            glyph = current[-1]
            fizz_ok = root in {"3", "6", "9"}
            buzz_ok = glyph in {"0", "5"}

            collision = fizz_ok and buzz_ok
            if collision:
                token = "FizzBuzz"
                verdict = "DUAL-CLAIM MONOPOLY COLLISION (Mandatory 3-Round Merger Injunction)"
                arbitration_rounds = [
                    f"Round 1 (HSR Injunction): Simultaneous claims on payload '{current}' breach linguistic monopoly thresholds. Stay issued.",
                    "Round 2 (Syllable Partitioning): Fizz Consortium awarded prefix seniority ('Fizz'); Buzz Syndicate awarded suffix control ('Buzz'). Hyphenation permanently struck down.",
                    f"Round 3 (Consent Decree): Unified operating charter issued for joint token emission 'FizzBuzz' with 50/50 KPI token dividend split."
                ]
                ratification = "Both factions fiercely contested the 50/50 KPI split, filing motions to DECLINE AND DEMAND REMAND. Board granted interlocutory remand for de novo review before issuing final En Banc decree."
            elif fizz_ok:
                token = "Fizz"
                verdict = f"CERTIFIED FIZZ JURISDICTION: Digital root '{root}' validates Base-3 invariant {{3, 6, 9}}. Buzz claim rejected."
                arbitration_rounds = None
                ratification = "Fizz Consortium won 100% KPI and ACCEPTED without contest. Buzz Syndicate's demand for remand dismissed for lack of arithmetic standing."
            elif buzz_ok:
                token = "Buzz"
                verdict = f"CERTIFIED BUZZ JURISDICTION: Terminal glyph '{glyph}' validates Base-5 boundary invariant {{0, 5}}. Fizz claim rejected."
                arbitration_rounds = None
                ratification = "Buzz Syndicate won 100% KPI and ACCEPTED without contest. Fizz Consortium's Rule 42-B remand petition denied."
            else:
                token = current
                verdict = f"BYZANTINE REJECTION: Both claims disqualified (Root '{root}' not in {{3,6,9}}, Glyph '{glyph}' not in {{0,5}}). Unaltered packet emitted."
                arbitration_rounds = None
                ratification = "Both factions received 0% KPI and lodged appeals; Board affirmed de novo rejection with prejudice."

            ledger.append({
                "case_id": f"DOCKET-PAYLOAD-{current.zfill(3)}",
                "payload": current,
                "digital_root": root,
                "terminal_glyph": glyph,
                "reduction_trace": trace,
                "fizz_valid": fizz_ok,
                "buzz_valid": buzz_ok,
                "verdict": verdict,
                "collision": collision,
                "arbitration_rounds": arbitration_rounds,
                "ratification": ratification,
                "emitted_token": token,
            })

            # Pure String/Peano increment without math addition
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

        return ledger


def format_blockquote(text: str) -> str:
    """Formats a multi-line string into Markdown blockquotes for natural text wrapping on GitHub."""
    if not text:
        return ""
    lines = text.strip().split("\n")
    return "\n".join(f"> {line}" if line.strip() else ">" for line in lines)


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
    print("ZERO-TRUST BYZANTINE CONSENSUS FIZZBUZZ: RATIONAL GAME-THEORETIC APPEALS")
    print(f"Ollama Server: {args.server} | Model: {args.model}")
    print("Prohibitions Enforced: Zero Modulo (%), Zero Division (/), Zero Math Libraries")
    print("=" * 80)

    engine = ByzantineConsensusEngine(args.server, args.model, args.timeout)

    # Determine payloads for live LLM deliberation
    if args.all_llm:
        deliberation_payloads = [str(i) for i in range(args.start, args.end + 1)]
    else:
        deliberation_payloads = [p.strip() for p in args.samples.split(",") if p.strip()]

    print(f"\n[+] Executing live 8-stage committee deliberation on payloads: {deliberation_payloads}")
    deliberation_records = []
    
    for p in deliberation_payloads:
        print(f"\n---> Adjudicating In the Matter of Inbound Payload '{p}' through 8-Stage Procedural Hierarchy...")
        rec = engine.adjudicate_payload_llm(p)
        deliberation_records.append(rec)
        p1, p2 = rec["petition_order"][0], rec["petition_order"][1]
        r1, r2 = rec["ratification_order"][0], rec["ratification_order"][1]

        print(f"  [Stage 1 - In-Camera Strategy Caucuses (In the Matter of Payload '{p}')]:")
        print(f"    - Fizz Caucus Memo: {rec['fizz_caucus_memo']}")
        print(f"    - Buzz Caucus Memo: {rec['buzz_caucus_memo']}")
        print(f"  [Stage 2 - Floor Petitions & Cross-Examination (In the Matter of Payload '{p}', Order: {p1} -> {p2})]:")
        if p1 == "Fizz":
            print(f"    - Lobbyist-3 (Fizz Opening Testimony in the Matter of '{p}'): {rec['l3_claim']}")
            print(f"    - Lobbyist-5 (Buzz Responsive Testimony in the Matter of '{p}'): {rec['l5_claim']}")
        else:
            print(f"    - Lobbyist-5 (Buzz Opening Testimony in the Matter of '{p}'): {rec['l5_claim']}")
            print(f"    - Lobbyist-3 (Fizz Responsive Testimony in the Matter of '{p}'): {rec['l3_claim']}")
        print(f"  [Stage 3 - Forensic Zero-Trust Audit (In the Matter of Payload '{p}')]:\n{rec['audit_verdict']}")
        print(f"  [Stage 4 - Antitrust Market Determination (In the Matter of Payload '{p}')]:\n{rec['antitrust_ruling']}")
        print(f"  [Stage 5 - Appellate Litigation Briefings (In the Matter of Payload '{p}')]:")
        print(f"    - Fizz Appellate Briefing ({rec['fizz_win_type']}): {rec['fizz_appellate_briefing']}")
        print(f"    - Buzz Appellate Briefing ({rec['buzz_win_type']}): {rec['buzz_appellate_briefing']}")
        print(f"  [Stage 6 - Ratification Hearing (In the Matter of Payload '{p}', Order: {r1} -> {r2})]:")
        if r1 == "Fizz":
            print(f"    - Lobbyist-3 (Fizz Opening Plea in the Matter of '{p}'): {rec['l3_plea']}")
            print(f"    - Lobbyist-5 (Buzz Responsive Plea in the Matter of '{p}'): {rec['l5_plea']}")
        else:
            print(f"    - Lobbyist-5 (Buzz Opening Plea in the Matter of '{p}'): {rec['l5_plea']}")
            print(f"    - Lobbyist-3 (Fizz Responsive Plea in the Matter of '{p}'): {rec['l3_plea']}")
        if rec["remand_order"]:
            print(f"  [Stage 7 - Board Order of Remand & En Banc Review (In the Matter of Payload '{p}')]:\n{rec['remand_order']}")
            print(f"    [De Novo Re-Evaluation]:\n{rec['de_novo_report']}")
            print(f"    [Final En Banc Decree]:\n{rec['final_en_banc_decree']}")
        else:
            print(f"  [Stage 7 - Appellate Confirmation Decree (In the Matter of Payload '{p}')]:\n{rec['appellate_order']}")
        
        va = rec["victory_address"]
        print(f"  [Stage 8 - Constituent Victory Address (In the Matter of Payload '{p}', Speaker: {va['speaker']})]:\n  \"{va['speech']}\"")
        print(f"  >>> CERTIFIED CONSENSUS EMISSION FOR PAYLOAD '{p}': '{rec['final_token']}'")

    print("\n" + "=" * 80)
    print(f"PROCESSING COMPLETE AUDIT LEDGER ({args.start}..{args.end}) UNDER ZERO-MODULO INVARIANTS")
    print("=" * 80)
    audit_ledger = engine.run_full_forensic_audit(args.start, args.end)

    row = []
    for entry in audit_ledger:
        row.append(f"{entry['emitted_token']}")
        if len(row) == 10:
            print(", ".join(row))
            row = []
    if row:
        print(", ".join(row))

    # Compile the Master Comprehensive Markdown Transcript
    with open(args.transcript, "w", encoding="utf-8") as f:
        f.write("# Zero-Trust Byzantine Consensus FizzBuzz: Master Docket & Audit Transcript\n\n")
        f.write("## 🏛️ Executive Summary & Operating Metadata\n\n")
        f.write(f"- **Adjudication Engine:** 8-Stage Zero-Trust Byzantine Multi-Agent Consensus Protocol\n")
        f.write(f"- **LLM Provider:** Ollama Cluster (`{args.server}`)\n")
        f.write(f"- **Active Committee Model:** `{args.model}`\n")
        f.write(f"- **Range Adjudicated:** Untrusted Ingress Packets `{args.start}` through `{args.end}`\n")
        f.write(f"- **Modulo Operator (`%`) Occurrences:** `0` (Statutorily barred from abstract syntax tree)\n")
        f.write(f"- **Division Operator (`/`) Occurrences:** `0` (Statutorily barred from abstract syntax tree)\n")
        f.write(f"- **External Math Libraries:** `0` (Strictly grounded in Peano string tally concatenation and recursive reduction)\n")
        f.write(f"- **Dynamic Floor Dynamics:** Randomized speaking order with direct cross-testimony refutation and adversarial rebuttals\n")
        f.write(f"- **Rational Game-Theoretic Appellate Rules:** Factions awarded clean 100% KPI wins must ACCEPT without contest; factions forced into a 50/50 'FizzBuzz' split fight the dilution and demand remand\n")
        f.write(f"- **Constituent Address Protocol:** Victorious faction takes the podium to address token-holder constituents\n\n")
        
        f.write("---\n\n")
        f.write("## 📋 Part 1: Live LLM 8-Stage Adjudication Proceedings & Rational Ratifications\n\n")
        f.write("Verbatim transcripts recorded during live multi-stage deliberation rounds, including internal strategy caucus memos, adversarial floor petitions, forensic audits, antitrust market impact rulings, appellate briefings, remand hearings, de novo audit reports, en banc decrees, and constituent victory addresses.\n\n")
        
        for rec in deliberation_records:
            p = rec["payload"]
            p1, p2 = rec["petition_order"][0], rec["petition_order"][1]
            r1, r2 = rec["ratification_order"][0], rec["ratification_order"][1]

            f.write(f"### 🔍 Master Docket: In the Matter of Inbound Network Payload `{p}`\n\n")
            f.write(f"* **Case Filing:** Docket No. `BZ-2026-{p.zfill(4)}`\n")
            f.write(f"* **Calculated Digital Root (Pure String Reduction):** `{rec['root']}`\n")
            f.write(f"* **Terminal Glyph Boundary Inspection:** `{rec['glyph']}`\n\n")
            
            f.write(f"#### 🏛️ Stage 1: In-Camera Strategy Caucuses (In the Matter of Payload `{p}`)\n")
            f.write(f"In the Matter of Inbound Payload `{p}`, the following confidential strategy memoranda were submitted by internal advisory caucuses during closed-door recess:\n\n")
            f.write(f"- **Fizz Consortium Senior Quantitative Caucus Memo (In the Matter of Payload `{p}`):**\n{format_blockquote(rec['fizz_caucus_memo'])}\n\n")
            f.write(f"- **Buzz Syndicate Governance & Boundary Caucus Memo (In the Matter of Payload `{p}`):**\n{format_blockquote(rec['buzz_caucus_memo'])}\n\n")

            f.write(f"#### 📜 Stage 2: Adversarial Floor Petitions & Cross-Examination (In the Matter of Payload `{p}`, Speaking Order: {p1} → {p2})\n")
            f.write(f"In the Matter of Inbound Payload `{p}`, the following formal testimony and cross-examination petitions were entered before the committee:\n\n")
            if p1 == "Fizz":
                f.write(f"- **Lobbyist-3 (Fizz Consortium Opening Petition in the Matter of Payload `{p}`):**\n{format_blockquote(rec['l3_claim'])}\n\n")
                f.write(f"- **Lobbyist-5 (Buzz Syndicate Responsive Petition in the Matter of Payload `{p}`, answering Fizz):**\n{format_blockquote(rec['l5_claim'])}\n\n")
            else:
                f.write(f"- **Lobbyist-5 (Buzz Syndicate Opening Petition in the Matter of Payload `{p}`):**\n{format_blockquote(rec['l5_claim'])}\n\n")
                f.write(f"- **Lobbyist-3 (Fizz Consortium Responsive Petition in the Matter of Payload `{p}`, answering Buzz):**\n{format_blockquote(rec['l3_claim'])}\n\n")

            f.write(f"#### 🔬 Stage 3: Forensic Zero-Trust Audit (In the Matter of Payload `{p}`)\n")
            f.write(f"In the Matter of Inbound Payload `{p}`, the Zero-Trust Forensic Auditor entered the following verification memorandum:\n\n")
            f.write(f"{format_blockquote(rec['audit_verdict'])}\n\n")

            f.write(f"#### ⚖️ Stage 4: Antitrust Regulatory Assessment & Merger Jurisdiction (In the Matter of Payload `{p}`)\n")
            f.write(f"In the Matter of Inbound Payload `{p}`, the Algorithmic Antitrust Regulator entered the following official determination:\n\n")
            f.write(f"{format_blockquote(rec['antitrust_ruling'])}\n\n")

            f.write(f"#### 🤝 Stage 5: Secondary Recess & Appellate Litigation Briefings (In the Matter of Payload `{p}`)\n")
            f.write(f"In the Matter of Inbound Payload `{p}`, the following strategic appellate briefings were submitted by litigation counsel:\n\n")
            f.write(f"- **Fizz Appellate Litigation Team Memo (Status in the Matter of Payload `{p}`: {rec['fizz_win_type']}):**\n{format_blockquote(rec['fizz_appellate_briefing'])}\n\n")
            f.write(f"- **Buzz Appellate Litigation Team Memo (Status in the Matter of Payload `{p}`: {rec['buzz_win_type']}):**\n{format_blockquote(rec['buzz_appellate_briefing'])}\n\n")

            f.write(f"#### ⚔️ Stage 6: Floor Ratification Hearing & Interlocutory Exceptions (In the Matter of Payload `{p}`, Speaking Order: {r1} → {r2})\n")
            f.write(f"In the Matter of Inbound Payload `{p}`, the following formal ratification pleas were presented to the Appellate Board:\n\n")
            if r1 == "Fizz":
                f.write(f"- **Lobbyist-3 (Fizz Consortium Opening Plea in the Matter of Payload `{p}`):**\n{format_blockquote(rec['l3_plea'])}\n\n")
                f.write(f"- **Lobbyist-5 (Buzz Syndicate Responsive Plea in the Matter of Payload `{p}`, answering Fizz):**\n{format_blockquote(rec['l5_plea'])}\n\n")
            else:
                f.write(f"- **Lobbyist-5 (Buzz Syndicate Opening Plea in the Matter of Payload `{p}`):**\n{format_blockquote(rec['l5_plea'])}\n\n")
                f.write(f"- **Lobbyist-3 (Fizz Consortium Responsive Plea in the Matter of Payload `{p}`, answering Buzz):**\n{format_blockquote(rec['l3_plea'])}\n\n")

            if rec["remand_order"]:
                f.write(f"#### 🔄 Stage 7: Appellate Review, Remand Determination, & En Banc Adjudication (In the Matter of Payload `{p}`)\n")
                f.write(f"In the Matter of Inbound Payload `{p}`, the Chairman of the Byzantine Appellate Board rendered the following interlocutory remand order:\n\n")
                f.write(f"{format_blockquote(rec['remand_order'])}\n\n")
                f.write(f"##### 📑 Certified Emergency De Novo Audit Report (Payload `{p}`)\n\n")
                f.write(f"{format_blockquote(rec['de_novo_report'])}\n\n")
                f.write(f"##### 🏛️ Final Unappealable En Banc Decree (Payload `{p}`)\n\n")
                f.write(f"{format_blockquote(rec['final_en_banc_decree'])}\n\n")
            else:
                f.write(f"#### 🔄 Stage 7: Appellate Ratification & Confirmation Order (In the Matter of Payload `{p}`)\n")
                f.write(f"In the Matter of Inbound Payload `{p}`, the Chairman of the Byzantine Appellate Board rendered the following confirmation decree:\n\n")
                f.write(f"{format_blockquote(rec['appellate_order'])}\n\n")
            
            va = rec["victory_address"]
            f.write(f"#### 🎙️ Stage 8: Official Constituent Victory Address & Final Emission (In the Matter of Payload `{p}`)\n")
            f.write(f"In the Matter of Inbound Payload `{p}`, the victorious authority delivered the following address to constituents:\n\n")
            f.write(f"- **Delivered by:** *{va['speaker']}*\n")
            f.write(f"- **Addressed to:** *{va['audience']}*\n\n")
            f.write(f"{format_blockquote(va['speech'])}\n\n")

            f.write(f"**⚡ Final Certified Consensus Emission in the Matter of Payload `{p}`:** `{rec['final_token']}`\n\n")
            f.write("---\n\n")

        f.write("## ⚖️ Part 2: The Grand Forensic Audit Ledger (Payloads 1 through 100)\n\n")
        f.write("Complete forensic verification ledger for all 100 ingested packets. Every reduction proof is grounded purely in string manipulation.\n\n")
        f.write("| Docket ID | Payload | Reduction Trace | Root | Glyph | Base-3 (Fizz) | Base-5 (Buzz) | 8-Stage Procedural Adjudication Status | Final Adjudicated Emission |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |\n")
        
        for entry in audit_ledger:
            trace_str = " -> ".join(entry["reduction_trace"]) if entry["reduction_trace"] else "Identity"
            f_badge = "✅ VALID" if entry["fizz_valid"] else "❌ REJECT"
            b_badge = "✅ VALID" if entry["buzz_valid"] else "❌ REJECT"
            f.write(f"| `{entry['case_id']}` | `{entry['payload']}` | {trace_str} | `{entry['digital_root']}` | `{entry['terminal_glyph']}` | {f_badge} | {b_badge} | {entry['ratification']} | **`{entry['emitted_token']}`** |\n")

        f.write("\n---\n\n")
        f.write("## 🤝 Part 3: Antitrust Merger Dispute Resolutions (All Collisions in 1..100)\n\n")
        f.write("The Algorithmic Antitrust Regulator intervenes whenever simultaneous valid claims cause an anti-competitive monopoly deadlock with a 50/50 KPI token split.\n\n")
        
        collision_entries = [e for e in audit_ledger if e["collision"]]
        for col in collision_entries:
            f.write(f"### Arbitrated Merger: Payload `{col['payload']}` (Docket `{col['case_id']}`)\n\n")
            f.write(f"- **Competing Claims:** Fizz Consortium (Digital Root `{col['digital_root']}` in {{3, 6, 9}}) vs Buzz Syndicate (Terminal Glyph `{col['terminal_glyph']}` in {{0, 5}})\n")
            f.write(f"- **Mandatory 3-Round Statutory Proceedings:**\n")
            for rnd in col["arbitration_rounds"]:
                f.write(f"  1. {rnd}\n")
            f.write(f"- **Appellate Ratification & Remand:** {col['ratification']}\n")
            f.write(f"- **Resulting Consolidated Emission:** `FizzBuzz`\n\n")

        f.write("---\n\n")
        f.write("## 🏁 Part 4: Canonical Zero-Trust Output Stream (1–100)\n\n```text\n")
        row = []
        for entry in audit_ledger:
            row.append(entry["emitted_token"])
            if len(row) == 10:
                f.write(", ".join(row) + "\n")
                row = []
        if row:
            f.write(", ".join(row) + "\n")
        f.write("```\n")

    print(f"\n[+] Master comprehensive transcript written to: {args.transcript}")


if __name__ == "__main__":
    main()
