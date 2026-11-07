"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (stz_precomputed.json): jede Zelle bei n = 20 frisch gerechnet, bei allen Zellen die ersten drei Instanzen einzeln (Stichprobe in der Datei); alle Zellen vollständig prüft
  `python generate_precomputed.py --check` (parallel). Das Orakel mit Schwerpunktfenster wird an einer Stichprobe der Instanzen mit CP-SAT noch einmal gerechnet.
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from pathlib import Path

import pytest

import stz_algorithm as A
import stz_constants as C
import stz_evaluation as ev
from stz_scenario import beispiel, mess_seed, zufallsinstanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))
V, G, H, L = C.VOLUMEN, C.GRUNDFLAECHE, C.HOEHE, C.LIEFERUNG


def alle():
    return {(v, ni): ev.zeile(v, ni) for v, ni in ZELLEN}


def gerundete():
    return {k: ev.gerundet(z["mittel"]) for k, z in alle().items()}


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 100 and daten["cap"] == C.CAP == 100
    assert set(daten["zellen"]) == {ev.zelle_schluessel(v, ni) for v, ni in ZELLEN} and len(ZELLEN) == 12
    assert set(daten["stichprobe"]) == set(daten["zellen"])
    assert set(daten["fenster_optimum"]) == {f"{name}|{n}" for n in C.FENSTER_OPT_N for name, *_x in C.VERTEILUNGEN}
    for z in daten["zellen"].values():
        assert set(z["schwerpunkt"]) == set(C.VARIANTEN)


def _addiere(a, b):
    if isinstance(a, dict):
        return {k: _addiere(a[k], b[k]) for k in a}
    return a + b


def _nicht_kleiner(a, b):
    if isinstance(a, dict):
        return all(_nicht_kleiner(a[k], b[k]) for k in a)
    return a >= b


@pytest.mark.parametrize("v", range(len(C.VERTEILUNGEN)))
def test_jede_zelle_bei_n_20_stimmt_mit_frischer_rechnung(v):
    ni = C.MESS_N.index(20)
    assert ev.messzelle(v, ni) == ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_stichprobe_jeder_zelle_stimmt_mit_frischer_rechnung(v, ni):
    schl = ev.zelle_schluessel(v, ni)
    daten = ev.vorberechnet()
    summe = None
    for j in C.STICHPROBE_J:
        gespeichert = daten["stichprobe"][schl][str(j)]
        assert ev.messzelle(v, ni, [j]) == gespeichert, (schl, j)
        summe = gespeichert if summe is None else {k: _addiere(summe[k], gespeichert[k]) for k in gespeichert}
    zelle = daten["zellen"][schl]
    for k in summe:                          # die Stichprobe ist Teil der Zelle: jede Summe der Zelle ist mindestens so groß (alle Beiträge sind nicht negativ)
        assert _nicht_kleiner(zelle[k], summe[k]), (schl, k)


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_summen_sind_in_sich_stimmig(v, ni):
    z = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    k = C.INSTANZEN
    for kk in "0123":
        zahlen = [z["ueber_schranke"][kk][s] for s in "0123"]
        assert min(zahlen) >= 0 and all(0 <= z["mehr_als_ohne"][kk][s] <= k for s in "123")
    sp = z["schwerpunkt"]
    for name, r in sp.items():
        assert 0 <= r["im5"] <= r["im10"] <= r["behaelter"] and r["ueber"] >= 0 and 0 <= r["schwelle"] <= r["behaelter"]
        if not C.VARIANTEN[name][2]:
            assert r["schwelle"] == 0
    assert sp["keine"]["behaelter"] == sp["keine_verschoben"]["behaelter"] and sp["nah"]["ueber"] == sp["nah_verschoben"]["ueber"]          # das Verschieben ändert die Behälterzahl nicht
    assert sp["keine_verschoben"]["im5"] >= sp["keine"]["im5"] and sp["nah_verschoben"]["im5"] >= sp["nah"]["im5"]                          # und kann den Schwerpunkt nur verbessern


