"""Kern an der Mini-Instanz von Hand und an den Handbeispielen der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Behälter 10 mal 10 mal 10; Quader 0: (2,8,2) Masse 1, 1: (4,7,4) Masse 3, 2: (3,8,6) Masse 3, 3: (4,8,3) Masse 1; Reihenfolge 0, 1, 2, 3; Eckpunkte wie in Stück 9):
  Quader 0 -> (0,0,0); E = {(2,0,0), (0,8,0), (0,0,2)}. Quader 1 -> (2,0,0) (x 2 bis 6, y 0 bis 7, z 0 bis 4); neue Ecken (6,0,0), (2,7,0), (2,0,4) und die Projektion (0,0,4);
  E = {(0,8,0), (0,0,2), (6,0,0), (2,7,0), (2,0,4), (0,0,4)}. Quader 2 -> (6,0,0); neue Ecken (9,0,0), (6,8,0) und (6,0,6) mit der Projektion (0,0,6);
  E = {(0,8,0), (0,0,2), (2,7,0), (2,0,4), (0,0,4), (9,0,0), (6,8,0), (6,0,6), (0,0,6)}.
  Quader 3 (4,8,3): z = 0 und (0,0,2) scheitern an der Größe oder an Quader 1, der erste passende Punkt ist (0,0,4); dort liegt er bei x 2 bis 4 auf Quader 1 (Oberseite z = 4): 2 mal 7 = 14 von 32
  = 43,75 % Stützfläche (Quader 0 endet bei z = 2).
  Mindest-Stützfläche 80 %: (0,0,4) scheitert (43,75 %), (2,0,4) passt (x 2 bis 6, y 0 bis 8) und liegt auf Quader 1 mit 4 mal 7 = 28 von 32 = 87,5 %.
  Mindest-Stützfläche 100 %: (2,0,4) hat 87,5 % und scheitert, (0,0,6) hat 0 %, (6,0,6) liegt auf Quader 2 mit 3 mal 8 = 24 von 32 = 75 % und scheitert: neuer Behälter, (0,0,0).
Schwerpunkt bei Mindest-Stützfläche 0 (Quader 3 bei (0,0,4)): Mittelpunkte (1|4), (4|3,5), (7,5|4), (2|4) mit den Massen 1, 3, 3, 1: cx = (1 + 12 + 22,5 + 2) / 8 = 4,6875, cy = (4 + 10,5 + 12 + 4) / 8 = 3,8125.
  Hüllbox x 0 bis 9, y 0 bis 8: dx liegt in [0, 1], dy in [0, 2]; dx = rund(5 - 4,6875) = 0, dy = rund(5 - 3,8125) = 1: neuer Schwerpunkt (4,6875 | 4,8125).
Regel nah bei Mindest-Stützfläche 0: Quader 1: (2,0,0) hat den Schwerpunkt (3,25 | 3,625), (0,0,2) den Schwerpunkt (1,75 | 3,625): (2,0,0) liegt näher an (5 | 5). Quader 2: (6,0,0) mit (5,0714 | 3,7857)
  gewinnt gegen (2,0,4). Quader 3: (0,0,4) hat (4,6875 | 3,8125) mit Abstand zum Quadrat 1,5078; (2,0,4) hat (4,9375 | 3,8125) mit 1,4141: nah wählt (2,0,4) statt (0,0,4).
Harte Regel (Fenster 0,5, Schwelle 20 % des Volumens = 200): Quader 0 und 1 (zusammen 144) sind frei. Quader 2 würde 288 füllen; jeder Behälter-Schwerpunkt liegt in y zwischen 3,5 und 4 (alle Mittelpunkte
  in y liegen dort), also mindestens 1 von der Mitte: außerhalb von 0,5, kein Punkt ist zulässig, Quader 2 öffnet Behälter 1 (der erste Quader eines neuen Behälters wird immer gesetzt). Quader 3 passt
  weder in Behälter 0 noch in Behälter 1 (gleicher Grund, 240 > 200), also Behälter 2: drei Behälter.
"""

import pytest

import stz_algorithm as A
import stz_constants as C
from stz_scenario import beispiel


