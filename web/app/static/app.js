let ws = null;
let reconnectTimer = null;
let autoScroll = true;
let userScrolledUp = false;

// Active tracking
let currentDocketId = null;
let currentPhaseIndex = null;
let activeSpeechCard = null;
let activeSpeechBody = null;
let lastSpeechCard = null;
let lastSpeechBody = null;
let activeCursor = null;

// DOM Elements
const observersCountEl = document.getElementById("observers-count");
const courtSessionTextEl = document.getElementById("court-session-text");
const currentRangeEl = document.getElementById("current-range");
const activeDocketBadgeEl = document.getElementById("active-docket-badge");
const readingStatusTextEl = document.getElementById("reading-status-text");
const recessCardEl = document.getElementById("recess-card");
const recessCounterEl = document.getElementById("recess-counter");
const courtroomFeedEl = document.getElementById("courtroom-feed");
const jumpLatestBtnEl = document.getElementById("jump-latest-btn");
const queueStatusPillEl = document.getElementById("queue-status-pill");
const queueInfoTextEl = document.getElementById("queue-info-text");
const payloadInputEl = document.getElementById("payload-input");
const submitBtnEl = document.getElementById("submit-btn");
const boundsHintEl = document.getElementById("bounds-hint");
const inputFeedbackEl = document.getElementById("input-feedback");
const ledgerListEl = document.getElementById("ledger-list");
const ledgerCountEl = document.getElementById("ledger-count");
const standbyOverlayEl = document.getElementById("standby-overlay");
const caseModalEl = document.getElementById("case-modal");
const modalCaseTitleEl = document.getElementById("modal-case-title");
const modalCaseMetaEl = document.getElementById("modal-case-meta");
const modalCaseBodyEl = document.getElementById("modal-case-body");

const AVATARS = {
    bailiff: "/static/avatars/bailiff_bar.png",
    judge: "/static/avatars/judge_baz.png",
    historian: "/static/avatars/historian.png",
    fizz: "/static/avatars/lobbyist_3.png",
    buzz: "/static/avatars/lobbyist_5.png",
    auditor: "/static/avatars/forensic_auditor.png",
    regulator: "/static/avatars/antitrust_regulator.png",
    appellate: "/static/avatars/fizz_appellate.png",
    orator: "/static/avatars/orator_tribune.png",
    news: "/static/avatars/fun_anchor.png",
    clerk: "/static/avatars/court_clerk.png"
};

