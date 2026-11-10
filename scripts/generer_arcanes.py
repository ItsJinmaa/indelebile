"""Génère les 10 cartes de tarot du projet (SVG originaux, noir et or).

7 arcanes pour les agents, 3 arcanes « sombres » pour les menaces.
Usage : uv run python scripts/generer_arcanes.py
"""

from pathlib import Path

SORTIE = Path(__file__).resolve().parent.parent / "docs" / "arcanes"

NOIR, OR, OR_PALE, SANG = "#0e0b10", "#c9a54a", "#8a7238", "#8e1b24"
L, H = 300, 520
CX, CY = 150, 250  # centre du symbole

# Chaque symbole est dessiné en traits dorés autour de (CX, CY).
TRAIT = f'fill="none" stroke="{OR}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"'
FIN = f'fill="none" stroke="{OR_PALE}" stroke-width="1.5" stroke-linecap="round"'

SYMBOLES = {
    # I · Le Bateleur : la table et ses quatre outils (liste fermée), l'infini au-dessus.
    "bateleur": f"""
      <path {TRAIT} d="M95 285 H205 M105 285 V345 M195 285 V345"/>
      <path {TRAIT} d="M112 262 h20 l-4 22 h-12 z"/>
      <circle {TRAIT} cx="155" cy="275" r="9"/>
      <path {TRAIT} d="M178 284 L196 238 M190 246 l12 5"/>
      <path {TRAIT} d="M150 168 c-14 -16 -34 -16 -34 0 s20 16 34 0 s34 -16 34 0 s-20 16 -34 0"/>""",
    # II · La Papesse : le registre fermé, scellé d'un fermoir.
    "papesse": f"""
      <path {TRAIT} d="M100 190 h85 a15 15 0 0 1 15 15 v110 a15 15 0 0 1 -15 15 h-85 z"/>
      <path {TRAIT} d="M100 190 v140 M112 190 v140"/>
      <path {TRAIT} d="M200 245 h-22 v30 h22"/>
      <circle {TRAIT} cx="178" cy="260" r="5"/>
      <path {TRAIT} d="M150 220 v40 M134 236 h32"/>
      <path {FIN} d="M128 300 h50 M128 312 h40"/>""",
    # IV · L'Empereur : le sceau de cire et la couronne.
    "empereur": f"""
      <path {TRAIT} d="{' '.join(
          ('M' if i == 0 else 'L') + f'{150 + (62 if i % 2 == 0 else 54) * __import__("math").cos(i * 3.14159 / 12):.1f} '
          f'{255 + (62 if i % 2 == 0 else 54) * __import__("math").sin(i * 3.14159 / 12):.1f}'
          for i in range(24)) + ' Z'}"/>
      <circle {TRAIT} cx="150" cy="255" r="40"/>
      <path {TRAIT} d="M125 272 h50 l6 -32 l-17 14 l-14 -22 l-14 22 l-17 -14 z"/>
      <circle {FIN} cx="150" cy="226" r="3"/>""",
    # VII · Le Chariot : la roue qui coordonne, l'étoile qui guide.
    "chariot": f"""
      <circle {TRAIT} cx="150" cy="275" r="50"/>
      <circle {TRAIT} cx="150" cy="275" r="9"/>
      <path {FIN} d="M150 225 V325 M100 275 H200 M115 240 L185 310 M185 240 L115 310"/>
      <path {TRAIT} d="M150 165 l7 18 l18 7 l-18 7 l-7 18 l-7 -18 l-18 -7 l18 -7 z"/>""",
    # IX · L'Ermite : la lanterne qui n'éclaire que ce qui est prouvé.
    "ermite": f"""
      <path {TRAIT} d="M150 168 v22 M138 190 h24 l10 18 h-44 z"/>
      <path {TRAIT} d="M128 208 h44 v76 h-44 z M122 284 h56 l-8 14 h-40 z"/>
      <path {TRAIT} d="M150 228 l7 12 h-14 z M150 264 l7 -12 h-14 z"/>
      <path {FIN} d="M108 230 l-22 -8 M108 250 h-26 M108 270 l-22 8 M192 230 l22 -8 M192 250 h26 M192 270 l22 8"/>
      <path {FIN} d="M120 330 h60"/>""",
    # XI · La Justice : la balance qui pèse les preuves, l'épée qui tranche.
    "justice": f"""
      <path {TRAIT} d="M150 175 V340 M140 340 h20 M138 195 h24"/>
      <path {TRAIT} d="M95 215 H205"/>
      <path {FIN} d="M95 215 L78 268 M95 215 L112 268 M205 215 L188 268 M205 215 L222 268"/>
      <path {TRAIT} d="M74 268 h42 a21 12 0 0 1 -42 0 z M184 268 h42 a21 12 0 0 1 -42 0 z"/>
      <path {TRAIT} d="M150 165 l-6 10 h12 z"/>""",
    # XX · Le Jugement : la trompette des témoins, les rayons de la publication.
    "jugement": f"""
      <path {TRAIT} d="M98 262 L182 218"/>
      <path {TRAIT} d="M182 218 L198 192 L210 222 Z"/>
      <path {TRAIT} d="M92 258 l4 10"/>
      <path {TRAIT} d="M128 246 L160 229 L160 265 L128 282 Z"/>
      <path {FIN} d="M144 240 v34 M130 263 l28 -15"/>
      <path {FIN} d="M212 196 l16 -10 M216 210 l20 -2 M202 186 l6 -18"/>
      <path {FIN} d="M108 330 h20 M140 330 h20 M172 330 h20"/>
      <path {TRAIT} d="M118 330 v-16 M150 330 v-20 M182 330 v-16"/>""",
    # XV · Le Diable : les chaînes de l'injection de prompt.
    "diable": f"""
      <path {TRAIT} d="M112 220 c-20 -20 -18 -50 -4 -62 c0 22 12 34 26 40 M188 220 c20 -20 18 -50 4 -62 c0 22 -12 34 -26 40"/>
      <path {TRAIT} d="M118 210 h64 l-8 50 l-24 18 l-24 -18 z"/>
      <circle {TRAIT} cx="136" cy="232" r="4"/><circle {TRAIT} cx="164" cy="232" r="4"/>
      <ellipse {TRAIT} cx="128" cy="300" rx="9" ry="14"/><ellipse {TRAIT} cx="150" cy="318" rx="14" ry="9"/>
      <ellipse {TRAIT} cx="172" cy="300" rx="9" ry="14"/>""",
    # XVI · La Tour : l'éclair qui fend l'histoire réécrite.
    "tour": f"""
      <path {TRAIT} d="M122 340 V215 h56 V340 M116 340 h68"/>
      <path {TRAIT} d="M118 215 v-14 h10 v8 h10 v-8 h10 v8 h10 v-8 h10 v8 h10 v-8 h10 v14"/>
      <path {TRAIT} d="M140 340 v-26 a10 10 0 0 1 20 0 v26 M136 250 h10 v16 h-10 z M156 280 h10 v16 h-10 z"/>
      <path d="M215 160 L172 214 h20 l-22 40 l42 -54 h-20 l18 -40 z" fill="{SANG}" stroke="{OR}" stroke-width="2"/>
      <path {FIN} d="M100 232 l-14 10 M98 262 l-16 4 M204 262 l16 6"/>""",
    # XVIII · La Lune : la lumière trompeuse, l'hallucination.
    "lune": f"""
      <path {TRAIT} d="M170 180 a55 55 0 1 0 0 110 a44 44 0 1 1 0 -110 z"/>
      <path {FIN} d="M112 300 v6 M132 310 v6 M152 302 v6 M172 312 v6 M192 304 v6"/>
      <path {TRAIT} d="M92 345 V300 h18 V345 M190 345 V300 h18 V345 M84 345 h132"/>""",
}