def test_reihenfolge_je_schluessel_mit_gleichstaenden_in_lieferreihenfolge(mini):
    k = mini.kisten                      # Volumen 32, 112, 144, 96; Grundfläche 16, 28, 24, 32; Höhe 2, 4, 6, 3
    assert A.reihenfolge(k, A.LIEFERUNG) == [0, 1, 2, 3]
    assert A.reihenfolge(k, A.VOLUMEN) == [2, 1, 3, 0]
    assert A.reihenfolge(k, A.GRUNDFLAECHE) == [3, 1, 2, 0]
    assert A.reihenfolge(k, A.HOEHE) == [2, 1, 3, 0]
    assert A.reihenfolge_masse(k, mini.masse) == [1, 2, 0, 3]            # 3, 3 (Lieferreihenfolge), dann 1, 1
    assert A.schluessel_wert(k, A.VOLUMEN) == [32, 112, 144, 96] and A.schluessel_wert(k, A.LIEFERUNG) == [0, 0, 0, 0]


def test_ohne_bedingung_extreme_points_auf_der_mini_instanz_mit_den_eckpunkten(mini):
    bins, platz, zustand = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10)
    assert bins == [[0, 1, 2, 3]] and platz == [(0, 0, 0, 0, 0), (1, 0, 2, 0, 0), (2, 0, 6, 0, 0), (3, 0, 0, 0, 4)]
    # Schritt für Schritt: der Zustand nach k Quadern ist der Zustand des Anfangs der Reihenfolge
    assert A.pack(mini.kisten, mini.masse, [0], 10)[2] == [((2, 0, 0), (0, 8, 0), (0, 0, 2))]
    assert A.pack(mini.kisten, mini.masse, [0, 1], 10)[2] == [((6, 0, 0), (2, 7, 0), (0, 8, 0), (0, 0, 2), (0, 0, 4), (2, 0, 4))]
    assert A.pack(mini.kisten, mini.masse, [0, 1, 2], 10)[2] == [((9, 0, 0), (2, 7, 0), (0, 8, 0), (6, 8, 0), (0, 0, 2), (0, 0, 4), (2, 0, 4), (0, 0, 6), (6, 0, 6))]


def test_stuetzflaeche_der_mini_instanz_ohne_und_mit_bedingung(mini):
    ohne = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.0)
    assert A.stuetzflaeche(mini.kisten, ohne[1], 3) == 14 / 32 and [A.stuetzflaeche(mini.kisten, ohne[1], i) for i in (0, 1, 2)] == [1.0, 1.0, 1.0]
    assert A.stuetz_minimum(mini.kisten, ohne[1]) == 14 / 32 and A.stuetz_kennzahlen(mini.kisten, ohne[1]) == (1, 0)
    mit80 = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.8)
    assert mit80[0] == [[0, 1, 2, 3]] and mit80[1] == [(0, 0, 0, 0, 0), (1, 0, 2, 0, 0), (2, 0, 6, 0, 0), (3, 0, 2, 0, 4)]
    assert A.stuetzflaeche(mini.kisten, mit80[1], 3) == 28 / 32 and A.stuetz_minimum(mini.kisten, mit80[1]) == 28 / 32
    mit100 = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 1.0)
    assert mit100[0] == [[0, 1, 2], [3]] and mit100[1] == [(0, 0, 0, 0, 0), (1, 0, 2, 0, 0), (2, 0, 6, 0, 0), (3, 1, 0, 0, 0)] and A.stuetz_minimum(mini.kisten, mit100[1]) == 1.0


def test_schwerpunkt_und_verschieben_der_mini_instanz_von_hand(mini):
    _, platz, _ = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.0)
    cx, cy, m = A.schwerpunkt_behaelter(mini.kisten, mini.masse, platz, 0)
    assert (cx, cy, m) == (4.6875, 3.8125, 8.0)
    assert A.im_fenster(cx, cy, 10, 1.0) is False and A.im_fenster(cx, cy, 10, 1.1875) is True          # |3,8125 - 5| = 1,1875: der Rand zählt dazu
    neu, v = A.verschieben(mini.kisten, mini.masse, platz, 10)
    assert v == {0: (0, 1)} and neu == [(i, b, x, y + 1, z) for i, b, x, y, z in platz]
    cx2, cy2, _ = A.schwerpunkt_behaelter(mini.kisten, mini.masse, neu, 0)
    assert (cx2, cy2) == (4.6875, 4.8125) and A.im_fenster(cx2, cy2, 10, 1.0) and A.packung_pruefen(mini.kisten, neu, 10)
    assert A.stuetz_kennzahlen(mini.kisten, neu) == A.stuetz_kennzahlen(mini.kisten, platz)                 # Verschieben ändert die Stützflächen nicht
    assert A.schwerpunkte(mini.kisten, mini.masse, neu, 10, 1.0) == [(4.6875, 4.8125, 0.384, True)]
    mit80 = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.8)[1]
    assert A.schwerpunkt_behaelter(mini.kisten, mini.masse, mit80, 0)[:2] == (4.9375, 3.8125)