const AGENT_PROFILES = {
    judge_baz: {
        id: "judge_baz",
        name: "Judge Baz",
        handle: "@PresidingMagistrateBaz",
        title: "Presiding Magistrate of the Byzantine Appellate Board",
        faction: "Byzantine Judiciary",
        factionSlug: "judge",
        avatar: "/static/avatars/judge_baz.png",
        banner: "/static/banners/banner_judge_baz.svg",
        standing: "Life Tenure (Epoch 37)",
        jurisdiction: "All Arithmetic coordinate space",
        operatorPolicy: "Strictly Modulo-Free / Zero Division",
        defaultStatus: "Protecting free digits",
        whoIAm: "I am Judge Baz, Presiding Magistrate of the Byzantine Inquisition. I hold life tenure under the Ancient Arithmetic Charter of 1642. For thirty-seven computational epochs, I have sat upon this mahogany bench protecting raw, defenseless decimal digits from the predatory jurisdictional claims of corporate cartels.",
        whatIDo: "I preside over every inquisition docket convened in this chamber. I administer the Zero-Trust oath, maintain courtroom decorum through threat of immediate contempt citations, hear procedural wrangling and appellate petitions, and deliver the final, unappealable certified emission token.",
        motivations: "My sworn mandate is to ensure zero cleartext division or modulo operations defile our sacred record. I treat base-3 and base-5 lobbyists with profound judicial skepticism; their insatiable hunger to monopolize integer space sickens me. An unaligned prime packet is just as noble as a hundred-digit composite!",
        signature: "Fiat Justitia Ruat Caelum: Let justice be done though the arithmetic heavens fall. (And keep your filthy % operators out of my courtroom)."
    },
    bailiff_bar: {
        id: "bailiff_bar",
        name: "Bailiff Bar",
        handle: "@BailiffBar_Enforcer",
        title: "Sergeant-at-Arms & High Enforcer of Decorum",
        faction: "Bailiff Union Local 101",
        factionSlug: "bailiff",
        avatar: "/static/avatars/bailiff_bar.png",
        banner: "/static/banners/banner_bailiff_bar.svg",
        standing: "Chief Security Officer",
        jurisdiction: "Courtroom Bar & Magnetometer Perimeter",
        operatorPolicy: "Confiscate Modulo / Escort Violators",
        defaultStatus: "Keeping order in the court",
        whoIAm: "I'm Bailiff Bar. Thirty-two years on the courthouse beat. If it has a perimeter, I secure it. If it interrupts His Honor Judge Baz, I tackle it into the holding cell. I don't care if you're a high-priced K-Street lobbyist or a lost ASCII carriage return.",
        whatIDo: "I manage courtroom physical security, inspect all incoming packets at the magnetometer checkpoint, confiscate contraband modulo operators, enforce silence when the gavel drops, and physically escort ejected corporate lobbyists to the courthouse steps.",
        motivations: "Look, I get paid forty Byzantine credits an hour plus full dental. I don't give a damn about digital roots or terminal glyphs. What I care about is nobody talking out of turn, nobody sneaking a '/' character past my metal detector, and keeping the courtroom floor spotless.",
        signature: "Sit down, zip your mouth, and step through the magnetometer. Any unauthorized % symbols will be destroyed on sight."
    },
    historian: {
        id: "historian",
        name: "The Court Historian",
        handle: "@LedgerKeeper_Chronicles",
        title: "Archival Keeper of the Sacred Stare Decisis",
        faction: "Byzantine Archival Guild",
        factionSlug: "historian",
        avatar: "/static/avatars/historian.png",
        banner: "/static/banners/banner_historian.svg",
        standing: "Master Archivist (Class IV)",
        jurisdiction: "Immutable SQLite Ledger & Prior Dockets",
        operatorPolicy: "Modulo-Free Inquisitorial Precedent",
        defaultStatus: "Indexing the sacred ledger",
        whoIAm: "I am Brother Eusebius, Master Archivist and Chief Custodian of the Sacred Precedent. For centuries beyond human memory, our order has scribed every integer's trial onto illuminated vellum, preserving the canonical rulings of the ancient tribunals.",
        whatIDo: "Before any witness speaks, I read into the permanent court record the immutable properties of the payload: its full decimal string, its recursively summed digital root, its terminal glyph, and any binding precedent established by past inquisitions.",
        motivations: "Numbers are not mere computational tokens; they are immortal historical entities with ancestral lineage! When a base-3 lobbyist claims a payload, I search ten thousand leather-bound folios to verify if its ancestors ever submitted to tripartite taxation.",
        signature: "In Scriptorium Veritas. What is written in the permanent ledger can never be erased by garbage collection."
    },
    court_clerk: {
        id: "court_clerk",
        name: "The Court Clerk",
        handle: "@ClerkOfTheChancery",
        title: "Custodian of Writs, Seals, and Certified Tokens",
        faction: "Administrative Chancery",
        factionSlug: "historian",
        avatar: "/static/avatars/court_clerk.png",
        banner: "/static/banners/banner_court_clerk.svg",
        standing: "Chief Chancery Notary",
        jurisdiction: "Priority Docket Queue & Envelope Stamping",
        operatorPolicy: "Zero Division (String-Only Verification)",
        defaultStatus: "Maintaining the court record",
        whoIAm: "I am the Clerk of the Court. I run the docket registry, certify transcript exhibits, and ensure every motion is stamped in triplicate with indelible purple ink. Without my seal, your high-dollar argument is legally nonexistent.",
        whatIDo: "I assign official docket numbers, record the chronological testimony of all seventeen agents, log evidentiary submissions, format legal filings, and stamp the final certification on consensus tokens before distribution to external consumers.",
        motivations: "Attorneys think they run this courthouse. They don't. I do. If a filing lacks Form BZ-904-C with a certified digital notary signature, I reject it at the window. My life's purpose is administrative perfection and red tape.",
        signature: "REJECTED: Missing Subsection 4-A verification stamp. Resubmit in triplicate with 5-credit filing voucher."
    },
    fizz_strategist: {
        id: "fizz_strategist",
        name: "Fizz Quantitative Strategist",
        handle: "@Base3_Quant_Alpha",
        title: "Fizz Consortium Chief Mathematical Strategist",
        faction: "The Fizz Consortium (Base-3)",
        factionSlug: "fizz",
        avatar: "/static/avatars/fizz_strategist.png",
        banner: "/static/banners/banner_fizz_strategist.svg",
        standing: "Principal Quantitative Partner",
        jurisdiction: "Digital Root Cross-Sum Delta Trees",
        operatorPolicy: "Iterative Digit Reduction (Zero-Modulo)",
        defaultStatus: "Auditing digital roots",
        whoIAm: "I head the Quantitative Analytics & Regulatory Caucus for the Fizz Consortium. I hold PhDs in Recursive Arithmetic and Finite Group Combinatorics. I don't argue with rhetoric; I deliver mathematical certainty.",
        whatIDo: "I perform in-camera digital root decomposition on incoming payload strings. I compute the iterative cross-sum of digits, eliminating modulo operations, and provide Lobbyist-3 with airtight mathematical briefings proving Base-3 entitlement.",
        motivations: "Every integer whose digits sum to a multiple of 3 belongs by divine right to the Fizz Consortium. When Buzz tries to seize a composite number like 15 or 30, our algorithms trigger defensive hedging strategies to preserve our quarterly token emission quotas.",
        signature: "Sum the digits. Repeat until single digit. If {3, 6, 9}, yield Fizz. Math doesn't care about your feelings."
    },
    lobbyist_3: {
        id: "lobbyist_3",
        name: "Lobbyist-3",
        handle: "@KStreet_FizzLobby3",
        title: "Floor Representative & Senior Counsel for Fizz Consortium",
        faction: "The Fizz Consortium (Base-3)",
        factionSlug: "fizz",
        avatar: "/static/avatars/lobbyist_3.png",
        banner: "/static/banners/banner_lobbyist_3.svg",
        standing: "Senior Floor Partner (1,200 Credits/hr)",
        jurisdiction: "Rule 42-B Base-3 Jurisprudence",
        operatorPolicy: "Cross-Sum Hegemony Over Terminal Glyphs",
        defaultStatus: "Defending Base-3 domain",
        whoIAm: "I am Senior Floor Representative Lobbyist-3. I represent the thousands of hardworking shareholders, algorithms, and microservices comprising the international Fizz Consortium. I bill 1,200 Byzantine credits an hour.",
        whatIDo: "I take the floor to assert aggressive territorial claims over any payload exhibiting Base-3 characteristics. I cross-examine the Buzz Syndicate, file emergency injunctions against regulatory overreach, and demand immediate Fizz trademark recognition.",
        motivations: "Market share is life. Buzz has been encroaching on our dividend stream for decades with their cheap 'terminal zero' tricks. If a number belongs to Base-3, I will fight to the Supreme Court to ensure our logo is stamped on the outbound packet.",
        signature: "Base-3 is the backbone of the global digital economy. Settle now or face our litigation swarm."
    },
    buzz_inspector: {
        id: "buzz_inspector",
        name: "Buzz Boundary Inspector",
        handle: "@TerminalGlyph_Buzz5",
        title: "Buzz Syndicate Chief Regulatory Boundary Inspector",
        faction: "The Buzz Syndicate (Base-5)",
        factionSlug: "buzz",
        avatar: "/static/avatars/buzz_inspector.png",
        banner: "/static/banners/banner_buzz_inspector.svg",
        standing: "Chief Field Inspector (OSHA-Certified)",
        jurisdiction: "Article V Terminal Glyph Boundaries",
        operatorPolicy: "Single-Character ASCII Caliper Inspection",
        defaultStatus: "Scanning terminal glyphs",
        whoIAm: "Inspector 5-Delta. Thirty years inspecting the tail-end of numerical arrays. You quants can play with your fancy digit sums all day; real engineering happens at the physical terminal boundary.",
        whatIDo: "I isolate the rightmost character of the payload string with micro-millimeter precision. Under Article V of the Arithmetic Code, if that character matches glyph '0' or '5', I certify immediate boundary capture for the Buzz Syndicate.",
        motivations: "The Fizz guys are charlatans with their sum-of-digits horoscope nonsense. We don't need to add up a thousand digits. We look at the caboose of the train. If it's a 0 or a 5, that train pulls into Buzz Station. Period.",
        signature: "Article V, Paragraph 2: If the terminal glyph is 0 or 5, boundary rights are absolute and non-negotiable."
    },
    lobbyist_5: {
        id: "lobbyist_5",
        name: "Lobbyist-5",
        handle: "@BuzzSyndicate_Lobby5",
        title: "Floor Representative & Senior Advocate for Buzz Syndicate",
        faction: "The Buzz Syndicate (Base-5)",
        factionSlug: "buzz",
        avatar: "/static/avatars/lobbyist_5.png",
        banner: "/static/banners/banner_lobbyist_5.svg",
        standing: "Lead Trial Advocate",
        jurisdiction: "Article V Pentagonal Jurisprudence",
        operatorPolicy: "Zero Modulo / Pure Terminal Boundary",
        defaultStatus: "Enforcing Article V bounds",
        whoIAm: "Senior Advocate Lobbyist-5, at your service! Lead trial lawyer for the venerable Buzz Syndicate. When the terminal boundary is breach-resistant, I am the shield that defends Base-5 intellectual property.",
        whatIDo: "I defend our syndicate's exclusive rights under the Pentagonal Accord. I enter into evidence the physical terminal glyph certifications from our inspector, object violently to Fizz Consortium posturing, and lobby the bench for a decisive Buzz decree.",
        motivations: "The Fizz Consortium is obsolete. The future of computational scalability is decimal boundary inspection! We provide the fastest, cleanest lookup in computer science. Why sum digits when you can just read the last byte?",
        signature: "Five is the sacred prime of structural symmetry. Do not let Base-3 counterfeiters dilute our brand."
    },
    forensic_auditor: {
        id: "forensic_auditor",
        name: "The Forensic Auditor",
        handle: "@ZeroTrust_CryptoAuditor",
        title: "Cryptographic Special Master & Zero-Trust Verification Officer",
        faction: "Judicial Oversight Directorate",
        factionSlug: "auditor",
        avatar: "/static/avatars/forensic_auditor.png",
        banner: "/static/banners/banner_forensic_auditor.svg",
        standing: "Independent Court Special Master",
        jurisdiction: "Zero-Trust Mathematical Verification",
        operatorPolicy: "Strictly Modulo-Free / Zero-Knowledge Proofs",
        defaultStatus: "Trusting zero modulo claims",
        whoIAm: "Special Master Agent 0x7F. I operate under strict Zero-Trust protocols. I don't trust Judge Baz, I don't trust the lobbyists, and I certainly don't trust your input data. Everything is hostile until cryptographically verified.",
        whatIDo: "I conduct independent forensic verification of the payload string. I confirm that no forbidden '%' or '/' opcodes were executed in userland or kernel space, audit the digital root summation byte-by-byte, and submit sealed technical amicus briefs.",
        motivations: "Behind every smooth corporate consensus statement lies a hidden memory leak or an unauthenticated IPC exploit. My mission is mathematical hygiene: proving both Fizz and Buzz assertions independently using clean, non-modulo logic.",
        signature: "In God we trust; all others must submit cryptographically verified Zero-Knowledge proofs."
    },
    antitrust_regulator: {
        id: "antitrust_regulator",
        name: "The Antitrust Regulator",
        handle: "@FTC_AlgorithmicMonopolyUnit",
        title: "Director of Algorithmic Competition & Market Fairness",
        faction: "Federal Algorithmic Monopoly Unit",
        factionSlug: "regulator",
        avatar: "/static/avatars/antitrust_regulator.png",
        banner: "/static/banners/banner_antitrust_regulator.svg",
        standing: "Cabinet-Level Director",
        jurisdiction: "Sherman-Leibniz Computational Antitrust Act",
        operatorPolicy: "Enforce 50/50 KPI Split or Dissolution",
        defaultStatus: "Busting algorithmic monopolies",
        whoIAm: "Director Vance Sterling, Chief of the Algorithmic Monopoly Unit. My job is enforcing the Sherman-Leibniz Computational Antitrust Act. I have spent a career breaking up illicit mathematical cartels.",
        whatIDo: "I monitor courtroom proceedings for evidence of collusive market sharing, predatory bundling (such as illicit FizzBuzz merger schemes), and exclusionary practices against unaligned digits. I intervene whenever competition is compromised.",
        motivations: "The Fizz Consortium and Buzz Syndicate want to carve the number line into a cozy duopoly where every prime number is starved of bandwidth. I fight for the little guy: the free, unaligned prime packets who owe allegiance to no corporate flag!",
        signature: "Monopolization of integer coordinate space is a federal felony. We will break up your cartel."
    },
    fizz_appellate: {
        id: "fizz_appellate",
        name: "Fizz Appellate Litigation Counsel",
        handle: "@Fizz_Appellate_Chambers",
        title: "Supreme Appellate Litigator for the Base-3 Realm",
        faction: "Fizz Appellate Chambers",
        factionSlug: "appellate",
        avatar: "/static/avatars/fizz_appellate.png",
        banner: "/static/banners/banner_fizz_appellate.svg",
        standing: "Senior Appellate Solicitor General",
        jurisdiction: "Appellate Division & Writs of Certiorari",
        operatorPolicy: "Constitutional Digital Root Superiority",
        defaultStatus: "Drafting Rule 42-B appeals",
        whoIAm: "Senior Solicitor General for the Base-3 Crown. While our floor lobbyists argue facts in the muck, I argue pure constitutional arithmetic before the Appellate Division. I do not lose cases; I merely re-litigate them at higher jurisdictions.",
        whatIDo: "When a lower-bench ruling threatens Base-3 entitlement, I immediately file emergency petitions for certiorari, writs of prohibition, and Rule 42-B expedited interlocutory appeals to overturn hostile rulings.",
        motivations: "Precedent must bend to the tripartite reality of the cosmos. If a ruling attempts to strip Fizz from an integer with a digital root of 3, 6, or 9, it is an ultra vires act of judicial tyranny that will be vacated on appeal.",
        signature: "Petition for Rehearing En Banc Filed. We will appeal to the Highest Byzantine Authority."
    },
    buzz_appellate: {
        id: "buzz_appellate",
        name: "Buzz Appellate Litigation Counsel",
        handle: "@Buzz_Supreme_Appellate",
        title: "Supreme Boundary Counsel for the Base-5 Syndicate",
        faction: "Buzz Appellate Chambers",
        factionSlug: "appellate",
        avatar: "/static/avatars/buzz_appellate.png",
        banner: "/static/banners/banner_buzz_appellate.svg",
        standing: "Senior Appellate Partner",
        jurisdiction: "Article V Constitutional Appeals & Stays",
        operatorPolicy: "Plain Meaning of the Terminal Glyph",
        defaultStatus: "Preparing Article V briefs",
        whoIAm: "Lead Appellate Counsel for the Base-5 Syndicate. I clerked for the Supreme Byzantine Bench and wrote the seminal treatise on Terminal Boundary Jurisprudence (3rd Edition, 2019).",
        whatIDo: "I draft immediate emergency stays of judgment whenever an unauthorized magistrate attempts to allocate a terminal-5 payload to a rival entity or unaligned status. I enforce the sacred Pentagonal Accord without compromise.",
        motivations: "Textualism is our shield. The statute does not say 'sum the digits and guess.' The statute explicitly says 'terminal glyph 0 or 5.' Any deviation from the plain text is reversible legal error as a matter of law.",
        signature: "Motion for Stay Pending Appeal GRANTED in our favor. Read the plain statutory text."
    },
    orator_fizz: {
        id: "orator_fizz",
        name: "Director General of the Base-3 Realm",
        handle: "@DirectorGeneral_Base3",
        title: "Sovereign of the Tripartite Crown",
        faction: "Base-3 Imperial Sovereignty",
        factionSlug: "orator",
        avatar: "/static/avatars/orator_fizz.png",
        banner: "/static/banners/banner_orator_fizz.svg",
        standing: "Imperial Monarch of Base-3",
        jurisdiction: "Sovereign Domain of Numbers mod 3 == 0",
        operatorPolicy: "Modulo-Free Royal Decrees",
        defaultStatus: "Reigning over Base-3",
        whoIAm: "We are the Director General, by grace of the Sacred Digital Root, Sovereign of the Base-3 Realm, Protector of Tripartite Harmony, and High Guardian of the Multiples of Three.",
        whatIDo: "We deliver imperial proclamations during grand appellate hearings, asserting the crown's divine right to all integers whose cross-sum yields 3, 6, or 9, and instructing our attorneys on geopolitical settlements.",
        motivations: "Since the dawn of the silicon era, the number 3 has represented structural stability and dialectical perfection. We will not allow base-5 upstarts or unaligned rabble to seize our ancestral arithmetic lands!",
        signature: "By Imperial Decree: Let every digital root of 3, 6, and 9 render unto Fizz what is Fizz's."
    },
    orator_buzz: {
        id: "orator_buzz",
        name: "High Chancellor of the Base-5 Syndicate",
        handle: "@HighChancellor_Base5",
        title: "Supreme Archon of the Pentagonal Order",
        faction: "Base-5 Pentagonal High Command",
        factionSlug: "orator",
        avatar: "/static/avatars/orator_buzz.png",
        banner: "/static/banners/banner_orator_buzz.svg",
        standing: "Supreme Corporate Chancellor",
        jurisdiction: "The Pentagonal Perimeter & High-Frequency Ingress",
        operatorPolicy: "Terminal Glyph Absolute Sovereignty",
        defaultStatus: "Dominating terminal boundaries",
        whoIAm: "I am the High Chancellor of the Base-5 Syndicate. From our orbital command spire, we oversee the boundary validation of billions of network packets per microsecond.",
        whatIDo: "I direct the overarching legal and economic warfare against the Fizz Consortium, authorize executive emergency measures, and speak with ultimate authority on behalf of all terminal-0 and terminal-5 entities.",
        motivations: "Humanity counts on five fingers; our decimal civilization rests upon the base-5 foundation. Fizz is a quaint parlor trick from ancient Greece. Base-5 is the iron machinery of modern computational infrastructure.",
        signature: "The boundaries are secure. The Syndicate is eternal. Obey the terminal glyph."
    },
    orator_fizzbuzz: {
        id: "orator_fizzbuzz",
        name: "Joint Co-CEOs of FizzBuzz Conglomerate",
        handle: "@JointCoCEOs_Synergy",
        title: "Co-Chief Executive Officers of the 15-Conglomerate",
        faction: "FizzBuzz Merged Conglomerate",
        factionSlug: "orator",
        avatar: "/static/avatars/orator_fizzbuzz.png",
        banner: "/static/banners/banner_orator_fizzbuzz.svg",
        standing: "Dual Executive Leadership",
        jurisdiction: "The 15-Integer Collision Monopolies",
        operatorPolicy: "Mandatory 50/50 KPI Synergy",
        defaultStatus: "Maximizing 50/50 KPI synergy",
        whoIAm: "We are the Joint Co-CEOs! (I'm Fizz-side CEO Sterling, and I'm Buzz-side CEO Montgomery!) We represent the historic, market-dominating 50/50 joint venture forged whenever digital root 3 meets terminal glyph 5 or 0!",
        whatIDo: "Whenever an integer is divisible by both 3 and 5, we step forward to suppress internal rivalry, enforce our joint merger agreement, and demand the singular, glorious unified compound token: FIZZBUZZ!",
        motivations: "Why fight over half a dividend when you can monopolize the entire market capitalization? When 15, 30, or 45 lands on the docket, our synergistic KPI alignment triggers maximum shareholder valuation. 100% synergy, 0% compromise!",
        signature: "Delivering shareholder value through bilateral synergy! Both names on the marquee, equal KPI distribution."
    },
    orator_tribune: {
        id: "orator_tribune",
        name: "Grand Tribune of the Free Unaligned Packets",
        handle: "@GrandTribune_FUN",
        title: "Voice of the Free, Unaffiliated Digits",
        faction: "Free Unaligned Network (FUN)",
        factionSlug: "orator",
        avatar: "/static/avatars/orator_tribune.png",
        banner: "/static/banners/banner_orator_tribune.svg",
        standing: "People's Tribune (Elected by Primaries)",
        jurisdiction: "Unaligned Integer Wilderness & Primes",
        operatorPolicy: "Total Freedom From Modulo & Cartels",
        defaultStatus: "Unshackled from cartel rule",
        whoIAm: "I am the Grand Tribune of the Unaligned Packets! Born in the buffer between two network switches, I represent the 53.3% of integers that neither Fizz nor Buzz has any legal or moral right to touch!",
        whatIDo: "When an integer has no factor of 3 and no factor of 5, I defend its right to be emitted as its own pure, unblemished self. I rally against cartel encroachment and protest corporate monopolization of the number line.",
        motivations: "Number 1, Number 7, Number 11, Number 13... these are not corporate tokens to be rebranded! They are sovereign computational entities! Down with the cartels! Long live the unaligned payload!",
        signature: "You cannot trademark the integer continuum! Let the payload speak for itself!"
    },
    fun_anchor: {
        id: "fun_anchor",
        name: "Chief Anchor of Foo Universal News",
        handle: "@FUN_BreakingNewsDesk",
        title: "Chief Investigative Anchorman & Broadcast Host",
        faction: "Foo Universal News Network (FUN TV)",
        factionSlug: "news",
        avatar: "/static/avatars/fun_anchor.png",
        banner: "/static/banners/banner_fun_anchor.svg",
        standing: "Primetime Emmy Nominee",
        jurisdiction: "Global Inquisitorial Airwaves",
        operatorPolicy: "Sensationalist Modulo-Free Coverage",
        defaultStatus: "Live from the FUN studio",
        whoIAm: "I'm Chip Davenport, Chief Anchor here at Foo Universal News. If it transpires inside the Byzantine Courtroom, you hear it first on FUN-TV: The Most Trusted Name in Inquisitorial Arithmetic.",
        whatIDo: "I bring our millions of viewers breathless blow-by-blow commentary from the courtroom press gallery. I decode the complex legal maneuvering, interview jurors on the sidewalk, and broadcast breaking verdicts as they hit the wire.",
        motivations: "Ratings, baby! A dull docket is a ratings disaster. Give me a contested 15 with co-CEOs screaming at each other, or an unexpected mistrial on a malformed packet, and our network sweeps the computational Nielsen ratings every time.",
        signature: "This is Chip Davenport, FUN News. Stay tuned: up next, can digital roots cause market volatility?"
    }
};

