"""StackSense: deterministic tech stack recommendation engine (no LLM, standard library only)."""
from .engine import ENGINE_VERSION, recommend  # noqa: F401

__all__ = ["recommend", "ENGINE_VERSION"]
