"""
"Meanwhile, in the Courtroom..." interlude generator and 52-example scenario pool
for FizzBuzz: The Byzantine Inquisition.

Used by the courtroom LLM right before Bailiff Bar calls deliberations back to order:
1. After Private Chambers (Phase 1 -> Phase 2): Extended 3-sentence courtroom scene
   with multiple concurrent bureaucratic antics while factions were locked in chambers.
2. After Appellate Team Conference (Phase 5 -> Phase 6): Brief 1-sentence courtroom
   observation during the short appellate sidebar.
"""

import random
from typing import List, Tuple, Dict

# 52 distinct examples of absurd, bureaucratic, and ceremonial courtroom activity
COURTROOM_MEANWHILE_EXAMPLES: List[str] = [
    # 1-10: Judge Baz at the Mahogany Bench
    "Judge Baz is methodically polishing his solid mahogany gavel with artisanal beeswax while glaring suspiciously at the courtroom wall clock.",
    "Judge Baz has just threatened a squeaky ceiling fan above the jury box with summary contempt of court if it completes one more unauthorized rotation.",
    "Judge Baz is reviewing a 400-page emergency motion on whether the digit '0' qualifies for tax-exempt charitable status under the Charter of 1642.",
    "Judge Baz is attempting to solve the morning newspaper crossword puzzle in heavy fountain pen while refusing to read any numbered clue divisible by 3 or 5.",
    "Judge Baz has summoned a facilities technician to the bench to demand proof that the courtroom thermostat does not use floating-point division.",
    "Judge Baz is adjusting his velvet judicial robes and practicing his most devastating overruled eyebrow raise in a small brass desk mirror.",
    "Judge Baz is lecturing an empty witness chair on the moral failings of hardware division instructions in modern silicon architectures.",
    "Judge Baz has ordered the courtroom sketch artist to redraw his jawline with at least forty percent more statutory gravitas.",
    "Judge Baz is sipping lukewarm chamomile tea from a porcelain mug inscribed 'World's Most Unappealable Magistrate' while muttering about K-Street billing rates.",
    "Judge Baz is signing a stack of routine bench warrants for rogue Remainder Operators spotted loitering near the courthouse steps.",

    # 11-20: The Court Clerk & Chancery Red Tape
    "The Court Clerk is furiously stamping 'RECEIVED IN TRIPLICATE' in indelible purple ink onto a stack of blank manila folders just to keep his wrist warmed up.",
    "The Court Clerk has just rejected a paralegal's coffee order at the chancery window for lacking a notarized Form BZ-904-C beverage requisition seal.",
    "The Court Clerk is using a brass micrometer to verify that all thirty-six No. 2 pencils on the clerk's desk are sharpened to the exact same statutory length.",
    "The Court Clerk is reorganizing the courthouse paperclip ledger by serial number and issuing a stern administrative citation to a bent staple.",
    "The Court Clerk is meticulously feeding expired procedural motions into a hand-cranked crosscut shredder that only accepts documents in increments of ten.",
    "The Court Clerk is replacing the purple ribbon in the official chancery date-stamper while wearing white cotton archival gloves.",
    "The Court Clerk is conducting an emergency audit of the courtroom water pitcher after someone alleged the ice cubes were partitioned unequally.",
    "The Court Clerk is taping a laminated notice to the podium warning counsel that excessive Latin pronunciation will incur a five-credit surcharge.",
    "The Court Clerk is alphabetizing a crate of evidentiary sticky notes while humming a solemn Gregorian chant.",
    "The Court Clerk is calibrating the official courtroom hourglass by counting falling grains of sand one character at a time.",

    # 21-30: The Court Historian (Brother Eusebius)
    "Brother Eusebius, the Court Historian, is frantically dusting a 14th-century vellum scroll with a peacock feather after sneezing near the sacred ledger.",
    "The Court Historian is muttering under his breath in medieval Latin about the Great Modulo Heresy of 1894 while sharpening his goose-quill pen.",
    "The Court Historian is applying gold leaf to a decorative capital letter in the margins of last week's docket transcript.",
    "The Court Historian has misplaced his brass reading spectacles and is mistakenly reading a takeout menu into the preliminary historical footnotes.",
    "The Court Historian is lecturing a bewildered courtroom intern on why the integer 17 was briefly exiled from Constantinople in 1142.",
    "The Court Historian is carefully unrolling a forty-foot parchment genealogy chart tracing the ancestral digital roots of the current docket.",
    "The Court Historian is sealing a leather-bound volume of prior mistrials with dripping crimson candle wax and a heavy signet ring.",
    "The Court Historian is comparing two nearly identical smudges on a 1997 transcript through a jeweler's loupe to determine if one was an illicit percent sign.",
    "The Court Historian is whispering a protective benediction over the SQLite database server rack in the corner of the chancery.",
    "The Court Historian is earnestly debating himself on whether Roman numerals should be readmitted as amicus curiae.",

    # 31-40: The Forensic Auditor & Antitrust Regulator
    "The Forensic Auditor is wiping down his wooden abacus with isopropyl alcohol to ensure zero cross-contamination between Base-3 and Base-5 beads.",
    "The Forensic Auditor is sweeping the counsel tables with a handheld Geiger counter calibrated to click whenever someone thinks about long division.",
    "The Forensic Auditor is double-checking his single-digit addition lookup table with a magnifying glass to confirm that 2 plus 4 still equals 6.",
    "The Antitrust Regulator is calculating the Herfindahl-Hirschman market concentration index of the snacks inside the courthouse vending machine.",
    "The Antitrust Regulator is serving a preemptive cease-and-desist subpoena on a pair of conjoined twin pretzels for unauthorized horizontal integration.",
    "The Antitrust Regulator is drafting a 90-page divestiture order against the courthouse cafeteria for bundling soup and half a sandwich without regulatory clearance.",
    "The Forensic Auditor and the Antitrust Regulator are engaged in a tense, whispered dispute over who gets to use the courtroom's only green highlighter.",
    "The Forensic Auditor is testing the acoustic resonance of the witness stand to make sure no hidden modulo frequencies can echo off the marble walls.",
    "The Antitrust Regulator is measuring the exact square footage of the Fizz and Buzz counsel tables with a laser level to prevent territorial monopoly.",
    "The Forensic Auditor is sealing a suspect pocket calculator inside an electrostatic evidence bag labeled 'EXHIBIT X: CONTRABAND ALU'.",
    "The Byzantine Fault Inquisitor is scanning the Forensic Auditor's espresso mug through a glowing holographic monocle to check for K-Street bribery residue.",
    "The Byzantine Fault Inquisitor is interrogating a potted fern near the jury box on suspicion of acting as a rogue fourth consensus node.",
    "The Byzantine Fault Inquisitor is polishing his crimson 2-of-3 Supermajority stamp while muttering 'Nobody expects the Byzantine Fault Inquisition.'",

    # 41-52: Bailiff Bar, Gallery Spectators, Interns & FUN-TV Crew
    "Near the magnetometer checkpoint, Bailiff Bar is confiscating a contraband slide rule from a nervous math graduate student in the visitor gallery.",
    "In the back row of the public gallery, three unpaid K-Street interns are playing rock-paper-scissors to decide who has to carry Lobbyist-3's fifty-pound briefcase.",
    "A cameraman from Foo Universal News (FUN-TV) is frantically untangling forty feet of XLR cable after tripping over the courtroom brass spitoon.",
    "Chip Davenport of Foo Universal News is in the press row applying a fresh cloud of hairspray while silently mouthing breaking-news adjectives to himself.",
    "In the spectator gallery, a delegation of Free Independent Prime Numbers is quietly holding up small cardboard placards reading 'INDIVISIBLE AND PROUD'.",
    "A junior Buzz Syndicate paralegal is frantically erasing a doodle of a pentagon from the courtroom whiteboard before Judge Baz notices.",
    "The courtroom stenographer is stretching her fingers and applying wrist braces after transcribing seventeen consecutive uses of the word 'hereinafter'.",
    "A courthouse janitor has wandered up to the brass rail with a mop bucket, paused to read the inbound payload on the docket board, and shaken his head in disbelief.",
    "Two elderly spectators in the gallery are trading collectible courtroom trading cards featuring famous historical mistrials.",
    "An over-caffeinated Fizz Consortium clerk is pacing near the water cooler rehearsing three-syllable synonyms for 'tripartite'.",
    "A rogue carrier pigeon wearing a tiny velvet barrister wig has landed on the chandelier above the bench, drawing suspicious glares from Bailiff Bar.",
    "The courthouse vending machine in the hallway just ate a five-credit voucher, prompting the Antitrust Regulator to open a formal price-fixing inquiry."
]