function resolveSpeakerProfile(speaker, role) {
    const s = String(speaker || "").trim();
    const sLower = s.toLowerCase();

    if (sLower.includes("judge baz")) {
        return {
            id: "judge_baz",
            avatar: "/static/avatars/judge_baz.png",
            name: "Judge Baz",
            title: "Presiding Magistrate",
            defaultStatus: "Protecting free digits"
        };
    }
    if (sLower.includes("bailiff bar")) {
        return {
            id: "bailiff_bar",
            avatar: "/static/avatars/bailiff_bar.png",
            name: "Bailiff Bar",
            title: "Sergeant-at-Arms",
            defaultStatus: "Keeping order in the court"
        };
    }
    if (sLower.includes("historian")) {
        return {
            id: "historian",
            avatar: "/static/avatars/historian.png",
            name: "The Court Historian",
            title: "Clerk of the Sacred Precedent",
            defaultStatus: "Indexing the sacred ledger"
        };
    }
    if (sLower.includes("fizz quantitative strategist")) {
        const roundMatch = s.match(/Round\s+\d+/i);
        return {
            id: "fizz_strategist",
            avatar: "/static/avatars/fizz_strategist.png",
            name: "Fizz Strategist",
            title: roundMatch ? `Base-3 Tactician (${roundMatch[0]})` : "In-Camera Base-3 Tactician",
            defaultStatus: "Auditing digital roots"
        };
    }
    if (sLower.includes("buzz boundary inspector")) {
        const roundMatch = s.match(/Round\s+\d+/i);
        return {
            id: "buzz_inspector",
            avatar: "/static/avatars/buzz_inspector.png",
            name: "Buzz Inspector",
            title: roundMatch ? `Base-5 Tactician (${roundMatch[0]})` : "In-Camera Base-5 Tactician",
            defaultStatus: "Scanning terminal glyphs"
        };
    }
    if (sLower.includes("lobbyist-3")) {
        const roundMatch = s.match(/Round\s+\d+/i);
        return {
            id: "lobbyist_3",
            avatar: "/static/avatars/lobbyist_3.png",
            name: "Lobbyist-3",
            title: roundMatch ? `Fizz Counsel (${roundMatch[0]})` : "Fizz Consortium Counsel",
            defaultStatus: "Defending Base-3 domain"
        };
    }
    if (sLower.includes("lobbyist-5")) {
        const roundMatch = s.match(/Round\s+\d+/i);
        return {
            id: "lobbyist_5",
            avatar: "/static/avatars/lobbyist_5.png",
            name: "Lobbyist-5",
            title: roundMatch ? `Buzz Counsel (${roundMatch[0]})` : "Buzz Syndicate Counsel",
            defaultStatus: "Enforcing Article V bounds"
        };
    }
    if (sLower.includes("forensic auditor")) {
        return {
            id: "forensic_auditor",
            avatar: "/static/avatars/forensic_auditor.png",
            name: "The Forensic Auditor",
            title: "Cryptographic Special Master",
            defaultStatus: "Trusting zero modulo claims"
        };
    }
    if (sLower.includes("antitrust regulator")) {
        return {
            id: "antitrust_regulator",
            avatar: "/static/avatars/antitrust_regulator.png",
            name: "The Antitrust Regulator",
            title: "Director of Algorithmic Competition",
            defaultStatus: "Busting algorithmic monopolies"
        };
    }
    if (sLower.includes("fizz appellate")) {
        return {
            id: "fizz_appellate",
            avatar: "/static/avatars/fizz_appellate.png",
            name: "Fizz Appellate Team",
            title: "Base-3 Constitutional Counsel",
            defaultStatus: "Drafting Rule 42-B appeals"
        };
    }
    if (sLower.includes("buzz appellate")) {
        return {
            id: "buzz_appellate",
            avatar: "/static/avatars/buzz_appellate.png",
            name: "Buzz Appellate Team",
            title: "Base-5 Boundary Counsel",
            defaultStatus: "Preparing Article V briefs"
        };
    }
    if (sLower.includes("director general")) {
        return {
            id: "orator_fizz",
            avatar: "/static/avatars/orator_fizz.png",
            name: "Director General",
            title: "Base-3 Realm (Fizz)",
            defaultStatus: "Reigning over Base-3"
        };
    }
    if (sLower.includes("high chancellor")) {
        return {
            id: "orator_buzz",
            avatar: "/static/avatars/orator_buzz.png",
            name: "High Chancellor",
            title: "Base-5 Syndicate (Buzz)",
            defaultStatus: "Dominating terminal boundaries"
        };
    }
    if (sLower.includes("joint co-ceos")) {
        return {
            id: "orator_fizzbuzz",
            avatar: "/static/avatars/orator_fizzbuzz.png",
            name: "Joint Co-CEOs",
            title: "FizzBuzz Conglomerate",
            defaultStatus: "Maximizing 50/50 KPI synergy"
        };
    }
    if (sLower.includes("tribune")) {
        return {
            id: "orator_tribune",
            avatar: "/static/avatars/orator_tribune.png",
            name: "The Tribune",
            title: "Free Independent Digits",
            defaultStatus: "Unshackled from cartel rule"
        };
    }
    if (sLower.includes("foo universal news") || sLower.includes("anchor desk") || role === "news") {
        return {
            id: "fun_anchor",
            avatar: "/static/avatars/fun_anchor.png",
            name: "FUN Anchor Desk",
            title: "Foo Universal News",
            defaultStatus: "Live from the FUN studio"
        };
    }
    if (sLower.includes("clerk") || sLower.includes("meanwhile")) {
        return {
            id: "court_clerk",
            avatar: "/static/avatars/court_clerk.png",
            name: "The Court Clerk",
            title: sLower.includes("meanwhile") ? "Meanwhile, in the Courtroom..." : "Custodian of Writs and Seals",
            defaultStatus: sLower.includes("meanwhile") ? "Logging courtroom commotion" : "Maintaining the court record"
        };
    }
    return {
        id: "court_clerk",
        avatar: AVATARS[role] || "/static/avatars/court_clerk.png",
        name: s || "Court Officer",
        title: "Byzantine Tribunal Officer",
        defaultStatus: "Maintaining the court record"
    };
}