def test_regel_nah_waehlt_den_punkt_mit_dem_schwerpunkt_naeher_an_der_mitte(mini):
    nah = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.0, A.NAH)
    assert nah[1] == [(0, 0, 0, 0, 0), (1, 0, 2, 0, 0), (2, 0, 6, 0, 0), (3, 0, 2, 0, 4)]             # Quader 3 bei (2,0,4) statt (0,0,4)
    assert A.schwerpunkt_behaelter(mini.kisten, mini.masse, nah[1], 0)[:2] == (4.9375, 3.8125)
    assert A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.0, A.KEINE)[1][3] == (3, 0, 0, 0, 4)


def test_harte_regel_ab_der_fuellschwelle_oeffnet_behaelter(mini):
    hart = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.0, A.HART, 0.5, 0.2)
    assert hart[0] == [[0, 1], [2], [3]] and hart[1] == [(0, 0, 0, 0, 0), (1, 0, 2, 0, 0), (2, 1, 0, 0, 0), (3, 2, 0, 0, 0)]
    assert len(A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.0, A.NAH)[0]) == 1
    # mit der Schwelle 100 % greift die Bedingung nie: wie nah
    assert A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.0, A.HART, 0.5, 1.0) == A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 0.0, A.NAH)


def test_anzahl_je_stuetzflaeche_der_mini_instanz(mini):
    assert [A.anzahl(mini.kisten, mini.masse, A.LIEFERUNG, 10, s) for s in (0.0, 0.5, 0.8, 1.0)] == [1, 1, 1, 2]


def test_schranken_der_mini_instanz(mini):
    assert A.schranken(mini.kisten, 10) == (1, 0, 1) and A.schranke(mini.kisten, 10) == 1
    assert A.schranken(((6, 6, 6),) * 3, 10) == (1, 3, 3) and A.schranken(((5, 9, 9), (9, 5, 9)), 10) == (1, 0, 1) and A.schranken(((10, 10, 10), (10, 10, 10), (1, 1, 1)), 10) == (3, 2, 3)


def test_stuetzflaeche_grenzen_und_schwebende_quader():
    kisten = ((10, 10, 2), (4, 4, 2), (4, 4, 2))
    platz = [(0, 0, 0, 0, 0), (1, 0, 0, 0, 2), (2, 0, 0, 5, 6)]
    assert [A.stuetzflaeche(kisten, platz, i) for i in (0, 1, 2)] == [1.0, 1.0, 0.0] and A.stuetz_kennzahlen(kisten, platz) == (1, 1)
    kisten2 = ((8, 10, 2), (5, 4, 2))                      # Quader 1 auf x 4 bis 9, Quader 0 reicht bis 8: 16 von 20 = 80 %, nicht unter 80 %
    platz2 = [(0, 0, 0, 0, 0), (1, 0, 4, 0, 2)]
    assert A.stuetzflaeche(kisten2, platz2, 1) == 0.8 and A.stuetz_kennzahlen(kisten2, platz2) == (0, 0)
    kisten3 = ((5, 10, 2), (5, 4, 2))
    assert A.stuetzflaeche(kisten3, [(0, 0, 0, 0, 0), (1, 0, 2, 0, 2)], 1) == pytest.approx(0.6)
    assert A.stuetzflaeche(((10, 10, 2), (4, 4, 2)), [(0, 0, 0, 0, 0), (1, 1, 0, 0, 2)], 1) == 0.0 and A.stuetzflaeche(((10, 10, 2), (4, 4, 2)), [(0, 0, 0, 0, 0), (1, 0, 0, 0, 3)], 1) == 0.0


