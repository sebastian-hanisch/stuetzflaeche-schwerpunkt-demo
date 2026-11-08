"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen (kleiner als nach Rundung auf zwei Stellen, Gleichstand) und jede genannte Zahl direkt."""

import stz_constants as C
import stz_evaluation as ev
from stz_scenario import Instance

V, G = C.VOLUMEN, C.GRUNDFLAECHE


def _tab(werte):
    """4 x 4 Tabelle (Schlüssel x Mindest-Stützfläche): werte = {(schluessel, s_index): Zahl}, sonst 5."""
    return tuple(tuple(werte.get((k, si), 5) for si in range(4)) for k in range(4))


def _a(schluessel=V, s_index=2, count=2, ohne=1, opt=1, tab=None, schranke=1, stuetz_min=0.8, unter80=0, schwebend=0, sp=(), regel=0, verschieben=0, fenster=5, n=12):
    inst = Instance(((5, 5, 5),) * n, (), 100)
    s = ev.Settings(schluessel=schluessel, s_index=s_index, regel=regel, verschieben=verschieben, fenster=fenster)
    return ev.Analysis(inst, tuple(range(n)), n, (), (), (), 0, count, ohne, 3, schranke, opt, tab or _tab({}), stuetz_min, unter80, schwebend, sp, sp, s)


def test_aktuell_ohne_bedingung_nennt_den_besten_schluessel_und_das_optimum():
    t = _tab({(V, 0): 1, (G, 0): 1})
    kind, text = ev.verdict_aktuell(_a(V, 0, 1, 1, 1, t))
    assert kind == "info"
    assert text == ("Nach dem Volumen sortiert und ohne Stützbedingung brauchen die Quader **1** Behälter. Das ist das Optimum ohne Stützbedingung (die Schranke allein ergäbe 1). "
                    "Das ist einer der besten Schlüssel dieser Instanz.")
    kind, text = ev.verdict_aktuell(_a(C.HOEHE, 0, 2, 2, None, t))
    assert "Ein Optimum ist für diese Instanz nicht berechnet; die Schranke ist 1." in text and "In der Tabelle ist Volumen oder Grundfläche besser (1)." in text


def test_aktuell_bedingung_kostet_ist_eine_warnung_und_nennt_den_besseren_schluessel():
    t = _tab({(V, 0): 1, (G, 0): 1, (V, 2): 2, (G, 2): 1})
    kind, text = ev.verdict_aktuell(_a(V, 2, 2, 1, 1, t))
    assert kind == "warning"
    assert text == ("Nach dem Volumen sortiert und mit mindestens 80 % Stützfläche gesetzt brauchen die Quader **2** Behälter, ohne Bedingung 1. Die Bedingung kostet hier 1. "
                    "Das Optimum ohne Stützbedingung ist **1** (die Schranke ist 1). Für diese Bedingung ist in der Tabelle Grundfläche besser (1).")


def test_aktuell_bedingung_kostet_nichts_und_bedingung_spart():
    t = _tab({(G, 2): 1})
    kind, text = ev.verdict_aktuell(_a(G, 2, 1, 1, 1, t))
    assert kind == "info" and "Die Bedingung kostet hier nichts." in text and "Für diese Bedingung ist das einer der besten Schlüssel dieser Instanz." in text and "Das ist das Optimum ohne Stützbedingung" in text
    kind, text = ev.verdict_aktuell(_a(G, 2, 1, 2, None, t))
    assert kind == "success" and "Die Bedingung spart hier 1 (die Platzierung der Quader ändert sich, die Reihenfolge nicht)." in text


