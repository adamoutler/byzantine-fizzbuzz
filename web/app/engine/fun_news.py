"""
Foo Universal News (FUN) — Live Parliamentary Recess Broadcast Generator.
Streams a satirical newscast script during the post-docket recess countdown featuring:
- Newscaster teleprompter & camera cues ([CUE: ...])
- Mandatory opening: "This just in..."
- Story 1: Recap of Judge Baz's Ruling and the Constituent Victory Speech
- Mandatory transition: "...In other news..."
- Story 2: A random short parody headline in the style of The Onion
- Mandatory sign-off: "You're watching FUN."
"""

import asyncio
import random
import time
from typing import Dict, Any, List


OPENING_CUES: List[str] = [
    "[CUE: STUDIO CAMERA 1 - ANCHOR DESK, STRAIGHTENS PAPERS]",
    "[CUE: FUN BREAKING NEWS STINGER - RED TALLY LIGHT ON CAMERA 1]",
    "[CUE: ANCHOR DESK - ADJUSTS EARPIECE, LOOKS DEADPAN INTO CAMERA 1]",
    "[CUE: STUDIO WIDE SHOT ZOOMING TO ANCHOR DESK - TELEPROMPTER ROLLING]",
    "[CUE: LIVE FEED FROM COURTHOUSE STEPS TO STUDIO CAMERA 1]",
    "[CUE: DRAMATIC BRASS FANFARE FADES - ANCHOR CLEARS THROAT AT CAMERA 1]",
]

VICTORY_CUES: List[str] = [
    "[CUE: SPLIT-SCREEN GRAPHIC - PODIUM HIGHLIGHTS]",
    "[CUE: B-ROLL FOOTAGE OF CONFETTI CANNONS IN THE ROTUNDA]",
    "[CUE: LOWER-THIRD BANNER - 'VICTORY LAP ORATORY']",
    "[ANCHOR CUE: NODS SOLEMNLY AT TELEPROMPTER, TAPS PEN ON DESK]",
    "[CUE: COURTROOM SKETCH ARTIST RENDERING OF THE PODIUM]",
    "[ANCHOR CUE: RAISES ONE EYEBROW AT MONITOR 2]",
]

TRANSITION_CUES: List[str] = [
    "[ANCHOR CUE: SHUFFLES PAPERS, PIVOTS SMOOTHLY TO CAMERA 2]",
    "[CUE: OVER-THE-SHOULDER GRAPHIC SWAP - ANCHOR TURNS TO CAMERA 2]",
    "[ANCHOR CUE: SETS DOWN TRIBUNAL BRIEF, STARES DEADPAN INTO CAMERA 2]",
    "[CUE: NEWSROOM TICKER CHIME - ANCHOR SWIVELS CHAIR TO CAMERA 2]",
    "[ANCHOR CUE: ADJUSTS TIE, READS URGENT WIRE SLIP ON CAMERA 2]",
    "[CUE: SATELLITE FEED GLITCHES TO STUDIO CAMERA 2]",
]

OUTRO_CUES: List[str] = [
    "[ANCHOR CUE: HOLDS FIXED NEWSCASTER SMILE FOR 3 SECONDS - CUE OUTRO THEME]",
    "[CUE: STUDIO LIGHTS DIM TO BLUE - ANCHOR CAPS PEN AND STACKS PAPERS]",
    "[ANCHOR CUE: SALUTES TELEPROMPTER - CUE FUN NETWORK JINGLE]",
    "[CUE: CRANE SHOT PULLING BACK FROM ANCHOR DESK]",
    "[ANCHOR CUE: NODS GRAVELY AT CAMERA 1 - FADE TO COMMERCIAL BUMPER]",
]

