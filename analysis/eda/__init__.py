"""Helpers for the exploratory data analysis (EDA) in `analysis/notebooks/`.

    from eda import sql, load_lens, style, univariate as uni, bivariate as bi, multivariate as multi

`data` reads the corpus and the lens tables through DuckDB; `build` makes the lens tables; `style` gives every chart
one look and every variable a plain-English label; `univariate`, `bivariate` and `multivariate` are the three stages.
"""

from . import bivariate, data, multivariate, style, univariate
from .data import TooManyRows, load_lens, sql

__all__ = ["TooManyRows", "bivariate", "data", "load_lens", "multivariate", "sql", "style", "univariate"]
