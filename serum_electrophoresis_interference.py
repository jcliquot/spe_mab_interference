"""
Serum Protein Electrophoresis Curve Decoder
============================================
Decodes raw hexadecimal capillary electrophoresis curves, detects fraction
delimiters, flags quality issues, and plots the resulting curve with optional
coloured interpretation zones.

Author : Julien Cliquot
License: MIT
"""

from __future__ import annotations

import re
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FRACTION_NAMES = [
    "",
    "Albumin",
    "Alpha-1 globulins",
    "Alpha-2 globulins",
    "Beta-1 globulins",
    "Beta-2 globulins",
    "Gamma globulins",
]

ZONE_COLORS = {
    "C": "#FF0000",
    "D": "#00FF00",
    "E": "#FFCF12",
}

ZONE_WIDTH = 16
ZONE_RECT_HEIGHT = 350


# ---------------------------------------------------------------------------
# Curve decoding
# ---------------------------------------------------------------------------

def decipher_curve(
    curva: str,
    threshold_error: int = 4_000,
    threshold_low: int = 10_000,
    threshold_high: int = 30_000,
) -> dict:
    """Decode a hexadecimal electrophoresis curve string.

    Parameters
    ----------
    curva:
        Raw hexadecimal string (4-character hex groups, optionally ending with
        a sentinel ``8000`` marker).
    threshold_error:
        Minimum jump amplitude considered a measurement artefact.
    threshold_low:
        Minimum value flagging a fraction-delimiter sample point.
    threshold_high:
        Minimum value distinguishing a major fraction from a sub-fraction.

    Returns
    -------
    dict with keys:
        ``curve``            – cleaned signal (list of int)
        ``fractions_coords`` – indices of major fraction delimiters
        ``subfractions_coords`` – indices of minor fraction delimiters
        ``peaks_coords``     – reserved, always empty list
        ``alertflag``        – bitmask (1 = missing values, 2 = artefact jump,
                               8 = wide delimiter gap)
    """
    warning_flag = 0

    # --- Parse hex string ------------------------------------------------
    raw_hex = re.findall(r".{4}", curva)
    samples = [int(h, 16) for h in raw_hex]

    # --- Handle missing values -------------------------------------------
    if any(v is None for v in samples):
        warning_flag |= 1
        samples = [0 if v is None else v for v in samples]

    signal = np.array(samples[::-1], dtype=np.int64)  # reverse: cathode→anode

    # --- Artefact detection ----------------------------------------------
    diffs = np.diff(signal)
    if np.any((np.abs(diffs) > threshold_error) & (np.abs(diffs) < threshold_low)):
        warning_flag |= 2

    # --- Delimiter detection & interpolation -----------------------------
    delim_idx = np.where(signal >= threshold_low)[0]
    delim_values = signal[delim_idx]
    non_delim_idx = np.setdiff1d(np.arange(len(signal)), delim_idx)

    values = signal.copy()
    for idx in delim_idx:
        replacement = _interpolate_delimiter(idx, signal, delim_idx, non_delim_idx)
        if replacement is None:
            raise ValueError(f"Cannot interpolate delimiter at index {idx}.")
        gap = _delimiter_gap(idx, delim_idx, non_delim_idx)
        if gap > 2:
            warning_flag |= 8
        values[idx] = replacement

    # --- Classify delimiters ---------------------------------------------
    fractions = delim_idx[delim_values >= threshold_high]
    subfractions = delim_idx[delim_values < threshold_high]

    return {
        "curve": values.tolist(),
        "fractions_coords": fractions.tolist(),
        "subfractions_coords": subfractions.tolist(),
        "peaks_coords": [],
        "alertflag": warning_flag,
    }


def _interpolate_delimiter(
    idx: int,
    signal: np.ndarray,
    delim_idx: np.ndarray,
    non_delim_idx: np.ndarray,
) -> int | None:
    """Return the interpolated value for a single delimiter sample."""
    before = non_delim_idx[non_delim_idx < idx]
    after = non_delim_idx[non_delim_idx >= idx]

    if len(before) == 0:
        return int(signal[after[0]]) if len(after) else None
    if len(after) == 0:
        return int(signal[before[-1]])

    return int(round((signal[before[-1]] + signal[after[0]]) / 2))