def test_tabellenverdikt_drei_faelle():
    t = _tab({(V, 0): 1, (G, 0): 3, (V, 2): 4, (G, 2): 2})                       # ohne Bedingung Volumen, mit 80 % Grundfläche: disjunkt
    kind, text = ev.verdict_tabelle(_a(V, 2, 4, 1, 1, t))
    assert kind == "warning" and text == "Ohne Bedingung ist Volumen am besten (1 Behälter), mit 80 % Stützfläche Grundfläche (2). **Die Bedingung ändert den besten Schlüssel.**"
    t2 = _tab({(V, 0): 1, (G, 0): 1, (V, 2): 2, (G, 2): 1})                       # ohne beide, mit nur Grundfläche: schließt Volumen aus
    kind, text = ev.verdict_tabelle(_a(V, 2, 2, 1, 1, t2))
    assert kind == "info" and "Die Bedingung schließt Volumen als besten Schlüssel aus." in text
    t3 = _tab({(V, 0): 1, (V, 2): 1})
    kind, text = ev.verdict_tabelle(_a(V, 2, 1, 1, 1, t3))
    assert kind == "info" and text.endswith("Der beste Schlüssel bleibt.")
    kind, text = ev.verdict_tabelle(_a(V, 0, 1, 1, 1, t3))
    assert kind == "info" and text == "Ohne Bedingung ist in der Tabelle Volumen am besten (1 Behälter). Wählen Sie eine Mindest-Stützfläche, um zu sehen, ob sich das ändert."


def test_stuetz_verdikt_mit_und_ohne_bedingung():
    kind, text = ev.verdict_stuetz(_a(s_index=2, stuetz_min=0.875))
    assert kind == "success" and text == "Jeder Quader liegt auf mindestens 80 % seiner Grundfläche auf; die kleinste Stützfläche in dieser Packung ist **88 %**."
    kind, text = ev.verdict_stuetz(_a(s_index=0, stuetz_min=0.0, unter80=5, schwebend=2))
    assert kind == "warning" and text == ("Ohne Bedingung haben **5** von 12 Quadern weniger als 80 % Stützfläche, **2** schweben ohne jede Stütze; die kleinste Stützfläche ist 0 %. "
                                         "Solche Quader würden in der Wirklichkeit nicht stehen.")
    kind, text = ev.verdict_stuetz(_a(s_index=0, stuetz_min=0.5, unter80=1, schwebend=0))
    assert kind == "info" and "**1** von 12" in text and "**0** schweben" in text and "50 %" in text
    kind, text = ev.verdict_stuetz(_a(s_index=0, stuetz_min=0.9, unter80=0, schwebend=0))
    assert kind == "success"


def test_schwerpunktverdikt_drei_zweige_und_die_zahlen():
    behaelter = ((50.0, 50.0, 0.5, True), (60.0, 50.0, 0.4, False), (49.0, 51.0, 0.3, True))
    kind, text = ev.verdict_schwerpunkt(_a(sp=behaelter, regel=1, verschieben=1, fenster=5))
    assert kind == "info" and text == ("Von 3 Behältern liegen **2** mit dem Schwerpunkt im Fenster ±5 (Regel nah, verschoben). "
                                       "Die übrigen liegen außerhalb; mit anderer Regel oder mit Verschieben kann sich das ändern.")
    kind, text = ev.verdict_schwerpunkt(_a(sp=((50.0, 50.0, 0.5, True),), regel=0, verschieben=0, fenster=10))
    assert kind == "success" and text == "Von 1 Behältern liegen **1** mit dem Schwerpunkt im Fenster ±10 (Regel keine)."
    kind, text = ev.verdict_schwerpunkt(_a(sp=((70.0, 50.0, 0.5, False), (30.0, 50.0, 0.5, False))))
    assert kind == "warning" and "**0**" in text and "keinen harten Schwerpunkt" in text


# --- Messraster ----------------------------------------------------------------------------------------------------------------------------


def _mittel(werte):
    return {k: {si: werte.get((k, si), 1.0) for si in range(4)} for k in range(4)}


def _sp(**kw):
    basis = {"ueber": 1.0, "behaelter_je_instanz": 2.0, "im5": 10.0, "im10": 50.0, "schwelle": 0.0}
    return {name: {**basis, **kw.get(name, {})} for name in C.VARIANTEN}


def _z(werte=None, verteilung=0, n=40, sp=None, mehr=None):
    return {"verteilung": verteilung, "name": C.VERTEILUNG_LANG[verteilung], "n": n, "instanzen": 100, "mittel": _mittel(werte or {}),
            "mehr": mehr or {k: {1: 0, 2: 0, 3: 0} for k in range(4)}, "schwerpunkt": sp or _sp()}


