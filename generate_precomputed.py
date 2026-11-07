"""Erzeugt stz_precomputed.json: das Messraster (vier Verteilungen × Quaderzahlen 20, 40, 80 × 100 feste Instanzen × vier Schlüssel × vier Mindest-Stützflächen, dazu die Schwerpunkt-Varianten), das
CP-SAT-Orakel mit hartem Schwerpunktfenster (Quaderzahlen 12 und 20) und die Stichprobe (die ersten Instanzen jeder Zelle einzeln, für die Tests).

    python generate_precomputed.py                         # rechnet alles neu (Orakel mit CP-SAT, Zeitlimit je Instanz, mehrere Prozesse)
    python generate_precomputed.py --keep-fenster          # behält das gespeicherte Orakel und rechnet Raster und Stichprobe neu
    python generate_precomputed.py --nur-stichprobe        # ergänzt in der vorhandenen Datei nur die Stichprobe
    python generate_precomputed.py --check                 # rechnet das Raster (parallel) nach und vergleicht mit der Datei (das Orakel nicht)

Das Orakel rechnet dev/opt.py (CP-SAT, ohne Stützbedingung): Je Instanz das Optimum ohne und mit hartem Schwerpunktfenster ±5; die Obergrenze ist die beste Behälterzahl der Packungen ohne Bedingung."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import stz_algorithm as A
import stz_constants as C
import stz_evaluation as ev
from stz_scenario import zufallsinstanz


def fenster_instanz(v: int, n: int, j: int) -> tuple:
    """(Optimum ohne Fenster, Optimum mit Fenster ±5); -1 = nicht entschieden. Beide ohne Stützbedingung."""
    from dev.opt import optimum_cpsat, optimum_cpsat_fenster

    inst = zufallsinstanz(v, n, ev.fenster_seed(v, n, j))
    k, m, cap = inst.kisten, inst.masse, inst.cap
    ober = min(A.anzahl(k, m, key, cap) for key in ev.SCHLUESSEL_LISTE)
    zeit = C.FENSTER_OPT_ZEIT[n]
    ohne = ober if ober == A.schranke(k, cap) else optimum_cpsat(k, cap, ober, zeit, 2)
    if ohne < 0:
        return -1, -1
    mit = -1
    for obergrenze in range(max(ohne, 1), ohne + 4):
        mit = optimum_cpsat_fenster(k, m, cap, obergrenze, 5, zeit, 2)
        if mit > 0:
            break
    return ohne, (mit if mit > 0 else -1)


def _fenster_zelle(args):
    v, n = args
    z = {"instanzen": C.FENSTER_OPT_N[n], "entschieden": 0, "offen": 0, "ohne": 0, "mit": 0, "gleich": 0, "mehr": 0}
    for j in range(C.FENSTER_OPT_N[n]):
        ohne, mit = fenster_instanz(v, n, j)
        if ohne < 0 or mit < 0:
            z["offen"] += 1
            continue
        z["entschieden"] += 1
        z["ohne"] += ohne
        z["mit"] += mit
        z["gleich" if mit == ohne else "mehr"] += 1
    return f"{C.VERTEILUNGEN[v][0]}|{n}", z


def _zelle(args):
    v, ni = args
    t = time.perf_counter()
    return v, ni, ev.messzelle(v, ni), time.perf_counter() - t


def _stichprobe_zelle(args):
    v, ni = args
    return ev.zelle_schluessel(v, ni), {str(j): ev.messzelle(v, ni, [j]) for j in C.STICHPROBE_J}


def _frisch(args):
    v, ni = args
    return ev.zelle_schluessel(v, ni), ev.messzelle(v, ni)


def _pool():
    return ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) // 2)))


def _zellen():
    return [(v, ni) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]


def stichprobe_ergaenzen(daten: dict) -> None:
    with _pool() as pool:
        daten["stichprobe"] = dict(pool.map(_stichprobe_zelle, _zellen()))


def erzeugen(behalten: bool) -> dict:
    daten = {"instanzen": C.INSTANZEN, "cap": C.CAP, "zellen": {}}
    if behalten:
        daten["fenster_optimum"] = ev.vorberechnet()["fenster_optimum"]
    else:
        with _pool() as pool:
            daten["fenster_optimum"] = dict(pool.map(_fenster_zelle, [(v, n) for n in sorted(C.FENSTER_OPT_N) for v in range(len(C.VERTEILUNGEN))]))
        for k, z in daten["fenster_optimum"].items():
            print(f"Fenster-Orakel {k}: {z['entschieden']} entschieden, {z['offen']} offen, gleich {z['gleich']}, mehr {z['mehr']}", flush=True)
    with _pool() as pool:
        for v, ni, z, sekunden in pool.map(_zelle, _zellen()):
            daten["zellen"][ev.zelle_schluessel(v, ni)] = z
            print(f"{ev.zelle_schluessel(v, ni)}: {sekunden:.0f} s", flush=True)
    daten["zellen"] = {ev.zelle_schluessel(v, ni): daten["zellen"][ev.zelle_schluessel(v, ni)] for v, ni in _zellen()}
    stichprobe_ergaenzen(daten)
    return daten


def schreiben(daten: dict) -> None:
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED.name)


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    with _pool() as pool:
        for schl, frisch in pool.map(_frisch, _zellen()):
            if frisch != gespeichert["zellen"][schl]:
                schlecht += 1
                print("ABWEICHUNG", schl, flush=True)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    if "--nur-stichprobe" in sys.argv:
        d = json.loads(ev.PRECOMPUTED.read_text(encoding="utf-8"))
        stichprobe_ergaenzen(d)
        schreiben(d)
        sys.exit(0)
    schreiben(erzeugen("--keep-fenster" in sys.argv))
