# ⚗️ Serum Protein Electrophoresis Analyser

[![Open Web App](https://img.shields.io/badge/Open%20Web%20App-%234361ee?style=for-the-badge&logo=html5&logoColor=white)](https://jcliquot.github.io/spe_mab_interference/spe_webapp.html)

> **Scientific reference** — *Article link to be added*

> 📄 [Publication — *Characterization of the migration profile of 36 Therapeutic Monoclonal Antibodies in Serum Protein Electrophoresis and Immunofixation*](#)

---
# Abstract
## Background

Therapeutic monoclonal antibodies (t-mAbs) are widely used in oncology, hematology, and immune-mediated diseases. Several t-mAbs are visualisable in serum protein electrophoresis (SPEP) and immunofixation electrophoresis (IF), potentially leading to misinterpretation of monoclonal gammopathies. However, the migration profile of these t-mAbs remains poorly described, even though many t-mAbs are widely used or have recently been approved.

### Methods

T-mAbs were tested in SPEP and IF using **Sebia Capillarys3** and **Hydrasis** systems respectively. Normal human sera — defined by the absence of abnormalities on SPEP — were spiked with t-mAbs at their highest reported therapeutic concentrations (*C*<sub>max</sub>) based on product characteristics and published data. Raw electropherogram data were exported and processed using a **reproducible Python-based workflow** to harmonize axes and enable standardized profile overlay and visualization. IF results were independently evaluated by four clinical chemists. Antibodies undetectable by SPEP or IF at *C*<sub>max</sub> were additionally spiked at **500 mg/L** to determine their electrophoretic migration profiles.

### Results

Thirty-six t-mAbs were analyzed. No interference was observed for t-mAbs at concentrations **below 110 mg/L**. All t-mAbs tested at *C*<sub>max</sub> above 110 mg/L or at 500 mg/L were detectable by SPEP and IF. Migration patterns were confirmed for previously described antibodies and newly characterized for several agents, including bispecific and drug-conjugated antibodies. The electropherogram overlay approach enabled refined attribution of migration zones, particularly within the **alpha** and **beta** regions.

### Conclusions

This study expanded current knowledge of t-mAb interference with SPEP and IF and provided standardized electrophoretic profiles for both established and emerging therapies. These data offer practical guidance for clinical laboratories and highlight the need for continued characterization as novel t-mAbs enter routine practice.

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
