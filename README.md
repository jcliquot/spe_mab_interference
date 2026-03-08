# Serum Protein Electrophoresis Curve Decoder

A lightweight Python utility to decode, validate, and visualise raw hexadecimal
capillary electrophoresis (SPE) curves produced by compatible analysers.

## Features

- **Hex decoding** – converts 4-character grouped hex strings to integer signal arrays
- **Quality flags** – bitmask alerts for missing values, artefact jumps, and wide delimiter gaps
- **Fraction interpolation** – replaces delimiter sample points with neighbour-averaged values
- **Visualisation** – clean matplotlib plot with optional coloured interpretation zones (C / D / E)
- **SVG + PNG export**

## Requirements

```
numpy
matplotlib
scipy  # optional – used for peak detection extensions
```

Install dependencies:

```bash
pip install numpy matplotlib scipy
```

## Usage

```python
from serum_electrophoresis import decipher_curve, plot_curve

result = decipher_curve(curva_hex_string)
plot_curve(result, output_path="my_curve.svg")
```

### `decipher_curve` return value

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

After the Beta-2 globulins delimitation, three 16-point coloured rectangles (C=red, D=green, E=yellow)
are overlaid on the plot to highlight post-beta migration zones.

## License

MIT — see [LICENSE](LICENSE) for details.