ONION_PARODY_HEADLINES: List[str] = [
    "Local Integer 7 Reportedly 'Just Happy To Be Included' After Surviving Third Consecutive Audit Unclaimed.",
    "Area Man Arrested For Attempting To Smuggle Contraband Percentage Sign Through Courthouse Metal Detector.",
    "Suburban Dad Spends Four Hours Explaining Why Digital Root Reduction Builds Character While Family Eats Cold Dinner.",
    "Fizz Consortium Intern Fired After Accidentally Asking What Happens If You Simply Divide By Three.",
    "Nation's Prime Numbers Threaten General Strike Unless Granted Immediate Tax-Exempt Sovereign Status.",
    "Buzz Syndicate Lobbyist Seen Furiously Shredding Napkins With The Number Four Written On Them.",
    "Exhausted Number Zero Files Restraining Order Against Both Cartels Claiming Perpetual Harassment.",
    "Study Finds 94 Percent Of Courtroom Spectators Only Tuning In Hoping To See Bailiff Bar Tackle A Fraction.",
    "Judge Baz's Gavel Certified As Deadly Weapon In Twelve Contiguous Mathematical Jurisdictions.",
    "Antitrust Regulator Admits He Sometimes Flips A Commemorative Coin When Nobody Is Looking At The Ledger.",
    "Local Floating-Point Decimal Denied Entry To Upscale Downtown Bistro For Lacking Whole-Number Standing.",
    "Forensic Auditor Reveals Shocking Scandal After Discovering Number Nine Was Actually Three Threes In A Trench Coat.",
    "Disgraced Calculator Recalled After Factory Defect Allows Users To Press The Forbidden Slash Key.",
    "Tribune Of Free Digits Caught Driving Luxury Sedan Paid For By Big Prime Super-PAC.",
    "Court Stenographer Hospitalized With Severe Carpal Tunnel After Seventeenth Consecutive In-Camera Caucus.",
    "Poll Shows Majority Of Americans Still Unsure Whether Zero Counts As FizzBuzz Or A Cry For Help.",
    "Aggressive Base-3Evangelist Goes Door To Door Asking Neighbors If They Have Accepted Digital Root Six.",
    "Buzz Boundary Inspector Confesses He Never Even Looks At The First Twelve Digits Of Any Number.",
    "High-Ranking Fizz Strategist Caught On Hot Mic Admitting He Has To Count On His Fingers Past Eight.",
    "Municipal Water Supply Temporarily Replaced With Sparkling Cider Following Aggressive Fizz Consortium Takeover.",
    "Court Historian Discovers Ancient Scroll Proving Pythagoras Was Once Held In Contempt By Judge Baz.",
    "Local Teen Suspended For Writing Prohibited Long-Division Symbol On High School Bathroom Stall.",
    "Appellate Litigation Team Bills Client Four Thousand Hours For Nodding Thoughtfully During Recess.",
    "Scientists Warn Global Supply Of Unclaimed Odd Integers Could Run Out By Late Thursday Afternoon.",
    "Bailiff Bar Announces Mandatory Ankle Monitors For All Numbers Ending In Suspiciously Round Glyphs.",
    "Area Man's Financial Portfolio Collapses After Investing Life Savings In Collectible Imaginary Numbers.",
    "Whistleblower Alleges FizzBuzz Conglomerate Merger Was Negotiated Entirely Over lukewarm Courthouse Pretzels.",
    "Roman Numeral XIVDetained At Border After Refusing To Declare Its Terminal Arabic Glyph.",
    "National Weather Service Issues Severe Rhetoric Advisory As Lobbyist-3 Approaches The Microphone.",
    "Local Toddler Impresses Tribunal By Successfully Summing Digits Of Twelve Without Hiring Legal Counsel.",
    "Pentagon Confirms Billions Spent Developing Stealth Integer That Appears Divisible By Five On Radar.",
    "Wellness Influencer Claims Drinking Alkaline Water Reduces Your Personal Digital Root To A Calm Three.",
    "Cafeteria Running Critically Low On Gavel Polish As Appellate Remand Petitions Reach Record High.",
    "Retired Remainder Living Under Witness Protection In Rural Nebraska After Testifying Against Modulo Cartel.",
    "Wall Street Panic Ensues After Rumor Spreads That Fifteen Might Demerger Back Into Separate Syllables.",
    "Survey Finds Four Out Of Five Mathematicians Prefer Staring Blankly Out Window To Attending Caucus.",
    "Judge Baz Rejects Motion To Allow Abacus In Courtroom As 'A Slippery Slope Toward Long Division.'",
    "Stubborn Palindrome Refuses To Tell Bailiff Which End Of Its Payload Is The Actual Terminal Glyph.",
    "Local Golden Retriever Appointed Honorary Magistrate After Barking Exactly Three Times At Payload Nine.",
    "Historians Confirm Great Depression Was Triggered When Wall Street Tried To Divide Zero By Zero.",
    "Buzz Syndicate Unveils Bold Rebrand Positioning Terminal Glyph Five As 'The People's Half-Ten.'",
    "Overworked GPU Fan In Server Closet Files Formal Grievance Demanding Longer Parliamentary Recesses.",
    "Archaeologists Uncover Prehistoric Cave Painting Depicting Early Hominids Arguing Over Number Fifteen.",
    "Newscaster Quietly Wonders If Anyone Reads The Scrolling Ticker Or Just Watches The Recess Countdown.",
    "City Council Votes Unanimously To Rename Main Street 'Recursive Digital Root Boulevard.'",
    "Strict Zero-Trust Parent Demands Newborn Baby Prove Its Base-10 Bounds Before Receiving Birth Certificate.",
    "Bored Jury Foreperson Caught Playing Tic-Tac-Toe On Official Stare Decisis Parchment.",
    "Fibonacci Sequence Placed On Administrative Watchlist Following Suspiciously Coordinated Growth Pattern.",
    "Local Man Still Waiting For High School Algebra Teacher To Explain When He Would Ever Need This.",
    "Emergency Plumber Called To Fizz Chambers After Strategists Flood Room With Unsubstantiated Claims.",
]