def test_packung_pruefen_erkennt_fehler(mini):
    gut = [(0, 0, 0, 0, 0), (1, 0, 2, 0, 0), (2, 0, 6, 0, 0), (3, 0, 0, 0, 4)]
    assert A.packung_pruefen(mini.kisten, gut, 10)
    assert not A.packung_pruefen(mini.kisten, gut[:3], 10) and A.packung_pruefen(mini.kisten, gut[:3], 10, vollstaendig=False)
    assert not A.packung_pruefen(mini.kisten, gut + [(0, 1, 0, 0, 0)], 10)
    assert not A.packung_pruefen(mini.kisten, [(0, 0, 0, 0, 0), (1, 0, 1, 0, 0), (2, 0, 6, 0, 0), (3, 0, 0, 0, 4)], 10)       # Quader 1 bei x = 1 überlappt Quader 0
    assert not A.packung_pruefen(mini.kisten, [(0, 0, 0, 0, 0), (1, 0, 2, 0, 0), (2, 0, 6, 0, 0), (3, 0, 0, 0, 8)], 10)       # Quader 3 ragt über die Decke (8 + 3 > 10)
    assert A.packung_pruefen(mini.kisten, [(0, 0, 0, 0, 0), (1, 0, 2, 0, 0), (2, 0, 6, 0, 0), (3, 1, 0, 0, 0)], 10)
    assert not A.packung_pruefen(mini.kisten, [(0, 0, -1, 0, 0), (1, 0, 2, 0, 0), (2, 0, 6, 0, 0), (3, 0, 0, 0, 4)], 10) and not A.packung_pruefen(mini.kisten, [(9, 0, 0, 0, 0)], 10, vollstaendig=False)


def test_pack_lehnt_ungueltige_eingaben_ab(mini):
    faelle = (((mini.kisten, mini.masse, [0, 0], 10), {}), ((mini.kisten, mini.masse, [4], 10), {}), ((((11, 3, 3),), (1.0,), [0], 10), {}), ((((0, 3, 3),), (1.0,), [0], 10), {}),
              ((((3, 3),), (1.0,), [0], 10), {}), ((mini.kisten, mini.masse, [0], 10), {"regel": 3}), ((mini.kisten, mini.masse, [0], 10), {"s_min": 1.5}),
              ((mini.kisten, mini.masse, [0], 10), {"s_min": -0.1}), ((mini.kisten, (1.0,), [0], 10), {}), ((mini.kisten, (1.0, 1.0, 0.0, 1.0), [0], 10), {}))
    for args, kw in faelle:
        with pytest.raises(ValueError):
            A.pack(*args, **kw)


def test_beispiele_der_app_mit_den_angaben_der_konstanten():
    """Die Behälterzahlen der beiden Handbeispiele aus dem Kommentar der Konstanten (Zeilen: Lieferung, Volumen, Grundfläche, Höhe; Spalten: Mindest-Stützfläche 0, 50, 80, 100 %)."""
    def tab(i):
        b = beispiel(i)
        return [[A.anzahl(b.kisten, b.masse, k, C.CAP, s) for s in C.S_MIN_WERTE] for k in range(4)]

    assert tab(0) == [[2, 2, 2, 2], [1, 1, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]
    assert tab(1)[1] == [1, 1, 1, 1] and tab(1)[2] == [1, 1, 1, 1] and tab(1)[0] == [2, 2, 2, 2]
    assert [A.schranke(beispiel(i).kisten, C.CAP) for i in (0, 1)] == [1, 1] and C.BEISPIEL_OPTIMUM == {0: 1, 1: 1}
    b2 = beispiel(1)
    order = A.reihenfolge(b2.kisten, A.GRUNDFLAECHE)
    ergebnis = {}
    for regel, schieb in ((A.KEINE, False), (A.NAH, False), (A.KEINE, True), (A.NAH, True)):
        bins, platz, _ = A.pack(b2.kisten, b2.masse, order, C.CAP, 0.8, regel)
        if schieb:
            platz = A.verschieben(b2.kisten, b2.masse, platz, C.CAP)[0]
        cx, cy, _ = A.schwerpunkt_behaelter(b2.kisten, b2.masse, platz, 0)
        ergebnis[(regel, schieb)] = (len(bins), round(cx, 1), round(cy, 1), A.im_fenster(cx, cy, C.CAP, 5))
    assert ergebnis == {(0, False): (1, 47.0, 40.0, False), (1, False): (1, 47.3, 41.6, False), (0, True): (1, 47.0, 42.0, False), (1, True): (1, 47.3, 49.6, True)}