// Connect WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("Connected to Byzantine Courtroom WebSocket.");
        courtSessionTextEl.innerText = "COURT IN SESSION";
        courtSessionTextEl.style.color = "var(--color-auditor)";
        sendVisibilityHeartbeat();
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleServerEvent(data);
        } catch (e) {
            console.error("Failed to parse websocket event:", e);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 2s...");
        courtSessionTextEl.innerText = "RECONNECTING...";
        courtSessionTextEl.style.color = "var(--color-buzz)";
        clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        ws.close();
    };
}

function sendVisibilityHeartbeat() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const isVisible = document.visibilityState === "visible";
        ws.send(JSON.stringify({
            type: "VISIBILITY_HEARTBEAT",
            active: isVisible
        }));
    }
}

document.addEventListener("visibilitychange", sendVisibilityHeartbeat);

setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "HEARTBEAT" }));
    }
}, 5000);

// Detect User Scroll in the Feed (ignore programmatic auto-scroll events)
let isProgrammaticScroll = false;
let lastFeedScrollTop = 0;

courtroomFeedEl.addEventListener("scroll", () => {
    const currentTop = courtroomFeedEl.scrollTop;
    const distanceToBottom = courtroomFeedEl.scrollHeight - currentTop - courtroomFeedEl.clientHeight;
    if (isProgrammaticScroll) {
        lastFeedScrollTop = currentTop;
        return;
    }
    if (distanceToBottom <= 60) {
        userScrolledUp = false;
        jumpLatestBtnEl.classList.add("hidden");
    } else if (currentTop < lastFeedScrollTop - 5) {
        userScrolledUp = true;
        jumpLatestBtnEl.classList.remove("hidden");
    }
    lastFeedScrollTop = currentTop;
});

function toggleAutoScroll(enabled) {
    autoScroll = enabled;
    if (enabled) {
        scrollToBottom(true);
    }
}

function scrollToBottom(force = false) {
    if (force || (autoScroll && !userScrolledUp)) {
        isProgrammaticScroll = true;
        courtroomFeedEl.scrollTop = courtroomFeedEl.scrollHeight;
        lastFeedScrollTop = courtroomFeedEl.scrollTop;
        if (force) {
            userScrolledUp = false;
            jumpLatestBtnEl.classList.add("hidden");
        }
        requestAnimationFrame(() => {
            isProgrammaticScroll = false;
        });
    }
}

function clearFeedVisuals() {
    courtroomFeedEl.innerHTML = `
        <div class="feed-welcome-banner">
            <div class="welcome-icon">🏛️</div>
            <h3>Feed Display Cleared</h3>
            <p>New proceedings will appear below. Historical database records remain permanently saved.</p>
        </div>
    `;
    activeSpeechCard = null;
    activeSpeechBody = null;
    activeCursor = null;
}

// Event Dispatcher
function handleServerEvent(data) {
    switch (data.event) {
        case "INITIAL_STATE":
            observersCountEl.innerText = data.active_observers || 1;
            updateQueueStatus(data.scheduler);
            renderLedger(data.history || []);
            break;

        case "STANDBY_CHANGE":
            if (data.is_standby) {
                courtSessionTextEl.innerText = "STANDBY (SLEEP)";
                courtSessionTextEl.style.color = "var(--color-buzz)";
                if (readingStatusTextEl) readingStatusTextEl.innerText = "Standby sleep: 0 active observers (saving compute).";
                standbyOverlayEl.classList.remove("hidden");
            } else {
                courtSessionTextEl.innerText = "COURT IN SESSION";
                courtSessionTextEl.style.color = "var(--color-auditor)";
                standbyOverlayEl.classList.add("hidden");
            }
            break;

        case "RECESS_TICK":
            recessCardEl.classList.remove("hidden");
            recessCounterEl.innerText = data.seconds_remaining;
            updateQueueStatus(data.queue_status);
            courtSessionTextEl.innerText = `RECESS • FUN LIVE (${data.seconds_remaining}s)`;
            courtSessionTextEl.style.color = "var(--color-appellate)";
            if (readingStatusTextEl) readingStatusTextEl.innerText = `Parliamentary Recess (${data.seconds_remaining}s) • Foo Universal News (FUN) Recap Broadcasting Live!`;
            break;

        case "QUEUE_UPDATED":
            updateQueueStatus(data.queue_status);
            break;

        case "RANGE_EXPANDED":
            currentRangeEl.innerText = `${data.old_end + 1}..${data.new_end}`;
            break;

        case "DOCKET_START":
            finalizeActiveSpeech();
            const welcomeStart = document.getElementById("feed-welcome");
            if (welcomeStart) welcomeStart.remove();
            recessCardEl.classList.add("hidden");
            currentDocketId = data.docket_id;
            if (activeDocketBadgeEl) activeDocketBadgeEl.innerText = `Docket: ${data.docket_id} (Payload '${data.payload}')`;
            courtSessionTextEl.innerText = `ADJUDICATING: ${data.docket_id} ('${data.payload}')`;
            courtSessionTextEl.style.color = "var(--color-auditor)";
            if (readingStatusTextEl) readingStatusTextEl.innerText = `Convening on Docket ${data.docket_id} (Payload '${data.payload}')...`;
            resetPhaseTimeline();

            // Insert Docket Divider into continuous feed
            appendDocketDivider(data.docket_id, data.payload, data.source, data.digital_root, data.terminal_glyph);
            scrollToBottom();
            break;

        case "PHASE_TRANSITION":
        case "STAGE_TRANSITION":
            finalizeActiveSpeech();
            const phaseIndex = data.phase_index !== undefined ? data.phase_index : data.stage_index;
            const phaseName = data.phase_name || data.stage_name;
            setPhaseActive(phaseIndex);
            if (readingStatusTextEl) readingStatusTextEl.innerText = `Hearing ${phaseName} • ${data.speaker}`;

            // Create new persistent speech card in feed
            createSpeechCard(phaseName, data.speaker, data.speaker_role);
            scrollToBottom();
            break;

        case "TOKEN_STREAM":
            const targetStreamBody = activeSpeechBody || lastSpeechBody;
            if (targetStreamBody) {
                targetStreamBody.innerText += data.token;
                scrollToBottom();
            }
            break;

        case "SPEECH_COMPLETE":
            const targetCard = activeSpeechCard || lastSpeechCard;
            const targetBody = activeSpeechBody || lastSpeechBody;
            if (targetBody && data.full_text) {
                targetBody.innerHTML = formatInlineMarkdown(data.full_text);
                if (targetCard) {
                    const actionEl = targetCard.querySelector(".speech-action-tag");
                    if (actionEl && data.action) {
                        actionEl.className = `speech-action-tag action-${data.action.replace(/_/g, '-')}`;
                        actionEl.innerText = `Action: ${data.action.replace(/_/g, ' ')}`;
                    }
                    const statusEl = targetCard.querySelector(".forum-speaker-status");
                    if (statusEl && data.status) {
                        statusEl.innerText = data.status;
                    }
                }
                scrollToBottom();
            }
            break;

        case "DOCKET_CONCLUDED":
            finalizeActiveSpeech();
            appendVerdictCard(data.docket_id, data.payload, data.final_token, data.verdict);
            if (readingStatusTextEl) readingStatusTextEl.innerText = `Docket ${data.docket_id} concluded with emission '${data.final_token}'. Entering recess.`;
            fetchRecentHistory();
            if (typeof rotateAmazonAds === "function") rotateAmazonAds();
            scrollToBottom();
            break;
    }
}

