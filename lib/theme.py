"""Palette and the fixed category -> colour map.

Values are the validated reference palette from the data-viz method (light mode).
We do not re-run the validator because nothing is swapped — these are the
reference hues as shipped. Streamlit's chart theme supplies the chrome (axes,
grid, background) for light and dark; we fix only the series colours here.

Rule that matters: colour follows the *entity*, never its rank. The maps below
are keyed by name, so a filter that drops a category never repaints the rest.
"""

# Reference categorical palette — slots 1..8, light mode.
CATEGORICAL = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]
OTHER_GREY = "#898781"  # muted ink — the "Other" bucket
SEQUENTIAL_HUE = "#2a78d6"  # single-hue magnitude ranking

# Reserved status colours (used from Stage 3 for avoidable fees; never as a series).
STATUS_WARNING = "#fab219"
STATUS_CRITICAL = "#d03b3b"

# The seven highest-net-spend categories get a stable slot each
# (docs/project_status.md "Net spend by category"). Everything else -> "Other".
_TOP7 = [
    "Groceries & Provisions",
    "Debt & EMI",
    "Health & Fitness",
    "Food & Dining",
    "Subscriptions & Software",
    "Shopping",
    "P2P / Personal",
]
CATEGORY_COLOURS = {name: CATEGORICAL[i] for i, name in enumerate(_TOP7)}
CATEGORY_COLOURS["Other"] = OTHER_GREY

# Analytical rollups (docs/data_models.md "category — analytical groupings").
CATEGORY_GROUP_ORDER = [
    "Day-to-day",
    "Committed",
    "Cost of credit",
    "Discretionary",
    "Not spend",
]

# Payment instruments (docs/data_models.md value list).
INSTRUMENT_LABELS = {
    "credit_card": "Credit card",
    "upi_bank": "UPI — bank",
    "upi_lite": "UPI Lite",
}
INSTRUMENT_COLOURS = {
    "Credit card": CATEGORICAL[0],
    "UPI — bank": CATEGORICAL[1],
    "UPI Lite": CATEGORICAL[2],
}


def category_colour(name: str) -> str:
    return CATEGORY_COLOURS.get(name, OTHER_GREY)


def fold_to_top7(name: str) -> str:
    """Collapse any category outside the fixed seven into 'Other'."""
    return name if name in CATEGORY_COLOURS else "Other"
