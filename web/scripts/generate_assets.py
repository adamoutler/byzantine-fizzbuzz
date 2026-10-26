"""
Asset generation script for FizzBuzz: Inquisition Edition PWA & Social Media.
Generates SVG and PNG assets for icons, favicons, maskables, and Open Graph banner.
"""

import os
import subprocess

ICONS_DIR = "/home/adamoutler/MeatloafBot/active-projects/byzantine-fizzbuzz/web/app/static/icons"
os.makedirs(ICONS_DIR, exist_ok=True)

# 1. Base App Icon SVG (512x512)
ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b0f19"/>
      <stop offset="50%" stop-color="#111827"/>
      <stop offset="100%" stop-color="#1e1b4b"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="50%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#ca8a04"/>
    </linearGradient>
    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
    <linearGradient id="amberGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#c084fc"/>
      <stop offset="100%" stop-color="#7e22ce"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background Shape -->
  <rect width="512" height="512" rx="108" fill="url(#bgGrad)"/>
  
  <!-- Outer Tech Border -->
  <rect x="20" y="20" width="472" height="472" rx="92" fill="none" stroke="#10b981" stroke-width="4" stroke-opacity="0.4" stroke-dasharray="16 8"/>
  <circle cx="256" cy="256" r="215" fill="none" stroke="url(#goldGrad)" stroke-width="3" stroke-opacity="0.3"/>

  <!-- Byzantine Crest Center / Scales of Justice -->
  <g transform="translate(256, 240)">
    <!-- Central Pillar -->
    <path d="M-8,140 L8,140 L12,150 L-12,150 Z" fill="url(#goldGrad)"/>
    <rect x="-24" y="150" width="48" height="12" rx="4" fill="url(#goldGrad)"/>
    <rect x="-6" y="-70" width="12" height="210" fill="url(#goldGrad)"/>
    <circle cx="0" cy="-70" r="16" fill="url(#goldGrad)"/>
    <circle cx="0" cy="-70" r="8" fill="#0b0f19"/>

    <!-- Scales Beam -->
    <path d="M-150,-62 L150,-62 L140,-52 L-140,-52 Z" fill="url(#goldGrad)"/>
    <circle cx="-140" cy="-57" r="7" fill="url(#goldGrad)"/>
    <circle cx="140" cy="-57" r="7" fill="url(#goldGrad)"/>

    <!-- Left Pan (Fizz III - Cyan) -->
    <line x1="-140" y1="-52" x2="-180" y2="40" stroke="#38bdf8" stroke-width="2.5" stroke-opacity="0.8"/>
    <line x1="-140" y1="-52" x2="-100" y2="40" stroke="#38bdf8" stroke-width="2.5" stroke-opacity="0.8"/>
    <path d="M-190,40 Q-140,75 -90,40 Z" fill="url(#cyanGrad)" filter="url(#glow)"/>
    <text x="-140" y="30" font-family="'Courier New', monospace" font-size="28" font-weight="900" fill="#38bdf8" text-anchor="middle">III</text>

    <!-- Right Pan (Buzz V - Amber) -->
    <line x1="140" y1="-52" x2="100" y2="40" stroke="#fbbf24" stroke-width="2.5" stroke-opacity="0.8"/>
    <line x1="140" y1="-52" x2="180" y2="40" stroke="#fbbf24" stroke-width="2.5" stroke-opacity="0.8"/>
    <path d="M90,40 Q140,75 190,40 Z" fill="url(#amberGrad)" filter="url(#glow)"/>
    <text x="140" y="30" font-family="'Courier New', monospace" font-size="28" font-weight="900" fill="#fbbf24" text-anchor="middle">V</text>

    <!-- Judge Baz Gavel in Center -->
    <g transform="translate(0, 10) rotate(-25)">
      <rect x="-6" y="-30" width="12" height="75" rx="3" fill="#94a3b8"/>
      <rect x="-24" y="-50" width="48" height="24" rx="5" fill="url(#purpleGrad)" stroke="#f8fafc" stroke-width="2"/>
    </g>
  </g>

  <!-- Zero Modulo Banner at Bottom -->
  <g transform="translate(256, 440)">
    <rect x="-160" y="-22" width="320" height="44" rx="22" fill="#0f172a" stroke="#10b981" stroke-width="2.5"/>
    <text x="0" y="7" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="900" fill="#10b981" text-anchor="middle" letter-spacing="3">ZERO MODULO (%)</text>
  </g>