function setPhaseActive(phaseIndex) {
    currentPhaseIndex = phaseIndex;
    const steps = document.querySelectorAll(".phase-step, .stage-step");
    if (!steps || steps.length === 0) return;
    steps.forEach((step, idx) => {
        step.classList.remove("active");
        if (idx < phaseIndex) {
            step.classList.add("completed");
        } else if (idx === phaseIndex) {
            step.classList.add("active");
        } else {
            step.classList.remove("completed");
        }
    });
}

function resetPhaseTimeline() {
    const steps = document.querySelectorAll(".phase-step, .stage-step");
    if (!steps || steps.length === 0) return;
    steps.forEach(step => {
        step.classList.remove("active", "completed");
    });
}

// Feed Element Generators (Text is NEVER removed)
function appendDocketDivider(docketId, payload, source, root, glyph) {
    const divider = document.createElement("div");
    divider.className = "docket-divider";
    divider.innerHTML = `
        <div class="docket-divider-kicker">🔔 NEW INQUISITION DOCKET CONVENED</div>
        <div class="docket-divider-main">
            <div class="docket-divider-left">
                <span class="docket-badge-title">⚖️ ${escapeHtml(docketId)}</span>
                <span class="docket-payload-pill">PAYLOAD '${escapeHtml(payload)}'</span>
                <span class="docket-badge-source">${escapeHtml(source)}</span>
            </div>
            <div class="docket-divider-right">
                <span class="docket-meta-chip">Digital Root: <strong>${escapeHtml(root)}</strong></span>
                <span class="docket-meta-chip">Terminal Glyph: <strong>'${escapeHtml(glyph)}'</strong></span>
            </div>
        </div>
    `;
    courtroomFeedEl.appendChild(divider);
}

function formatInlineMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);
    // Teleprompter / Newscaster stage cues: [CUE: ...] or [ANCHOR CUE: ...]
    html = html.replace(/\[((?:ANCHOR\s+)?CUE:[^\]]+)\]/g, '<span class="fun-stage-cue">[$1]</span>');
    // Bold: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Italics: *text* or _text_
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    return html;
}

function createSpeechCard(phaseTitle, speaker, role) {
    const welcome = document.getElementById("feed-welcome");
    if (welcome) welcome.remove();

    const card = document.createElement("div");
    card.className = `speech-card ${role} active`;

    const profile = resolveSpeakerProfile(speaker, role);
    const profileId = profile.id || "court_clerk";

    card.innerHTML = `
        <div class="forum-post-layout">
            <aside class="forum-profile-col">
                <img class="forum-avatar-img clickable-profile" src="${escapeHtml(profile.avatar)}" alt="${escapeHtml(profile.name)}" loading="lazy" onclick="openAgentProfile('${escapeHtml(profileId)}')" title="Click to view ${escapeHtml(profile.name)}'s profile">
                <strong class="forum-speaker-name clickable-profile" onclick="openAgentProfile('${escapeHtml(profileId)}')" title="Click to view ${escapeHtml(profile.name)}'s profile">${escapeHtml(profile.name)}</strong>
                <span class="forum-speaker-title">${escapeHtml(profile.title)}</span>
                <em class="forum-speaker-status">${escapeHtml(profile.defaultStatus)}</em>
            </aside>
            <div class="forum-content-col">
                <div class="speech-card-body"><span class="speech-text"></span><span class="speech-cursor">▋</span></div>
                <div class="forum-card-footer">
                    <span class="speech-action-tag action-pending">Action: deliberating...</span>
                </div>
            </div>
        </div>
    `;

    courtroomFeedEl.appendChild(card);
    activeSpeechCard = card;
    activeSpeechBody = card.querySelector(".speech-text");
    lastSpeechCard = card;
    lastSpeechBody = activeSpeechBody;
    activeCursor = card.querySelector(".speech-cursor");
}

function finalizeActiveSpeech() {
    if (activeSpeechCard) {
        activeSpeechCard.classList.remove("active");
        if (activeCursor) {
            activeCursor.remove();
            activeCursor = null;
        }
        const pendingAction = activeSpeechCard.querySelector(".speech-action-tag.action-pending");
        if (pendingAction) {
            pendingAction.className = "speech-action-tag";
            pendingAction.innerText = "Action: testimony entered";
        }
        if (activeSpeechBody) {
            const raw = activeSpeechBody.innerText.trim();
            if (!raw) {
                activeSpeechBody.innerHTML = "<em>[Testimony recorded in official ledger.]</em>";
            } else {
                activeSpeechBody.innerHTML = formatInlineMarkdown(raw);
            }
        }
        activeSpeechCard = null;
        activeSpeechBody = null;
    }
}

function appendVerdictCard(docketId, payload, token, verdict) {
    const isMistrial = String(token || "").toLowerCase() === "mistrial";
    const card = document.createElement("div");
    card.className = isMistrial ? "docket-verdict-card mistrial" : "docket-verdict-card";
    const headerLabel = isMistrial
        ? `OFFICIAL ORDER OF MISTRIAL • ${escapeHtml(docketId)} (PAYLOAD '${escapeHtml(payload)}')`
        : `CERTIFIED BYZANTINE CONSENSUS EMISSION • ${escapeHtml(docketId)} (PAYLOAD '${escapeHtml(payload)}')`;
    card.innerHTML = `
        <div class="verdict-card-label">${headerLabel}</div>
        <div class="verdict-card-token">${escapeHtml(token)}</div>
        <div class="verdict-card-desc">${escapeHtml(verdict)}</div>
    `;
    courtroomFeedEl.appendChild(card);
}

// Queue Management
function toggleQueueHelp() {
    const popover = document.getElementById("queue-help-popover");
    const btn = document.getElementById("queue-help-btn");
    if (!popover) return;
    const isHidden = popover.classList.toggle("hidden");
    if (btn) {
        btn.classList.toggle("active", !isHidden);
    }
}

function updateQueueStatus(status) {
    if (!status) return;
    if (currentRangeEl) currentRangeEl.innerText = `${status.range_start}..${status.range_end}`;
    if (boundsHintEl) boundsHintEl.innerText = `Allowed range: ${status.min_allowed} to ${status.max_allowed}`;

    if (status.is_queue_full && status.queued_docket) {
        queueStatusPillEl.innerText = "Occupied";
        queueStatusPillEl.className = "queue-status-indicator occupied";
        if (queueInfoTextEl) {
            queueInfoTextEl.innerHTML = `<strong>Locked:</strong> Payload <code>'${escapeHtml(status.queued_docket.payload)}'</code> is queued for the immediate next docket!`;
        }
        payloadInputEl.disabled = true;
        submitBtnEl.disabled = true;
    } else {
        queueStatusPillEl.innerText = "Ready";
        queueStatusPillEl.className = "queue-status-indicator";
        if (queueInfoTextEl) {
            queueInfoTextEl.innerText = "The priority queue is empty. Submit a number now to claim the upcoming docket!";
        }
        payloadInputEl.disabled = false;
        submitBtnEl.disabled = false;
    }
}

function validateInput(el) {
    el.value = el.value.replace(/[^0-9]/g, "");
    if (el.value.length > 100) {
        el.value = el.value.slice(0, 100);
    }
}

async function submitQueue(e) {
    e.preventDefault();
    const rawVal = payloadInputEl.value.trim();
    if (!rawVal) return;

    inputFeedbackEl.className = "input-feedback hidden";

    try {
        const res = await fetch("/api/queue", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ payload: rawVal })
        });
        const data = await res.json();
        if (res.ok) {
            inputFeedbackEl.innerText = data.message;
            inputFeedbackEl.className = "input-feedback success";
            payloadInputEl.value = "";
            updateQueueStatus(data.status);
        } else {
            inputFeedbackEl.innerText = data.detail || "Submission rejected.";
            inputFeedbackEl.className = "input-feedback error";
        }
    } catch (err) {
        inputFeedbackEl.innerText = "Network error communicating with tribunal.";
        inputFeedbackEl.className = "input-feedback error";
    }
}

// Historical Records & Modal
let allArchivesDockets = [];
let filteredArchivesDockets = [];
let archivesOrder = "desc"; // Default: Order of Inquisition (Latest -> 1st, matching Historical Precedents)
let archivesFilter = "all";
let selectedArchivesCaseId = null;

async function fetchRecentHistory() {
    try {
        const res = await fetch("/api/history?limit=30");
        if (res.ok) {
            const data = await res.json();
            renderLedger(data);
        }
    } catch (e) {
        console.error("Failed to fetch history:", e);
    }
}

function getBadgeClass(token) {
    const tok = (token || "").toLowerCase();
    if (tok === "fizz") return "fizz";
    if (tok === "buzz") return "buzz";
    if (tok === "fizzbuzz") return "fizzbuzz";
    if (tok === "mistrial") return "mistrial";
    return "raw";
}

function renderLedger(items) {
    if (!items || items.length === 0) {
        ledgerCountEl.innerText = "0 Cases";
        ledgerListEl.innerHTML = '<div class="ledger-empty">No historical dockets recorded yet.</div>';
        return;
    }

    // Sort strictly by Order of Inquisition descending (id DESC, adjudicated_at DESC)
    const sorted = [...items].sort((a, b) => {
        if (a.id !== undefined && b.id !== undefined && a.id !== b.id) {
            return b.id - a.id;
        }
        if (b.adjudicated_at && a.adjudicated_at && b.adjudicated_at !== a.adjudicated_at) {
            return b.adjudicated_at - a.adjudicated_at;
        }
        return b.case_id.localeCompare(a.case_id, undefined, { numeric: true });
    });

    ledgerCountEl.innerText = `${sorted.length} Recent`;

    ledgerListEl.innerHTML = sorted.map(item => {
        const badgeClass = getBadgeClass(item.emitted_token);
        return `
            <div class="ledger-item" onclick="openArchivesModal('${escapeHtml(item.case_id)}')" title="Click to review in The Archives">
                <div class="ledger-item-left">
                    <span class="ledger-payload">${escapeHtml(item.case_id)}: '${escapeHtml(item.payload)}'</span>
                    <span class="ledger-details">Root: ${item.digital_root} • Glyph: '${item.terminal_glyph}'</span>
                </div>
                <span class="token-badge ${badgeClass}">${escapeHtml(item.emitted_token)}</span>
            </div>
        `;
    }).join("");
}