def test_kosten_verdikt_nennt_alle_zahlen_und_den_zuwachs():
    z = _z({(V, 0): 1.18, (V, 1): 1.53, (V, 2): 1.73, (V, 3): 2.20, (G, 0): 1.42, (G, 1): 1.47, (G, 2): 1.58, (G, 3): 1.82})
    kind, text = ev.verdict_kosten(z)
    assert kind == "warning"
    assert text == ("Für mittlere Quader mit n = 40 brauchen die Quader über der Schranke (Mindest-Stützfläche 0 / 50 / 80 / 100 %): Volumen 1.18 / 1.53 / 1.73 / 2.20, Grundfläche 1.42 / 1.47 / 1.58 / 1.82 "
                    "Behälter (100 Instanzen). Von keiner Bedingung auf volle Auflage wächst der Bedarf mit dem Volumen um 1.02, mit der Grundfläche um 0.40. Die Stützbedingung kostet Behälter.")
    kind, text = ev.verdict_kosten(_z({}))
    assert kind == "info" and "kostet in dieser Zelle nichts" in text


def test_messung_verdikt_kippt_der_beste_schluessel():
    z = _z({(V, 0): 0.5, (G, 0): 0.8, (C.HOEHE, 0): 0.9, (C.LIEFERUNG, 0): 1.2, (V, 2): 1.5, (G, 2): 1.0, (C.HOEHE, 2): 1.7, (C.LIEFERUNG, 2): 2.0, (V, 1): 0.6, (G, 1): 0.9, (V, 3): 2.0, (G, 3): 1.2, (C.HOEHE, 1): 1.0, (C.LIEFERUNG, 1): 1.0, (C.HOEHE, 3): 1.8, (C.LIEFERUNG, 3): 2.5})
    kind, text = ev.verdict_messung(z)
    assert kind == "warning"
    assert text == ("Für mittlere Quader mit n = 40 ist der beste Schlüssel je Mindest-Stützfläche (Mittel über 100 Instanzen): 0 % Volumen, 50 % Volumen, 80 % Grundfläche, 100 % Grundfläche. "
                    "**Die Bedingung ändert den besten Schlüssel.**")
    kind, text = ev.verdict_messung(_z({(V, 0): 0.5, (V, 2): 0.7, (G, 2): 1.5}))
    assert kind == "info" and "der Schlüssel bleibt" not in text and "derselbe oder gleichauf" in text
    kind, text = ev.verdict_messung(_z({}))
    assert "0 % alle gleich, 50 % alle gleich, 80 % alle gleich, 100 % alle gleich" in text and kind == "info"


def test_messung_gleich_nach_rundung_ist_kein_kippen():
    z = _z({(V, 0): 0.500, (G, 0): 0.504, (V, 2): 0.9, (G, 2): 0.9})            # Volumen und Grundfläche liegen bei 0 % und bei 80 % jeweils gleichauf
    kind, text = ev.verdict_messung(z)
    assert kind == "info"


def test_schwerpunktraster_verdikt_prozente_und_der_zweig_100():
    sp = _sp(keine={"im5": 11.4, "im10": 54.0}, nah={"im5": 19.0, "im10": 60.0}, nah_verschoben={"im5": 68.4, "im10": 97.2})
    kind, text = ev.verdict_schwerpunkt_raster(_z(sp=sp))
    assert kind == "warning"
    assert text == ("Für mittlere Quader mit n = 40 liegen im Fenster ±5 ohne Regel 11 %, mit der Regel „nah“ 19 % und mit „nah“ und Verschieben 68 % der Behälter (im Fenster ±10 mit „nah“ und Verschieben 97 %). "
                    "Das ist **keine Garantie**: Wo die Ladung die ganze Breite oder Tiefe füllt oder schon an einer Wand anliegt, bleibt wenig oder nichts zu verschieben.")
    kind, text = ev.verdict_schwerpunkt_raster(_z(sp=_sp(nah_verschoben={"im5": 99.6, "im10": 100.0})))
    assert kind == "success" and "ein Fenster für alle Behälter" in text