</svg>
"""

# 2. Maskable Icon SVG (512x512 with 20% safe-zone margin)
MASKABLE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="mBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b0f19"/>
      <stop offset="50%" stop-color="#111827"/>
      <stop offset="100%" stop-color="#1e1b4b"/>
    </linearGradient>
    <linearGradient id="mGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="50%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#ca8a04"/>
    </linearGradient>
    <linearGradient id="mCyan" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
    <linearGradient id="mAmber" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
  </defs>

  <!-- Full Bleed Background for Maskable Icon -->
  <rect width="512" height="512" fill="url(#mBg)"/>

  <!-- Safe Zone Scale Down (0.75x) centered -->
  <g transform="translate(256, 256) scale(0.75) translate(-256, -256)">
    <!-- Tech Ring -->
    <circle cx="256" cy="256" r="215" fill="none" stroke="#10b981" stroke-width="4" stroke-opacity="0.6" stroke-dasharray="14 7"/>

    <!-- Scales of Justice -->
    <g transform="translate(256, 235)">
      <rect x="-6" y="-70" width="12" height="210" fill="url(#mGold)"/>
      <circle cx="0" cy="-70" r="16" fill="url(#mGold)"/>
      <rect x="-24" y="145" width="48" height="15" rx="4" fill="url(#mGold)"/>

      <path d="M-140,-62 L140,-62 L130,-52 L-130,-52 Z" fill="url(#mGold)"/>

      <!-- Left Pan -->
      <line x1="-130" y1="-52" x2="-165" y2="40" stroke="#38bdf8" stroke-width="2.5"/>
      <line x1="-130" y1="-52" x2="-95" y2="40" stroke="#38bdf8" stroke-width="2.5"/>
      <path d="M-175,40 Q-130,70 -85,40 Z" fill="url(#mCyan)"/>
      <text x="-130" y="30" font-family="'Courier New', monospace" font-size="26" font-weight="900" fill="#38bdf8" text-anchor="middle">III</text>

      <!-- Right Pan -->
      <line x1="130" y1="-52" x2="95" y2="40" stroke="#fbbf24" stroke-width="2.5"/>
      <line x1="130" y1="-52" x2="165" y2="40" stroke="#fbbf24" stroke-width="2.5"/>
      <path d="M85,40 Q130,70 175,40 Z" fill="url(#mAmber)"/>
      <text x="130" y="30" font-family="'Courier New', monospace" font-size="26" font-weight="900" fill="#fbbf24" text-anchor="middle">V</text>
    </g>

    <!-- Banner -->
    <g transform="translate(256, 435)">
      <rect x="-150" y="-22" width="300" height="44" rx="22" fill="#0f172a" stroke="#10b981" stroke-width="3"/>
      <text x="0" y="7" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="900" fill="#10b981" text-anchor="middle" letter-spacing="3">ZERO MODULO (%)</text>
    </g>
  </g>
</svg>
"""

# 3. Favicon SVG (Clean, sharp at 16x16 / 32x32)
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect width="64" height="64" rx="14" fill="#0b0f19"/>
  <rect x="2" y="2" width="60" height="60" rx="12" fill="none" stroke="#10b981" stroke-width="2" stroke-opacity="0.8"/>
  <g transform="translate(32, 30)">
    <!-- Pillar -->
    <rect x="-2" y="-12" width="4" height="30" fill="#facc15"/>
    <rect x="-8" y="18" width="16" height="4" rx="2" fill="#facc15"/>
    <circle cx="0" cy="-12" r="3.5" fill="#facc15"/>
    <!-- Beam -->
    <path d="M-20,-11 L20,-11 L18,-9 L-18,-9 Z" fill="#facc15"/>
    <!-- Left Pan -->
    <line x1="-18" y1="-9" x2="-23" y2="4" stroke="#38bdf8" stroke-width="1.2"/>
    <line x1="-18" y1="-9" x2="-13" y2="4" stroke="#38bdf8" stroke-width="1.2"/>
    <path d="M-25,4 Q-18,10 -11,4 Z" fill="#0284c7"/>
    <!-- Right Pan -->
    <line x1="18" y1="-9" x2="13" y2="4" stroke="#fbbf24" stroke-width="1.2"/>
    <line x1="18" y1="-9" x2="23" y2="4" stroke="#fbbf24" stroke-width="1.2"/>
    <path d="M11,4 Q18,10 25,4 Z" fill="#d97706"/>
  </g>
