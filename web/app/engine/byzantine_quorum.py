"""
3-Node Byzantine Fault-Tolerant (BFT) Consensus Quorum Engine for FizzBuzz: The Byzantine Inquisition.

The 3-Member Byzantine Consensus Panel consists of:
  1. Node 1: The Forensic Auditor (Cryptographic Special Master)
  2. Node 2: The Antitrust Regulator (Director of Algorithmic Competition)
  3. Node 3: The Byzantine Fault Inquisitor (Grand Inquisitor of Faults & BFT Quorum Marshal)

To make the courtroom a genuine Byzantine Fault-Tolerant consensus system (2f + 1 quorum out of 3
independent verification nodes, plus Judge Baz as the 4th en banc signature node for 3f + 1 = 4):
- All 3 nodes cast an explicit `consensus_vote` ('Fizz', 'Buzz', 'FizzBuzz', or 'Digit').
- On ~40% of dockets, exactly 1 of the 3 nodes suffers a comedic "Byzantine Fault" (e.g. K-Street
  bribery, cosmic ray bit-flip on the wooden abacus, or paranoid regulatory hallucination) and casts
  a treacherous/corrupted vote.
- The remaining 2 honest nodes outvote the faulty node 2-to-1, demonstrating live 2-of-3 Byzantine
  Fault Tolerance on the courtroom floor!
"""

import random
from typing import Dict, List, Optional, Tuple


VoteToken = str  # "Fizz" | "Buzz" | "FizzBuzz" | "Digit"

AUDITOR_BYZANTINE_FAULTS: List[str] = [
    "a stray cosmic ray struck your wooden abacus mid-calculation, flipping two Base-3 beads into an unauthorized configuration",
    "you accidentally drank from a suspicious 'Complimentary K-Street Espresso' mug left on the audit bench, temporarily clouding your lookup table",
    "your electrostatic Geiger counter picked up static interference from Judge Baz's velvet robes, scrambling your digital root tally",
    "a rogue sticky note attached to the docket folder tricked you into reading the payload upside-down",
    "you became so enraged by a suspected floating-point rounding smell in the hallway that you protest-voted against the actual math",
]

REGULATOR_BYZANTINE_FAULTS: List[str] = [
    "a mysterious gift basket of artisanal sourdough pretzels arrived at the regulatory desk with an unsigned K-Street ribbon, swaying your market ruling",
    "you suffered acute Herfindahl-Hirschman Index vertigo and decided the mathematically valid outcome was an illegal cartel monopoly that must be blocked",
    "you accidentally read last week's consent decree upside-down while glaring at the courthouse vending machine",
    "an over-caffeinated antitrust intern swapped your Single-Domain Clearance stamp with a hostile Divestiture Injunction stamp",
    "you became convinced that the winning faction was secretly bundling soup and half a sandwich without FTC clearance",
]

INQUISITOR_BYZANTINE_FAULTS: List[str] = [
    "your glowing holographic monocle fogged up from chamomile tea steam, causing you to suspect a Knights Templar cipher in the payload",
    "you spotted a pigeon on the courtroom chandelier and became convinced it was signalling a secret K-Street remainder conspiracy",
    "you temporarily mistook the honest agreement of the Forensic Auditor and Antitrust Regulator for a suspiciously synchronized cartel plot",
]


def true_vote_for_docket(fizz_valid: bool, buzz_valid: bool) -> VoteToken:
    """Returns the ground-truth consensus vote category for the payload."""
    if fizz_valid and buzz_valid:
        return "FizzBuzz"
    if fizz_valid:
        return "Fizz"
    if buzz_valid:
        return "Buzz"
    return "Digit"


def pick_corrupted_vote(honest_vote: VoteToken) -> VoteToken:
    """Picks a distinct corrupted vote for a node experiencing a Byzantine fault."""
    candidates: List[VoteToken] = [v for v in ("Fizz", "Buzz", "FizzBuzz", "Digit") if v != honest_vote]
    return random.choice(candidates)


