"""Kern der Demo (nur Standardbibliothek): Schlüssel, Extreme Points mit Projektionen unter einer Mindest-Stützfläche, die Schwerpunktregeln, das starre Verschieben, Schranken und der unabhängige Prüfer.

Quader (Breite, Tiefe, Höhe), ohne Drehung, in Behälter der Kantenlänge `cap`, mit einer Masse je Quader. Jeder Quader kommt in den ersten Behälter, in dem ein Eckpunkt ihn aufnimmt (Stück 9),
und dort an den Eckpunkt, den die Regel wählt. Eine Packung ist eine Liste (Quader, Behälter, x, y, z) mit der linken hinteren unteren Ecke.

Zwei Bedingungen kommen zu Stück 9 hinzu:
  * Mindest-Stützfläche `s_min`: ein Eckpunkt ist nur zulässig, wenn der Quader dort auf mindestens diesem Anteil seiner Grundfläche aufliegt (auf dem Boden oder auf Oberseiten anderer Quader).
  * Schwerpunktregel: 0 keine (tiefster, hinterster, linkester zulässiger Punkt), 1 nah (unter den zulässigen Punkten des ersten Behälters, der einen hat, der Punkt, bei dem der Schwerpunkt des Behälters
    der Mitte der Grundfläche am nächsten liegt), 2 hart ab einer Füllschwelle (wie nah; aber sobald der Behälter nach dem Setzen mehr als `schwelle` seines Volumens füllt, muss der Schwerpunkt im
    Fenster liegen, sonst ist der Punkt unzulässig)."""

import math

LIEFERUNG, VOLUMEN, GRUNDFLAECHE, HOEHE = 0, 1, 2, 3
KEINE, NAH, HART = 0, 1, 2
EPS = 1e-9


# --- Schlüssel --------------------------------------------------------------------------------------------------------------------------------------


def schluessel_wert(kisten, schluessel: int) -> list:
    """Wert jedes Quaders unter dem Schlüssel (Lieferung: 0 für alle)."""
    if schluessel == LIEFERUNG:
        return [0] * len(kisten)
    f = {VOLUMEN: lambda k: k[0] * k[1] * k[2], GRUNDFLAECHE: lambda k: k[0] * k[1], HOEHE: lambda k: k[2]}[schluessel]
    return [f(k) for k in kisten]


def reihenfolge(kisten, schluessel: int) -> list:
    """Quadernummern, absteigend nach dem Schlüssel; Gleichstände bleiben in der Lieferreihenfolge (bei der Lieferung ist es die Lieferreihenfolge selbst)."""
    if schluessel == LIEFERUNG:
        return list(range(len(kisten)))
    werte = schluessel_wert(kisten, schluessel)
    return sorted(range(len(kisten)), key=lambda i: (-werte[i], i))


def reihenfolge_masse(kisten, masse) -> list:
    """Quadernummern nach fallender Masse (schwere zuerst); Gleichstände bleiben in der Lieferreihenfolge."""
    return sorted(range(len(kisten)), key=lambda i: (-masse[i], i))


# --- Geometrie --------------------------------------------------------------------------------------------------------------------------------------


def _ueberlappt(a, b) -> bool:
    """Zwei Quader (x, y, z, w, d, h) überlappen in einem Rauminhalt über null (Berührung zählt nicht)."""
    return a[0] < b[0] + b[3] and b[0] < a[0] + a[3] and a[1] < b[1] + b[4] and b[1] < a[1] + a[4] and a[2] < b[2] + b[5] and b[2] < a[2] + a[5]


def _pruefe_kisten(kisten, masse, cap: int):
    if len(masse) != len(kisten):
        raise ValueError("zu jedem Quader gehört genau eine Masse")
    for k in kisten:
        if len(k) != 3 or any(not isinstance(x, int) or x <= 0 or x > cap for x in k):
            raise ValueError(f"Quader {k!r} ungültig (drei ganze Maße, je 1 bis {cap})")
    if any(m <= 0 for m in masse):
        raise ValueError("Massen müssen positiv sein")


