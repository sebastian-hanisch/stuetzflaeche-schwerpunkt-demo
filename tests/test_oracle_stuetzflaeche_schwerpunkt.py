"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 30 Sekunden.

  Dekodierer mit Mindest-Stützfläche und Schwerpunktregel  gegen  eine Umsetzung, die die Eckpunkte nach jedem Quader aus der Liste der gesetzten Quader NEU erzeugt und die Stützfläche jedes Punktes
                                                                aus einem Voxelraster liest (Zellen der Grundfläche, unter denen eine Zelle eines anderen Quaders liegt).
  Schwerpunkt                                              gegen  die Summe über alle Zellen eines Voxelrasters (jede Zelle trägt Masse mal Zellenanteil; hier mit ganzzahligen Maßen exakt).
  Starres Verschieben                                      gegen  eine Suche über alle ganzzahligen Verschiebungen (kleinster Abstand zur Mitte, bei Gleichstand der kleinere Betrag der Verschiebung).
  Optimum (CP-SAT, mit Fenster)                            gegen  das Optimum ohne Fenster (nie kleiner) und gegen die Packung (nie über ihr), in tests/test_claims.py für die Stichprobe der Orakel-Instanzen.
  Eigenschaften:  jede Packung zulässig und jede Stützfläche mindestens s_min, Verschieben ändert weder Behälterzahl noch Stützflächen, ohne Regel und ohne Bedingung stimmt der Dekodierer mit Stück 9 überein
                  (gleiche Platzierungen), gemeinsames Skalieren.