def test_fensterorakel_in_sich_stimmig_und_stichprobe_mit_cpsat():
    pytest.importorskip("ortools")
    from generate_precomputed import fenster_instanz

    daten = ev.vorberechnet()["fenster_optimum"]
    for n in sorted(C.FENSTER_OPT_N):
        for v, (name, *_x) in enumerate(C.VERTEILUNGEN):
            z = daten[f"{name}|{n}"]
            assert z["instanzen"] == C.FENSTER_OPT_N[n] and z["entschieden"] + z["offen"] == z["instanzen"] and z["gleich"] + z["mehr"] == z["entschieden"] and z["ohne"] >= z["entschieden"]
            assert z["mit"] >= z["ohne"]
            for j in range(2 if n == 20 else 3):
                ohne, mit = fenster_instanz(v, n, j)
                assert ohne >= 1 and mit == ohne, (name, n, j)                      # das Fenster kostet in der Stichprobe keinen Behälter


# --- Beispiele ------------------------------------------------------------------------------------------------------------------------------------


def test_beispiele_sind_zufallsinstanzen_mit_dem_optimum_von_cpsat():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    for b, (v, seed) in enumerate(((0, 5_000_034), (1, 5_001_173))):
        inst = zufallsinstanz(v, 12, seed)
        assert inst.kisten == beispiel(b).kisten and inst.masse == beispiel(b).masse
        ober = min(A.anzahl(inst.kisten, inst.masse, k, inst.cap) for k in range(4))
        assert ober == 1 == optimum_cpsat(inst.kisten, inst.cap, ober, 60.0, 2) == C.BEISPIEL_OPTIMUM[b]