def packung_pruefen(kisten, platz, cap: int, vollstaendig: bool = True) -> bool:
    """Unabhängiger Prüfer: jeder Quader höchstens einmal (bei `vollstaendig` genau einmal), ganz im Behälter, keine zwei Quader eines Behälters überlappen."""
    nummern = sorted(p[0] for p in platz)
    if vollstaendig and nummern != list(range(len(kisten))):
        return False
    if len(set(nummern)) != len(nummern) or any(not 0 <= i < len(kisten) for i in nummern):
        return False
    je = {}
    for i, b, x, y, z in platz:
        w, d, h = kisten[i]
        if x < 0 or y < 0 or z < 0 or x + w > cap or y + d > cap or z + h > cap:
            return False
        je.setdefault(b, []).append((x, y, z, w, d, h))
    for lst in je.values():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                if _ueberlappt(lst[a], lst[c]):
                    return False
    return True


def schranken(kisten, cap: int):
    """(Volumenschranke, Zahl der großen Quader, Schranke): das Volumen aller Quader durch das Behältervolumen aufgerundet; die Zahl der Quader, die in allen drei Maßen über die Hälfte reichen
    (zwei solche überlappen in jedem Behälter über dem Mittelpunkt); das Größere von beiden."""
    volumen = -(-sum(w * d * h for w, d, h in kisten) // cap ** 3)
    gross = sum(1 for w, d, h in kisten if 2 * w > cap and 2 * d > cap and 2 * h > cap)
    return volumen, gross, max(volumen, gross)


def schranke(kisten, cap: int) -> int:
    return schranken(kisten, cap)[2]


# --- Stützfläche ------------------------------------------------------------------------------------------------------------------------------------


def _stuetz_gegen(quader, gesetzt) -> float:
    """Anteil der Grundfläche von `quader` (x, y, z, w, d, h), der auf dem Boden oder auf Oberseiten der Quader `gesetzt` aufliegt."""
    x, y, z, w, d, _h = quader
    if z == 0:
        return 1.0
    flaeche = 0
    for q in gesetzt:
        if q[2] + q[5] == z:
            flaeche += max(0, min(x + w, q[0] + q[3]) - max(x, q[0])) * max(0, min(y + d, q[1] + q[4]) - max(y, q[1]))
    return flaeche / (w * d)


def stuetzflaeche(kisten, platz, i: int) -> float:
    """Anteil der Grundfläche von Quader i, der auf dem Boden oder auf den Oberseiten anderer Quader desselben Behälters aufliegt (1,0 am Boden)."""
    _, b, x, y, z = next(p for p in platz if p[0] == i)
    andere = [(x2, y2, z2, *kisten[j]) for j, bb, x2, y2, z2 in platz if bb == b and j != i]
    return _stuetz_gegen((x, y, z, *kisten[i]), andere)


def stuetz_minimum(kisten, platz) -> float:
    """Kleinste Stützfläche aller Quader der Packung (1,0 bei leerer Packung)."""
    return min((stuetzflaeche(kisten, platz, p[0]) for p in platz), default=1.0)


def stuetz_kennzahlen(kisten, platz) -> tuple:
    """(Zahl der Quader mit Stützfläche unter 80 %, Zahl der Quader ohne jede Stütze). 80 % zählt nicht als darunter."""
    f = [stuetzflaeche(kisten, platz, p[0]) for p in platz]
    return sum(1 for s in f if s < 0.8), sum(1 for s in f if s == 0)


# --- Schwerpunkt ------------------------------------------------------------------------------------------------------------------------------------


def schwerpunkt_behaelter(kisten, masse, platz, behaelter: int):
    """(cx, cy, Gesamtmasse) des Behälters: Mittel der Mittelpunkte der Quader, gewichtet mit der Masse (x und y; z spielt hier keine Rolle). None bei leerem Behälter."""
    m = sx = sy = 0.0
    for i, b, x, y, _z in platz:
        if b == behaelter:
            m += masse[i]
            sx += masse[i] * (x + kisten[i][0] / 2)
            sy += masse[i] * (y + kisten[i][1] / 2)
    return None if m == 0 else (sx / m, sy / m, m)


def im_fenster(cx: float, cy: float, cap: int, fenster: float) -> bool:
    """Liegt der Schwerpunkt in x und y höchstens `fenster` von der Mitte der Grundfläche entfernt? Der Rand zählt dazu."""
    return abs(cx - cap / 2) <= fenster + EPS and abs(cy - cap / 2) <= fenster + EPS


def schwerpunkte(kisten, masse, platz, cap: int, fenster: float) -> list:
    """Je Behälter (cx, cy, Füllung als Anteil des Behältervolumens, im Fenster)."""
    out = []
    for b in range(1 + max((p[1] for p in platz), default=-1)):
        cx, cy, _m = schwerpunkt_behaelter(kisten, masse, platz, b)
        fuell = sum(kisten[i][0] * kisten[i][1] * kisten[i][2] for i, bb, *_ in platz if bb == b) / cap ** 3
        out.append((cx, cy, fuell, im_fenster(cx, cy, cap, fenster)))
    return out


def verschieben(kisten, masse, platz, cap: int):
    """Starres Verschieben: je Behälter alle Quader gemeinsam um dieselbe ganze Zahl in x und in y, so dass der Schwerpunkt der Mitte so nahe kommt, wie es die Hüllbox der Ladung erlaubt (die Quader
    bleiben im Behälter; Lage zueinander und Stützfläche ändern sich nicht). Gerundet wird auf die nächste ganze Zahl, bei .5 nach oben. Gibt (neue Platzierung, {Behälter: (dx, dy)}) zurück."""
    verschiebung = {}
    for b in range(1 + max((p[1] for p in platz), default=-1)):
        lst = [(i, x, y) for i, bb, x, y, _z in platz if bb == b]
        cx, cy, _m = schwerpunkt_behaelter(kisten, masse, platz, b)
        x_lo, x_hi = min(x for _i, x, _y in lst), max(x + kisten[i][0] for i, x, _y in lst)
        y_lo, y_hi = min(y for _i, _x, y in lst), max(y + kisten[i][1] for i, _x, y in lst)
        dx = max(-x_lo, min(cap - x_hi, math.floor(cap / 2 - cx + 0.5)))
        dy = max(-y_lo, min(cap - y_hi, math.floor(cap / 2 - cy + 0.5)))
        verschiebung[b] = (dx, dy)
    neu = [(i, b, x + verschiebung[b][0], y + verschiebung[b][1], z) for i, b, x, y, z in platz]
    return neu, verschiebung


# --- Extreme Points mit Stützfläche und Schwerpunktregel -------------------------------------------------------------------------------------


def _projiziere(p, achse: int, gesetzt):
    """Punkt p in negativer Richtung der Achse (0 x, 1 y, 2 z) bis zur nächsten Fläche eines gesetzten Quaders oder bis zur Wand schieben."""
    a, b = [k for k in (0, 1, 2) if k != achse]
    wert = 0
    for q in gesetzt:
        qa = q[achse] + q[3 + achse]
        if qa <= p[achse] and q[a] <= p[a] < q[a] + q[3 + a] and q[b] <= p[b] < q[b] + q[3 + b]:
            wert = max(wert, qa)
    r = list(p)
    r[achse] = wert
    return tuple(r)


def pack(kisten, masse, order, cap: int, s_min: float = 0.0, regel: int = KEINE, fenster: float = 5.0, schwelle: float = 0.5):
    """Packt die Quader in der Reihenfolge `order` (jeder höchstens einmal, auch ein Anfang der Reihenfolge ist erlaubt). Gibt (bins, platz, zustand) zurück: bins[b] = Quadernummern,
    platz = (Quader, Behälter, x, y, z), zustand[b] = die Eckpunkte (x, y, z) des Behälters nach dem letzten Quader, sortiert nach (z, y, x)."""
    order = list(order)
    if len(set(order)) != len(order) or any(not 0 <= i < len(kisten) for i in order):
        raise ValueError("die Reihenfolge darf jeden Quader höchstens einmal enthalten")
    if regel not in (KEINE, NAH, HART):
        raise ValueError(f"Regel {regel!r} unbekannt")
    if not 0 <= s_min <= 1:
        raise ValueError("die Mindest-Stützfläche liegt zwischen 0 und 1")
    _pruefe_kisten(kisten, masse, cap)
    behaelter = []          # je Behälter: {"punkte", "gesetzt", "m", "mx", "my", "v"}
    platz = []
    bins = []
    for i in order:
        w, d, h = kisten[i]
        m = masse[i]
        wahl = None
        for b, c in enumerate(behaelter):
            kandidaten = []
            for (x, y, z) in sorted(c["punkte"], key=lambda p: (p[2], p[1], p[0])):
                if x + w > cap or y + d > cap or z + h > cap:
                    continue
                k = (x, y, z, w, d, h)
                if any(_ueberlappt(k, q) for q in c["gesetzt"]):
                    continue
                if s_min > 0 and _stuetz_gegen(k, c["gesetzt"]) < s_min - EPS:
                    continue
                if regel == KEINE:
                    kandidaten.append((0, (z, y, x), (x, y, z)))
                    break
                mm = c["m"] + m
                cx, cy = (c["mx"] + m * (x + w / 2)) / mm, (c["my"] + m * (y + d / 2)) / mm
                if regel == HART and (c["v"] + w * d * h) / cap ** 3 > schwelle and not im_fenster(cx, cy, cap, fenster):
                    continue
                kandidaten.append(((cx - cap / 2) ** 2 + (cy - cap / 2) ** 2, (z, y, x), (x, y, z)))
            if kandidaten:
                wahl = (b, min(kandidaten)[2])
                break
        if wahl is None:
            behaelter.append({"punkte": {(0, 0, 0)}, "gesetzt": [], "m": 0.0, "mx": 0.0, "my": 0.0, "v": 0})
            bins.append([])
            wahl = (len(behaelter) - 1, (0, 0, 0))
        b, (x, y, z) = wahl
        c = behaelter[b]
        platz.append((i, b, x, y, z))
        bins[b].append(i)
        c["punkte"].discard((x, y, z))
        for p, achsen in (((x + w, y, z), (1, 2)), ((x, y + d, z), (0, 2)), ((x, y, z + h), (0, 1))):
            if max(p) < cap:
                c["punkte"].add(p)
            for a in achsen:
                q = _projiziere(p, a, c["gesetzt"])
                if max(q) < cap:
                    c["punkte"].add(q)
        c["gesetzt"].append((x, y, z, w, d, h))
        c["m"] += m
        c["mx"] += m * (x + w / 2)
        c["my"] += m * (y + d / 2)
        c["v"] += w * d * h
        c["punkte"] = {p for p in c["punkte"] if not any(q[0] <= p[0] < q[0] + q[3] and q[1] <= p[1] < q[1] + q[4] and q[2] <= p[2] < q[2] + q[5] for q in c["gesetzt"])}
    return bins, platz, [tuple(sorted(c["punkte"], key=lambda p: (p[2], p[1], p[0]))) for c in behaelter]


def anzahl(kisten, masse, schluessel: int, cap: int, s_min: float = 0.0, regel: int = KEINE, fenster: float = 5.0, schwelle: float = 0.5) -> int:
    """Behälterzahl der Packung aller Quader mit dem Schlüssel, der Mindest-Stützfläche und der Schwerpunktregel."""
    return len(pack(kisten, masse, reihenfolge(kisten, schluessel), cap, s_min, regel, fenster, schwelle)[0])
