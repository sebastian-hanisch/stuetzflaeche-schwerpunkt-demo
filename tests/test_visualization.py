"""3D-Darstellung: Die Dreiecke eines Quaders decken jede der sechs Seitenflächen lückenlos und ohne Überlappung ab; die Abbildung enthält genau die Quader, Eckpunkte, das Fenster und den Schwerpunkt, die
sie zeigen soll; die Farbe der Quader folgt der Stützfläche."""

import stz_algorithm as A
import stz_constants as C
import stz_evaluation as ev
import stz_visualization as V


def flaeche_dreieck(a, b, c):
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    kreuz = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return (kreuz[0] ** 2 + kreuz[1] ** 2 + kreuz[2] ** 2) ** 0.5 / 2


def test_dreiecke_decken_jede_seitenflaeche_genau_zweimal_halb_ab():
    w, d, h = 3, 5, 7
    e = V.ecken(0, 0, 0, w, d, h)
    seiten = {"unten": w * d, "oben": w * d, "vorn": w * h, "hinten": w * h, "links": d * h, "rechts": d * h}
    ebenen = {"unten": lambda p: p[2] == 0, "oben": lambda p: p[2] == h, "vorn": lambda p: p[1] == 0, "hinten": lambda p: p[1] == d, "links": lambda p: p[0] == 0, "rechts": lambda p: p[0] == w}
    summe, anzahl = {n: 0.0 for n in seiten}, {n: 0 for n in seiten}
    for t in V.DREIECKE:
        pts = [e[i] for i in t]
        in_ebenen = [n for n in seiten if all(ebenen[n](p) for p in pts)]
        assert len(in_ebenen) == 1, t
        anzahl[in_ebenen[0]] += 1
        summe[in_ebenen[0]] += flaeche_dreieck(*pts)
    assert len(V.DREIECKE) == 12
    for n, flaeche in seiten.items():
        assert anzahl[n] == 2 and abs(summe[n] - flaeche) < 1e-9, n


def test_dreiecke_einer_seite_ueberlappen_nicht_und_die_kanten_verbinden_benachbarte_ecken():
    for a in range(0, 12, 2):
        s1, s2 = set(V.DREIECKE[a]), set(V.DREIECKE[a + 1])
        assert len(s1 & s2) == 2 and len(s1 | s2) == 4
    e = V.ecken(0, 0, 0, 2, 3, 4)
    assert all(sum(1 for i in range(3) if e[a][i] != e[b][i]) == 1 for a, b in V.KANTEN) and len({frozenset(k) for k in V.KANTEN}) == 12


def test_stuetzfarbe_nach_den_stufen():
    assert [V.stuetz_farbe(x) for x in (1.0, 0.9, 0.8, 0.79, 0.5, 0.49, 0.01, 0.0)] == [C.STUETZ_FARBEN[0][1], C.STUETZ_FARBEN[1][1], C.STUETZ_FARBEN[1][1], C.STUETZ_FARBEN[2][1], C.STUETZ_FARBEN[2][1],
                                                                                       C.STUETZ_FARBEN[3][1], C.STUETZ_FARBEN[3][1], C.STUETZ_FARBEN[4][1]]
    assert len({f for _g, f, _t in C.STUETZ_FARBEN}) == 5


def test_abbildung_enthaelt_quader_rahmen_eckpunkte_fenster_und_schwerpunkt(mini):
    bins, platz, zustand = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10)
    fig = V.build_behaelter(mini.kisten, platz, 0, 10, zustand[0], 1, (4.6875, 3.8125), 1.0)
    meshes = [t for t in fig.data if t.type == "mesh3d"]
    assert len(meshes) == 4 and all(len(m.x) == 8 and len(m.i) == 12 for m in meshes)
    marker = [t for t in fig.data if t.type == "scatter3d" and t.mode == "markers"]
    rauten = [t for t in marker if t.marker.symbol == "diamond"]
    kreuz = [t for t in marker if t.marker.symbol == "cross"]
    assert len(rauten) == 1 and len(rauten[0].x) == len(zustand[0]) and len(kreuz) == 1 and (kreuz[0].x[0], kreuz[0].y[0], kreuz[0].z[0]) == (4.6875, 3.8125, 0)
    fenster = [t for t in fig.data if t.type == "scatter3d" and t.mode == "lines" and t.line.color == C.COLOR_FENSTER]
    assert len(fenster) == 1 and list(fenster[0].x) == [4.0, 6.0, 6.0, 4.0, 4.0] and list(fenster[0].y) == [4.0, 4.0, 6.0, 6.0, 4.0] and set(fenster[0].z) == {0}


def test_farbe_nach_stuetzflaeche_und_nach_reihenfolge(mini):
    bins, platz, zustand = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10)
    fig1 = V.build_behaelter(mini.kisten, platz, 0, 10, zustand[0], 1)
    farben = [t.color for t in fig1.data if t.type == "mesh3d"]
    assert farben == [C.STUETZ_FARBEN[0][1], C.STUETZ_FARBEN[0][1], C.STUETZ_FARBEN[0][1], C.STUETZ_FARBEN[3][1]]       # Quader 3 hat 43,75 %: orange, die anderen liegen am Boden: grün
    fig0 = V.build_behaelter(mini.kisten, platz, 0, 10, zustand[0], 0)
    assert [t.color for t in fig0.data if t.type == "mesh3d"] == list(C.KISTEN_FARBEN[:4])
    fig2 = V.build_behaelter(mini.kisten, platz[:3], 0, 10, zustand[0], 1, vollplatz=platz)
    assert [t.color for t in fig2.data if t.type == "mesh3d"] == [C.STUETZ_FARBEN[0][1]] * 3
    hover = [t.hovertext for t in fig1.data if t.type == "mesh3d"][3]
    assert "Stützfläche 44 %" in hover and "Quader 4" in hover


def test_abbildung_zeigt_nur_den_gewaehlten_behaelter(mini):
    bins, platz, zustand = A.pack(mini.kisten, mini.masse, [0, 1, 2, 3], 10, 1.0)           # [[0, 1, 2], [3]]
    assert len([t for t in V.build_behaelter(mini.kisten, platz, 0, 10, zustand[0], 1).data if t.type == "mesh3d"]) == 3
    assert len([t for t in V.build_behaelter(mini.kisten, platz, 1, 10, zustand[1], 1).data if t.type == "mesh3d"]) == 1


def test_leerer_behaelter_und_leerer_zustand_werfen_nicht():
    fig = V.build_behaelter((), [], 0, 10, (), 1)
    assert len([t for t in fig.data if t.type == "mesh3d"]) == 0 and len(fig.data) == 1


def test_messdiagramm_hat_je_schluessel_einen_balken_je_stuetzflaeche():
    m = {k: {si: float(k + si) for si in range(4)} for k in range(4)}
    fig = V.build_messung(m, "Titel")
    assert len(fig.data) == 4 and all(len(t.x) == 4 for t in fig.data)
    assert [t.name for t in fig.data] == [C.SCHLUESSEL_KURZ[k] for k in range(4)] and list(fig.data[1].y) == [1.0, 2.0, 3.0, 4.0] and list(fig.data[0].x) == [C.S_MIN_KURZ[si] for si in range(4)]
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_abbildung_zur_analyse_der_app():
    a = ev.analyse(ev.Settings())
    fig = V.build_behaelter(a.inst.kisten, a.platz, a.gezeigt, a.inst.cap, a.zustand[a.gezeigt], a.settings.farbe)
    assert len([t for t in fig.data if t.type == "mesh3d"]) == a.inst.n