def test_beispiel_tabellen_in_der_readme():
    t1, t2 = ev.tabelle(beispiel(0)), ev.tabelle(beispiel(1))
    assert [list(r) for r in t1] == [[2, 2, 2, 2], [1, 1, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]
    assert [list(r) for r in t2] == [[2, 2, 2, 2], [1, 1, 1, 1], [1, 1, 1, 1], [1, 2, 2, 2]]
    assert "Ohne Bedingung braucht das Volumen **1** Behälter, mit 80 % Stützfläche **2**; die Grundfläche bleibt bei **1**" in README
    assert "Lieferung und Höhe brauchen mit jeder Bedingung 2" in README and "Beispiel 1 (zwölf Quader, Optimum 1)" in README and "Beispiel 2 (zwölf andere Quader, Optimum 1)" in README
    assert "bei (47,0 / 40,0), mit „nah“ bei (47,3 / 41,6), ohne Regel verschoben bei (47,0 / 42,0): überall außerhalb des Fensters ±5. **Mit „nah“ und Verschieben** liegt er bei (47,3 / 49,6): im Fenster" in README


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def test_kosten_der_stuetzbedingung():
    g = gerundete()
    zuwachs = {k: [round(sum(x[k][si] - x[k][0] for x in g.values()) / len(g), 2) for si in (1, 2, 3)] for k in (V, G)}
    assert zuwachs == {V: [0.42, 1.23, 2.69], G: [0.36, 0.5, 1.15]}
    assert "mit dem Volumen **+0,42 / +1,23 / +2,69** Behälter bei einer Mindest-Stützfläche von 50 / 80 / 100 %, mit der Grundfläche **+0,36 / +0,50 / +1,15**" in README
    flach80 = g[(3, 2)][V]
    assert [flach80[si] for si in range(4)] == [2.19, 3.69, 6.33, 12.58] and "n = 80, Volumen: 2,19 → 3,69 / 6,33 / 12,58" in README
    assert max(g, key=lambda k: g[k][V][3] - g[k][V][0]) == (3, 2)                       # flache Quader bei n = 80 zahlen am meisten


def test_bester_schluessel_je_stuetzflaeche():
    g = gerundete()

    def zaehlung(si):
        alleine, gleichauf = {}, []
        for zelle, x in g.items():
            beste = ev.beste_schluessel_zelle(x, si)
            if len(beste) == 1:
                alleine[beste[0]] = alleine.get(beste[0], 0) + 1
            else:
                gleichauf.append((zelle, beste))
        return alleine, gleichauf

    assert zaehlung(0) == ({V: 10}, [((2, 0), [0, 1, 2, 3]), ((2, 2), [V, H])])
    a1, gl1 = zaehlung(1)
    assert a1 == {V: 8, G: 1, H: 1} and [z for z, _ in gl1] == [(3, 0), (3, 1)]
    assert zaehlung(2) == ({G: 12}, []) and zaehlung(3) == ({G: 12}, [])
    assert "ist das Volumen in **10** von 12 Zellen allein der beste Schlüssel (zwei Zellen mit kleinen Quadern gleichauf mit anderen); mit 80 % und mit 100 % ist es die **Grundfläche in allen 12** Zellen. Bei 50 % ist es gemischt (Volumen allein in 8)" in README
    assert all(x[G][2] < x[V][2] for x in g.values())                                   # bei 80 % ist die Grundfläche in jeder Zelle besser als das Volumen


def test_instanz_fuer_instanz_zaehlungen():
    z = alle()
    bei80 = {k: sum(x["mehr"][k][2] for x in z.values()) for k in range(4)}
    bei100 = {k: sum(x["mehr"][k][3] for x in z.values()) for k in range(4)}
    assert (bei80[V], bei80[G], bei100[V], bei100[G]) == (814, 512, 1073, 746) and sum(C.INSTANZEN for _ in z) == 1200
    assert "Von 1200 Instanzen braucht die Mindest-Stützfläche 80 % mit dem Volumen in **814** mehr Behälter als ohne Bedingung, mit der Grundfläche in **512**; bei 100 % in 1073 beziehungsweise 746" in README


def test_schwerpunkt_regeln_und_verschieben():
    z = alle()
    sp = lambda name, art: [round(x["schwerpunkt"][name][art]) for x in z.values()]       # noqa: E731
    assert (min(sp("keine", "im5")), max(sp("keine", "im5"))) == (1, 50) and (min(sp("nah", "im5")), max(sp("nah", "im5"))) == (1, 95)
    assert (z[(2, 0)]["schwerpunkt"]["keine"]["im5"], z[(2, 0)]["schwerpunkt"]["nah"]["im5"]) == pytest.approx((38.0, 95.0), abs=0.5) and [round(z[(3, ni)]["schwerpunkt"]["nah"]["im5"]) for ni in range(3)] == [1, 2, 3]
    unterschied = [round(round(x["schwerpunkt"]["nah"]["ueber"], 2) - round(x["schwerpunkt"]["keine"]["ueber"], 2), 2) for x in z.values()]
    assert (min(unterschied), max(unterschied)) == (-0.22, 0.07)
    assert (min(sp("nah_verschoben", "im5")), max(sp("nah_verschoben", "im5"))) == (44, 100) and (min(sp("nah_verschoben", "im10")), max(sp("nah_verschoben", "im10"))) == (69, 100)
    assert "Sie bringt **1 bis 95 %** der Behälter ins Fenster ±5 (ohne Regel 1 bis 50 %): am meisten bei kleinen Quadern (n = 20: 38 → 95 %), kaum bei flachen (1 bis 3 %). Sie ändert die Behälterzahl um −0,22 bis +0,07" in README
    assert "Mit „nah“ und Verschieben liegen **44 bis 100 %** der Behälter im Fenster ±5 und **69 bis 100 %** im Fenster ±10" in README
    assert all(x["schwerpunkt"]["nah_verschoben"]["ueber"] == x["schwerpunkt"]["nah"]["ueber"] for x in z.values()) and "Es kostet **keinen** Behälter" in README


def test_schwere_zuerst_hilft_nicht():
    z = alle()
    mehr = [round(round(x["schwerpunkt"]["nah_masse"]["ueber"], 2) - round(x["schwerpunkt"]["nah"]["ueber"], 2), 2) for x in z.values()]
    assert min(mehr) == 0.16 and max(mehr) == 2.55 and all(m > 0 for m in mehr)
    besser = max(x["schwerpunkt"]["nah_masse"]["im5"] - x["schwerpunkt"]["nah"]["im5"] for x in z.values())
    assert besser <= 1.0
    assert "Der Schlüssel Masse (mit „nah“) braucht in allen 12 Zellen mehr Behälter als die Grundfläche (+0,16 bis +2,55) und bringt den Anteil im Fenster nirgends um mehr als 1 Prozentpunkt nach oben" in README


def test_harte_regel_ab_der_fuellschwelle():
    z = alle()
    mehr50 = [round(round(x["schwerpunkt"]["hart_50"]["ueber"], 2) - round(x["schwerpunkt"]["nah"]["ueber"], 2), 2) for x in z.values()]
    mehr75 = [round(round(x["schwerpunkt"]["hart_75"]["ueber"], 2) - round(x["schwerpunkt"]["nah"]["ueber"], 2), 2) for x in z.values()]
    assert max(mehr50) == 1.89 and list(z)[mehr50.index(1.89)] == (0, 2) and min(mehr50) == 0.0 and max(mehr75) == 0.05
    s50 = [round(x["schwerpunkt"]["hart_50"]["schwelle"]) for x in z.values()]
    s75 = [round(x["schwerpunkt"]["hart_75"]["schwelle"]) for x in z.values()]
    assert (min(s50), max(s50), min(s75), max(s75)) == (0, 46, 0, 20)
    assert "Ab 50 % Füllung kostet die harte Regel bis zu **+1,89** Behälter gegenüber „nah“ (mittlere Quader, n = 80), und die Garantie gilt nur für die 0 bis 46 % der Behälter über der Schwelle; ab 75 % sind es höchstens +0,05 und 0 bis 20 % der Behälter" in README


def test_orakel_mit_hartem_fenster_in_der_readme():
    zeilen = ev.fenster_zeilen()
    assert len(zeilen) == 8
    entschieden, offen, gleich, mehr = (sum(r[k] for r in zeilen) for k in ("entschieden", "offen", "gleich", "mehr"))
    assert (entschieden, offen, gleich, mehr) == (236, 4, 236, 0) and sum(r["instanzen"] for r in zeilen) == 240
    assert "in **236 von 236** entschiedenen Instanzen genauso viele Behälter wie ohne Fenster (4 von 240 nicht entschieden)" in README
    assert ev.verdict_fenster(zeilen)[0] == "success" and all(abs(r["ohne"] - r["mit"]) < 1e-12 for r in zeilen)


# --- Tabellen der README -------------------------------------------------------------------------------------------------------------------


def test_readme_tabellen_geben_jede_zeile_wieder():
    from dev.readme_bauen import tabellen

    for tabelle in tabellen():
        for zeile in tabelle.split("\n"):
            assert zeile in README, zeile


# --- Texte ---------------------------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"Behälter {C.CAP} mal {C.CAP} mal {C.CAP}" in t and f"{C.INSTANZEN} Instanzen" in t and "(20, 40, 80)" in t and "30 Sekunden Zeitlimit" in t and "bei 12 und 20 Quadern" in t
    assert C.MESS_N == (20, 40, 80) and C.CPSAT_ZEIT == 30.0 and C.FENSTER_OPT_N == {12: 40, 20: 20} and C.FENSTER_OPT_ZEIT == {12: 20.0, 20: 30.0}


def test_readme_nennt_die_verteilungen_und_das_raster_wie_der_code():
    assert "*mittel* (alle Kanten 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *flach* (Breite und Tiefe 30 bis 80, Höhe 5 bis 30)" in README
    assert [vt[2] for vt in C.VERTEILUNGEN] == [((20, 60),) * 3, ((5, 70),) * 3, ((10, 40),) * 3, ((30, 80), (30, 80), (5, 30))]
    assert "vier Verteilungen × drei Quaderzahlen (20, 40, 80) × **100 feste Instanzen** je Zelle × vier Schlüssel × vier Werte der Mindest-Stützfläche" in README
    assert "bei 12 Quadern 40, bei 20 Quadern 20 Instanzen je Verteilung (eigene Seeds), CP-SAT mit 20 beziehungsweise 30 Sekunden Zeitlimit je Instanz, Fenster ±5" in README
    assert C.S_MIN_WERTE == (0.0, 0.5, 0.8, 1.0) and C.FENSTER_RASTER == (5, 10) and C.SCHWELLEN == (0.5, 0.75)


def test_readme_hat_keine_offenen_platzhalter_ausser_dem_live_link():
    ohne_link = README.replace("<!-- TODO nach dem Deploy", "")
    assert "{{" not in README and "TESTZAHL" not in README and ohne_link.count("TODO") == 0
