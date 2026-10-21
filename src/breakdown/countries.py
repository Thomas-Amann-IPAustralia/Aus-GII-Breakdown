"""Country names to ISO3 codes, so the GII, the HDR and the WHR line up economy by economy.

Exact lookups only (the GII's own names first, then ISO 3166 names through pycountry, then the aliases below): a
regional aggregate such as "Arab States" or "World" must never match a country by a fuzzy guess. Names that match
nothing are reported in the manifest so a missed country is visible.
"""

from __future__ import annotations

import pycountry

# The sources' own spellings that ISO 3166 does not carry. None: not a country we can place (left out on purpose).
ALIASES: dict[str, str | None] = {
    # UNDP's Human Development Report
    "hong kong, china (sar)": "HKG",
    "korea (republic of)": "KOR",
    "korea (democratic people's rep. of)": "PRK",
    "moldova (republic of)": "MDA",
    "eswatini (kingdom of)": "SWZ",
    "micronesia (federated states of)": "FSM",
    "tanzania (united republic of)": "TZA",
    "congo (democratic republic of the)": "COD",
    # the World Happiness Report
    "côte d’ivoire": "CIV",
    "dr congo": "COD",
    "hong kong sar of china": "HKG",
    "kosovo": "XKX",
    "lao pdr": "LAO",
    "state of palestine": "PSE",
    "swaziland": "SWZ",
    "taiwan province of china": "TWN",
    "north cyprus": None,
    "somaliland region": None,
}


class Countries:
    def __init__(self, gii_names: dict[str, str]):
        """`gii_names` maps ISO3 to the GII's own economy names, which are used for display where they exist."""
        self.names = dict(gii_names)
        self._by_name = {n.lower(): iso for iso, n in gii_names.items()}

    def iso3(self, name: str) -> str | None:
        key = str(name).strip().lower()
        if not key:
            return None
        if key in self._by_name:
            return self._by_name[key]
        if key in ALIASES:
            return ALIASES[key]
        try:
            c = pycountry.countries.lookup(key)
        except LookupError:
            return None
        return c.alpha_3

    def name(self, iso3: str, fallback: str | None = None) -> str:
        if iso3 in self.names:
            return self.names[iso3]
        c = pycountry.countries.get(alpha_3=iso3)
        if c is not None:
            return getattr(c, "common_name", None) or c.name
        return fallback or iso3
