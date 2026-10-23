"""The research corpus behind IP Australia's research goal: ingest each source, and read the tables back."""

from .core import CorpusError, load, path

__all__ = ["CorpusError", "load", "path"]
