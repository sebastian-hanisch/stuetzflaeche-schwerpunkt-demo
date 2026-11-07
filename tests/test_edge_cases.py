"""Randfälle: leere Eingabe, ein Quader, Quader gleich Behälter, Verschieben ohne Spielraum, Fensterrand, Gleichstände, Schritte, ungültige Eingaben, Grenzen der Regler."""

import pytest

import stz_algorithm as A
import stz_constants as C
import stz_evaluation as ev
from stz_scenario import Instance, massen_aus, mess_seed, zufallsinstanz


def test_leere_eingabe_ergibt_keine_behaelter():
    assert A.pack((), (), [], 10) == ([], [], [])
    assert A.schranken((), 10) == (0, 0, 0) and A.stuetz_kennzahlen((), []) == (0, 0) and A.stuetz_minimum((), []) == 1.0
    assert A.schwerpunkte((), (), [], 10, 5) == [] and A.verschieben((), (), [], 10) == ([], {})


@pytest.mark.parametrize("regel", (A.KEINE, A.NAH, A.HART))
@pytest.mark.parametrize("s_min", (0.0, 0.8, 1.0))
def test_ein_quader_und_quader_gleich_behaelter(regel, s_min):
    bins, platz, _ = A.pack(((7, 3, 5),), (2.0,), [0], 10, s_min, regel)
    assert bins == [[0]] and platz == [(0, 0, 0, 0, 0)]
    bins, platz, _ = A.pack(((10, 10, 10), (1, 1, 1)), (5.0, 1.0), [0, 1], 10, s_min, regel)
    assert bins == [[0], [1]] and platz == [(0, 0, 0, 0, 0), (1, 1, 0, 0, 0)]


def test_verschieben_ohne_spielraum_aendert_nichts_und_mit_spielraum_ist_begrenzt():
    voll = ((10, 10, 3), (4, 4, 3))                         # Quader 0 füllt die Grundfläche: kein Spielraum
    platz = [(0, 0, 0, 0, 0), (1, 0, 0, 0, 3)]
    neu, v = A.verschieben(voll, (1.0, 9.0), platz, 10)
    assert v == {0: (0, 0)} and neu == platz
    klein = ((2, 2, 2),)                                    # ein Quader in der Ecke: der Schwerpunkt kommt in die Mitte (5), 4 von der Ecke weg: dx = 4
    neu, v = A.verschieben(klein, (1.0,), [(0, 0, 0, 0, 0)], 10)
    assert v == {0: (4, 4)} and neu == [(0, 0, 4, 4, 0)] and A.schwerpunkt_behaelter(klein, (1.0,), neu, 0)[:2] == (5.0, 5.0)
    rand = ((2, 2, 2),)                                     # Quader schon ganz am anderen Rand: der Spielraum ist nach links begrenzt
    neu, v = A.verschieben(rand, (1.0,), [(0, 0, 8, 8, 0)], 10)
    assert v == {0: (-4, -4)} and neu == [(0, 0, 4, 4, 0)]


def test_verschieben_wirkt_je_behaelter_und_laesst_die_quader_im_behaelter():
    kisten = ((2, 2, 2), (3, 3, 3))
    platz = [(0, 0, 0, 0, 0), (1, 1, 7, 7, 0)]
    neu, v = A.verschieben(kisten, (1.0, 1.0), platz, 10)
    assert v == {0: (4, 4), 1: (-3, -3)} and neu == [(0, 0, 4, 4, 0), (1, 1, 4, 4, 0)] and A.packung_pruefen(kisten, neu, 10)          # Quader 1: Mitte 8,5, -3,5 wird bei .5 nach oben zu -3


def test_fensterrand_zaehlt_dazu_und_die_gleitkommatoleranz_haelt():
    assert A.im_fenster(55.0, 45.0, 100, 5) and not A.im_fenster(55.01, 50.0, 100, 5) and A.im_fenster(50.0, 50.0, 100, 0)
    assert A.im_fenster(0.1 + 0.2 + 49.7, 50.0, 100, 0)                                   # 50,0000000000000x: durch EPS im Fenster der Breite 0


def test_gleichstaende_der_schluessel_bleiben_in_lieferreihenfolge():
    kisten = ((3, 3, 3), (3, 3, 3), (1, 1, 1), (3, 3, 3))
    for schluessel in (A.VOLUMEN, A.GRUNDFLAECHE, A.HOEHE):
        assert A.reihenfolge(kisten, schluessel) == [0, 1, 3, 2]