</svg>
"""

# 4. Open Graph Social Media Banner SVG (1200x630)
OG_IMAGE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="ogBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070a10"/>
      <stop offset="40%" stop-color="#0b0f19"/>
      <stop offset="100%" stop-color="#17122b"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fde047"/>
      <stop offset="50%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#ca8a04"/>
    </linearGradient>
    <linearGradient id="emerald" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="liveRed" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#dc2626"/>
      <stop offset="100%" stop-color="#991b1b"/>
    </linearGradient>
    <filter id="redGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="1" stroke-opacity="0.35"/>
    </pattern>
  </defs>

  <!-- Deep Canvas -->
  <rect width="1200" height="630" fill="url(#ogBg)"/>
  <rect width="1200" height="630" fill="url(#grid)"/>

  <!-- Ambient Glow Orbs -->
  <circle cx="260" cy="315" r="280" fill="#06b6d4" opacity="0.08" filter="blur(70px)"/>
  <circle cx="950" cy="180" r="240" fill="#ef4444" opacity="0.09" filter="blur(70px)"/>
  <circle cx="650" cy="500" r="220" fill="#10b981" opacity="0.08" filter="blur(70px)"/>

  <!-- Left Side: Large Tribunal Emblem (Emblem at x=230, y=315) -->
  <g transform="translate(230, 315)">
    <!-- Base Shield -->
    <rect x="-160" y="-180" width="320" height="360" rx="40" fill="#0d1322" stroke="#10b981" stroke-width="3" stroke-opacity="0.6"/>
    <circle cx="0" cy="0" r="140" fill="none" stroke="url(#gold)" stroke-width="2.5" stroke-opacity="0.4"/>

    <!-- Scales of Justice -->
    <rect x="-5" y="-70" width="10" height="170" fill="url(#gold)"/>
    <circle cx="0" cy="-70" r="14" fill="url(#gold)"/>
    <rect x="-24" y="100" width="48" height="12" rx="3" fill="url(#gold)"/>
    <path d="M-110,-62 L110,-62 L100,-54 L-100,-54 Z" fill="url(#gold)"/>

    <!-- Left Pan (Fizz III) -->
    <line x1="-100" y1="-54" x2="-130" y2="25" stroke="#38bdf8" stroke-width="2"/>
    <line x1="-100" y1="-54" x2="-70" y2="25" stroke="#38bdf8" stroke-width="2"/>
    <path d="M-140,25 Q-100,55 -60,25 Z" fill="#0284c7"/>
    <text x="-100" y="16" font-family="'Courier New', monospace" font-size="22" font-weight="900" fill="#38bdf8" text-anchor="middle">III</text>

    <!-- Right Pan (Buzz V) -->
    <line x1="100" y1="-54" x2="70" y2="25" stroke="#fbbf24" stroke-width="2"/>
    <line x1="100" y1="-54" x2="130" y2="25" stroke="#fbbf24" stroke-width="2"/>
    <path d="M60,25 Q100,55 140,25 Z" fill="#d97706"/>
    <text x="100" y="16" font-family="'Courier New', monospace" font-size="22" font-weight="900" fill="#fbbf24" text-anchor="middle">V</text>

    <!-- Zero Modulo Badge -->
    <rect x="-120" y="130" width="240" height="34" rx="17" fill="#052e16" stroke="#10b981" stroke-width="2"/>
    <text x="0" y="152" font-family="system-ui, sans-serif" font-size="14" font-weight="900" fill="#34d399" text-anchor="middle" letter-spacing="2">ZERO MODULO (%)</text>
  </g>

  <!-- Right Side: Typography & Badges -->
  <g transform="translate(465, 110)">
    <!-- Top Super-Header Badge -->
    <rect x="0" y="0" width="355" height="38" rx="19" fill="#1e1b4b" stroke="#818cf8" stroke-width="1.5"/>
    <text x="177" y="24" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="800" fill="#c7d2fe" text-anchor="middle" letter-spacing="2">BYZANTINE ZERO-TRUST TRIBUNAL</text>

    <!-- High-Impact LIVE Indicator Pill -->
    <g transform="translate(375, -2)">
      <rect x="0" y="0" width="150" height="42" rx="21" fill="url(#liveRed)" stroke="#fca5a5" stroke-width="2" filter="url(#redGlow)"/>
      <rect x="0" y="0" width="150" height="42" rx="21" fill="url(#liveRed)" stroke="#f87171" stroke-width="2"/>
      <circle cx="32" cy="21" r="11" fill="#fca5a5" opacity="0.35"/>
      <circle cx="32" cy="21" r="6.5" fill="#ffffff"/>
      <text x="88" y="28" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="2.5">LIVE</text>
    </g>

    <!-- Main Title -->
    <text x="0" y="92" font-family="system-ui, -apple-system, sans-serif" font-size="50" font-weight="900" fill="#ffffff" letter-spacing="-1">
      FizzBuzz: <tspan fill="#10b981">The Inquisition</tspan>
    </text>
    <text x="0" y="140" font-family="system-ui, -apple-system, sans-serif" font-size="25" font-weight="800" fill="#94a3b8" letter-spacing="0.8">
      17 Agent Swarm - No Modulo - No Division
    </text>

    <!-- Punchy Callout Box -->
    <g transform="translate(0, 178)">
      <rect x="0" y="0" width="655" height="86" rx="16" fill="#0f172a" stroke="#334155" stroke-width="1.5"/>
      <circle cx="28" cy="29" r="5" fill="#10b981"/>
      <text x="44" y="35" font-family="system-ui, sans-serif" font-size="18" font-weight="800" fill="#f8fafc">
        Adversarial AI Caucuses • Forensic Audits • Live Public Queue
      </text>
      <text x="44" y="63" font-family="system-ui, sans-serif" font-size="15" font-weight="600" fill="#94a3b8">
        Submit any integer to the docket and watch Judge Baz rule in real time.
      </text>
    </g>

    <!-- 3 Faction Pills with Native Vector Icons -->
    <g transform="translate(0, 290)">
      <!-- Fizz Pill -->
      <rect x="0" y="0" width="205" height="44" rx="10" fill="#082f49" stroke="#0284c7" stroke-width="1.5"/>
      <polygon points="24,14 32,22 24,30 16,22" fill="#38bdf8"/>
      <text x="42" y="27" font-family="system-ui, sans-serif" font-size="15" font-weight="800" fill="#38bdf8">Fizz Consortium</text>

      <!-- Buzz Pill -->
      <rect x="222" y="0" width="205" height="44" rx="10" fill="#451a03" stroke="#d97706" stroke-width="1.5"/>
      <polygon points="246,14 254,22 246,30 238,22" fill="#fbbf24"/>
      <text x="264" y="27" font-family="system-ui, sans-serif" font-size="15" font-weight="800" fill="#fbbf24">Buzz Syndicate</text>

      <!-- Judge Pill -->
      <rect x="444" y="0" width="211" height="44" rx="10" fill="#3b0764" stroke="#9333ea" stroke-width="1.5"/>
      <polygon points="468,14 476,22 468,30 460,22" fill="#c084fc"/>
      <text x="486" y="27" font-family="system-ui, sans-serif" font-size="15" font-weight="800" fill="#c084fc">Magistrate Baz</text>
    </g>

    <!-- Bottom URL Link Badge -->
    <g transform="translate(0, 365)">
      <text x="0" y="35" font-family="'Courier New', monospace" font-size="22" font-weight="800" fill="#10b981">
        fizzbuzz.adamoutler.com
      </text>
    </g>
  </g>
</svg>
"""