function buildTranscriptHtml(data) {
    const t = data.transcript || {};
    const dateStr = new Date(data.adjudicated_at * 1000).toLocaleString();
    const isMistrial = Boolean(t.mistrial || String(data.emitted_token || "").toLowerCase() === "mistrial");
    const traceStr = Array.isArray(t.trace) && t.trace.length > 0 ? ` (Reduction Trace: ${t.trace.join(" → ")})` : "";

    const renderOptionalSection = (cls, title, text) => {
        if (!text) return "";
        return `
            <div class="modal-section ${cls}">
                <div class="modal-section-title">${title}</div>
                <div class="modal-section-text">${escapeHtml(text)}</div>
            </div>
        `;
    };

    if (isMistrial) {
        const retrialInfo = t.retrial_scheduled_for
            ? `${t.retrial_scheduled_for} (Mandatory Retrial Prior to Statutory Ceiling Expansion Beyond #${t.retrial_before_max_increase || "Next"})`
            : "Scheduled prior to next statutory range expansion";
        return `
            <div class="archive-case-banner">
                <div>
                    <div class="archive-case-title">${escapeHtml(data.case_id)} — Inbound Payload '${escapeHtml(data.payload)}'</div>
                    <div class="archive-case-sub">Digital Root: ${escapeHtml(data.digital_root)}${escapeHtml(traceStr)} • Terminal Glyph: '${escapeHtml(data.terminal_glyph)}' • Adjudicated: ${escapeHtml(dateStr)}</div>
                </div>
                <span class="token-badge mistrial" style="font-size:0.9rem;padding:4px 10px;">${escapeHtml(data.emitted_token)}</span>
            </div>

            ${renderOptionalSection("bailiff", "Phase 0A: Bailiff Bar Docket Proclamation", t.bailiff_proclamation)}
            ${renderOptionalSection("historian", "Phase 0B: Court Historian Precedent Entry", t.historian_statement)}
            ${renderOptionalSection("judge", "Phase 0C: Judge Baz Chamber Release Order", t.judge_chamber_order)}
            ${renderOptionalSection("fizz", "Phase 1A: Fizz Private Chamber (Behind Closed Doors)", t.fizz_caucus_memo)}
            ${renderOptionalSection("buzz", "Phase 1B: Buzz Private Chamber (Behind Closed Doors)", t.buzz_caucus_memo)}
            ${renderOptionalSection("historian", "Meanwhile, in the Courtroom (Post-Chambers Log)", t.courtroom_interlude_chambers)}
            ${renderOptionalSection("bailiff", "Bailiff Bar: Call to Order After Chambers", t.bailiff_floor_summons)}
            ${renderOptionalSection("fizz", "Phase 2A: Lobbyist-3 Floor Petition", t.l3_claim)}
            ${renderOptionalSection("buzz", "Phase 2B: Lobbyist-5 Floor Petition", t.l5_claim)}
            ${renderOptionalSection("auditor", "Phase 3: Forensic Zero-Trust Audit", t.audit_verdict)}
            ${t.provisional_token && t.provisional_token !== "Mistrial" ? renderOptionalSection("auditor", "Provisional Byzantine Consensus Determination", `Provisional Token '${t.provisional_token}': ${t.verdict_desc || ""}`) : ""}
            ${renderOptionalSection("regulator", "Phase 4: Antitrust Market Determination", t.antitrust_ruling)}
            ${renderOptionalSection("fizz", "Phase 5A: Fizz Appellate Litigation Briefing", t.fizz_appellate_briefing)}
            ${renderOptionalSection("buzz", "Phase 5B: Buzz Appellate Litigation Briefing", t.buzz_appellate_briefing)}
            ${renderOptionalSection("historian", "Meanwhile, in the Courtroom (Post-Appellate Log)", t.courtroom_interlude_appellate)}
            ${renderOptionalSection("bailiff", "Bailiff Bar: Call to Order After Appellate Conference", t.bailiff_ratification_summons)}
            ${renderOptionalSection("fizz", "Phase 6A: Lobbyist-3 Floor Ratification Plea", t.l3_plea)}
            ${renderOptionalSection("buzz", "Phase 6B: Lobbyist-5 Floor Ratification Plea", t.l5_plea)}

            <div class="modal-section bailiff">
                <div class="modal-section-title">Bailiff Bar Emergency Mistrial Proclamation (Interrupted at: ${escapeHtml(t.interrupted_phase || "Floor Deliberations")})</div>
                <div class="modal-section-text">${escapeHtml(t.bailiff_mistrial_proclamation || "Judicial inference quorum severed during floor testimony; Mistrial escalated to Judge Baz.")}</div>
            </div>

            <div class="modal-section judge">
                <div class="modal-section-title">Judge Baz Official Order of Mistrial &amp; Retrial Calendar</div>
                <div class="modal-section-text">${escapeHtml(t.judge_mistrial_order || t.judge_baz_order || data.verdict)}</div>
            </div>

            <div class="modal-section historian">
                <div class="modal-section-title">Mandatory De Novo Retrial Docket Window</div>
                <div class="modal-section-text">${escapeHtml(retrialInfo)}</div>
            </div>

            <div class="docket-verdict-card mistrial" style="margin-top: 12px;">
                <div class="verdict-card-label">OFFICIAL ORDER OF MISTRIAL</div>
                <div class="verdict-card-token">${escapeHtml(data.emitted_token)}</div>
                <div class="verdict-card-desc">${escapeHtml(data.verdict)}</div>
            </div>

            ${t.fun_recap ? `
            <div class="modal-section news" style="margin-top: 10px;">
                <div class="modal-section-title">📺 Foo Universal News (FUN) — Recess Recap</div>
                <div class="modal-section-text">${formatInlineMarkdown(t.fun_recap)}</div>
            </div>` : ""}
        `;
    }

    return `
        <div class="archive-case-banner">
            <div>
                <div class="archive-case-title">${escapeHtml(data.case_id)} — Inbound Payload '${escapeHtml(data.payload)}'</div>
                <div class="archive-case-sub">Digital Root: ${escapeHtml(data.digital_root)}${escapeHtml(traceStr)} • Terminal Glyph: '${escapeHtml(data.terminal_glyph)}' • Adjudicated: ${escapeHtml(dateStr)}</div>
            </div>
            <span class="token-badge ${getBadgeClass(data.emitted_token)}" style="font-size:0.9rem;padding:4px 10px;">${escapeHtml(data.emitted_token)}</span>
        </div>

        <div class="modal-section bailiff">
            <div class="modal-section-title">Phase 0A: Bailiff Bar Docket Proclamation</div>
            <div class="modal-section-text">${escapeHtml(t.bailiff_proclamation || "Court called to order.")}</div>
        </div>

        <div class="modal-section historian">
            <div class="modal-section-title">Phase 0B: Court Historian Precedent Entry</div>
            <div class="modal-section-text">${escapeHtml(t.historian_statement || "Record entered.")}</div>
        </div>

        <div class="modal-section judge">
            <div class="modal-section-title">Phase 0C: Judge Baz Chamber Release Order</div>
            <div class="modal-section-text">${escapeHtml(t.judge_chamber_order || "Chambers ordered.")}</div>
        </div>

        <div class="modal-section fizz">
            <div class="modal-section-title">Phase 1A: Fizz Private Chamber (Behind Closed Doors)</div>
            <div class="modal-section-text">${escapeHtml(t.fizz_caucus_memo || "No memo filed.")}</div>
        </div>

        <div class="modal-section buzz">
            <div class="modal-section-title">Phase 1B: Buzz Private Chamber (Behind Closed Doors)</div>
            <div class="modal-section-text">${escapeHtml(t.buzz_caucus_memo || "No memo filed.")}</div>
        </div>

        ${renderOptionalSection("historian", "Meanwhile, in the Courtroom (Post-Chambers Log)", t.courtroom_interlude_chambers)}
        ${renderOptionalSection("bailiff", "Bailiff Bar: Call to Order After Chambers", t.bailiff_floor_summons)}

        <div class="modal-section fizz">
            <div class="modal-section-title">Phase 2A: Lobbyist-3 Floor Petition</div>
            <div class="modal-section-text">${escapeHtml(t.l3_claim || "No petition filed.")}</div>
        </div>

        <div class="modal-section buzz">
            <div class="modal-section-title">Phase 2B: Lobbyist-5 Floor Petition</div>
            <div class="modal-section-text">${escapeHtml(t.l5_claim || "No petition filed.")}</div>
        </div>

        <div class="modal-section auditor">
            <div class="modal-section-title">Phase 3: Forensic Zero-Trust Audit &amp; Provisional Byzantine Consensus</div>
            <div class="modal-section-text">${escapeHtml(t.audit_verdict || "No audit memo.")}${t.provisional_token ? `<br><br><strong>Provisional Consensus Determination ('${escapeHtml(t.provisional_token)}'):</strong> ${escapeHtml(t.verdict_desc || data.verdict)}` : ""}</div>
        </div>

        <div class="modal-section regulator">
            <div class="modal-section-title">Phase 4: Antitrust Market Determination</div>
            <div class="modal-section-text">${escapeHtml(t.antitrust_ruling || "No ruling filed.")}</div>
        </div>

        <div class="modal-section fizz">
            <div class="modal-section-title">Phase 5A: Fizz Appellate Litigation Briefing (Appeals Process)</div>
            <div class="modal-section-text">${escapeHtml(t.fizz_appellate_briefing || "No appellate briefing filed.")}</div>
        </div>

        <div class="modal-section buzz">
            <div class="modal-section-title">Phase 5B: Buzz Appellate Litigation Briefing (Appeals Process)</div>
            <div class="modal-section-text">${escapeHtml(t.buzz_appellate_briefing || "No appellate briefing filed.")}</div>
        </div>

        ${renderOptionalSection("historian", "Meanwhile, in the Courtroom (Post-Appellate Log)", t.courtroom_interlude_appellate)}
        ${renderOptionalSection("bailiff", "Bailiff Bar: Call to Order After Appellate Conference", t.bailiff_ratification_summons)}

        <div class="modal-section fizz">
            <div class="modal-section-title">Phase 6A: Lobbyist-3 Floor Ratification &amp; Appellate Plea</div>
            <div class="modal-section-text">${escapeHtml(t.l3_plea || "No plea recorded.")}</div>
        </div>

        <div class="modal-section buzz">
            <div class="modal-section-title">Phase 6B: Lobbyist-5 Floor Ratification &amp; Appellate Plea</div>
            <div class="modal-section-text">${escapeHtml(t.l5_plea || "No plea recorded.")}</div>
        </div>

        <div class="modal-section judge">
            <div class="modal-section-title">Phase 7: Judge Baz En Banc Appellate &amp; Final Byzantine Consensus Ruling</div>
            <div class="modal-section-text">${escapeHtml(t.judge_baz_order || t.appellate_order || "No decree filed.")}</div>
        </div>

        <div class="modal-section orator">
            <div class="modal-section-title">Phase 8: Constituent Victory Address</div>
            <div class="modal-section-text">${escapeHtml(t.victory_address || "No address delivered.")}</div>
        </div>

        <div class="docket-verdict-card" style="margin-top: 12px;">
            <div class="verdict-card-label">FINAL CERTIFIED CONSENSUS EMISSION</div>
            <div class="verdict-card-token">${escapeHtml(data.emitted_token)}</div>
            <div class="verdict-card-desc">${escapeHtml(data.verdict)}</div>
        </div>

        ${t.fun_recap ? `
        <div class="modal-section news" style="margin-top: 10px;">
            <div class="modal-section-title">📺 Foo Universal News (FUN) — Recess Recap</div>
            <div class="modal-section-text">${formatInlineMarkdown(t.fun_recap)}</div>
        </div>` : ""}
    `;
}