def test_ungueltige_instanzen_werden_abgelehnt():
    for kisten in (((0, 3, 3),), ((11, 3, 3),), ((3, 3),), ((3.5, 2, 2),), ((3, 3, 3, 3),)):
        with pytest.raises(ValueError):
            Instance(kisten, (1.0,), 10)
    with pytest.raises(ValueError):
        Instance(((1, 1, 1),), (1.0,), 0)
    with pytest.raises(ValueError):
        Instance(((1, 1, 1),), (1.0, 2.0), 10)
    with pytest.raises(ValueError):
        Instance(((1, 1, 1),), (0.0,), 10)
    assert Instance(((1, 1, 1), (2, 2, 2)), (), 10).masse == (1.0, 1.0)                  # ohne Massen: jede Masse 1


def test_massen_sind_deterministisch_positiv_und_unabhaengig_von_den_massen_der_kisten():
    kisten = zufallsinstanz(0, 20, 123).kisten
    m = massen_aus(kisten, 123)
    assert m == massen_aus(kisten, 123) and all(x >= 0.1 for x in m) and all(round(x, 1) == x for x in m)
    assert zufallsinstanz(0, 20, 123).masse == m and zufallsinstanz(0, 20, 124).kisten != kisten
    for (w, d, h), x in zip(kisten, m):
        assert w * d * h / 1000 * 0.5 - 0.06 <= x <= w * d * h / 1000 * 2.0 + 0.06 or x == 0.1


def test_analyse_an_den_grenzen_der_regler():
    for quelle in C.QUELLEN:
        for n_index in range(len(C.N_WERTE)):
            for seed in (0, C.SEED_MAX):
                for schritt in (0, 1, 12, 13, 200):
                    a = ev.analyse(ev.Settings(quelle, n_index, seed, C.VOLUMEN, 2, 1, 1, C.FENSTER_MIN, schritt, 50, 1))
                    assert A.packung_pruefen(a.inst.kisten, a.platz, a.inst.cap, vollstaendig=False)
                    assert 0 <= a.gezeigt < max(1, len(a.bins)) and 1 <= a.schritt <= a.inst.n and a.stuetz_min >= 0.8 - 1e-9
    a = ev.analyse(ev.Settings(0, 0, 7, 1, 0, 0, 0, 5, 3, 1, 0))
    assert a.schritt == 3 and len(a.platz) == 3
    assert ev.wirksamer_schritt(ev.Settings(schritt=0), 12) == 12 and ev.wirksamer_schritt(ev.Settings(schritt=13), 12) == 12 and ev.wirksamer_schritt(ev.Settings(schritt=-4), 12) == 12


def test_der_gezeigte_behaelter_wird_auf_den_letzten_begrenzt():
    a = ev.analyse(ev.Settings(0, 0, 7, C.LIEFERUNG, 0, 0, 0, 5, 0, 1, 1))          # Beispiel 1, Lieferung: zwei Behälter
    assert a.count == 2 and a.gezeigt == 0
    for wunsch, erwartet in ((2, 1), (3, 1), (50, 1)):
        assert ev.analyse(ev.Settings(0, 0, 7, C.LIEFERUNG, 0, 0, 0, 5, 0, wunsch, 1)).gezeigt == erwartet
    assert ev.analyse(ev.Settings(0, 0, 7, C.LIEFERUNG, 0, 0, 0, 5, 2, 2, 1)).gezeigt == 0                      # nach zwei Quadern gibt es nur einen Behälter


def test_verschieben_in_der_analyse_verschiebt_auch_die_eckpunkte():
    a0 = ev.analyse(ev.Settings(1, 0, 7, C.GRUNDFLAECHE, 2, 1, 0))
    a1 = ev.analyse(ev.Settings(1, 0, 7, C.GRUNDFLAECHE, 2, 1, 1))
    assert a0.count == a1.count == 1 and a0.platz != a1.platz
    dx, dy = a1.platz[0][2] - a0.platz[0][2], a1.platz[0][3] - a0.platz[0][3]
    assert (dx, dy) == (0, 8) and all((q[2], q[3], q[4]) == (p[2] + dx, p[3] + dy, p[4]) and q[:2] == p[:2] for p, q in zip(a0.platz, a1.platz))
    assert a1.zustand[0] == tuple((x + dx, y + dy, z) for x, y, z in a0.zustand[0])


def test_zufallsinstanzen_wachsen_mit_n_und_bleiben_im_bereich():
    for v, (_, _, bereiche) in enumerate(C.VERTEILUNGEN):
        for n in C.N_WERTE + C.MESS_N:
            inst = zufallsinstanz(v, n, mess_seed(v, 0, 5))
            assert inst.n == n and len(inst.masse) == n and all(bereiche[a][0] <= k[a] <= bereiche[a][1] for k in inst.kisten for a in range(3))


def test_mess_seeds_sind_verschieden():
    seeds = {mess_seed(v, ni, j) for v in range(4) for ni in range(3) for j in range(C.INSTANZEN)}
    assert len(seeds) == 4 * 3 * C.INSTANZEN
