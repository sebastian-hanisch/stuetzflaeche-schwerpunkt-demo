"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in stz_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import stz_algorithm as A
import stz_constants as C
from stz_scenario import Instance, mess_seed, quelle_instanz, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "stz_precomputed.json"
SCHLUESSEL_LISTE = tuple(sorted(C.SCHLUESSEL))
S_LISTE = tuple(range(len(C.S_MIN_WERTE)))
VOLUMEN, GRUNDFLAECHE, HOEHE = C.VOLUMEN, C.GRUNDFLAECHE, C.HOEHE


@dataclass(frozen=True)
class Settings:
    quelle: int = 0
    n_index: int = 0
    seed: int = C.DEFAULT_SEED
    schluessel: int = VOLUMEN
    s_index: int = 0            # Index in C.S_MIN_WERTE: Mindest-Stützfläche
    regel: int = 0              # Schwerpunktregel: 0 keine, 1 nah
    verschieben: int = 0        # 1 = die Ladung jedes Behälters wird starr verschoben
    fenster: int = C.FENSTER_STANDARD
    schritt: int = 0            # 0 = alle Quader, sonst der Zwischenstand nach so vielen Quadern
    behaelter: int = 1          # welcher Behälter gezeichnet wird (1 = erster); größere Werte zeigen den letzten
    farbe: int = 1              # 0 Reihenfolge des Setzens, 1 Stützfläche


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    order: tuple          # alle Quadernummern in der Reihenfolge, in der gepackt wird
    schritt: int          # Zahl der gesetzten Quader im gezeigten Zustand
    bins: tuple           # Behälter (Quadernummern) im gezeigten Zustand
    platz: tuple          # Platzierungen im gezeigten Zustand (nach dem Verschieben, wenn es an ist)
    zustand: tuple        # Eckpunkte je Behälter im gezeigten Zustand (mit verschoben)
    gezeigt: int          # Nummer (ab 0) des gezeichneten Behälters im gezeigten Zustand
    count: int            # Behälterzahl der ganzen Packung
    ohne: int             # Behälterzahl ohne Stützbedingung bei gleichem Schlüssel und gleicher Regel
    liefer: int           # Behälterzahl in Lieferreihenfolge bei gleicher Stützbedingung und Regel
    schranke: int
    opt: object           # Optimum ohne Stützbedingung (int) bei den Handbeispielen, sonst None
    tabelle: tuple        # tabelle[schluessel][s_index] = Behälterzahl, 4 x 4
    stuetz_min: float     # kleinste Stützfläche aller Quader der ganzen Packung
    unter80: int          # Quader der ganzen Packung mit Stützfläche unter 80 %
    schwebend: int        # Quader der ganzen Packung ohne jede Stütze
    sp_gezeigt: tuple     # je Behälter des gezeigten Zustands (cx, cy, Füllung, im Fenster)
    sp_ganz: tuple        # je Behälter der ganzen Packung (cx, cy, Füllung, im Fenster), nach dem Verschieben, wenn es an ist
    settings: Settings


def s_min(s: Settings) -> float:
    return C.S_MIN_WERTE[s.s_index]


def tabelle(inst: Instance, regel: int = 0) -> tuple:
    """Behälterzahl für jede Kombination aus Schlüssel (Zeile) und Mindest-Stützfläche (Spalte)."""
    return tuple(tuple(A.anzahl(inst.kisten, inst.masse, k, inst.cap, C.S_MIN_WERTE[si], regel) for si in S_LISTE) for k in SCHLUESSEL_LISTE)


def wirksamer_schritt(settings: Settings, n: int) -> int:
    """Zahl der gezeigten Schritte: 0 oder mehr als n bedeutet alle Quader."""
    return n if settings.schritt <= 0 or settings.schritt > n else settings.schritt


