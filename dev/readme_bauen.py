"""Setzt die README zusammen: Tabellen und Text der Annahmen kommen aus denselben Funktionen wie in der App (nur zum Schreiben der README, nicht Teil der Laufzeit).

    python dev/readme_bauen.py [ANZAHL_TESTS]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import stz_constants as C  # noqa: E402
import stz_evaluation as ev  # noqa: E402
from stz_scenario import beispiel  # noqa: E402


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def zellen():
    return [(v, ni) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]


def tabellen():
    """(A, B, C, D, Beispiel 1, Beispiel 2): A = Behälter über der Schranke je Zelle (Volumen und Grundfläche, Mindest-Stützfläche 0 / 50 / 80 / 100 %), B = Anteil der Behälter im Fenster je Variante,
    C = Orakel mit hartem Fenster, D = die harte Regel ab Füllschwelle, die Beispiele = Behälterzahlen je Schlüssel und Mindest-Stützfläche."""
    ta = ["| Verteilung | n | Volumen 0 / 50 / 80 / 100 % | Grundfläche 0 / 50 / 80 / 100 % |", "|---|---|---|---|"]
    tb = ["| Verteilung | n | keine Regel ±5 | nah ±5 | keine, verschoben ±5 | nah, verschoben ±5 | nah, verschoben ±10 |", "|---|---|---|---|---|---|---|"]
    td = ["| Verteilung | n | nah: Behälter über Schranke | hart ab 50 %: Behälter über Schranke | davon über der Schwelle | hart ab 75 %: Behälter über Schranke | davon über der Schwelle |",
          "|---|---|---|---|---|---|---|"]
    for v, ni in zellen():
        z = ev.zeile(v, ni)
        n = C.MESS_N[ni]
        ta.append(f"| {C.VERTEILUNG_KURZ[v]} | {n} | " + " / ".join(de(z["mittel"][C.VOLUMEN][si]) for si in ev.S_LISTE) + " | " + " / ".join(de(z["mittel"][C.GRUNDFLAECHE][si]) for si in ev.S_LISTE) + " |")
        sp = z["schwerpunkt"]
        tb.append(f"| {C.VERTEILUNG_KURZ[v]} | {n} | {sp['keine']['im5']:.0f} % | {sp['nah']['im5']:.0f} % | {sp['keine_verschoben']['im5']:.0f} % | {sp['nah_verschoben']['im5']:.0f} % | "
                  f"{sp['nah_verschoben']['im10']:.0f} % |")
        td.append(f"| {C.VERTEILUNG_KURZ[v]} | {n} | {de(sp['nah']['ueber'])} | {de(sp['hart_50']['ueber'])} | {sp['hart_50']['schwelle']:.0f} % | {de(sp['hart_75']['ueber'])} | {sp['hart_75']['schwelle']:.0f} % |")
    tc = ["| Verteilung | n | entschiedene Instanzen | Optimum ohne Fenster | Optimum mit Fenster ±5 | gleich viele Behälter |", "|---|---|---|---|---|---|"]
    for r in ev.fenster_zeilen():
        offen = f", {r['offen']} offen" if r["offen"] else ""
        tc.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} | {r['n']} | {r['entschieden']} von {r['instanzen']}{offen} | {de(r['ohne'])} | {de(r['mit'])} | {r['gleich']} von {r['entschieden']} |")
    bsp = []
    for b in (0, 1):
        t = ev.tabelle(beispiel(b))
        zeilen = ["| Schlüssel | " + " | ".join(C.S_MIN_KURZ[si] for si in ev.S_LISTE) + " |", "|---|---|---|---|---|"]
        for k in ev.SCHLUESSEL_LISTE:
            zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(str(t[k][si]) for si in ev.S_LISTE) + " |")
        bsp.append("\n".join(zeilen))
    return "\n".join(ta), "\n".join(tb), "\n".join(tc), "\n".join(td), bsp[0], bsp[1]


if __name__ == "__main__":
    vorlage = (ROOT / "dev" / "readme_vorlage.md").read_text(encoding="utf-8")
    ta, tb, tc, td, b1, b2 = tabellen()
    anzahl = sys.argv[1] if len(sys.argv) > 1 else "TESTZAHL"
    text = (vorlage.replace("{{TABELLE_A}}", ta).replace("{{TABELLE_B}}", tb).replace("{{TABELLE_C}}", tc).replace("{{TABELLE_D}}", td).replace("{{BEISPIEL_1}}", b1).replace("{{BEISPIEL_2}}", b2)
            .replace("{{ANNAHMEN}}", C.ASSUMPTIONS_MARKDOWN).replace("{{TESTS}}", anzahl))
    (ROOT / "README.md").write_text(text, encoding="utf-8")
    print("README.md geschrieben")
