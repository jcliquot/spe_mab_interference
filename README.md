# ⚗️ Serum Protein Electrophoresis Analyser

[![Open Web App](https://img.shields.io/badge/Open%20Web%20App-4361ee?style=for-the-badge&logo=googlechrome&logoColor=white)](https://jcliquot.github.io/serum-electrophoresis-decoder/spe_webapp.html)

> **Scientific reference** — *Article link to be added*

> 📄 [Publication — *Characterization of the migration profile of 36 Therapeutic Monoclonal Antibodies in Serum Protein Electrophoresis and Immunofixation*](#)

---

A lightweight Python/JavaScript toolkit to decode, validate, and visualise raw hexadecimal capillary electrophoresis (SPE) curves produced by compatible analysers.

## Features

- **Hex decoding** — converts 4-character grouped hex strings to integer signal arrays
- **Quality flags** — bitmask alerts for missing values, artefact jumps, and wide delimiter gaps
- **Fraction interpolation** — replaces delimiter sample points with neighbour-averaged values
- **Interactive web app** — colour-coded fractions, ±3-point click integration, C/D/E zone toggle
- **Google Colab notebook** — slider-based integration with live Matplotlib rendering
- **SVG + PNG export**

## Repository structure

```
├── spe_webapp.html        # Standalone interactive web app (no server needed)
├── serum_electrophoresis.py   # Core Python module
├── server.py              # Optional Flask backend for Matplotlib PNG rendering
├── README.md
└── LICENSE
```

## Quick start

### Web app (no installation)
Download `spe_webapp.html` and open it in any browser — or use the badge above if GitHub Pages is enabled.

### Python module
```python
from serum_electrophoresis import decipher_curve, plot_curve

result = decipher_curve(curva_hex_string)
plot_curve(result, output_path="my_curve.svg")
```

### Flask server (optional — enables Matplotlib PNG in the web app)
```bash
pip install flask matplotlib numpy
python server.py
# → open http://localhost:5000
```

## Requirements

```
numpy
matplotlib
scipy      # optional — for peak detection extensions
flask      # optional — only for server.py
plotly
```

Install all at once:
```bash
pip install numpy matplotlib scipy flask plotly
```

## `decipher_curve` return value

| Key | Type | Description |
|-----|------|-------------|
| `curve` | `list[int]` | Cleaned signal |
| `fractions_coords` | `list[int]` | Major fraction delimiter indices |
| `subfractions_coords` | `list[int]` | Minor fraction delimiter indices |
| `peaks_coords` | `list` | Reserved (always empty) |
| `alertflag` | `int` | Bitmask: `1`=missing, `2`=artefact, `8`=wide gap |

### Alert flag bits

| Bit | Value | Meaning |
|-----|-------|---------|
| 0 | `1` | Missing/None values in raw data |
| 1 | `2` | Artefact jump detected |
| 3 | `8` | Delimiter gap wider than 2 points |

## Fraction naming convention

```
Index 0 → (empty sentinel)
Index 1 → Albumin
Index 2 → Alpha-1 globulins
Index 3 → Alpha-2 globulins
Index 4 → Beta-1 globulins
Index 5 → Beta-2 globulins
Index 6 → Gamma globulins
```

## Interpretation zones

After the Beta-2 globulins delimitation, three 16-point coloured rectangles (C = red, D = green, E = yellow)
are overlaid on the plot to highlight post-beta migration zones. They can be toggled on/off via the **Hide/Show C/D/E zones** button in the web app.

## License

MIT — see [LICENSE](LICENSE) for details.