def test_hart_verdikt_mehrbedarf_und_abdeckung():
    sp = _sp(nah={"ueber": 2.38}, hart_50={"ueber": 4.35, "schwelle": 30.3}, hart_75={"ueber": 2.40, "schwelle": 18.4})
    kind, text = ev.verdict_hart(_z(sp=sp))
    assert kind == "warning"
    assert text == ("Für mittlere Quader mit n = 40 braucht die harte Regel ab 50 % Füllung +1.97 Behälter gegenüber „nah“, ab 75 % +0.02; über der Schwelle liegen 30 % (50 %) beziehungsweise 18 % (75 %) "
                    "der Behälter, nur für diese gilt die Garantie. Die Garantie ist teuer und gilt nur für einen Teil der Behälter.")
    kind, text = ev.verdict_hart(_z(sp=_sp()))
    assert kind == "info" and "+0.00" in text and "kostet sie nichts" in text


def test_fensterorakel_verdikt():
    zeilen = [{"verteilung": 0, "n": 12, "instanzen": 40, "entschieden": 39, "offen": 1, "ohne": 1.5, "mit": 1.5, "gleich": 39, "mehr": 0},
              {"verteilung": 1, "n": 12, "instanzen": 40, "entschieden": 40, "offen": 0, "ohne": 1.5, "mit": 1.5, "gleich": 40, "mehr": 0}]
    kind, text = ev.verdict_fenster(zeilen)
    assert kind == "success"
    assert text == ("Mit freier Platzierung braucht das harte Schwerpunktfenster ±5 in **79** von 79 entschiedenen Instanzen genauso viele Behälter wie ohne Fenster und in 0 mehr "
                    "(ohne Stützbedingung, Quaderzahlen 12 und 20). Ohne Stützbedingung und bei 12 und 20 Quadern erlaubt die Aufgabe das Fenster also ohne Mehrkosten; mit Eckpunkten ist die Mitte oft nicht erreichbar. Mit Stützbedingung und bei mehr Quadern ist das nicht gemessen.")
    zeilen[1] = {**zeilen[1], "gleich": 39, "mehr": 1}
    kind, text = ev.verdict_fenster(zeilen)
    assert kind == "info" and "in **78** von 79" in text and "und in 1 mehr" in text and "kostet das Fenster Behälter" in text


def test_zeile_rechnet_mittel_anteile_und_zaehlungen_aus_den_summen():
    uebers = {str(k): {str(si): 4 * (k + si + 1) for si in range(4)} for k in range(4)}
    mehr = {str(k): {str(si): k + si for si in range(1, 4)} for k in range(4)}
    sp = {name: {"ueber": 8, "behaelter": 16, "im5": 4, "im10": 12, "schwelle": 2} for name in C.VARIANTEN}
    daten = {"instanzen": 4, "cap": 100, "zellen": {"mittel|20": {"ueber_schranke": uebers, "mehr_als_ohne": mehr, "schwerpunkt": sp}}}
    z = ev.zeile(0, 0, daten)
    assert z["mittel"][2][1] == 4 * 4 / 4 and z["mehr"][3][2] == 5 and z["n"] == 20 and z["instanzen"] == 4
    r = z["schwerpunkt"]["nah"]
    assert (r["ueber"], r["behaelter_je_instanz"], r["im5"], r["im10"], r["schwelle"]) == (2.0, 4.0, 25.0, 75.0, 12.5)
    assert ev.gerundet({0: {0: 1.005, 1: 2.0, 2: 3.0, 3: 4.0}, 1: {si: 0.0 for si in range(4)}, 2: {si: 0.0 for si in range(4)}, 3: {si: 0.0 for si in range(4)}})[0][1] == 2.0


def test_fensterzeilen_aus_den_gespeicherten_summen():
    daten = {"instanzen": 100, "fenster_optimum": {f"{name}|{n}": {"instanzen": C.FENSTER_OPT_N[n], "entschieden": 4, "offen": 1, "ohne": 6, "mit": 8, "gleich": 3, "mehr": 1}
                                                    for n in C.FENSTER_OPT_N for name, *_ in C.VERTEILUNGEN}}
    zeilen = ev.fenster_zeilen(daten)
    assert len(zeilen) == 8 and [(z["n"], z["verteilung"]) for z in zeilen] == [(12, 0), (12, 1), (12, 2), (12, 3), (20, 0), (20, 1), (20, 2), (20, 3)]
    assert zeilen[0]["ohne"] == 1.5 and zeilen[0]["mit"] == 2.0 and zeilen[0]["offen"] == 1 and zeilen[0]["gleich"] == 3