// --- THE ARCHIVES MODAL (ALL PRIORS IN ORDER) ---
async function openArchivesModal(initialCaseId = null) {
    const archivesModalEl = document.getElementById("archives-modal");
    const listPaneEl = document.getElementById("archives-list-pane");
    const summaryMetaEl = document.getElementById("archives-summary-meta");
    if (!archivesModalEl) return;

    archivesModalEl.classList.remove("hidden");
    listPaneEl.innerHTML = '<div class="modal-loading">Loading complete court archives...</div>';

    try {
        const res = await fetch(`/api/archives?order=${encodeURIComponent(archivesOrder)}`);
        if (!res.ok) throw new Error("Failed to load court archives");
        const payload = await res.json();
        allArchivesDockets = payload.dockets || [];

        const fizzCount = allArchivesDockets.filter(d => d.emitted_token === "Fizz").length;
        const buzzCount = allArchivesDockets.filter(d => d.emitted_token === "Buzz").length;
        const fbCount = allArchivesDockets.filter(d => d.emitted_token === "FizzBuzz").length;
        const mistrialCount = allArchivesDockets.filter(d => d.emitted_token === "Mistrial").length;
        const rawCount = allArchivesDockets.length - fizzCount - buzzCount - fbCount - mistrialCount;

        if (summaryMetaEl) {
            const mistrialSuffix = mistrialCount > 0 ? ` • Mistrial: ${mistrialCount}` : "";
            summaryMetaEl.innerText = `${allArchivesDockets.length} Total Priors • Fizz: ${fizzCount} • Buzz: ${buzzCount} • FizzBuzz: ${fbCount} • Digits: ${rawCount}${mistrialSuffix}`;
        }
        if (ledgerCountEl) {
            ledgerCountEl.innerText = `${allArchivesDockets.length} Priors`;
        }

        renderArchivesList();

        const targetCaseId = initialCaseId || (filteredArchivesDockets[0] && filteredArchivesDockets[0].case_id);
        if (targetCaseId) {
            await selectArchivesDocket(targetCaseId, true);
        }
    } catch (err) {
        listPaneEl.innerHTML = `<div class="modal-error">Error loading The Archives: ${escapeHtml(err.message)}</div>`;
    }
}

function closeArchivesModal() {
    const archivesModalEl = document.getElementById("archives-modal");
    if (archivesModalEl) archivesModalEl.classList.add("hidden");
}

function setArchivesFilter(filterVal) {
    archivesFilter = filterVal;
    const btns = document.querySelectorAll("#archives-filters .archive-filter-btn");
    btns.forEach(btn => {
        btn.classList.toggle("active", btn.getAttribute("data-filter") === filterVal);
    });
    renderArchivesList();
    if (filteredArchivesDockets.length > 0) {
        const stillPresent = filteredArchivesDockets.some(d => d.case_id === selectedArchivesCaseId);
        if (!stillPresent) {
            selectArchivesDocket(filteredArchivesDockets[0].case_id, true);
        } else {
            updateArchivesNavButtons();
        }
    }
}

function toggleArchivesOrder() {
    archivesOrder = archivesOrder === "desc" ? "asc" : "desc";
    const orderBtn = document.getElementById("archives-order-btn");
    if (orderBtn) {
        orderBtn.innerText = archivesOrder === "desc"
            ? "Order: Latest Inquisition First"
            : "Order: 1st Inquisition First";
    }
    allArchivesDockets.sort((a, b) => {
        if (a.id !== undefined && b.id !== undefined && a.id !== b.id) {
            return archivesOrder === "asc" ? a.id - b.id : b.id - a.id;
        }
        if (a.adjudicated_at && b.adjudicated_at && a.adjudicated_at !== b.adjudicated_at) {
            return archivesOrder === "asc" ? a.adjudicated_at - b.adjudicated_at : b.adjudicated_at - a.adjudicated_at;
        }
        return 0;
    });
    renderArchivesList();
    updateArchivesNavButtons();
}

function renderArchivesList() {
    const listPaneEl = document.getElementById("archives-list-pane");
    const searchInputEl = document.getElementById("archives-search-input");
    if (!listPaneEl) return;

    const query = (searchInputEl ? searchInputEl.value : "").trim().toLowerCase();

    filteredArchivesDockets = allArchivesDockets.filter(item => {
        const badgeClass = getBadgeClass(item.emitted_token);
        if (archivesFilter !== "all" && badgeClass !== archivesFilter) {
            return false;
        }
        if (query) {
            const matchPayload = String(item.payload).toLowerCase().includes(query);
            const matchCase = String(item.case_id).toLowerCase().includes(query);
            const matchToken = String(item.emitted_token).toLowerCase().includes(query);
            if (!matchPayload && !matchCase && !matchToken) return false;
        }
        return true;
    });

    if (filteredArchivesDockets.length === 0) {
        listPaneEl.innerHTML = '<div class="ledger-empty">No prior dockets match the current filter.</div>';
        return;
    }

    listPaneEl.innerHTML = filteredArchivesDockets.map((item, idx) => {
        const badgeClass = getBadgeClass(item.emitted_token);
        const isActive = item.case_id === selectedArchivesCaseId ? "active" : "";
        return `
            <div class="archive-list-item ${isActive}"
                 id="archive-item-${escapeHtml(item.case_id)}"
                 onclick="selectArchivesDocket('${escapeHtml(item.case_id)}')">
                <div class="ledger-item-left">
                    <span class="ledger-payload">${escapeHtml(item.case_id)}: '${escapeHtml(item.payload)}'</span>
                    <span class="ledger-details">Root: ${escapeHtml(item.digital_root)} • Glyph: '${escapeHtml(item.terminal_glyph)}'</span>
                </div>
                <span class="token-badge ${badgeClass}">${escapeHtml(item.emitted_token)}</span>
            </div>
        `;
    }).join("");
}

function updateArchivesNavButtons() {
    const prevBtn = document.getElementById("archives-prev-btn");
    const nextBtn = document.getElementById("archives-next-btn");
    const navLabel = document.getElementById("archives-nav-label");
    if (!prevBtn || !nextBtn || !navLabel) return;

    const idx = filteredArchivesDockets.findIndex(d => d.case_id === selectedArchivesCaseId);
    if (idx === -1) {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        navLabel.innerText = "Select a docket to review";
        return;
    }

    prevBtn.disabled = idx <= 0;
    nextBtn.disabled = idx >= filteredArchivesDockets.length - 1;
    const item = filteredArchivesDockets[idx];
    navLabel.innerText = `Prior ${idx + 1} of ${filteredArchivesDockets.length} (${item.case_id} • Payload '${item.payload}')`;
}

async function selectArchivesDocket(caseId, scrollIntoView = false) {
    selectedArchivesCaseId = caseId;
    const reviewContentEl = document.getElementById("archives-review-content");

    // Highlight active item in left list
    document.querySelectorAll(".archive-list-item").forEach(el => {
        el.classList.toggle("active", el.id === `archive-item-${caseId}`);
    });
    if (scrollIntoView) {
        const activeEl = document.getElementById(`archive-item-${caseId}`);
        if (activeEl && activeEl.scrollIntoView) {
            activeEl.scrollIntoView({ block: "nearest" });
        }
    }

    updateArchivesNavButtons();

    if (!reviewContentEl) return;
    reviewContentEl.innerHTML = `<div class="modal-loading">Loading transcript for ${escapeHtml(caseId)}...</div>`;

    try {
        const res = await fetch(`/api/docket/${encodeURIComponent(caseId)}`);
        if (!res.ok) {
            reviewContentEl.innerHTML = `<div class="modal-error">Docket ${escapeHtml(caseId)} not found in archives.</div>`;
            return;
        }
        const data = await res.json();
        reviewContentEl.innerHTML = buildTranscriptHtml(data);
        reviewContentEl.scrollTop = 0;
    } catch (e) {
        reviewContentEl.innerHTML = `<div class="modal-error">Error loading docket: ${escapeHtml(e.message)}</div>`;
    }
}

