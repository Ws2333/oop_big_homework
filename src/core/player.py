"""Player module

Defines a small Player class used by board games. The class stores a player
name and a color (either 'black' or 'white') and provides a human-readable
string representation suitable for teaching and debugging.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Player:
	"""Simple player representation.

	Attributes:
		name: The player's display name
		color: Either 'black' or 'white'
	"""

	VALID_COLORS: ClassVar[set] = {"black", "white"}

	name: str
	color: str

	def __post_init__(self) -> None:
		if not isinstance(self.name, str) or not self.name:
			raise ValueError("name must be a non-empty string")
		if self.color not in self.VALID_COLORS:
			raise ValueError(f"color must be one of {self.VALID_COLORS}")

	def __str__(self) -> str:
		"""Return a compact human-friendly representation.

		Examples:
			Player('Alice', 'black') -> 'Alice (black)'
		"""
		return f"{self.name} ({self.color})"