"""

import random

import pytest

import stz_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=24, seed0=0, kante_hi=None):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        hi = kante_hi or cap
        kisten = tuple(tuple(rng.randint(1, min(hi, cap)) for _ in range(3)) for _ in range(n))
        yield cap, kisten, tuple(float(rng.randint(1, 5)) for _ in range(n))


def innen(p, q):
    return q[0] <= p[0] < q[0] + q[3] and q[1] <= p[1] < q[1] + q[4] and q[2] <= p[2] < q[2] + q[5]


def projektion(p, achse, davor):
    a, b = [k for k in range(3) if k != achse]
    kandidaten = [0]
    for q in davor:
        if q[achse] + q[3 + achse] <= p[achse] and q[a] <= p[a] < q[a] + q[3 + a] and q[b] <= p[b] < q[b] + q[3 + b]:
            kandidaten.append(q[achse] + q[3 + achse])
    return max(kandidaten)


def eckpunkte_neu(gesetzt, cap):
    """Alle Eckpunkte eines Behälters aus den gesetzten Quadern (in der Reihenfolge des Setzens), ohne eine laufende Menge: je Quader die drei Ecken und deren Projektionen gegen die Quader davor,
    dann alle Punkte streichen, die an die Wand stoßen oder in einem Quader liegen."""
    punkte = {(0, 0, 0)}
    for s, q in enumerate(gesetzt):
        x, y, z, w, d, h = q
        for p, achsen in (((x + w, y, z), (1, 2)), ((x, y + d, z), (0, 2)), ((x, y, z + h), (0, 1))):
            punkte.add(p)
            for a in achsen:
                r = list(p)
                r[a] = projektion(p, a, gesetzt[:s])
                punkte.add(tuple(r))
    return sorted((p for p in punkte if max(p) < cap and not any(innen(p, q) for q in gesetzt)), key=lambda p: (p[2], p[1], p[0]))


def stuetz_voxel(quader, gesetzt):
    """Anteil der Zellen (x, y) der Grundfläche, unter denen die Zelle (x, y, z - 1) von einem Quader der Liste belegt ist (am Boden: alle)."""
    x0, y0, z0, w, d, _h = quader
    if z0 == 0:
        return 1.0
    belegt = sum(1 for x in range(x0, x0 + w) for y in range(y0, y0 + d) if any(q[0] <= x < q[0] + q[3] and q[1] <= y < q[1] + q[4] and q[2] <= z0 - 1 < q[2] + q[5] for q in gesetzt))
    return belegt / (w * d)


def dekodierer_naiv(kisten, masse, order, cap, s_min, regel, fenster=5.0, schwelle=0.5):
    behaelter = []                                   # je Behälter: Liste (x, y, z, w, d, h) in der Reihenfolge des Setzens
    platz = []
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b, lst in enumerate(behaelter):
            kandidaten = []
            for (x, y, z) in eckpunkte_neu(lst, cap):
                k = (x, y, z, w, d, h)
                if x + w > cap or y + d > cap or z + h > cap or any(A._ueberlappt(k, q) for q in lst):
                    continue
                if s_min > 0 and stuetz_voxel(k, lst) < s_min - 1e-9:
                    continue
                if regel == A.KEINE:
                    kandidaten.append((0, (z, y, x), (x, y, z)))
                    continue
                gesamt = [(q, masse[j]) for q, j in zip(lst, [p[0] for p in platz if p[1] == b])] + [(k, masse[i])]
                m = sum(mm for _, mm in gesamt)
                cx = sum(mm * (q[0] + q[3] / 2) for q, mm in gesamt) / m
                cy = sum(mm * (q[1] + q[4] / 2) for q, mm in gesamt) / m
                volumen = sum(q[3] * q[4] * q[5] for q, _ in gesamt) / cap ** 3
                if regel == A.HART and volumen > schwelle and not (abs(cx - cap / 2) <= fenster + 1e-9 and abs(cy - cap / 2) <= fenster + 1e-9):
                    continue
                kandidaten.append(((cx - cap / 2) ** 2 + (cy - cap / 2) ** 2, (z, y, x), (x, y, z)))
            if kandidaten:
                wahl = (b, min(kandidaten)[2])
                break
        if wahl is None:
            behaelter.append([])
            wahl = (len(behaelter) - 1, (0, 0, 0))
        b, (x, y, z) = wahl
        behaelter[b].append((x, y, z, w, d, h))
        platz.append((i, b, x, y, z))
    return platz, behaelter


@pytest.mark.parametrize("s_min,regel", [(0.0, A.KEINE), (0.5, A.KEINE), (0.8, A.KEINE), (1.0, A.KEINE), (0.8, A.NAH), (0.0, A.NAH), (0.8, A.HART)])
def test_dekodierer_gegen_neu_erzeugte_eckpunkte_und_voxelstuetzflaeche(s_min, regel):
    geprueft = mehrere_behaelter = bedingung_wirkt = 0
    for cap, kisten, masse in list(instanzen(20, 1, 12, seed0=500)) + list(instanzen(20, 5, 14, cap_lo=12, seed0=600, kante_hi=7)):
        rng = random.Random(cap)
        for order in (A.reihenfolge(kisten, A.GRUNDFLAECHE), rng.sample(range(len(kisten)), len(kisten))):
            bins, platz, zustand = A.pack(kisten, masse, order, cap, s_min, regel, 3.0, 0.3)
            platz_naiv, behaelter = dekodierer_naiv(kisten, masse, order, cap, s_min, regel, 3.0, 0.3)
            assert platz == platz_naiv, (cap, kisten, masse, order)
            assert [list(z) for z in zustand] == [eckpunkte_neu(lst, cap) for lst in behaelter], (cap, kisten, order)
            geprueft += 1
            mehrere_behaelter += len(bins) >= 2
            bedingung_wirkt += platz != A.pack(kisten, masse, order, cap, 0.0, A.KEINE)[1]
    assert geprueft == 80 and mehrere_behaelter >= 20                                       # der Test prüft wirklich etwas
    if s_min > 0 or regel != A.KEINE:
        assert bedingung_wirkt >= 5


@pytest.mark.parametrize("s_min", (0.5, 0.8, 1.0))
def test_jede_stuetzflaeche_ist_mindestens_s_min_und_nach_dem_verschieben_unveraendert(s_min):
    for cap, kisten, masse in instanzen(30, 2, 16, cap_lo=10, cap_hi=40, seed0=700):
        for order in (A.reihenfolge(kisten, A.VOLUMEN), A.reihenfolge(kisten, A.GRUNDFLAECHE)):
            bins, platz, _ = A.pack(kisten, masse, order, cap, s_min, A.NAH)
            assert A.packung_pruefen(kisten, platz, cap) and len(bins) >= A.schranke(kisten, cap)
            assert A.stuetz_minimum(kisten, platz) >= s_min - 1e-9, (cap, kisten, s_min)
            neu, _ = A.verschieben(kisten, masse, platz, cap)
            assert A.packung_pruefen(kisten, neu, cap) and [A.stuetzflaeche(kisten, neu, i) for i in range(len(kisten))] == [A.stuetzflaeche(kisten, platz, i) for i in range(len(kisten))]


def test_schwerpunkt_gegen_das_voxelraster():
    for cap, kisten, masse in instanzen(25, 2, 12, seed0=900):
        platz = A.pack(kisten, masse, A.reihenfolge(kisten, A.VOLUMEN), cap, 0.5)[1]
        for b in range(1 + max(p[1] for p in platz)):
            sx = sy = m = 0.0
            for i, bb, x0, y0, _z in platz:
                if bb != b:
                    continue
                w, d, _h = kisten[i]
                zellen = w * d
                for x in range(x0, x0 + w):
                    for y in range(y0, y0 + d):
                        sx += masse[i] / zellen * (x + 0.5)
                        sy += masse[i] / zellen * (y + 0.5)
                m += masse[i]
            cx, cy, mm = A.schwerpunkt_behaelter(kisten, masse, platz, b)
            assert (cx, cy, mm) == pytest.approx((sx / m, sy / m, m)), (cap, kisten, b)


def verschieben_bruteforce(kisten, masse, platz, cap, b):
    lst = [(i, x, y) for i, bb, x, y, _z in platz if bb == b]
    x_lo, x_hi = min(x for _i, x, _y in lst), max(x + kisten[i][0] for i, x, _y in lst)
    y_lo, y_hi = min(y for _i, _x, y in lst), max(y + kisten[i][1] for i, _x, y in lst)
    m = sum(masse[i] for i, _, _ in lst)
    kand = []
    for dx in range(-x_lo, cap - x_hi + 1):
        for dy in range(-y_lo, cap - y_hi + 1):
            cx = sum(masse[i] * (x + dx + kisten[i][0] / 2) for i, x, _y in lst) / m
            cy = sum(masse[i] * (y + dy + kisten[i][1] / 2) for i, _x, y in lst) / m
            kand.append((max(abs(cx - cap / 2), abs(cy - cap / 2)), abs(dx) + abs(dy), (dx, dy)))
    return min(kand)


def test_verschieben_ist_in_jeder_achse_die_beste_ganzzahlige_verschiebung():
    """Der Abstand der Achse zur Mitte nach dem Verschieben ist so klein wie bei der Suche über alle ganzzahligen Verschiebungen (die Achsen sind unabhängig, die Rundung bei .5 geht nach oben)."""
    for cap, kisten, masse in instanzen(25, 1, 12, cap_lo=10, cap_hi=30, seed0=1100):
        platz = A.pack(kisten, masse, A.reihenfolge(kisten, A.GRUNDFLAECHE), cap, 0.0)[1]
        neu, v = A.verschieben(kisten, masse, platz, cap)
        for b in v:
            bester_abstand = verschieben_bruteforce(kisten, masse, platz, cap, b)[0]
            cx, cy, _ = A.schwerpunkt_behaelter(kisten, masse, neu, b)
            assert max(abs(cx - cap / 2), abs(cy - cap / 2)) == pytest.approx(bester_abstand), (cap, kisten, b)


def test_ohne_bedingung_und_regel_ist_der_dekodierer_stueck_9():
    """Mit s_min = 0 und ohne Regel gilt dieselbe Regel „tiefster, hinterster, linkester Punkt“ wie in Stück 9: jede Platzierung ist zulässig, und das Ergebnis ändert sich nicht, wenn die Massen ändern."""
    for cap, kisten, masse in instanzen(20, 1, 14, seed0=1300):
        order = A.reihenfolge(kisten, A.VOLUMEN)
        a = A.pack(kisten, masse, order, cap, 0.0, A.KEINE)
        b = A.pack(kisten, tuple(2.0 * x for x in masse), order, cap, 0.0, A.KEINE)
        assert a == b and A.packung_pruefen(kisten, a[1], cap)


def test_gemeinsames_skalieren_aendert_die_behaelterzahl_nicht():
    for cap, kisten, masse in instanzen(25, 1, 12, cap_lo=10, cap_hi=30, seed0=1500):
        gross = tuple(tuple(3 * x for x in k) for k in kisten)
        for s_min in (0.0, 0.8):
            for k in range(4):
                assert A.anzahl(gross, masse, k, 3 * cap, s_min) == A.anzahl(kisten, masse, k, cap, s_min), (cap, kisten, k, s_min)


def test_optimum_von_cpsat_mit_fenster_liegt_zwischen_dem_ohne_fenster_und_der_packung():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat, optimum_cpsat_fenster

    for cap, kisten, masse in instanzen(6, 3, 7, cap_lo=10, cap_hi=20, seed0=1900):
        ober = min(A.anzahl(kisten, masse, k, cap) for k in range(4))
        ohne = optimum_cpsat(kisten, cap, ober, 20.0, 2)
        mit = optimum_cpsat_fenster(kisten, masse, cap, ober + 2, max(1, cap // 10), 20.0, 2)
        assert 0 < A.schranke(kisten, cap) <= ohne <= mit, (cap, kisten, ohne, mit)