CARTES = [
    # (fichier, numéro, nom de l'arcane, rôle dans Indélébile, symbole, sombre ?)
    ("01-bateleur", "I", "LE BATELEUR", "Le Pochoir · Réceptionniste", "bateleur", False),
    ("02-papesse", "II", "LA PAPESSE", "Le Tatoueur · Greffier", "papesse", False),
    ("04-empereur", "IV", "L'EMPEREUR", "Le Sceau · Signataire", "empereur", False),
    ("07-chariot", "VII", "LE CHARIOT", "Orchestrateur", "chariot", False),
    ("09-ermite", "IX", "L'ERMITE", "L'Oracle · Enquêteur", "ermite", False),
    ("11-justice", "XI", "LA JUSTICE", "L'Inquisiteur · Vérificateur", "justice", False),
    ("20-jugement", "XX", "LE JUGEMENT", "Les Veilleurs · Témoins", "jugement", False),
    ("15-diable", "XV", "LE DIABLE", "Menace · injection de prompt", "diable", True),
    ("16-tour", "XVI", "LA TOUR", "Menace · réécriture d'historique", "tour", True),
    ("18-lune", "XVIII", "LA LUNE", "Menace · preuve hallucinée", "lune", True),
]


def carte_svg(numero: str, nom: str, role: str, symbole: str, sombre: bool) -> str:
    accent = SANG if sombre else OR
    coins = "".join(
        f'<path {FIN} transform="translate({x} {y}) scale({sx} {sy})" '
        f'd="M0 18 V0 H18 M6 26 c0 -12 8 -20 20 -20"/>'
        for x, y, sx, sy in [(22, 22, 1, 1), (278, 22, -1, 1), (22, 498, 1, -1), (278, 498, -1, -1)]
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {L} {H}" width="{L}" height="{H}" role="img" aria-label="{nom} : {role}">
  <rect width="{L}" height="{H}" rx="18" fill="{NOIR}"/>
  <rect x="10" y="10" width="{L - 20}" height="{H - 20}" rx="12" fill="none" stroke="{OR}" stroke-width="2"/>
  <rect x="18" y="18" width="{L - 36}" height="{H - 36}" rx="8" fill="none" stroke="{OR_PALE}" stroke-width="1"/>
  {coins}
  <text x="150" y="70" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="30" fill="{OR}" letter-spacing="4">{numero}</text>
  <path stroke="{accent}" stroke-width="1.5" d="M95 86 H205"/>
  <circle cx="150" cy="86" r="3" fill="{accent}"/>
  <circle cx="150" cy="255" r="105" fill="none" stroke="{OR_PALE}" stroke-width="1" stroke-dasharray="2 6"/>
  {SYMBOLES[symbole]}
  <path stroke="{accent}" stroke-width="1.5" d="M95 404 H205"/>
  <text x="150" y="440" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="22" fill="{OR}" letter-spacing="3">{nom}</text>
  <text x="150" y="470" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="12.5" font-style="italic" fill="{OR_PALE}">{role}</text>
</svg>
"""


def main() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    for fichier, numero, nom, role, symbole, sombre in CARTES:
        nom_xml = nom.replace("'", "&#8217;")
        role_xml = role.replace("'", "&#8217;")
        (SORTIE / f"{fichier}.svg").write_text(carte_svg(numero, nom_xml, role_xml, symbole, sombre), encoding="utf-8")
    print(f"{len(CARTES)} cartes écrites dans {SORTIE}")


if __name__ == "__main__":
    main()
