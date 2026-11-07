"""Instanzen: die Handbeispiele und Zufallsinstanzen (Quader mit Massen) für App und Messraster."""

import random
from dataclasses import dataclass

import stz_constants as C


@dataclass(frozen=True)
class Instance:
    kisten: tuple         # Quader als (Breite, Tiefe, Höhe) in Lieferreihenfolge, ganzzahlig und positiv
    masse: tuple = ()     # Masse je Quader (positiv); leer = jede Masse 1,0
    cap: int = C.CAP      # Kantenlänge eines Behälters

    def __post_init__(self):
        if self.cap <= 0:
            raise ValueError("Kapazität muss positiv sein")
        for t in self.kisten:
            if len(t) != 3 or any((not isinstance(x, int)) or x <= 0 or x > self.cap for x in t):
                raise ValueError(f"Quader {t!r} ungültig (drei ganze Maße, je 1 bis {self.cap})")
        if not self.masse:
            object.__setattr__(self, "masse", (1.0,) * len(self.kisten))
        if len(self.masse) != len(self.kisten) or any(m <= 0 for m in self.masse):
            raise ValueError("zu jedem Quader gehört genau eine positive Masse")

    @property
    def n(self) -> int:
        return len(self.kisten)


def massen_aus(kisten, seed: int) -> tuple:
    """Masse je Quader: Volumen / 1000 mal Dichte (gleichverteilt 0,5 bis 2,0), auf eine Stelle gerundet, mindestens 0,1. Eigene Zufallsquelle (Seed + 17), damit die Maße der Quader unabhängig bleiben."""
    rng = random.Random(seed + 17)
    return tuple(max(0.1, round(w * d * h / 1000.0 * (0.5 + 1.5 * rng.random()), 1)) for w, d, h in kisten)


def beispiel(index: int) -> Instance:
    return Instance(tuple(C.BEISPIELE[index]), tuple(C.BEISPIEL_MASSEN[index]), C.CAP)


def mess_seed(verteilung: int, n_index: int, j: int) -> int:
    """Fester Seed der j-ten Instanz einer Zelle des Messrasters (Verteilung 0 bis 3, Index der Quaderzahl); stabil über Läufe und Rechner."""
    return 1_000_000 * (verteilung + 1) + 1_000 * (n_index + 1) + j


def zufallsinstanz(verteilung: int, n: int, seed: int, cap: int = C.CAP) -> Instance:
    """n Quader, Breite, Tiefe und Höhe gleichverteilt (ganzzahlig) in den Bereichen der Verteilung, dazu die Massen."""
    _, _, bereiche = C.VERTEILUNGEN[verteilung]
    rng = random.Random(seed)
    kisten = tuple(tuple(rng.randint(*bereiche[a]) for a in range(3)) for _ in range(n))
    return Instance(kisten, massen_aus(kisten, seed), cap)


def quelle_instanz(quelle: int, n: int, seed: int) -> Instance:
    """Instanz der App: Quelle 0 und 1 = Handbeispiele (n und seed ohne Wirkung), 2 bis 5 = Zufallsinstanz der Verteilung quelle - 2."""
    if quelle in C.BEISPIELE:
        return beispiel(quelle)
    return zufallsinstanz(quelle - 2, n, seed)