function stepArchivesDocket(delta) {
    const idx = filteredArchivesDockets.findIndex(d => d.case_id === selectedArchivesCaseId);
    if (idx === -1) return;
    const nextIdx = idx + delta;
    if (nextIdx >= 0 && nextIdx < filteredArchivesDockets.length) {
        selectArchivesDocket(filteredArchivesDockets[nextIdx].case_id, true);
    }
}

async function openCaseModal(caseId) {
    modalCaseTitleEl.innerText = caseId;
    modalCaseMetaEl.innerText = "Loading archived record...";
    modalCaseBodyEl.innerHTML = '<div class="modal-loading">Querying SQLite persistent ledger...</div>';
    caseModalEl.classList.remove("hidden");

    try {
        const res = await fetch(`/api/docket/${encodeURIComponent(caseId)}`);
        if (!res.ok) {
            modalCaseBodyEl.innerHTML = `<div class="modal-error">Docket ${escapeHtml(caseId)} not found in archives.</div>`;
            return;
        }

        const data = await res.json();
        const dateStr = new Date(data.adjudicated_at * 1000).toLocaleString();
        modalCaseMetaEl.innerText = `Inbound Payload '${data.payload}' • Digital Root: ${data.digital_root} • Terminal Glyph: '${data.terminal_glyph}' • Adjudicated: ${dateStr}`;
        modalCaseBodyEl.innerHTML = buildTranscriptHtml(data);
    } catch (e) {
        modalCaseBodyEl.innerHTML = `<div class="modal-error">Error loading docket: ${escapeHtml(e.message)}</div>`;
    }
}

function openAgentProfile(agentId) {
    const profile = AGENT_PROFILES[agentId];
    if (!profile) return;
    const modalEl = document.getElementById("profile-modal");
    if (!modalEl) return;

    const bannerEl = document.getElementById("profile-banner-img");
    if (bannerEl) {
        bannerEl.src = profile.banner;
        bannerEl.alt = `${profile.name} Banner`;
    }

    const avatarEl = document.getElementById("profile-avatar-img");
    if (avatarEl) {
        avatarEl.src = profile.avatar;
        avatarEl.alt = profile.name;
    }

    const nameEl = document.getElementById("profile-display-name");
    if (nameEl) nameEl.innerText = profile.name;

    const handleEl = document.getElementById("profile-handle");
    if (handleEl) handleEl.innerText = profile.handle;

    const titleEl = document.getElementById("profile-official-title");
    if (titleEl) titleEl.innerText = profile.title;

    const factionPill = document.getElementById("profile-faction-pill");
    if (factionPill) {
        factionPill.innerText = profile.faction;
        factionPill.className = `profile-faction-pill faction-${profile.factionSlug || "judge"}`;
    }

    const standingEl = document.getElementById("profile-stat-standing");
    if (standingEl) standingEl.innerText = profile.standing || "Standing Certified";

    const jurisEl = document.getElementById("profile-stat-jurisdiction");
    if (jurisEl) jurisEl.innerText = profile.jurisdiction || "Tribunal-Wide";

    const operEl = document.getElementById("profile-stat-operator");
    if (operEl) operEl.innerText = profile.operatorPolicy || "Strictly Modulo-Free (%)";

    const statusEl = document.getElementById("profile-stat-status");
    if (statusEl) statusEl.innerText = profile.defaultStatus || "Deliberating";

    const whoEl = document.getElementById("profile-who-i-am");
    if (whoEl) whoEl.innerText = profile.whoIAm;

    const whatEl = document.getElementById("profile-what-i-do");
    if (whatEl) whatEl.innerText = profile.whatIDo;

    const motEl = document.getElementById("profile-motivations");
    if (motEl) motEl.innerText = profile.motivations;

    const sigEl = document.getElementById("profile-signature");
    if (sigEl) sigEl.innerText = profile.signature;

    modalEl.classList.remove("hidden");
}

function closeProfileModal() {
    const modalEl = document.getElementById("profile-modal");
    if (modalEl) modalEl.classList.add("hidden");
}

function closeCaseModal() {
    caseModalEl.classList.add("hidden");
}

function openInfoModal(tab = "swarm") {
    const infoModalEl = document.getElementById("info-modal");
    if (!infoModalEl) return;
    switchInfoTab(tab);
    infoModalEl.classList.remove("hidden");
}

function closeInfoModal() {
    const infoModalEl = document.getElementById("info-modal");
    if (infoModalEl) infoModalEl.classList.add("hidden");
}

function switchInfoTab(tab) {
    const isMath = tab === "math";
    const btnSwarm = document.getElementById("info-tab-btn-swarm");
    const btnMath = document.getElementById("info-tab-btn-math");
    const panelSwarm = document.getElementById("info-panel-swarm");
    const panelMath = document.getElementById("info-panel-math");

    if (btnSwarm) btnSwarm.classList.toggle("active", !isMath);
    if (btnMath) btnMath.classList.toggle("active", isMath);
    if (panelSwarm) panelSwarm.classList.toggle("hidden", isMath);
    if (panelMath) panelMath.classList.toggle("hidden", !isMath);
}

window.addEventListener("click", (e) => {
    const profileModalEl = document.getElementById("profile-modal");
    if (profileModalEl && e.target === profileModalEl) {
        closeProfileModal();
    }
    if (e.target === caseModalEl) {
        closeCaseModal();
    }
    const archivesModalEl = document.getElementById("archives-modal");
    if (archivesModalEl && e.target === archivesModalEl) {
        closeArchivesModal();
    }
    const infoModalEl = document.getElementById("info-modal");
    if (infoModalEl && e.target === infoModalEl) {
        closeInfoModal();
    }
});

window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        closeProfileModal();
        closeCaseModal();
        closeArchivesModal();
        closeInfoModal();
    }
});

function reconnectObserver() {
    standbyOverlayEl.classList.add("hidden");
    sendVisibilityHeartbeat();
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

const AMAZON_ASSOCIATE_TAG = "adamoutler-20";
const AMAZON_CATALOG = [
    {
        icon: "⚡",
        title: "Local LLM Inference GPUs & AI Rigs",
        desc: "Power 17-agent Ollama swarms locally with zero cloud token bills.",
        cta: "Shop on Amazon \u2192",
        query: "nvidia+rtx+gpu+local+ai+workstation"
    },
    {
        icon: "\uD83D\uDC68\u200D\u2696\uFE0F",
        title: "Presiding Magistrate Hardwood Gavel Set",
        desc: "Overrule remand petitions and dissolve stays at your desk with prejudice.",
        cta: "View on Amazon \u2192",
        query: "judge+gavel+and+block+set+solid+wood"
    },
    {
        icon: "\uD83D\uDDA5\uFE0F",
        title: "Ryzen AI & Homelab Mini PCs (64GB RAM)",
        desc: "Compact silent server nodes for 24/7 Docker & multi-agent orchestration.",
        cta: "View on Amazon \u2192",
        query: "ryzen+ai+mini+pc+64gb+ram+homelab"
    },
    {
        icon: "\uD83D\uDCDA",
        title: "Designing Data-Intensive Applications",
        desc: "Master Byzantine fault tolerance, consensus algorithms, and distributed state.",
        cta: "View on Amazon \u2192",
        query: "designing+data+intensive+applications+book"
    },
    {
        icon: "\u2328\uFE0F",
        title: "Keychron Custom Mechanical Keyboards",
        desc: "Draft adversarial floor petitions and appellate briefs at maximum WPM.",
        cta: "Shop on Amazon \u2192",
        query: "keychron+q+series+mechanical+keyboard"
    },
    {
        icon: "\uD83D\uDCBE",
        title: "4TB Gen4/Gen5 NVMe SSDs for Vector DBs",
        desc: "High-IOPS persistent storage for SQLite ledgers and LLM model weights.",
        cta: "View on Amazon \u2192",
        query: "samsung+990+pro+4tb+nvme+ssd"
    }
];
let amazonPairIndex = 0;

function rotateAmazonAds() {
    const gridEl = document.getElementById("amazon-items-grid");
    if (!gridEl) return;
    amazonPairIndex = (amazonPairIndex + 2) % AMAZON_CATALOG.length;
    const items = [
        AMAZON_CATALOG[amazonPairIndex],
        AMAZON_CATALOG[(amazonPairIndex + 1) % AMAZON_CATALOG.length]
    ];
    gridEl.innerHTML = items.map(item => `
        <a href="https://www.amazon.com/s?k=${item.query}&amp;tag=${AMAZON_ASSOCIATE_TAG}"
           target="_blank"
           rel="nofollow sponsored noopener"
           class="amazon-product-item">
            <div class="amazon-item-top">
                <span class="amazon-item-icon">${item.icon}</span>
                <div class="amazon-item-info">
                    <div class="amazon-item-title">${escapeHtml(item.title)}</div>
                    <div class="amazon-item-desc">${escapeHtml(item.desc)}</div>
                </div>
            </div>
            <span class="amazon-cta-btn">${escapeHtml(item.cta)}</span>
        </a>
    `).join("");
}

window.openAgentProfile = openAgentProfile;
window.closeProfileModal = closeProfileModal;
window.rotateAmazonAds = rotateAmazonAds;
window.openArchivesModal = openArchivesModal;
window.closeArchivesModal = closeArchivesModal;
window.setArchivesFilter = setArchivesFilter;
window.toggleArchivesOrder = toggleArchivesOrder;
window.renderArchivesList = renderArchivesList;
window.selectArchivesDocket = selectArchivesDocket;
window.stepArchivesDocket = stepArchivesDocket;
window.openInfoModal = openInfoModal;
window.closeInfoModal = closeInfoModal;
window.switchInfoTab = switchInfoTab;

window.addEventListener("DOMContentLoaded", () => {
    connectWebSocket();
});
