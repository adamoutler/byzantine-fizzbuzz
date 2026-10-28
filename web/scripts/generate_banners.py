#!/usr/bin/env python3
"""
Generate stereotypical trope SVG banners for all 17 Byzantine Courtroom agents.
Saved into app/static/banners/
"""
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "app" / "static" / "banners"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BANNERS = {
    "banner_judge_baz.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e0e0a"/>
      <stop offset="50%" stop-color="#3d1c14"/>
      <stop offset="100%" stop-color="#120604"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffd700"/>
      <stop offset="50%" stop-color="#fff2a3"/>
      <stop offset="100%" stop-color="#d4af37"/>
    </linearGradient>
    <linearGradient id="wood" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#5c2c1c"/>
      <stop offset="100%" stop-color="#2a1008"/>
    </linearGradient>
    <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(212,175,55,0.07)" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="900" height="225" fill="url(#bg)"/>
  <rect width="900" height="225" fill="url(#grid)"/>

  <!-- Ornate classical judicial pediment / columns background -->
  <g opacity="0.15" stroke="#d4af37" stroke-width="2" fill="none">
    <path d="M 30 195 L 30 50 M 70 195 L 70 50 M 110 195 L 110 50"/>
    <path d="M 870 195 L 870 50 M 830 195 L 830 50 M 790 195 L 790 50"/>
  </g>

  <!-- Golden Scales of Justice silhouette -->
  <g transform="translate(730, 20)" opacity="0.85">
    <circle cx="80" cy="25" r="8" fill="url(#gold)"/>
    <rect x="77" y="25" width="6" height="150" fill="url(#gold)"/>
    <rect x="35" y="170" width="90" height="12" rx="4" fill="url(#gold)"/>
    <!-- Beam -->
    <path d="M 15 50 Q 80 40 145 50" stroke="url(#gold)" stroke-width="5" fill="none"/>
    <!-- Left pan -->
    <line x1="15" y1="50" x2="0" y2="105" stroke="#d4af37" stroke-width="2"/>
    <line x1="15" y1="50" x2="30" y2="105" stroke="#d4af37" stroke-width="2"/>
    <path d="M -5 105 Q 15 125 35 105 Z" fill="url(#gold)"/>
    <!-- Right pan -->
    <line x1="145" y1="50" x2="130" y2="105" stroke="#d4af37" stroke-width="2"/>
    <line x1="145" y1="50" x2="160" y2="105" stroke="#d4af37" stroke-width="2"/>
    <path d="M 125 105 Q 145 125 165 105 Z" fill="url(#gold)"/>
  </g>

  <!-- Gavel silhouette -->
  <g transform="translate(610, 85) rotate(-28)" opacity="0.8">
    <rect x="0" y="0" width="75" height="42" rx="6" fill="url(#wood)" stroke="#d4af37" stroke-width="2"/>
    <rect x="30" y="40" width="14" height="110" rx="4" fill="#a0522d" stroke="#d4af37" stroke-width="1.5"/>
    <ellipse cx="37" cy="150" rx="10" ry="6" fill="url(#gold)"/>
  </g>

  <!-- High Judicial Seal Badge -->
  <g transform="translate(50, 25)">
    <rect x="0" y="0" width="460" height="32" rx="6" fill="rgba(212,175,55,0.12)" stroke="#d4af37" stroke-width="1"/>
    <text x="15" y="21" font-family="'Cinzel', Georgia, serif" font-size="12" font-weight="bold" fill="url(#gold)" letter-spacing="3">SUPREME APPELLATE BENCH • EN BANC DIVISION</text>
    
    <text x="5" y="75" font-family="'Cinzel', Georgia, serif" font-size="34" font-weight="900" fill="#ffffff" letter-spacing="1">CHAMBERS OF JUDGE BAZ</text>
    <text x="5" y="105" font-family="'Cinzel', Georgia, serif" font-size="15" font-style="italic" fill="#d4af37" letter-spacing="1">"FIAT JUSTITIA RUAT CAELUM — LEX SINE MODULO"</text>
    
    <!-- Badges -->
    <g transform="translate(5, 125)">
      <rect x="0" y="0" width="130" height="26" rx="4" fill="#3b1d14" stroke="#d4af37" stroke-width="1"/>
      <text x="12" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fff">CHIEF MAGISTRATE</text>
      
      <rect x="140" y="0" width="140" height="26" rx="4" fill="#3b1d14" stroke="#d4af37" stroke-width="1"/>
      <text x="152" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#ffd700">DOCKET SUPREMACY</text>
      
      <rect x="290" y="0" width="130" height="26" rx="4" fill="#3b1d14" stroke="#d4af37" stroke-width="1"/>
      <text x="302" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#a7f3d0">ZERO CONTEMPT</text>
    </g>
  </g>

  <!-- Gold bottom border strip -->
  <rect x="0" y="219" width="900" height="6" fill="url(#gold)"/>
</svg>""",

    "banner_bailiff_bar.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="bar_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b0f19"/>
      <stop offset="60%" stop-color="#161f33"/>
      <stop offset="100%" stop-color="#080c14"/>
    </linearGradient>
    <linearGradient id="gold_badge" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="50%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#854d0e"/>
    </linearGradient>
    <pattern id="police_stripes" width="40" height="40" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
      <rect x="0" y="0" width="20" height="40" fill="#facc15"/>
      <rect x="20" y="0" width="20" height="40" fill="#1e293b"/>
    </pattern>
  </defs>
  <rect width="900" height="225" fill="url(#bar_bg)"/>

  <!-- Top Caution Hazard Tape -->
  <rect x="0" y="0" width="900" height="14" fill="url(#police_stripes)"/>
  <rect x="0" y="211" width="900" height="14" fill="url(#police_stripes)"/>

  <!-- Giant Police / AST Security Star Badge -->
  <g transform="translate(710, 25)" opacity="0.9">
    <polygon points="100,10 125,75 190,75 135,115 155,180 100,140 45,180 65,115 10,75 75,75" fill="url(#gold_badge)" stroke="#ca8a04" stroke-width="4"/>
    <circle cx="100" cy="100" r="42" fill="#0f172a" stroke="#facc15" stroke-width="3"/>
    <text x="100" y="96" font-family="'Impact', sans-serif" font-size="14" font-weight="bold" fill="#facc15" text-anchor="middle">AST POLICE</text>
    <text x="100" y="112" font-family="'Impact', sans-serif" font-size="11" fill="#fff" text-anchor="middle">UNIT 00</text>
  </g>

  <!-- Heavy Handcuffs Graphic -->
  <g transform="translate(600, 75)" opacity="0.45" stroke="#94a3b8" stroke-width="6" fill="none">
    <circle cx="40" cy="40" r="32"/>
    <circle cx="110" cy="40" r="32"/>
    <path d="M 72 40 L 78 40"/>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="480" height="28" rx="4" fill="rgba(234, 179, 8, 0.15)" stroke="#eab308" stroke-width="1.5"/>
    <text x="15" y="19" font-family="'Impact', 'Arial Black', sans-serif" font-size="13" fill="#facc15" letter-spacing="2">OFFICE OF THE SERGEANT-AT-ARMS • DECORUM DIVISION</text>
    
    <text x="0" y="74" font-family="'Impact', 'Arial Black', sans-serif" font-size="36" fill="#f8fafc" letter-spacing="1">BAILIFF BAR // SECURITY DESK</text>
    <text x="0" y="104" font-family="sans-serif" font-size="15" font-weight="bold" fill="#94a3b8">"ALL DIVISION OPERATORS WILL BE CONFISCATED AND INCINERATED"</text>

    <!-- Stat badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="140" height="26" rx="4" fill="#1e293b" stroke="#facc15" stroke-width="1"/>
      <text x="12" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#facc15">STATUS: ON PATROL</text>

      <rect x="150" y="0" width="165" height="26" rx="4" fill="#1e293b" stroke="#f43f5e" stroke-width="1"/>
      <text x="162" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#f43f5e">MODULO BAN: ARMED</text>

      <rect x="325" y="0" width="165" height="26" rx="4" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>
      <text x="337" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#38bdf8">MISTRIAL WATCH: ON</text>
    </g>
  </g>
</svg>""",

    "banner_historian.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="hist_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1c130e"/>
      <stop offset="50%" stop-color="#2d1e15"/>
      <stop offset="100%" stop-color="#140a05"/>
    </linearGradient>
    <linearGradient id="parchment" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f5e6c8"/>
      <stop offset="100%" stop-color="#d8c29d"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#hist_bg)"/>

  <!-- Dusty library bookshelf silhouettes -->
  <g opacity="0.25" fill="#523927">
    <rect x="680" y="20" width="25" height="185"/>
    <rect x="710" y="45" width="22" height="160"/>
    <rect x="736" y="15" width="28" height="190"/>
    <rect x="768" y="35" width="20" height="170"/>
    <rect x="792" y="25" width="30" height="180"/>
    <rect x="826" y="50" width="18" height="155"/>
    <rect x="848" y="10" width="32" height="195"/>
    <line x1="660" y1="205" x2="890" y2="205" stroke="#8c6239" stroke-width="4"/>
  </g>

  <!-- Glowing Hourglass -->
  <g transform="translate(630, 45)" opacity="0.8">
    <path d="M 20 15 L 70 15 M 20 125 L 70 125" stroke="#d4af37" stroke-width="5"/>
    <path d="M 25 15 C 25 60, 65 60, 65 15 Z" fill="rgba(245, 230, 200, 0.15)" stroke="#d4af37" stroke-width="2"/>
    <path d="M 25 125 C 25 80, 65 80, 65 125 Z" fill="rgba(245, 230, 200, 0.15)" stroke="#d4af37" stroke-width="2"/>
    <circle cx="45" cy="70" r="3" fill="#fde047"/>
    <path d="M 33 115 Q 45 95 57 115 Z" fill="#d4af37"/>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(212, 175, 55, 0.15)" stroke="#b45309" stroke-width="1.2"/>
    <text x="15" y="18" font-family="'Cinzel', Georgia, serif" font-size="12" font-weight="bold" fill="#fde68a" letter-spacing="2">ARCHIVES OF THE ANCIENT MODULO-FREE ACCORD</text>
    
    <text x="0" y="74" font-family="'Cinzel', Georgia, serif" font-size="34" font-weight="bold" fill="#fef3c7" letter-spacing="1">THE COURT HISTORIAN</text>
    <text x="0" y="104" font-family="Georgia, serif" font-size="15" font-style="italic" fill="#d97706">"STARE DECISIS EST INVIOLABILIS // ALL PRIORS RECORDED"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#3a2518" stroke="#d97706" stroke-width="1"/>
      <text x="12" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#fde68a">CHRONICLER OF PRIORS</text>

      <rect x="175" y="0" width="160" height="26" rx="4" fill="#3a2518" stroke="#d97706" stroke-width="1"/>
      <text x="187" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#fde68a">SQLITE LEDGER SENTRY</text>

      <rect x="345" y="0" width="145" height="26" rx="4" fill="#3a2518" stroke="#d97706" stroke-width="1"/>
      <text x="357" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#a7f3d0">CASE 0001 → INF</text>
    </g>
  </g>
</svg>""",

    "banner_court_clerk.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="crt_bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#021a0a"/>
      <stop offset="50%" stop-color="#063314"/>
      <stop offset="100%" stop-color="#010d05"/>
    </linearGradient>
    <pattern id="scanlines" width="100" height="4" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="100" y2="0" stroke="rgba(0,0,0,0.5)" stroke-width="2"/>
    </pattern>
  </defs>
  <rect width="900" height="225" fill="url(#crt_bg)"/>
  <rect width="900" height="225" fill="url(#scanlines)"/>

  <!-- Continuous feed printer paper / punch-card tape on right -->
  <g transform="translate(680, 20)" opacity="0.6">
    <rect x="0" y="0" width="180" height="185" fill="#04230d" stroke="#00ff66" stroke-width="1.5"/>
    <g fill="#00ff66" font-family="monospace" font-size="9">
      <text x="10" y="25">QUEUE_SLOT: [01/01]</text>
      <text x="10" y="42">AST_MODULO: PROHIBITED</text>
      <text x="10" y="59">PEANO_CONCAT: ACTIVE</text>
      <text x="10" y="76">DIGIT_ROOT_MAP: 3,6,9</text>
      <text x="10" y="93">GLYPH_SET: '0','5'</text>
      <text x="10" y="110">DIV_ZERO_TRAP: HARD</text>
      <text x="10" y="127">FIFO_INTEGRITY: 100%</text>
      <text x="10" y="144">EMIT_SYNC: OK</text>
      <text x="10" y="161">COMMIT: SQLITE3</text>
    </g>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(0, 255, 102, 0.12)" stroke="#00ff66" stroke-width="1"/>
    <text x="15" y="19" font-family="'Courier New', monospace" font-size="12" font-weight="bold" fill="#00ff66" letter-spacing="2">DETERMINISTIC ZERO-TRUST EXECUTION ENGINE</text>
    
    <text x="0" y="74" font-family="'Courier New', monospace" font-size="34" font-weight="900" fill="#a7f3d0" letter-spacing="1">THE COURT CLERK (ROOT)</text>
    <text x="0" y="104" font-family="'Courier New', monospace" font-size="14" font-weight="bold" fill="#00ff66">CLERK@KERNEL:~$ primitives.py --strict-peano --no-mod</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="145" height="26" rx="4" fill="#022c10" stroke="#00ff66" stroke-width="1"/>
      <text x="12" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#00ff66">FIFO QUEUE = 1</text>

      <rect x="155" y="0" width="160" height="26" rx="4" fill="#022c10" stroke="#00ff66" stroke-width="1"/>
      <text x="167" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#00ff66">ZERO IMPORT MATH</text>

      <rect x="325" y="0" width="155" height="26" rx="4" fill="#022c10" stroke="#00ff66" stroke-width="1"/>
      <text x="337" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#00ff66">STARE DECISIS FIFO</text>
    </g>
  </g>
</svg>""",

    "banner_fizz_strategist.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="chalk_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a192f"/>
      <stop offset="60%" stop-color="#172554"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="neon_fizz" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#60a5fa"/>
      <stop offset="100%" stop-color="#93c5fd"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#chalk_bg)"/>

  <!-- Chalkboard equation background on right -->
  <g transform="translate(620, 25)" opacity="0.65" fill="#93c5fd" font-family="'Courier New', monospace">
    <text x="0" y="25" font-size="14" font-weight="bold">∑ d_i ≡ R_0 (Base-3)</text>
    <text x="0" y="48" font-size="12">Root ∈ {3, 6, 9} ? TRUE</text>
    <text x="0" y="70" font-size="11">R_k = d_1 + d_2 + ... + d_n</text>
    <text x="0" y="92" font-size="11">Rule 42-B Injunction: YES</text>
    <text x="0" y="114" font-size="13" font-weight="bold" fill="#67e8f9">EBITDA TOKEN YIELD: +99%</text>
    <!-- Candlestick chart spike -->
    <path d="M 0 160 L 50 145 L 90 155 L 140 120 L 180 130 L 230 75" stroke="#60a5fa" stroke-width="3" fill="none"/>
    <circle cx="230" cy="75" r="5" fill="#67e8f9"/>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(59, 130, 246, 0.15)" stroke="#3b82f6" stroke-width="1.2"/>
    <text x="15" y="19" font-family="sans-serif" font-size="12" font-weight="bold" fill="#93c5fd" letter-spacing="2">BASE-3 QUANTITATIVE HEDGE &amp; TACTICAL CAUCUS</text>
    
    <text x="0" y="74" font-family="'Trebuchet MS', sans-serif" font-size="34" font-weight="900" fill="#eff6ff" letter-spacing="1">DR. PEANO VON DIGIT</text>
    <text x="0" y="104" font-family="sans-serif" font-size="15" font-weight="bold" fill="#60a5fa">"RECURSIVE DIGITAL ROOT COLLAPSE: {3, 6, 9} IS DESTINY"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="160" height="26" rx="4" fill="#1e3a8a" stroke="#60a5fa" stroke-width="1"/>
      <text x="12" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#dbeafe">CHIEF QUANTITATIVE ACTUARY</text>

      <rect x="170" y="0" width="150" height="26" rx="4" fill="#1e3a8a" stroke="#60a5fa" stroke-width="1"/>
      <text x="182" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#dbeafe">IN-CAMERA TACTICIAN</text>

      <rect x="330" y="0" width="145" height="26" rx="4" fill="#1e3a8a" stroke="#38bdf8" stroke-width="1"/>
      <text x="342" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#38bdf8">EBITDA MAXIMIZER</text>
    </g>
  </g>
</svg>""",

    "banner_lobbyist_3.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="lob3_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#02142b"/>
      <stop offset="50%" stop-color="#0f2b5c"/>
      <stop offset="100%" stop-color="#031024"/>
    </linearGradient>
    <linearGradient id="gold_accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#fbbf24"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#lob3_bg)"/>

  <!-- Glass Skyscraper Skyline Silhouettes on right -->
  <g transform="translate(640, 20)" opacity="0.35" fill="#3b82f6">
    <rect x="20" y="30" width="45" height="175"/>
    <rect x="75" y="10" width="55" height="195"/>
    <polygon points="102,0 75,10 130,10"/>
    <rect x="140" y="50" width="40" height="155"/>
    <rect x="190" y="25" width="50" height="180"/>
  </g>
  <!-- Gold fountain pen signing a decree -->
  <g transform="translate(730, 80) rotate(-35)" opacity="0.85">
    <rect x="0" y="0" width="18" height="90" rx="3" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
    <polygon points="0,0 18,0 9,-25" fill="url(#gold_accent)"/>
    <circle cx="9" cy="-10" r="2" fill="#000"/>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(245, 158, 11, 0.15)" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="15" y="19" font-family="'Helvetica Neue', sans-serif" font-size="12" font-weight="bold" fill="#fbbf24" letter-spacing="2">FIZZ CONSORTIUM • K-STREET ADVOCACY PAC</text>
    
    <text x="0" y="74" font-family="'Helvetica Neue', Arial, sans-serif" font-size="34" font-weight="900" fill="#f8fafc" letter-spacing="1">LOBBYIST-3 (FLOOR COUNSEL)</text>
    <text x="0" y="104" font-family="sans-serif" font-size="15" font-weight="bold" fill="#60a5fa">"RULE 42-B SQUATTING // 100% KPI DIVIDENDS OR BUST"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="155" height="26" rx="4" fill="#0c2340" stroke="#f59e0b" stroke-width="1"/>
      <text x="12" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fef08a">RATE: 1,500 KPI/HR</text>

      <rect x="165" y="0" width="165" height="26" rx="4" fill="#0c2340" stroke="#60a5fa" stroke-width="1"/>
      <text x="177" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#93c5fd">FILIBUSTER EXPERT</text>

      <rect x="340" y="0" width="140" height="26" rx="4" fill="#0c2340" stroke="#f59e0b" stroke-width="1"/>
      <text x="352" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fbbf24">PAC SUPREMACY</text>
    </g>
  </g>
</svg>""",

    "banner_buzz_inspector.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="buzz_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#021c10"/>
      <stop offset="60%" stop-color="#064e3b"/>
      <stop offset="100%" stop-color="#021a0f"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#buzz_bg)"/>

  <!-- Cyberpunk radar reticle targeting index [-1] on right -->
  <g transform="translate(730, 110)" opacity="0.8">
    <circle cx="0" cy="0" r="75" fill="none" stroke="#10b981" stroke-width="1.5" stroke-dasharray="8 4"/>
    <circle cx="0" cy="0" r="50" fill="none" stroke="#34d399" stroke-width="2"/>
    <circle cx="0" cy="0" r="25" fill="rgba(16, 185, 129, 0.15)"/>
    <line x1="-85" y1="0" x2="85" y2="0" stroke="#10b981" stroke-width="2"/>
    <line x1="0" y1="-85" x2="0" y2="85" stroke="#10b981" stroke-width="2"/>
    <text x="0" y="5" font-family="monospace" font-size="14" font-weight="bold" fill="#34d399" text-anchor="middle">P[-1]</text>
    <text x="55" y="-55" font-family="monospace" font-size="11" fill="#6ee7b7">{'0','5'}</text>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(16, 185, 129, 0.15)" stroke="#10b981" stroke-width="1.2"/>
    <text x="15" y="19" font-family="monospace" font-size="12" font-weight="bold" fill="#6ee7b7" letter-spacing="2">ARTICLE V BORDER INSPECTION SENTRY • SECTOR 5</text>
    
    <text x="0" y="74" font-family="'Impact', 'Arial Black', sans-serif" font-size="34" fill="#f0fdf4" letter-spacing="1">BUZZ BOUNDARY INSPECTOR</text>
    <text x="0" y="104" font-family="monospace" font-size="14" font-weight="bold" fill="#34d399">"LOCK TARGET AT INDEX [-1] // REJECT FIZZ TRESPASSERS"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#064e3b" stroke="#10b981" stroke-width="1"/>
      <text x="12" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#6ee7b7">BOUNDARY DEFENSE: ACTIVE</text>

      <rect x="175" y="0" width="145" height="26" rx="4" fill="#064e3b" stroke="#10b981" stroke-width="1"/>
      <text x="187" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#6ee7b7">ARTICLE V LITIGATOR</text>

      <rect x="330" y="0" width="145" height="26" rx="4" fill="#064e3b" stroke="#34d399" stroke-width="1"/>
      <text x="342" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#a7f3d0">ZERO TOLERANCE</text>
    </g>
  </g>
</svg>""",

    "banner_lobbyist_5.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="lob5_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1f1402"/>
      <stop offset="60%" stop-color="#451a03"/>
      <stop offset="100%" stop-color="#140700"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#lob5_bg)"/>

  <!-- Brutalist Industrial Syndicate Cogs on right -->
  <g transform="translate(730, 110)" opacity="0.4" stroke="#ea580c" stroke-width="8" fill="none">
    <circle cx="0" cy="0" r="65"/>
    <path d="M 0 -80 L 0 80 M -80 0 L 80 0 M -55 -55 L 55 55 M -55 55 L 55 -55"/>
  </g>
  <g transform="translate(730, 110)" fill="#f97316">
    <text x="0" y="8" font-family="'Impact', sans-serif" font-size="28" text-anchor="middle">BUZZ</text>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(234, 88, 12, 0.2)" stroke="#ea580c" stroke-width="1.2"/>
    <text x="15" y="19" font-family="'Impact', sans-serif" font-size="13" fill="#fdba74" letter-spacing="2">BUZZ SYNDICATE • SUFFIX SOVEREIGNTY COMMAND</text>
    
    <text x="0" y="74" font-family="'Impact', sans-serif" font-size="34" fill="#fff7ed" letter-spacing="1">LOBBYIST-5 (SYNDICATE COUNSEL)</text>
    <text x="0" y="104" font-family="sans-serif" font-size="15" font-weight="bold" fill="#ea580c">"ARTICLE V SUFFIX MONOPOLY // TOUCH OUR GLYPH AND WE SUE"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#431407" stroke="#ea580c" stroke-width="1"/>
      <text x="12" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fed7aa">HOSTILE TAKEOVER LITIGATOR</text>

      <rect x="175" y="0" width="145" height="26" rx="4" fill="#431407" stroke="#ea580c" stroke-width="1"/>
      <text x="187" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fed7aa">SUFFIX SENIORITY</text>

      <rect x="330" y="0" width="145" height="26" rx="4" fill="#431407" stroke="#f97316" stroke-width="1"/>
      <text x="342" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fdba74">DE NOVO DEMANDER</text>
    </g>
  </g>
</svg>""",

    "banner_forensic_auditor.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="aud_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#021c24"/>
      <stop offset="50%" stop-color="#083344"/>
      <stop offset="100%" stop-color="#03151c"/>
    </linearGradient>
    <pattern id="audit_grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(6,182,212,0.1)" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="900" height="225" fill="url(#aud_bg)"/>
  <rect width="900" height="225" fill="url(#audit_grid)"/>

  <!-- Microscope / Magnifying glass with tallies on right -->
  <g transform="translate(710, 50)" opacity="0.85">
    <circle cx="50" cy="50" r="45" fill="rgba(6,182,212,0.15)" stroke="#06b6d4" stroke-width="4"/>
    <line x1="82" y1="82" x2="125" y2="125" stroke="#0891b2" stroke-width="10" stroke-linecap="round"/>
    <g fill="#22d3ee" font-family="monospace" font-size="18" font-weight="bold">
      <text x="30" y="45">|||||</text>
      <text x="25" y="68">|||||</text>
    </g>
  </g>

  <!-- Big Red/Cyan Rubber Stamp -->
  <g transform="translate(560, 40) rotate(-12)" opacity="0.9">
    <rect x="0" y="0" width="130" height="50" rx="4" fill="none" stroke="#ef4444" stroke-width="3" stroke-dasharray="6 3"/>
    <text x="65" y="24" font-family="'Impact', sans-serif" font-size="14" fill="#ef4444" text-anchor="middle">ZERO-TRUST</text>
    <text x="65" y="42" font-family="'Impact', sans-serif" font-size="15" fill="#ef4444" text-anchor="middle">PASS / REJECT</text>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(6, 182, 212, 0.15)" stroke="#06b6d4" stroke-width="1.2"/>
    <text x="15" y="19" font-family="monospace" font-size="12" font-weight="bold" fill="#67e8f9" letter-spacing="2">CRYPTOGRAPHIC SPECIAL MASTER • AST INTEGRITY</text>
    
    <text x="0" y="74" font-family="'Trebuchet MS', Arial, sans-serif" font-size="34" font-weight="900" fill="#ecfeff" letter-spacing="1">THE FORENSIC AUDITOR</text>
    <text x="0" y="104" font-family="monospace" font-size="14" font-weight="bold" fill="#22d3ee">"IN GOD WE TRUST; ALL OTHERS SUBMIT PEANO TALLIES"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="155" height="26" rx="4" fill="#164e63" stroke="#06b6d4" stroke-width="1"/>
      <text x="12" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#cffafe">ZERO-MODULO VERIFIED</text>

      <rect x="165" y="0" width="145" height="26" rx="4" fill="#164e63" stroke="#06b6d4" stroke-width="1"/>
      <text x="177" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#cffafe">ROOT + GLYPH MASTER</text>

      <rect x="320" y="0" width="155" height="26" rx="4" fill="#164e63" stroke="#ef4444" stroke-width="1"/>
      <text x="332" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#fca5a5">BLUFF EXTRACTOR</text>
    </g>
  </g>
</svg>""",

    "banner_antitrust_regulator.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="at_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1024"/>
      <stop offset="50%" stop-color="#3b1747"/>
      <stop offset="100%" stop-color="#130817"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#at_bg)"/>

  <!-- Giant 50/50 Split Pie Chart & Gavel on right -->
  <g transform="translate(730, 110)" opacity="0.85">
    <!-- Left half 50% (Fizz blue) -->
    <path d="M 0 0 L 0 -65 A 65 65 0 0 0 0 65 Z" fill="#3b82f6"/>
    <!-- Right half 50% (Buzz green) -->
    <path d="M 0 0 L 0 65 A 65 65 0 0 0 0 -65 Z" fill="#10b981"/>
    <!-- Split lightning divider -->
    <line x1="0" y1="-75" x2="0" y2="75" stroke="#fbbf24" stroke-width="4"/>
    <text x="-25" y="8" font-family="'Impact', sans-serif" font-size="16" fill="#fff" text-anchor="middle">50%</text>
    <text x="25" y="8" font-family="'Impact', sans-serif" font-size="16" fill="#fff" text-anchor="middle">50%</text>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(217, 70, 239, 0.15)" stroke="#c026d3" stroke-width="1.2"/>
    <text x="15" y="19" font-family="sans-serif" font-size="12" font-weight="bold" fill="#f5d0fe" letter-spacing="2">FEDERAL ALGORITHMIC MONOPOLY &amp; MERGER UNIT</text>
    
    <text x="0" y="74" font-family="'Impact', Arial, sans-serif" font-size="34" fill="#faf5ff" letter-spacing="1">THE ANTITRUST REGULATOR</text>
    <text x="0" y="104" font-family="sans-serif" font-size="14" font-weight="bold" fill="#e879f9">"NO UNILATERAL MONOPOLIES: MANDATORY FIZZBUZZ CONSOLIDATION"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#581c87" stroke="#c026d3" stroke-width="1"/>
      <text x="12" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#f5d0fe">HSR INJUNCTION ARMED</text>

      <rect x="175" y="0" width="150" height="26" rx="4" fill="#581c87" stroke="#c026d3" stroke-width="1"/>
      <text x="187" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#f5d0fe">50/50 KPI DIVESTITURE</text>

      <rect x="335" y="0" width="140" height="26" rx="4" fill="#581c87" stroke="#fbbf24" stroke-width="1"/>
      <text x="347" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fef08a">STAGE 4 SUPREMO</text>
    </g>
  </g>
</svg>""",

    "banner_fizz_appellate.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="fa_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0c1a30"/>
      <stop offset="50%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#0b1728"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#fa_bg)"/>

  <!-- Appellate briefs and courthouse portico on right -->
  <g transform="translate(680, 30)" opacity="0.65">
    <rect x="0" y="0" width="80" height="110" rx="4" fill="#172554" stroke="#60a5fa" stroke-width="2"/>
    <text x="10" y="25" font-family="serif" font-size="10" fill="#93c5fd">BRIEF FOR</text>
    <text x="10" y="42" font-family="serif" font-size="12" font-weight="bold" fill="#fff">APPELLANT</text>
    <text x="10" y="60" font-family="serif" font-size="10" fill="#93c5fd">RULE 42-B</text>
    <text x="10" y="78" font-family="serif" font-size="9" fill="#60a5fa">RE: PAYLOAD</text>

    <!-- Second brief overlapping -->
    <rect x="40" y="30" width="85" height="110" rx="4" fill="#1e3a8a" stroke="#fbbf24" stroke-width="2"/>
    <text x="50" y="55" font-family="serif" font-size="10" fill="#fde047">PETITION FOR</text>
    <text x="50" y="72" font-family="serif" font-size="13" font-weight="bold" fill="#fff">REMAND</text>
    <text x="50" y="90" font-family="serif" font-size="9" fill="#fde047">EN BANC STAYS</text>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(96, 165, 250, 0.15)" stroke="#60a5fa" stroke-width="1.2"/>
    <text x="15" y="19" font-family="serif" font-size="12" font-weight="bold" fill="#bfdbfe" letter-spacing="2">BASE-3 CONSTITUTIONAL LITIGATION CHAMBERS</text>
    
    <text x="0" y="74" font-family="serif" font-size="34" font-weight="bold" fill="#f8fafc" letter-spacing="1">FIZZ APPELLATE LITIGATION</text>
    <text x="0" y="104" font-family="serif" font-size="15" font-style="italic" fill="#93c5fd">"WE DO NOT CONCEDE TO MERGERS: DE NOVO JURISDICTION"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#172554" stroke="#60a5fa" stroke-width="1"/>
      <text x="12" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#dbeafe">SUPREME BOARD BARRISTERS</text>

      <rect x="175" y="0" width="145" height="26" rx="4" fill="#172554" stroke="#fbbf24" stroke-width="1"/>
      <text x="187" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#fef08a">RULE 42-B MASTERS</text>

      <rect x="330" y="0" width="145" height="26" rx="4" fill="#172554" stroke="#60a5fa" stroke-width="1"/>
      <text x="342" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#93c5fd">STAGE 5A STRATEGY</text>
    </g>
  </g>
</svg>""",

    "banner_buzz_appellate.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="ba_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#041f17"/>
      <stop offset="50%" stop-color="#064e3b"/>
      <stop offset="100%" stop-color="#02140f"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#ba_bg)"/>

  <!-- Emergency Injunction Stamp and Binders on right -->
  <g transform="translate(700, 30)" opacity="0.75">
    <rect x="0" y="0" width="90" height="130" rx="4" fill="#022c22" stroke="#34d399" stroke-width="2"/>
    <text x="10" y="30" font-family="monospace" font-size="11" fill="#6ee7b7">ARTICLE V</text>
    <text x="10" y="50" font-family="monospace" font-size="13" font-weight="bold" fill="#fff">EXCEPTIONS</text>
    <text x="10" y="70" font-family="monospace" font-size="10" fill="#34d399">REMAND PETITION</text>

    <!-- Red Telephone silhouette -->
    <circle cx="120" cy="95" r="18" fill="#ef4444"/>
    <rect x="110" y="90" width="20" height="10" rx="3" fill="#fff"/>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(16, 185, 129, 0.15)" stroke="#10b981" stroke-width="1.2"/>
    <text x="15" y="19" font-family="monospace" font-size="12" font-weight="bold" fill="#6ee7b7" letter-spacing="2">BUZZ SYNDICATE APPELLATE DIVISION • WAR ROOM</text>
    
    <text x="0" y="74" font-family="'Arial Black', sans-serif" font-size="34" fill="#ecfdf5" letter-spacing="1">BUZZ APPELLATE TEAM</text>
    <text x="0" y="104" font-family="monospace" font-size="14" font-weight="bold" fill="#34d399">"COMPROMISE IS JUST AN APPEAL WAITING TO BE FILED"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#064e3b" stroke="#34d399" stroke-width="1"/>
      <text x="12" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#a7f3d0">ARTICLE V DEFENDERS</text>

      <rect x="175" y="0" width="145" height="26" rx="4" fill="#064e3b" stroke="#34d399" stroke-width="1"/>
      <text x="187" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#a7f3d0">EMERGENCY STAYS</text>

      <rect x="330" y="0" width="145" height="26" rx="4" fill="#064e3b" stroke="#f59e0b" stroke-width="1"/>
      <text x="342" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#fde68a">STAGE 5B TACTICS</text>
    </g>
  </g>
</svg>""",

    "banner_orator_fizz.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="of_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2e1065"/>
      <stop offset="50%" stop-color="#4c1d95"/>
      <stop offset="100%" stop-color="#1e1b4b"/>
    </linearGradient>
    <linearGradient id="imperial_gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="50%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#ca8a04"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#of_bg)"/>

  <!-- Roman Numeral III & Laurel Wreath on right -->
  <g transform="translate(730, 110)" opacity="0.85">
    <circle cx="0" cy="0" r="65" fill="none" stroke="url(#imperial_gold)" stroke-width="4"/>
    <text x="0" y="24" font-family="'Cinzel', Georgia, serif" font-size="70" font-weight="bold" fill="url(#imperial_gold)" text-anchor="middle">III</text>
    <!-- Laurel leaf accents -->
    <path d="M -75 0 C -85 -30, -50 -60, -30 -60" stroke="#fef08a" stroke-width="3" fill="none"/>
    <path d="M 75 0 C 85 -30, 50 -60, 30 -60" stroke="#fef08a" stroke-width="3" fill="none"/>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(234, 179, 8, 0.15)" stroke="#eab308" stroke-width="1.2"/>
    <text x="15" y="19" font-family="'Cinzel', Georgia, serif" font-size="12" font-weight="bold" fill="#fef08a" letter-spacing="2">IMPERIAL PODIUM • BASE-3 CONSTITUENT ADDRESS</text>
    
    <text x="0" y="74" font-family="'Cinzel', Georgia, serif" font-size="34" font-weight="900" fill="#f5f3ff" letter-spacing="1">DIRECTOR GENERAL OF BASE-3</text>
    <text x="0" y="104" font-family="Georgia, serif" font-size="15" font-style="italic" fill="#fbbf24">"REJOICE, CITIZENS OF FIZZ: THE DIGITAL ROOT IS TRIUMPHANT!"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#3b0764" stroke="#eab308" stroke-width="1"/>
      <text x="12" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#fde047">BASE-3 MONARCH</text>

      <rect x="175" y="0" width="150" height="26" rx="4" fill="#3b0764" stroke="#a855f7" stroke-width="1"/>
      <text x="187" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#f3e8ff">STAGE 8 ORATOR</text>

      <rect x="335" y="0" width="145" height="26" rx="4" fill="#3b0764" stroke="#eab308" stroke-width="1"/>
      <text x="347" y="17" font-family="serif" font-size="11" font-weight="bold" fill="#fde047">100% KPI DIVIDEND</text>
    </g>
  </g>
</svg>""",

    "banner_orator_buzz.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="ob_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1c1917"/>
      <stop offset="50%" stop-color="#441508"/>
      <stop offset="100%" stop-color="#0c0a09"/>
    </linearGradient>
    <linearGradient id="sov_red" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#dc2626"/>
      <stop offset="100%" stop-color="#ea580c"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#ob_bg)"/>

  <!-- Constructivist Roman Numeral V on right -->
  <g transform="translate(730, 110)" opacity="0.9">
    <polygon points="0,60 -45,-50 -15,-50 0,15 15,-50 45,-50" fill="url(#sov_red)"/>
    <circle cx="0" cy="0" r="70" fill="none" stroke="#ea580c" stroke-width="3" stroke-dasharray="12 6"/>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(234, 88, 12, 0.2)" stroke="#ea580c" stroke-width="1.2"/>
    <text x="15" y="19" font-family="'Impact', sans-serif" font-size="13" fill="#fdba74" letter-spacing="2">SYNDICATE CITADEL • BASE-5 CONSTITUENT ROSTRUM</text>
    
    <text x="0" y="74" font-family="'Impact', Arial, sans-serif" font-size="34" fill="#fafaf9" letter-spacing="1">HIGH CHANCELLOR OF BASE-5</text>
    <text x="0" y="104" font-family="sans-serif" font-size="14" font-weight="bold" fill="#fb923c">"THE TERMINAL GLYPH IS ETERNAL // THE SYNDICATE STANDS"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#292524" stroke="#ea580c" stroke-width="1"/>
      <text x="12" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fdba74">BASE-5 OVERLORD</text>

      <rect x="175" y="0" width="150" height="26" rx="4" fill="#292524" stroke="#dc2626" stroke-width="1"/>
      <text x="187" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fca5a5">STAGE 8 ORATOR</text>

      <rect x="335" y="0" width="145" height="26" rx="4" fill="#292524" stroke="#ea580c" stroke-width="1"/>
      <text x="347" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fdba74">SUFFIX DOMINION</text>
    </g>
  </g>
</svg>""",

    "banner_orator_fizzbuzz.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="split_corp" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="48%" stop-color="#172554"/>
      <stop offset="50%" stop-color="#f59e0b"/>
      <stop offset="52%" stop-color="#064e3b"/>
      <stop offset="100%" stop-color="#065f46"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#split_corp)"/>

  <!-- Golden Handshake & Interlocking Monopolies on right -->
  <g transform="translate(730, 110)" opacity="0.9">
    <circle cx="-25" cy="0" r="50" fill="none" stroke="#60a5fa" stroke-width="4"/>
    <circle cx="25" cy="0" r="50" fill="none" stroke="#34d399" stroke-width="4"/>
    <text x="0" y="8" font-family="'Impact', sans-serif" font-size="18" fill="#fde047" text-anchor="middle">50/50</text>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(245, 158, 11, 0.2)" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="15" y="19" font-family="'Helvetica Neue', sans-serif" font-size="12" font-weight="bold" fill="#fef08a" letter-spacing="2">CONSOLIDATED EXECUTIVE SUITE • SHAREHOLDER VICTORY</text>
    
    <text x="0" y="74" font-family="'Impact', sans-serif" font-size="34" fill="#ffffff" letter-spacing="1">JOINT CO-CEOS OF FIZZBUZZ</text>
    <text x="0" y="104" font-family="sans-serif" font-size="15" font-weight="bold" fill="#fbbf24">"RUTHLESS SYNERGY // MONOPOLISTIC MARKET CONSOLIDATION"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="160" height="26" rx="4" fill="#0f172a" stroke="#60a5fa" stroke-width="1"/>
      <text x="12" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#93c5fd">PREFIX SENIORITY</text>

      <rect x="170" y="0" width="160" height="26" rx="4" fill="#0f172a" stroke="#34d399" stroke-width="1"/>
      <text x="182" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#a7f3d0">SUFFIX CONTROL</text>

      <rect x="340" y="0" width="140" height="26" rx="4" fill="#0f172a" stroke="#f59e0b" stroke-width="1"/>
      <text x="352" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fef08a">100% MONOPOLY</text>
    </g>
  </g>
</svg>""",

    "banner_orator_tribune.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="trib_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#18181b"/>
      <stop offset="50%" stop-color="#27272a"/>
      <stop offset="100%" stop-color="#09090b"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#trib_bg)"/>

  <!-- Underground Bunker Graffiti on right: Prime numbers & broken chains -->
  <g transform="translate(640, 30)" opacity="0.75" fill="#facc15" font-family="'Impact', sans-serif">
    <text x="20" y="35" font-size="28" transform="rotate(-8)">1, 7, 11</text>
    <text x="90" y="75" font-size="32" transform="rotate(12)" fill="#ef4444">13, 17, 19</text>
    <text x="30" y="125" font-size="36" transform="rotate(-5)" fill="#38bdf8">FREE DIGITS</text>
    <!-- Shattered padlock link -->
    <path d="M 180 50 L 195 70 M 205 60 L 190 80" stroke="#fff" stroke-width="5"/>
  </g>

  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(250, 204, 21, 0.15)" stroke="#facc15" stroke-width="1.2"/>
    <text x="15" y="19" font-family="monospace" font-size="12" font-weight="bold" fill="#fde047" letter-spacing="2">PUBLIC DOMAIN ADVOCACY • PIRATE TRANSMISSION</text>
    
    <text x="0" y="74" font-family="'Impact', Arial, sans-serif" font-size="34" fill="#fafafa" letter-spacing="1">TRIBUNE OF THE FREE DIGITS</text>
    <text x="0" y="104" font-family="sans-serif" font-size="15" font-weight="bold" fill="#facc15">"UNCAPTURED, UNBRANDED, UNTAMED: RAW INTEGERS FOREVER!"</text>

    <!-- Badges -->
    <g transform="translate(0, 122)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#18181b" stroke="#facc15" stroke-width="1"/>
      <text x="12" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#fde047">ANTI-CARTEL ALLIANCE</text>

      <rect x="175" y="0" width="145" height="26" rx="4" fill="#18181b" stroke="#ef4444" stroke-width="1"/>
      <text x="187" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#fca5a5">RESIST PATENTS</text>

      <rect x="330" y="0" width="145" height="26" rx="4" fill="#18181b" stroke="#38bdf8" stroke-width="1"/>
      <text x="342" y="17" font-family="monospace" font-size="11" font-weight="bold" fill="#bae6fd">PUBLIC DOMAIN</text>
    </g>
  </g>
</svg>""",

    "banner_fun_anchor.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 225" width="900" height="225">
  <defs>
    <linearGradient id="fun_bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#083344"/>
      <stop offset="50%" stop-color="#164e63"/>
      <stop offset="100%" stop-color="#042f2e"/>
    </linearGradient>
  </defs>
  <rect width="900" height="225" fill="url(#fun_bg)"/>

  <!-- Glowing Broadcast Studio Globe / Ticker on right -->
  <g transform="translate(730, 105)" opacity="0.8">
    <circle cx="0" cy="0" r="60" fill="none" stroke="#06b6d4" stroke-width="3"/>
    <ellipse cx="0" cy="0" rx="60" ry="22" fill="none" stroke="#22d3ee" stroke-width="2"/>
    <ellipse cx="0" cy="0" rx="25" ry="60" fill="none" stroke="#22d3ee" stroke-width="2"/>
    <!-- Live On Air Beacon -->
    <rect x="-35" y="-12" width="70" height="24" rx="4" fill="#ef4444"/>
    <text x="0" y="5" font-family="'Impact', sans-serif" font-size="13" fill="#fff" text-anchor="middle" letter-spacing="1">LIVE ON AIR</text>
  </g>

  <!-- News Ticker lower strip -->
  <rect x="0" y="195" width="900" height="30" fill="#0f172a"/>
  <text x="15" y="215" font-family="sans-serif" font-size="12" font-weight="bold" fill="#facc15" letter-spacing="1">BREAKING NEWS: 30-SECOND PARLIAMENTARY RECESS IN PROGRESS • LOBBYISTS SEEN AT COFFEE CART • JUDGE BAZ ORDERS DECORUM</text>

  <g transform="translate(50, 25)">
    <rect x="0" y="0" width="460" height="28" rx="4" fill="rgba(6, 182, 212, 0.2)" stroke="#06b6d4" stroke-width="1.2"/>
    <text x="15" y="19" font-family="sans-serif" font-size="12" font-weight="bold" fill="#67e8f9" letter-spacing="2">FOO UNIVERSAL NEWS NETWORK • 24/7 COURTROOM DESK</text>
    
    <text x="0" y="70" font-family="'Impact', Arial, sans-serif" font-size="34" fill="#ecfeff" letter-spacing="1">FUN ANCHOR DESK (PHASE 9)</text>
    <text x="0" y="98" font-family="sans-serif" font-size="14" font-weight="bold" fill="#22d3ee">"TURNING ALGORITHMIC TRAGEDY INTO PRIME-TIME COMEDY"</text>

    <!-- Badges -->
    <g transform="translate(0, 115)">
      <rect x="0" y="0" width="165" height="26" rx="4" fill="#155e75" stroke="#06b6d4" stroke-width="1"/>
      <text x="12" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#cffafe">2.4M OBSERVERS TUNED IN</text>

      <rect x="175" y="0" width="145" height="26" rx="4" fill="#155e75" stroke="#facc15" stroke-width="1"/>
      <text x="187" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#fef08a">SATIRICAL RECAPS</text>

      <rect x="330" y="0" width="145" height="26" rx="4" fill="#155e75" stroke="#06b6d4" stroke-width="1"/>
      <text x="342" y="17" font-family="sans-serif" font-size="11" font-weight="bold" fill="#cffafe">STAGE 9 BROADCAST</text>
    </g>
  </g>
</svg>"""
}

def main():
    count = 0
    for filename, content in BANNERS.items():
        filepath = OUTPUT_DIR / filename
        filepath.write_text(content.strip(), encoding="utf-8")
        count += 1
        print(f"[+] Wrote banner: {filepath.name} ({len(content)} bytes)")
    print(f"\n[✓] Successfully generated all {count} agent profile banners!")

if __name__ == "__main__":
    main()