def _delimiter_gap(
    idx: int,
    delim_idx: np.ndarray,
    non_delim_idx: np.ndarray,
) -> int:
    """Return the index distance across the delimiter cluster containing *idx*."""
    before = non_delim_idx[non_delim_idx < idx]
    after = non_delim_idx[non_delim_idx >= idx]
    if len(before) == 0 or len(after) == 0:
        return 0
    return int(after[0] - before[-1])


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def _find_beta2_bounds(fractions_coords: list[int], n_points: int) -> tuple[int | None, int | None]:
    """Return the (start, end) index of the Beta-2 globulin zone, or (None, None)."""
    fractions = sorted(fractions_coords)
    current_start = 0
    beta2_start = beta2_end = None

    for j, end in enumerate(fractions):
        name = FRACTION_NAMES[j] if j < len(FRACTION_NAMES) else f"Segment {j + 1}"
        if name == "Beta-2 globulins" and current_start < end:
            beta2_start, beta2_end = current_start, end
        current_start = end

    # Check the final (rightmost) segment
    last_name = (
        FRACTION_NAMES[len(fractions)] if len(fractions) < len(FRACTION_NAMES)
        else f"Segment {len(fractions) + 1}"
    )
    if last_name == "Beta-2 globulins":
        beta2_start, beta2_end = current_start, n_points

    return beta2_start, beta2_end


def plot_curve(result: dict, output_path: str = "electrophoresis_curve.svg") -> None:
    """Plot the decoded electrophoresis curve and save it as SVG.

    Parameters
    ----------
    result:
        Output dict from :func:`decipher_curve`.
    output_path:
        Destination file path for the SVG output.
    """
    x = np.arange(len(result["curve"]))
    y = np.array(result["curve"])

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(x, y, color="black", linewidth=3, zorder=1, label="Curve")

    # --- Axis cosmetics --------------------------------------------------
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_xticklabels([])
    ax.grid(False)

    # --- Coloured interpretation zones (C / D / E) -----------------------
    _, beta2_end = _find_beta2_bounds(result["fractions_coords"], len(x))
    if beta2_end is not None:
        starts = [
            beta2_end,
            beta2_end + ZONE_WIDTH,
            beta2_end + 2 * ZONE_WIDTH,
        ]
        for (label, color), zone_start in zip(ZONE_COLORS.items(), starts):
            zone_end = zone_start + ZONE_WIDTH
            if zone_start < len(x):
                width = min(zone_end, len(x)) - zone_start
                rect = patches.Rectangle(
                    (zone_start, 0), width, ZONE_RECT_HEIGHT,
                    linewidth=0, edgecolor="none",
                    facecolor=color, alpha=0.50, zorder=0,
                )
                ax.add_patch(rect)

    fig.tight_layout()
    plt.savefig(output_path, format="svg")
    plt.savefig(output_path.replace(".svg", ".png"), format="png", dpi=150)
    plt.show()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    CURVA = (
        "80050005000400040002000200010001000100000000000000000000000000000000000100010002000200020004000500060009000B000D00110015001A002000260030003B00470052005D00680073007E00870091009C00A700B200BC00C600CE00D500DC00DF00E900F400FD01040106010500FF00F500EE00E500DE00D400CA00C100B500AB00A00095008A0080007900738071007A0087009800A800B500BD00C000BB00B000A30097008B0081007A0074006E0066005E0057805400580063007E00A800E401210156017D01880175014F012200F300C600A5008E007C007000660060005D005A805A005B005D005F00630068006D0073007B0084008C009600A000A700B000B700C000CC00DC00F2010B0125013E015301620168016201560144012D011200F400D300B20094007A006500580051004D004C004C004A0049004880470048004C005300600074008B00A200B800C600CA00C400B5009D0085006E00590048003C0032002C00270023001E001C001B001A001880170018001C001E00230027002C0033003900440052006B009800E201530204032004DF076F0A730D240F140FFF0FBD0E560C2B09E607FA066105160413035002BF024E01F401AB01700140011700F400D300B6009D00850070005E004D003E00310026001E001A001600140012001200120011001100100010000F000F00100011001400160018001D002000210020001E001C001A00160012000F000D000B000A00090009000700070006000600060005000500050004000400020002000100010001000000000000000000000000000000000000000000008000"
    )

    result = decipher_curve(CURVA)
    print(f"Alert flag : {result['alertflag']:#04b}")
    print(f"Fractions  : {result['fractions_coords']}")
    print(f"Subfractions: {result['subfractions_coords']}")
    plot_curve(result, output_path="electrophoresis_curve.svg")