def _verschoben(inst, platz, zustand, an: bool):
    """Platzierung und Eckpunkte nach dem starren Verschieben (wenn `an`), sonst unverändert."""
    if not an or not platz:
        return list(platz), list(zustand)
    neu, v = A.verschieben(inst.kisten, inst.masse, platz, inst.cap)
    punkte = [tuple((x + v[b][0], y + v[b][1], z) for x, y, z in pts) for b, pts in enumerate(zustand)]
    return neu, punkte


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.quelle, C.N_WERTE[s.n_index], s.seed)
    order = A.reihenfolge(inst.kisten, s.schluessel)
    smin = s_min(s)
    schritt = wirksamer_schritt(s, inst.n)
    bins_voll, platz_voll, zustand_voll = A.pack(inst.kisten, inst.masse, order, inst.cap, smin, s.regel, s.fenster)
    assert A.packung_pruefen(inst.kisten, platz_voll, inst.cap)
    assert A.stuetz_minimum(inst.kisten, platz_voll) >= smin - 1e-9
    platz_ganz, _ = _verschoben(inst, platz_voll, zustand_voll, bool(s.verschieben))
    assert A.packung_pruefen(inst.kisten, platz_ganz, inst.cap)
    bins, platz0, zustand0 = A.pack(inst.kisten, inst.masse, order[:schritt], inst.cap, smin, s.regel, s.fenster)
    platz, zustand = _verschoben(inst, platz0, zustand0, bool(s.verschieben))
    assert A.packung_pruefen(inst.kisten, platz, inst.cap, vollstaendig=False)
    tab = tabelle(inst, s.regel)
    ohne = A.anzahl(inst.kisten, inst.masse, s.schluessel, inst.cap, 0.0, s.regel, s.fenster)
    liefer = A.anzahl(inst.kisten, inst.masse, C.LIEFERUNG, inst.cap, smin, s.regel, s.fenster)
    gezeigt = max(0, min(s.behaelter, len(bins)) - 1)
    return Analysis(inst, tuple(order), schritt, tuple(tuple(b) for b in bins), tuple(platz), tuple(zustand), gezeigt, len(bins_voll), ohne, liefer, A.schranke(inst.kisten, inst.cap),
                    C.BEISPIEL_OPTIMUM.get(s.quelle), tab, A.stuetz_minimum(inst.kisten, platz_voll), *A.stuetz_kennzahlen(inst.kisten, platz_voll), tuple(A.schwerpunkte(inst.kisten, inst.masse, platz, inst.cap, s.fenster)),
                    tuple(A.schwerpunkte(inst.kisten, inst.masse, platz_ganz, inst.cap, s.fenster)), s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def beste_schluessel(tab: tuple, s_index: int) -> list:
    """Schlüssel mit der kleinsten Behälterzahl in der Spalte der Mindest-Stützfläche."""
    spalte = [tab[k][s_index] for k in SCHLUESSEL_LISTE]
    return [k for k in SCHLUESSEL_LISTE if tab[k][s_index] == min(spalte)]


def _namen(schluessel: list) -> str:
    return " oder ".join(C.SCHLUESSEL_KURZ[k] for k in schluessel)


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zur gewählten Kombination: Behälterzahl der ganzen Packung gegen die Behälterzahl ohne Stützbedingung (gleicher Schlüssel), gegen das Optimum ohne Bedingung, wo es bekannt ist."""
    s = a.settings
    schluessel = C.SCHLUESSEL_MIT[s.schluessel]
    if a.opt is None:
        opt_teil = f" Ein Optimum ist für diese Instanz nicht berechnet; die Schranke ist {a.schranke}."
    elif a.count == a.opt:
        opt_teil = f" Das ist das Optimum ohne Stützbedingung (die Schranke allein ergäbe {a.schranke})."
    else:
        opt_teil = f" Das Optimum ohne Stützbedingung ist **{a.opt}** (die Schranke ist {a.schranke})."
    if s.s_index == 0:
        beste = beste_schluessel(a.tabelle, 0)
        passt = " Das ist einer der besten Schlüssel dieser Instanz." if s.schluessel in beste else f" In der Tabelle ist {_namen(beste)} besser ({a.tabelle[beste[0]][0]})."
        return "info", f"Nach {schluessel} sortiert und ohne Stützbedingung brauchen die Quader **{a.count}** Behälter." + opt_teil + passt
    kopf = f"Nach {schluessel} sortiert und mit mindestens {C.S_MIN_KURZ[s.s_index]} Stützfläche gesetzt brauchen die Quader **{a.count}** Behälter, ohne Bedingung {a.ohne}."
    beste = beste_schluessel(a.tabelle, s.s_index)
    passt = " Für diese Bedingung ist das einer der besten Schlüssel dieser Instanz." if s.schluessel in beste else f" Für diese Bedingung ist in der Tabelle {_namen(beste)} besser ({a.tabelle[beste[0]][s.s_index]})."
    if a.count > a.ohne:
        return "warning", kopf + f" Die Bedingung kostet hier {a.count - a.ohne}." + opt_teil + passt
    if a.count < a.ohne:
        return "success", kopf + f" Die Bedingung spart hier {a.ohne - a.count} (die Reihenfolge der Quader ändert sich)." + opt_teil + passt
    return "info", kopf + " Die Bedingung kostet hier nichts." + opt_teil + passt


def verdict_tabelle(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Ändert die Mindest-Stützfläche den besten Schlüssel? Verglichen werden die Spalten ohne Bedingung und mit der gewählten Bedingung dieser Instanz."""
    s = a.settings
    ohne = beste_schluessel(a.tabelle, 0)
    mit = beste_schluessel(a.tabelle, s.s_index)
    if s.s_index == 0:
        return "info", f"Ohne Bedingung ist in der Tabelle {_namen(ohne)} am besten ({a.tabelle[ohne[0]][0]} Behälter). Wählen Sie eine Mindest-Stützfläche, um zu sehen, ob sich das ändert."
    teil = (f"Ohne Bedingung ist {_namen(ohne)} am besten ({a.tabelle[ohne[0]][0]} Behälter), mit {C.S_MIN_KURZ[s.s_index]} Stützfläche {_namen(mit)} ({a.tabelle[mit[0]][s.s_index]}).")
    if set(ohne).isdisjoint(mit):
        return "warning", teil + " **Die Bedingung ändert den besten Schlüssel.**"
    ausgeschlossen = [k for k in ohne if k not in mit]
    if ausgeschlossen:
        return "info", teil + f" Die Bedingung schließt {_namen(ausgeschlossen)} als besten Schlüssel aus."
    return "info", teil + " Der beste Schlüssel bleibt."


def verdict_stuetz(a: Analysis) -> tuple[str, str]:
    """Verdikt zur Stützfläche der ganzen Packung: bei einer Bedingung die kleinste Stützfläche (muss die Bedingung erfüllen), ohne Bedingung die Zahl der Quader unter 80 % und der schwebenden."""
    s = a.settings
    if s.s_index == 0:
        teil = (f"Ohne Bedingung haben **{a.unter80}** von {a.inst.n} Quadern weniger als 80 % Stützfläche, **{a.schwebend}** schweben ohne jede Stütze; die kleinste Stützfläche ist "
                f"{100 * a.stuetz_min:.0f} %.")
        if a.schwebend > 0:
            return "warning", teil + " Solche Quader würden in der Wirklichkeit nicht stehen."
        return ("info" if a.unter80 > 0 else "success"), teil
    return "success", (f"Jeder Quader liegt auf mindestens {C.S_MIN_KURZ[s.s_index]} seiner Grundfläche auf; die kleinste Stützfläche in dieser Packung ist **{100 * a.stuetz_min:.0f} %**.")


def verdict_schwerpunkt(a: Analysis) -> tuple[str, str]:
    """Verdikt zum Schwerpunkt der ganzen Packung: wie viele Behälter liegen im Fenster ±f (der Rand zählt dazu)? Die Regeln und das Verschieben stehen in den Einstellungen."""
    s = a.settings
    k = len(a.sp_ganz)
    im = sum(1 for *_x, ok in a.sp_ganz if ok)
    regel = f"Regel {C.REGEL_KURZ[s.regel]}" + (", verschoben" if s.verschieben else "")
    teil = f"Von {k} Behältern liegen **{im}** mit dem Schwerpunkt im Fenster ±{s.fenster} ({regel})."
    if im == k:
        return "success", teil
    if im == 0:
        return "warning", teil + " Dieses Stück liefert keinen harten Schwerpunkt: Die Eckpunkte erlauben keine Mittenlage."
    return "info", teil + " Die übrigen liegen außerhalb; mit anderer Regel oder mit Verschieben kann sich das ändern."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def messzelle(verteilung: int, n_index: int, instanzen=None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen) über INSTANZEN feste Instanzen (oder nur über die Nummern `instanzen`, so rechnen die Tests Stichproben nach).

    ueber_schranke[k][s]: Summe von (Behälter mit Schlüssel k und Mindest-Stützfläche s minus Schranke), Regel keine. mehr_als_ohne[k][s] (s ab 1): Zahl der Instanzen mit mehr Behältern als ohne Bedingung.
    schwerpunkt[variante]: bei Mindest-Stützfläche 80 % und Schlüssel Grundfläche (Variante "nah_masse": nach Masse): ueber (Summe Behälter minus Schranke), behaelter (Zahl aller Behälter),
    im5 und im10 (Zahl der Behälter mit Schwerpunkt im Fenster ±5 und ±10), schwelle (Zahl der Behälter über der Füllschwelle, nur bei den harten Regeln)."""
    n = C.MESS_N[n_index]
    out = {"ueber_schranke": {str(k): {str(s): 0 for s in S_LISTE} for k in SCHLUESSEL_LISTE}, "mehr_als_ohne": {str(k): {str(s): 0 for s in S_LISTE[1:]} for k in SCHLUESSEL_LISTE},
           "schwerpunkt": {name: {"ueber": 0, "behaelter": 0, "im5": 0, "im10": 0, "schwelle": 0} for name in C.VARIANTEN}}
    for j in (range(C.INSTANZEN) if instanzen is None else instanzen):
        inst = zufallsinstanz(verteilung, n, mess_seed(verteilung, n_index, j))
        kisten, masse, cap = inst.kisten, inst.masse, inst.cap
        s = A.schranke(kisten, cap)
        for k in SCHLUESSEL_LISTE:
            zahlen = [A.anzahl(kisten, masse, k, cap, C.S_MIN_WERTE[si]) for si in S_LISTE]
            for si in S_LISTE:
                out["ueber_schranke"][str(k)][str(si)] += zahlen[si] - s
                if si > 0:
                    out["mehr_als_ohne"][str(k)][str(si)] += zahlen[si] > zahlen[0]
        smin = C.S_MIN_WERTE[C.SCHWERPUNKT_SMIN_INDEX]
        for name, (regel, verschieben, schwelle, art) in C.VARIANTEN.items():
            order = A.reihenfolge_masse(kisten, masse) if art == "masse" else A.reihenfolge(kisten, C.SCHWERPUNKT_SCHLUESSEL)
            bins, platz, _ = A.pack(kisten, masse, order, cap, smin, regel, C.FENSTER_RASTER[0], schwelle or 0.5)
            if verschieben:
                platz = A.verschieben(kisten, masse, platz, cap)[0]
            r = out["schwerpunkt"][name]
            r["ueber"] += len(bins) - s
            for cx, cy, fuell, _ok in A.schwerpunkte(kisten, masse, platz, cap, C.FENSTER_RASTER[0]):
                r["behaelter"] += 1
                r["im5"] += A.im_fenster(cx, cy, cap, 5)
                r["im10"] += A.im_fenster(cx, cy, cap, 10)
                r["schwelle"] += bool(schwelle) and fuell > schwelle
    return out


def fenster_seed(verteilung: int, n: int, j: int) -> int:
    """Seed der j-ten Instanz des CP-SAT-Orakels mit hartem Schwerpunktfenster (eigene Instanzen, nicht aus dem Raster)."""
    return 6_000_000 + 100_000 * verteilung + 1_000 * n + j


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    k = daten["instanzen"]
    sp = {}
    for name, r in z["schwerpunkt"].items():
        b = r["behaelter"]
        sp[name] = {"ueber": r["ueber"] / k, "behaelter_je_instanz": b / k, "im5": 100.0 * r["im5"] / b, "im10": 100.0 * r["im10"] / b, "schwelle": 100.0 * r["schwelle"] / b}
    return {
        "verteilung": verteilung,
        "name": C.VERTEILUNG_LANG[verteilung],
        "n": C.MESS_N[n_index],
        "instanzen": k,
        "mittel": {s_k: {si: z["ueber_schranke"][str(s_k)][str(si)] / k for si in S_LISTE} for s_k in SCHLUESSEL_LISTE},
        "mehr": {s_k: {si: z["mehr_als_ohne"][str(s_k)][str(si)] for si in S_LISTE[1:]} for s_k in SCHLUESSEL_LISTE},
        "schwerpunkt": sp,
    }


def gerundet(m: dict) -> dict:
    return {k: {si: round(m[k][si], 2) for si in S_LISTE} for k in SCHLUESSEL_LISTE}


def beste_schluessel_zelle(g: dict, s_index: int) -> list:
    """Schlüssel mit dem kleinsten (auf zwei Stellen gerundeten) Mittel bei der Mindest-Stützfläche."""
    kleinster = min(g[k][s_index] for k in SCHLUESSEL_LISTE)
    return [k for k in SCHLUESSEL_LISTE if g[k][s_index] == kleinster]


def verdict_kosten(z: dict) -> tuple[str, str]:
    """Experiment 1: Kosten der Mindest-Stützfläche in der gewählten Zelle für Volumen und Grundfläche (Mittel der Behälter über der Schranke, auf zwei Stellen gerundet): der Zuwachs von 0 auf 100 %."""
    g = gerundet(z["mittel"])
    def zeilen(k):
        return " / ".join(f"{g[k][si]:.2f}" for si in S_LISTE)
    zuwachs_v, zuwachs_g = round(g[VOLUMEN][3] - g[VOLUMEN][0], 2), round(g[GRUNDFLAECHE][3] - g[GRUNDFLAECHE][0], 2)
    teil = (f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} brauchen die Quader über der Schranke (Mindest-Stützfläche 0 / 50 / 80 / 100 %): Volumen {zeilen(VOLUMEN)}, Grundfläche {zeilen(GRUNDFLAECHE)} "
            f"Behälter ({z['instanzen']} Instanzen). Von keiner Bedingung auf volle Auflage wächst der Bedarf mit dem Volumen um {zuwachs_v:.2f}, mit der Grundfläche um {zuwachs_g:.2f}.")
    if zuwachs_v > 0 or zuwachs_g > 0:
        return "warning", teil + " Die Stützbedingung kostet Behälter."
    return "info", teil + " Die Stützbedingung kostet in dieser Zelle nichts."


def verdict_messung(z: dict) -> tuple[str, str]:
    """Experiment 2: der beste Schlüssel je Mindest-Stützfläche (Mittel, auf zwei Stellen gerundet); kippt er zwischen keiner Bedingung und 80 %?"""
    g = gerundet(z["mittel"])
    teile = []
    for si in S_LISTE:
        beste = beste_schluessel_zelle(g, si)
        teile.append(f"{C.S_MIN_KURZ[si]} {'alle gleich' if len(beste) == len(SCHLUESSEL_LISTE) else ' und '.join(C.SCHLUESSEL_KURZ[k] for k in beste)}")
    kopf = f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} ist der beste Schlüssel je Mindest-Stützfläche (Mittel über {z['instanzen']} Instanzen): " + ", ".join(teile) + "."
    ohne, mit = beste_schluessel_zelle(g, 0), beste_schluessel_zelle(g, C.SCHWERPUNKT_SMIN_INDEX)
    if len(ohne) < len(SCHLUESSEL_LISTE) and len(mit) < len(SCHLUESSEL_LISTE) and set(ohne).isdisjoint(mit):
        return "warning", kopf + " **Die Bedingung ändert den besten Schlüssel.**"
    return "info", kopf + " Der beste Schlüssel bleibt zwischen keiner Bedingung und 80 % derselbe oder gleichauf."


def verdict_schwerpunkt_raster(z: dict) -> tuple[str, str]:
    """Experiment 3: Anteil der Behälter im Fenster ±5 für keine Regel, die Regel nah und nah mit Verschieben (Mindest-Stützfläche 80 %, Schlüssel Grundfläche), auf ganze Prozent gerundet."""
    sp = z["schwerpunkt"]
    a, b, c = round(sp["keine"]["im5"]), round(sp["nah"]["im5"]), round(sp["nah_verschoben"]["im5"])
    d = round(sp["nah_verschoben"]["im10"])
    teil = (f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} liegen im Fenster ±5 ohne Regel {a} %, mit der Regel „nah“ {b} % und mit „nah“ und Verschieben {c} % der Behälter "
            f"(im Fenster ±10 mit „nah“ und Verschieben {d} %).")
    if c == 100:
        return "success", teil + " Hier liefert die Kombination ein Fenster für alle Behälter."
    return "warning", teil + " Das ist **keine Garantie**: Wo die Ladung die ganze Breite oder Tiefe füllt, gibt es nichts zu verschieben."


def verdict_hart(z: dict) -> tuple[str, str]:
    """Experiment 5: die harte Regel ab einer Füllschwelle gegen „nah“: Mehrbedarf an Behältern und Anteil der Behälter über der Schwelle (auf zwei Stellen beziehungsweise ganze Prozent gerundet)."""
    sp = z["schwerpunkt"]
    mehr50 = round(sp["hart_50"]["ueber"], 2) - round(sp["nah"]["ueber"], 2)
    mehr75 = round(sp["hart_75"]["ueber"], 2) - round(sp["nah"]["ueber"], 2)
    teil = (f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} braucht die harte Regel ab 50 % Füllung {mehr50:+.2f} Behälter gegenüber „nah“, ab 75 % {mehr75:+.2f}; "
            f"über der Schwelle liegen {round(sp['hart_50']['schwelle'])} % (50 %) beziehungsweise {round(sp['hart_75']['schwelle'])} % (75 %) der Behälter, nur für diese gilt die Garantie.")
    if mehr50 > 0:
        return "warning", teil + " Die Garantie ist teuer und gilt nur für einen Teil der Behälter."
    return "info", teil + " In dieser Zelle kostet sie nichts, schützt aber nur die Behälter über der Schwelle."


def fenster_zeilen(daten: dict | None = None) -> list:
    """Experiment 4: je Verteilung und Quaderzahl (12, 20) das Optimum ohne und mit hartem Schwerpunktfenster ±5 (CP-SAT, ohne Stützbedingung), Mittel über die entschiedenen Instanzen."""
    daten = daten or vorberechnet()
    zeilen = []
    for n in sorted(C.FENSTER_OPT_N):
        for v, (name, *_x) in enumerate(C.VERTEILUNGEN):
            z = daten["fenster_optimum"][f"{name}|{n}"]
            e = z["entschieden"]
            zeilen.append({"verteilung": v, "n": n, "instanzen": z["instanzen"], "entschieden": e, "offen": z["offen"], "ohne": z["ohne"] / e if e else None, "mit": z["mit"] / e if e else None,
                           "gleich": z["gleich"], "mehr": z["mehr"]})
    return zeilen


def verdict_fenster(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 4: in wie vielen entschiedenen Instanzen braucht das harte Fenster mehr Behälter als der Optimum ohne Fenster?"""
    entschieden = sum(z["entschieden"] for z in zeilen)
    gleich = sum(z["gleich"] for z in zeilen)
    mehr = sum(z["mehr"] for z in zeilen)
    teil = (f"Mit freier Platzierung braucht das harte Schwerpunktfenster ±5 in **{gleich}** von {entschieden} entschiedenen Instanzen genauso viele Behälter wie ohne Fenster und in {mehr} mehr "
            "(ohne Stützbedingung, Quaderzahlen 12 und 20).")
    if mehr == 0:
        return "success", teil + " Die Grenze liegt im Dekodierer, nicht in der Aufgabe: Mit Eckpunkten ist die Mitte oft nicht erreichbar."
    return "info", teil + " In diesen Instanzen kostet das Fenster Behälter."