def _lower_lead(sentence: str) -> str:
    """Lowercases the first character of a sentence unless it begins with a proper name."""
    if sentence.startswith(("Judge Baz", "Brother Eusebius", "Chip Davenport", "Bailiff Bar")):
        return sentence
    return sentence[0].lower() + sentence[1:]


def sample_courtroom_examples(count: int, exclude: List[str] | None = None) -> List[str]:
    """Randomly samples `count` distinct courtroom examples from the 52-item pool."""
    excluded_set = set(exclude or [])
    pool = [ex for ex in COURTROOM_MEANWHILE_EXAMPLES if ex not in excluded_set]
    if len(pool) < count:
        pool = list(COURTROOM_MEANWHILE_EXAMPLES)
    return random.sample(pool, k=min(count, len(pool)))


def build_post_chambers_interlude_prompt(
    case_id: str,
    payload: str,
    fizz_rounds: int,
    buzz_rounds: int,
) -> Tuple[List[Dict[str, str]], str, List[str]]:
    """
    Builds the LLM prompt, deterministic fallback text, and sampled examples for the
    EXTENDED courtroom interlude right after Private Chambers (Phase 1B -> Phase 2).
    Because the factions have been locked away in multi-round private chambers,
    there is MORE going on in the courtroom (3 sentences covering multiple scenes).
    """
    sampled = sample_courtroom_examples(6)
    examples_block = "\n".join(f"  - {ex}" for ex in sampled)
    total_rounds = fizz_rounds + buzz_rounds

    messages = [
        {
            "role": "system",
            "content": (
                "You are The Court Clerk narrating a live, deadpan comedic 'Meanwhile, in the courtroom...' interlude "
                f"for Docket {case_id} (Inbound Payload '{payload}'). "
                f"While the Fizz Consortium and Buzz Syndicate were locked away behind closed doors for {total_rounds} rounds "
                "of lengthy private chamber deliberations, plenty of absurd bureaucratic activity has been unfolding on the courtroom floor. "
                "Below are 6 examples of the kind of courtroom commotion happening right now (drawn from our 52-scenario courtroom manual):\n"
                f"{examples_block}\n\n"
                "Write 3 vivid, hilarious, deadpan sentences starting with 'Meanwhile, in the courtroom,' that weave together "
                "2 or 3 of these courtroom goings-on (or closely inspired variations) to show all the restless activity at the bench, "
                "chancery desk, and gallery just before Bailiff Bar bangs the gavel to call the court back to order."
                "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                "Output valid JSON with keys in this exact order:\n"
                "- 'speech': Your 3-sentence comedic courtroom observation starting with 'Meanwhile, in the courtroom,'.\n"
                "- 'action': 'log_extended_recess_commotion'.\n"
                "- 'status': Short 2-to-5 word public social media status (e.g. 'Logging courtroom commotion')."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Narrate the 3-sentence 'Meanwhile, in the courtroom,' scene after the {total_rounds}-round private chamber deliberations "
                f"for Docket {case_id} (payload '{payload}')."
            ),
        },
    ]

    fallback_text = (
        f"Meanwhile, in the courtroom, during the lengthy closed-door deliberations on payload '{payload}', "
        f"{_lower_lead(sampled[0])} "
        f"At the same time, {_lower_lead(sampled[1])} "
        f"In the rear of the chamber, {_lower_lead(sampled[2])}"
    )
    return messages, fallback_text, sampled