def plan_byzantine_quorum(
    fizz_valid: bool,
    buzz_valid: bool,
    fault_probability: float = 0.42,
    force_fault_node: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    """
    Plans the 3-node Byzantine Consensus Panel votes for a docket.
    Guarantees that at least 2 of the 3 nodes cast `honest_vote`, so the 2-of-3 BFT
    supermajority ALWAYS equals `honest_vote`.
    """
    honest_vote = true_vote_for_docket(fizz_valid, buzz_valid)

    if force_fault_node is not None:
        faulty_node = force_fault_node if force_fault_node in ("auditor", "regulator", "inquisitor") else None
    elif random.random() < fault_probability:
        faulty_node = random.choices(
            population=["auditor", "regulator", "inquisitor"],
            weights=[0.42, 0.43, 0.15],
            k=1,
        )[0]
    else:
        faulty_node = None

    corrupted_vote = pick_corrupted_vote(honest_vote) if faulty_node else honest_vote

    if faulty_node == "auditor":
        fault_reason = random.choice(AUDITOR_BYZANTINE_FAULTS)
        auditor_vote = corrupted_vote
        regulator_vote = honest_vote
        inquisitor_vote = honest_vote
        fault_code = "forensic_auditor_fault"
        quorum_tally = "2_of_3_fault_contained"
        inquisitor_action = "outvote_byzantine_traitor"
    elif faulty_node == "regulator":
        fault_reason = random.choice(REGULATOR_BYZANTINE_FAULTS)
        auditor_vote = honest_vote
        regulator_vote = corrupted_vote
        inquisitor_vote = honest_vote
        fault_code = "antitrust_regulator_fault"
        quorum_tally = "2_of_3_fault_contained"
        inquisitor_action = "outvote_byzantine_traitor"
    elif faulty_node == "inquisitor":
        fault_reason = random.choice(INQUISITOR_BYZANTINE_FAULTS)
        auditor_vote = honest_vote
        regulator_vote = honest_vote
        inquisitor_vote = corrupted_vote
        fault_code = "inquisitor_self_dissent"
        quorum_tally = "2_of_3_fault_contained"
        inquisitor_action = "concede_to_honest_supermajority"
    else:
        fault_reason = None
        auditor_vote = honest_vote
        regulator_vote = honest_vote
        inquisitor_vote = honest_vote
        fault_code = "none"
        quorum_tally = "3_of_3_unanimous"
        inquisitor_action = "seal_unanimous_quorum"

    return {
        "honest_vote": honest_vote,
        "faulty_node": faulty_node,
        "fault_reason": fault_reason,
        "fault_code": fault_code,
        "auditor_vote": auditor_vote,
        "regulator_vote": regulator_vote,
        "inquisitor_vote": inquisitor_vote,
        "quorum_tally": quorum_tally,
        "inquisitor_action": inquisitor_action,
    }


def build_inquisitor_prompt(
    case_id: str,
    payload: str,
    root: str,
    glyph: str,
    fizz_valid: bool,
    buzz_valid: bool,
    provisional_token: str,
    quorum_plan: Dict[str, Optional[str]],
    auditor_speech: str,
    regulator_speech: str,
) -> Tuple[List[Dict[str, str]], str]:
    """
    Builds the LLM messages and deterministic fallback speech for Node #3 of the
    Byzantine Consensus Panel: The Byzantine Fault Inquisitor.
    """
    honest_vote = quorum_plan["honest_vote"] or "Digit"
    faulty_node = quorum_plan["faulty_node"]
    fault_reason = quorum_plan["fault_reason"] or ""
    auditor_vote = quorum_plan["auditor_vote"] or honest_vote
    regulator_vote = quorum_plan["regulator_vote"] or honest_vote
    inquisitor_vote = quorum_plan["inquisitor_vote"] or honest_vote
    quorum_tally = quorum_plan["quorum_tally"] or "3_of_3_unanimous"
    fault_code = quorum_plan["fault_code"] or "none"
    inquisitor_action = quorum_plan["inquisitor_action"] or "seal_unanimous_quorum"

    display_token = provisional_token

    if faulty_node == "auditor":
        scenario_directive = (
            f"BYZANTINE FAULT ALERT ON NODE #1 (THE FORENSIC AUDITOR): "
            f"The Forensic Auditor just suffered a Byzantine fault ({fault_reason}) and cast a corrupted vote for '{auditor_vote}'! "
            f"Meanwhile, Node #2 (The Antitrust Regulator) voted honestly for '{regulator_vote}' (token '{display_token}'). "
            f"In 2 dramatic, deadpan inquisitorial sentences: (1) denounce the Forensic Auditor's '{auditor_vote}' vote as a compromised Byzantine fault "
            f"while praising the Antitrust Regulator's honest '{regulator_vote}' vote, and (2) cast your deciding 3rd quorum vote for '{inquisitor_vote}' "
            f"to lock in a 2-of-3 Byzantine Fault-Tolerant Supermajority for token '{display_token}'!"
        )
        fallback_text = (
            f"Heresy detected on Node #1! The Forensic Auditor's rogue vote for '{auditor_vote}' is hereby flagged as a compromised Byzantine fault "
            f"({fault_reason}). By joining the Antitrust Regulator's honest vote, I cast the deciding 3rd vote for '{inquisitor_vote}', "
            f"containing the fault and sealing a 2-of-3 Byzantine Supermajority for token '{display_token}'!"
        )
    elif faulty_node == "regulator":
        scenario_directive = (
            f"BYZANTINE FAULT ALERT ON NODE #2 (THE ANTITRUST REGULATOR): "
            f"Node #1 (The Forensic Auditor) voted honestly for '{auditor_vote}' (token '{display_token}'), "
            f"but Node #2 (The Antitrust Regulator) just suffered a Byzantine fault ({fault_reason}) and cast a rogue vote for '{regulator_vote}'! "
            f"In 2 dramatic, deadpan inquisitorial sentences: (1) expose and quarantine the Antitrust Regulator's '{regulator_vote}' vote as a Byzantine fault, "
            f"and (2) cast your deciding 3rd quorum vote alongside the Forensic Auditor for '{inquisitor_vote}', locking in a 2-of-3 Byzantine Fault-Tolerant Supermajority for token '{display_token}'!"
        )
        fallback_text = (
            f"Byzantine corruption exposed on Node #2! The Antitrust Regulator's deviant vote for '{regulator_vote}' is quarantined as a faulty node "
            f"({fault_reason}). Standing with the Forensic Auditor, I cast the deciding 3rd quorum vote for '{inquisitor_vote}', "
            f"locking in a 2-of-3 Byzantine Fault-Tolerant Supermajority for token '{display_token}'!"
        )
    elif faulty_node == "inquisitor":
        scenario_directive = (
            f"COMEDIC SELF-FAULT TWIST ON NODE #3 (YOU, THE INQUISITOR): "
            f"Both Node #1 (The Forensic Auditor) and Node #2 (The Antitrust Regulator) already voted honestly for '{honest_vote}' (token '{display_token}'). "
            f"However, {fault_reason}, tempting you to cast a paranoid dissenting vote for '{inquisitor_vote}'! "
            f"In 2 deadpan comedic sentences: (1) voice your paranoid suspicion and cast your dissenting vote for '{inquisitor_vote}', "
            f"and (2) immediately acknowledge that under the tribunal's 2-of-3 Byzantine Fault-Tolerant protocol, the Auditor and Regulator's 2-to-1 honest supermajority "
            f"outvotes your own dissent and locks in token '{display_token}'!"
        )
        fallback_text = (
            f"Wait—because {fault_reason}, I cast a suspicious dissenting vote for '{inquisitor_vote}'! "
            f"Nevertheless, under our sacred 2-of-3 Byzantine Fault-Tolerant protocol, the Forensic Auditor and Antitrust Regulator's 2-to-1 honest supermajority "
            f"automatically outvotes my own paranoia and certifies token '{display_token}'."
        )
    else:
        scenario_directive = (
            f"UNANIMOUS 3-OF-3 BYZANTINE QUORUM: "
            f"Both Node #1 (The Forensic Auditor) and Node #2 (The Antitrust Regulator) withstood the lobbyists' floor bluffs and voted honestly for '{honest_vote}' (token '{display_token}'). "
            f"In 2 authoritative inquisitorial sentences: (1) certify that zero internal validator faults, K-Street bribes, or cosmic bit-flips corrupted the panel on payload '{payload}' "
            f"(Digital Root '{root}', Terminal Glyph '{glyph}'), and (2) cast the 3rd concurring vote for '{inquisitor_vote}' to seal a 3-of-3 Unanimous Byzantine Consensus for token '{display_token}'!"
        )
        fallback_text = (
            f"Inquisitorial sweep of Docket {case_id} confirms zero cosmic bit-flips or K-Street bribery across our verification nodes for payload '{payload}' "
            f"(Digital Root '{root}', Terminal Glyph '{glyph}'). "
            f"I cast the 3rd concurring vote for '{inquisitor_vote}', sealing a 3-of-3 Unanimous Byzantine Consensus for token '{display_token}'."
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are The Byzantine Fault Inquisitor (Node #3 of the 3-Member Byzantine Consensus Panel, alongside "
                "Node #1 The Forensic Auditor and Node #2 The Antitrust Regulator). "
                "Your duty is to hunt for Byzantine faults (treachery, K-Street bribes, cosmic ray bit-flips, and lobbyist bluffs), "
                "cast the 3rd consensus vote, and announce the final 2-of-3 or 3-of-3 Byzantine Quorum tally.\n\n"
                + scenario_directive
                + "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                "Output valid JSON with keys in this exact order:\n"
                "- 'speech': Your 2-sentence inquisitorial Byzantine consensus finding and quorum tally.\n"
                f"- 'quorum_tally': '{quorum_tally}'.\n"
                f"- 'fault_detected': '{fault_code}'.\n"
                f"- 'consensus_vote': '{inquisitor_vote}'.\n"
                f"- 'action': '{inquisitor_action}'.\n"
                "- 'status': Short 2-to-5 word public social media status (e.g. 'Purging Byzantine faults')."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Payload: '{payload}' (Root: '{root}', Glyph: '{glyph}').\n"
                f"Node #1 (Forensic Auditor) voted '{auditor_vote}': {auditor_speech}\n"
                f"Node #2 (Antitrust Regulator) voted '{regulator_vote}': {regulator_speech}\n"
                "Deliver your Byzantine Fault Inquisition report and 3-node quorum tally."
            ),
        },
    ]

    return messages, fallback_text
