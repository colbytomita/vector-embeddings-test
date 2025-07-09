import os
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Sample document contents
docs = {
    "document1_taxonomy.pdf": """Title: A Revision of North American Unionid Mussels (Bivalvia: Unionidae)

1. Tribes & Subtribes:
   - Unionini Rafinesque, 1820
     • Genus: Quadrula Rafinesque, 1819
     • Subgenus: Quadrula (Ictinodonta) Simpson, 1900
2. Morphological diagnostics:
   - Beak sculpture: concentric lamellae alternating sharp/ragged (λ≈0.2–0.5 mm)
   - Pseudocardinal teeth: bifid or trifid, inner lamella sclerotic
3. Observations:
   - Q. pustulosa: specimens from Ohio River basin often exhibit aberrant “denticulations” on the anterior pseudocardinal, suggesting possible hybrid introgression with Q. verrucosa.
   - Ictinodonta spp.: preliminary allozyme assays (PEP, MDH) show ∼12% divergence.

Notes:
• See Stansbery 1960 for original keys.
• Abbreviations follow Turgeon et al. (1998).
• Don’t confuse with Asian Asiaticolla; incipient cryptic speciation under study.
""",

    "document2_archaic_english.pdf": """Excerpt from “The Chronicle of Brihtwold” (c. 1050–1080 AD)

“Lo, in the year of our lord, the thrall of King Æthelred didst wander beyond the Fen, where bogs clutched the boots of steel. Oft did the raven croak ere the dawn, and forthwith the fyrd assembled—each noble bearing his byrnie and his fyrd-blade. Yet ’twas in the still of Eadwig’s eve that the wyrm of Wessex didst rise, its blood-red coils eclipsing the moon, so that no man knew hope but in prayer.”

Annotations:
- “fyrd” → common levy
- “byrnie” → mailshirt
- “fyrd-blade” → any single-edged sword
- “wyrm” → serpent or dragon
""",

    "document3_chemical_notation.pdf": """Document: Synthesis and Characterization of [Fe(CN)6]3–/4– Redox Couple in Ionic Liquids

Abstract:
We report cyclic voltammetry of ferrocyanide/ferricyanide in 1-ethyl-3-methylimidazolium tetrafluoroborate ([EMIM][BF4]). Observed ΔEₚ = 75 mV at ν = 100 mV/s; diffusion coefficient D calculated via Randles–Ševčík:

    i_p = (2.69×10^5)·n^(3/2)·A·C·D^(1/2)·ν^(1/2)

Table 1:

  scan rate (mV/s) | E_pa (V vs. Ag/AgCl) | E_pc (V vs. Ag/AgCl) | ΔE_p (mV)
  -----------------|-----------------------|-----------------------|-----------
         50        | 0.225                 | 0.150                 | 75        
        100        | 0.230                 | 0.155                 | 75        
        200        | 0.235                 | 0.160                 | 75        

Conclusion: IL viscosity η ≈ 250 cP at 25 °C retards diffusion; D ≈ 2.3×10⁻⁷ cm²/s.
""",

    "document4_mathematical_proof.pdf": """Proof of the Uniform Boundedness Principle

Let X be a Banach space, Y a normed space, and {T_n: X→Y} a family of bounded linear operators. Suppose:
    ∀x ∈ X,  sup_n ‖T_n x‖ < ∞.

We show sup_n ‖T_n‖ < ∞.

1. For each m ∈ ℕ, define:
       E_m = { x ∈ X :  sup_n ‖T_n x‖ ≤ m }.
2. Each E_m is closed (by continuity of T_n and taking supremum).
3. ⋃_{m=1}^∞ E_m = X, so by Baire Category, some E_M has nonempty interior.
4. ∃ ball B(x₀, r) ⊆ E_M ⇒ ∀‖h‖ ≤ r,  sup_n ‖T_n (x₀ + h)‖ ≤ M.
5. Then for any y ∈ X, write y = x₀ + h scaled: T_n y = T_n(x₀ + h) − T_n(x₀).  
   ⇒ ‖T_n y‖ ≤ 2M·(‖y‖/r + 1).  
6. Hence sup_n ‖T_n‖ < ∞.

✎ See Rudin, Functional Analysis, Theorem 1.14.
""",

    "document5_pseudocode_and_edge_cases.pdf": """# Pseudocode: Token-based API Authentication

function requestAccessToken(client_id, client_secret, grant_type, scope):
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type,
        "scope": scope
    }
    response = HTTP.post("https://auth.example.com/token", json=payload)
    if response.status_code != 200:
        logError(response.body)
        raise AuthError("Failed token issuance")
    token_data = parseJSON(response.body)
    return token_data["access_token"], token_data["expires_in"]

# Edge cases
- When grant_type="refresh_token", payload needs "refresh_token" field, not client_secret.
- If JSON has BOM or non-UTF8, parseJSON will throw; wrap in try/catch.
- Rate limit: if 429 returned, backoff exponentially: base_delay=1s, max_delay=32s.

# Notes:
• Some servers ignore unknown JSON fields; others reject outright.
• Clock skew: tokens issued at T₀ may be invalid until T₀ + Δ; clock sync required.
"""
}

# Generate PDFs
for fname, content in docs.items():
    path = os.path.join(".", fname)  # Save in current directory
    c = canvas.Canvas(path, pagesize=letter)
    text = c.beginText(40, 750)
    for line in content.split("\n"):
        wrapped = textwrap.wrap(line, width=85)
        if not wrapped:
            text.textLine("")
        for wrap_line in wrapped:
            text.textLine(wrap_line)
    c.drawText(text)
    c.save()

# Provide download links
print("Your sample PDFs have been created in the current directory:")
for fname in docs.keys():
    print(f"- {fname}")

