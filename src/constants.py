# META
MARGIN = 0.01

# in usd
COMMISSION = 0.00015
CASH = 50_000
RISK_PCT = 0.002  # ~100USD of 50K
RISK_PER_TRADE = CASH * RISK_PCT

SESSIONS = [
    {"name": "ASIAN", "start": "03:00:00", "end": "09:00:00"},
    {"name": "LONDON", "start": "10:30:00", "end": "18:30:00"},
    {"name": "NEWYORK", "start": "16:30:00", "end": "23:00:00"},
    {"name": "OVERLAP", "start": "16:30:00", "end": "18:30:00"},
]

TABLE_STYLES = [
    # Outer table border
    {
        "selector": "table",
        "props": [
            ("border", "1px solid #444444"),
            ("border-collapse", "collapse"),
        ],
    },
    # Header cells (borders + padding)
    {
        "selector": "th",
        "props": [
            ("border", "1px solid #444444"),
            ("padding", "8px 12px"),
            ("background-color", "#1e1e1e"),
            ("color", "#ffffff"),
        ],
    },
    # Data cells (borders + padding)
    {
        "selector": "td",
        "props": [
            ("border", "1px solid #444444"),
            ("padding", "8px 12px"),
        ],
    },
]