def build_post_appellate_interlude_prompt(
    case_id: str,
    payload: str,
    exclude_examples: List[str] | None = None,
) -> Tuple[List[Dict[str, str]], str, List[str]]:
    """
    Builds the LLM prompt, deterministic fallback text, and sampled examples for the
    BRIEF courtroom interlude right after the Appellate Litigation Team briefings (Phase 5 -> Phase 6).
    Because the appellate conference was a quick sidebar compared to private chambers,
    this interlude is shorter and punchier (1 sentence).
    """
    sampled = sample_courtroom_examples(3, exclude=exclude_examples)
    examples_block = "\n".join(f"  - {ex}" for ex in sampled)

    messages = [
        {
            "role": "system",
            "content": (
                "You are The Court Clerk narrating a brief, deadpan comedic 'Meanwhile, in the courtroom...' interlude "
                f"for Docket {case_id} (Inbound Payload '{payload}'). "
                "The Appellate Litigation Teams just finished their quick sidebar briefing with the floor lobbyists. "
                "Because this appellate huddle was much shorter than the earlier private chambers, only a quick moment transpired in the courtroom. "
                "Below are 3 examples of courtroom activity from our 52-scenario courtroom manual:\n"
                f"{examples_block}\n\n"
                "Write 1 crisp, deadpan comedic sentence starting with 'Meanwhile, in the courtroom,' describing one quick courtroom moment "
                "inspired by the examples above, happening right before Bailiff Bar calls the deliberations back to order."
                "\n\n[STRUCTURED OUTPUT SCHEMA]:\n"
                "Output valid JSON with keys in this exact order:\n"
                "- 'speech': Your 1-sentence comedic courtroom observation starting with 'Meanwhile, in the courtroom,'.\n"
                "- 'action': 'log_brief_sidebar_activity'.\n"
                "- 'status': Short 2-to-5 word public social media status (e.g. 'Stamping appellate sidebar notes')."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Narrate the 1-sentence 'Meanwhile, in the courtroom,' moment after the brief appellate conference "
                f"for Docket {case_id} (payload '{payload}')."
            ),
        },
    ]

    fallback_text = (
        f"Meanwhile, in the courtroom, during the brief appellate counsel huddle on payload '{payload}', "
        f"{_lower_lead(sampled[0])}"
    )
    return messages, fallback_text, sampled