# Write SVGs
with open(os.path.join(ICONS_DIR, "icon-512.svg"), "w") as f:
    f.write(ICON_SVG)

with open(os.path.join(ICONS_DIR, "icon-maskable-512.svg"), "w") as f:
    f.write(MASKABLE_SVG)

with open(os.path.join(ICONS_DIR, "favicon.svg"), "w") as f:
    f.write(FAVICON_SVG)

with open(os.path.join(ICONS_DIR, "og-image.svg"), "w") as f:
    f.write(OG_IMAGE_SVG)

print("Generated SVGs successfully.")

# Convert to PNGs using ImageMagick
commands = [
    # Main Icons
    ["convert", "-background", "none", os.path.join(ICONS_DIR, "icon-512.svg"), "-resize", "512x512", os.path.join(ICONS_DIR, "icon-512.png")],
    ["convert", "-background", "none", os.path.join(ICONS_DIR, "icon-512.svg"), "-resize", "192x192", os.path.join(ICONS_DIR, "icon-192.png")],
    ["convert", "-background", "none", os.path.join(ICONS_DIR, "icon-512.svg"), "-resize", "180x180", os.path.join(ICONS_DIR, "apple-touch-icon.png")],
    
    # Maskable Icons
    ["convert", "-background", "none", os.path.join(ICONS_DIR, "icon-maskable-512.svg"), "-resize", "512x512", os.path.join(ICONS_DIR, "icon-maskable-512.png")],
    ["convert", "-background", "none", os.path.join(ICONS_DIR, "icon-maskable-512.svg"), "-resize", "192x192", os.path.join(ICONS_DIR, "icon-maskable-192.png")],
    
    # Favicon ICO (Multi-resolution 16, 32, 48)
    ["convert", "-background", "none", os.path.join(ICONS_DIR, "favicon.svg"), "-define", "icon:auto-resize=48,32,16", os.path.join(ICONS_DIR, "favicon.ico")],
    
    # Open Graph Banner (1200x630)
    ["convert", "-background", "none", os.path.join(ICONS_DIR, "og-image.svg"), "-resize", "1200x630", os.path.join(ICONS_DIR, "og-image.png")],
]

for cmd in commands:
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)

print("All icon and social media assets successfully compiled!")