class FooUniversalNewsDesk:
    """Generates and streams the Foo Universal News (FUN) recap script during Parliamentary Recess."""

    def __init__(self) -> None:
        self._headline_deck: List[str] = []

    def _next_parody_headline(self) -> str:
        """Draws a random Onion-style parody headline without repeating until the deck is exhausted."""
        if not self._headline_deck:
            self._headline_deck = list(ONION_PARODY_HEADLINES)
            random.shuffle(self._headline_deck)
        return self._headline_deck.pop()

    @staticmethod
    def _first_sentence(text: str, fallback: str) -> str:
        cleaned = (text or "").strip().replace("\n", " ")
        if not cleaned:
            return fallback
        for sep in (". ", "! ", "? "):
            if sep in cleaned:
                idx = cleaned.find(sep)
                return cleaned[: idx + 1].strip()
        return cleaned

    def build_recap_script(self, transcript: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds the complete Foo Universal News (FUN) broadcast script with newscaster cues,
        Story 1 (Judge Baz's Ruling + Victory Speech), and Story 2 (random Onion parody headline).
        """
        case_id = transcript.get("case_id", "BZ-2026-0000")
        payload = transcript.get("payload", "0")
        final_token = transcript.get("final_token", payload)
        is_mistrial = bool(transcript.get("mistrial") or final_token == "Mistrial")

        open_cue = random.choice(OPENING_CUES)
        victory_cue = random.choice(VICTORY_CUES)
        trans_cue = random.choice(TRANSITION_CUES)
        outro_cue = random.choice(OUTRO_CUES)
        parody_headline = self._next_parody_headline()

        if is_mistrial:
            interrupted_phase = transcript.get("interrupted_phase", "floor deliberations")
            retrial_before = transcript.get("retrial_before_max_increase", "the next ceiling expansion")
            story_one = (
                f"This just in... pandemonium erupted moments ago on Docket {case_id} concerning Inbound Payload '{payload}' "
                f"when a catastrophic loss of inference quorum severed testimony during {interrupted_phase}. "
                f"{victory_cue} Following Bailiff Bar's emergency proclamation, Presiding Magistrate Judge Baz struck the partial record, "
                f"declared an official MISTRIAL without prejudice, and pre-empted any victory speech by ordering mandatory de novo retrial "
                f"prior to statutory ceiling expansion beyond Docket #{retrial_before}."
            )
        else:
            judge_summary = self._first_sentence(
                transcript.get("judge_baz_order", ""),
                f"Judge Baz brought down the gavel to certify consensus token '{final_token}'."
            )
            victory_summary = self._first_sentence(
                transcript.get("victory_address", ""),
                f"The winning faction immediately took the podium to celebrate '{final_token}' supremacy."
            )
            if final_token == "Fizz":
                orator_label = "the Director General of the Fizz Consortium"
            elif final_token == "Buzz":
                orator_label = "the High Chancellor of the Buzz Syndicate"
            elif final_token == "FizzBuzz":
                orator_label = "the Joint Co-CEOs of the FizzBuzz Conglomerate"
            else:
                orator_label = "the Tribune of the Free Independent Digits"

            story_one = (
                f"This just in... the gavel has fallen on Docket {case_id} for Inbound Payload '{payload}', "
                f"where Presiding Magistrate Judge Baz certified final consensus emission '{final_token}'—ruling from the bench: "
                f"\"{judge_summary}\" "
                f"{victory_cue} Moments later, {orator_label} seized the courtroom microphone for a triumphant victory address, declaring: "
                f"\"{victory_summary}\""
            )

        full_script = (
            f"{open_cue} {story_one}\n\n"
            f"{trans_cue} ...In other news... {parody_headline}\n\n"
            f"{outro_cue} You're watching FUN."
        )

        return {
            "script": full_script,
            "story_one": story_one,
            "parody_headline": parody_headline,
            "case_id": case_id,
            "payload": payload,
            "final_token": final_token,
        }


fun_news_desk = FooUniversalNewsDesk()
