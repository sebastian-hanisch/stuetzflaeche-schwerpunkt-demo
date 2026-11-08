"""Packen: Nebenbedingungen, Stützfläche und Schwerpunkt - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 10 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Stück 9 hat Quader ohne Stützbedingung gepackt; hier gilt eine Mindest-Stützfläche als harte Bedingung, und der Schwerpunkt jedes Behälters
wird als Kennzahl, mit einer weichen Regel und durch starres Verschieben der Ladung behandelt. Das Messraster (vorberechnet in stz_precomputed.json) zeigt an je 100 Zufallsinstanzen, was die Bedingung kostet.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import stz_constants as C
from stz_evaluation import (
    S_LISTE,
    SCHLUESSEL_LISTE,
    Settings,
    analyse,
    fenster_zeilen,
    verdict_aktuell,
    verdict_fenster,
    verdict_hart,
    verdict_kosten,
    verdict_messung,
    verdict_schwerpunkt,
    verdict_schwerpunkt_raster,
    verdict_stuetz,
    verdict_tabelle,
    zeile,
)
from stz_layout import dunkles_design, kopf_css
from stz_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from stz_visualization import build_behaelter, build_messung

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in stz_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("⚖️ Nebenbedingungen: Stützfläche und Schwerpunkt")
st.markdown(
    """
Stück 9 hat gezeigt: Ohne Stützbedingung stehen viele Quader nicht sicher. Hier wird die **Mindest-Stützfläche** zur harten Bedingung. Drei Fragen: **Was kostet sie in Behältern**, **ändert sie den besten Sortierschlüssel**, und **wie weit kommt man beim Schwerpunkt**? Beim Schwerpunkt gibt es eine ehrliche Antwort: Eine weiche Regel und das starre Verschieben der Ladung helfen oft, aber **einen harten Schwerpunkt liefert dieses Verfahren nicht**. Das Orakel (CP-SAT) zeigt, dass ohne Stützbedingung und bei 12 und 20 Quadern die Aufgabe selbst das Fenster ohne Mehrkosten erlaubt; die Heuristik erreicht es dort oft nicht. Mit Stützbedingung und bei mehr Quadern ist das nicht gemessen.

Wer die Frage zuerst ohne Fachbegriffe verstehen will, öffnet „💬 In einfachen Worten“. Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

# erklaerseite:einfach:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/packen-stuetzflaeche-erklaert.json, nicht von Hand ändern)
with st.expander("💬 In einfachen Worten"):
    st.markdown(
        """
Ein Packverfahren lädt Quader der Reihe nach in Behälter. Dieses Programm fragt, was zwei Bedingungen kosten, die in der Praxis selbstverständlich sind. Erstens darf kein Quader schweben: Er muss mit einem Mindestanteil seiner Grundfläche auf dem Boden oder auf anderen Quadern aufliegen. Zweitens soll der Schwerpunkt der Ladung nahe der Mitte des Behälters liegen. Gesucht ist die Packung mit möglichst wenigen Behältern. Das Programm zeigt, wie viele Behälter die Aufliegebedingung zusätzlich kostet und ob sie ändert, nach welchem Maß man die Quader am besten vorsortiert. Beim Schwerpunkt prüft es eine weiche Regel und das gemeinsame Verschieben der Ladung eines Behälters. Einen harten Schwerpunkt liefert das Verfahren nicht; das Programm zeigt die Grenze. Alle Quader und Massen sind erfunden.

[Ausführlich und verständlich erklärt, mit Fachteil](https://sebastianhanisch.net/packen-stuetzflaeche-erklaert.html)
        """
    )
# erklaerseite:einfach:end

with st.expander("So funktionieren die Bedingungen", expanded=True):
    st.markdown(
        """
1. **Stützfläche:** Der Packer ist Extreme Points mit Projektionen aus Stück 9. Ein Eckpunkt ist jetzt nur zulässig, wenn der Quader dort auf mindestens dem gewählten Anteil seiner Grundfläche aufliegt (auf dem Boden oder auf den Oberseiten anderer Quader). Schweben ist bei jeder Bedingung über 0 % verboten.
2. **Schwerpunkt:** Jeder Quader hat eine Masse. Der Schwerpunkt eines Behälters ist der Mittelwert der Mittelpunkte seiner Quader, gewichtet mit der Masse, in x und y; das **Fenster** ist die halbe Breite um die Mitte der Grundfläche. Die Regel *nah* wählt unter den zulässigen Eckpunkten den, bei dem der Schwerpunkt der Mitte am nächsten liegt. **Verschieben** schiebt die ganze Ladung eines Behälters starr in x und y, so nahe an die Mitte, wie die Hüllbox der Ladung erlaubt: Das kostet keinen Behälter und ändert die Stützflächen nicht.
3. **Farbe:** In der 3D-Ansicht zeigt die Farbe die Stützfläche jedes Quaders (grün 100 %, hellgrün ab 80 %, gelb ab 50 %, orange darunter, rot schwebend) oder die Reihenfolge des Setzens. Das schwarze Kreuz am Boden ist der Schwerpunkt, das grüne Rechteck das Fenster.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Quader**")
    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=C.QUELLEN.get, key="quelle_select",
                          help="Die beiden Beispiele haben je zwölf feste Quader mit Massen. Die anderen vier sind Zufallsinstanzen mit verschiedener Verteilung der Kanten.")
    n_index = st.selectbox("Zahl der Quader (nur Zufallsinstanzen)", list(range(len(C.N_WERTE))), format_func=lambda i: str(C.N_WERTE[i]), key="n_select", help="Gilt nur für Zufallsinstanzen.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt nur bei den Zufallsinstanzen.")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)
    st.markdown("**Packen**")
    schluessel = st.selectbox("Sortierschlüssel", list(C.SCHLUESSEL), format_func=C.SCHLUESSEL.get, key="schluessel_select", help="Wonach die Quader sortiert werden, absteigend.")
    s_index = st.selectbox("Mindest-Stützfläche", list(S_LISTE), format_func=C.S_MIN_TEXT.get, key="smin_select",
                           help="Anteil der Grundfläche, auf dem jeder Quader mindestens aufliegen muss (Boden oder Oberseiten anderer Quader).")
    st.markdown("**Schwerpunkt**")
    regel = st.selectbox("Regel für die Wahl des Eckpunkts", list(C.REGELN), format_func=C.REGELN.get, key="regel_select",
                         help="„nah“: unter den zulässigen Eckpunkten der, bei dem der Schwerpunkt des Behälters der Mitte am nächsten liegt.")
    verschieben = st.selectbox("Ladung verschieben", [0, 1], format_func=lambda i: "aus" if i == 0 else "ein (starr, je Behälter)", key="verschieben_select",
                               help="Schiebt alle Quader eines Behälters gemeinsam in x und y so nahe an die Mitte, wie die Hüllbox der Ladung erlaubt.")
    fenster = st.number_input("Fenster (halbe Breite um die Mitte)", *bounds("fenster_input"), key="fenster_input", step=1, help="Der Schwerpunkt liegt im Fenster, wenn er in x und y höchstens so weit von der Mitte (50) entfernt ist.")
    st.markdown("**Ansicht**")
    schritt = st.number_input("Schritt (0 = alle Quader)", *bounds("schritt_input"), key="schritt_input", step=1,
                              help="Zeigt den Zustand nach den ersten k Quadern in der Reihenfolge des Schlüssels. Größere Werte als die Zahl der Quader zeigen alle.")
    behaelter = st.number_input("Behälter (der gezeichnet wird)", *bounds("behaelter_input"), key="behaelter_input", step=1, help="Nummer des Behälters, der gezeichnet wird. Gibt es weniger, wird der letzte gezeigt.")
    farbe = st.selectbox("Farbe der Quader", list(C.FARBEN), format_func=C.FARBEN.get, key="farbe_select", help="Stützfläche oder Reihenfolge des Setzens.")

sync_query_params({"quelle_select": int(quelle), "n_select": int(n_index), "seed_input": int(seed), "schluessel_select": int(schluessel), "smin_select": int(s_index), "regel_select": int(regel),
                   "verschieben_select": int(verschieben), "fenster_input": int(fenster), "schritt_input": int(schritt), "behaelter_input": int(behaelter), "farbe_select": int(farbe)})

settings = Settings(int(quelle), int(n_index), int(seed), int(schluessel), int(s_index), int(regel), int(verschieben), int(fenster), int(schritt), int(behaelter), int(farbe))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
m1.metric("Behälter (ganze Packung)", a.count, delta=a.count - a.ohne, delta_color="inverse", help="Delta: Behälterzahl mit der gewählten Bedingung minus Behälterzahl ohne Bedingung (gleicher Schlüssel, gleiche Regel).")
m2.metric("Ohne Stützbedingung", a.ohne, delta="Vergleich", delta_color="off")
if a.opt is not None:
    m3.metric("Optimum ohne Stützbedingung", a.opt, delta="Referenz (CP-SAT)", delta_color="off")
else:
    m3.metric("Optimum", "nicht berechnet", delta="nur für die Beispiele", delta_color="off")
m4.metric("Untere Schranke", a.schranke, delta="Volumen oder große Quader", delta_color="off")
volumen = sum(w * d * h for w, d, h in a.inst.kisten)
st.caption(f"{a.inst.n} Quader, Gesamtvolumen {volumen} von {a.inst.cap ** 3} je Behälter, Gesamtmasse {sum(a.inst.masse):.1f}. Kleinste Stützfläche in der ganzen Packung: {100 * a.stuetz_min:.0f} %.")
sp = a.sp_gezeigt[a.gezeigt] if a.sp_gezeigt else None
st.markdown(f"**Zustand nach {a.schritt} von {a.inst.n} Quadern, Behälter {a.gezeigt + 1} von {len(a.bins)}:** der rote Rahmen ist der Behälter"
            + (", die Farbe zeigt die Stützfläche jedes Quaders." if settings.farbe == 1 else ", die Farbe zeigt die Reihenfolge des Setzens."))
st.plotly_chart(build_behaelter(a.inst.kisten, a.platz, a.gezeigt, a.inst.cap, a.zustand[a.gezeigt] if a.zustand else (), settings.farbe, (sp[0], sp[1]) if sp else None, settings.fenster),
                width="stretch", key="main_chart")
if settings.farbe == 1:
    st.caption("Stützfläche: " + " · ".join(f"{text}" for _g, _f, text in C.STUETZ_FARBEN) + " (grün bis rot). Schwarzes Kreuz: Schwerpunkt des Behälters; grünes Rechteck: Fenster; grüne Rauten: Eckpunkte. Der Behälter lässt sich mit der Maus drehen.")
else:
    st.caption("Farbe nach der Reihenfolge des Setzens. Schwarzes Kreuz: Schwerpunkt des Behälters; grünes Rechteck: Fenster; grüne Rauten: Eckpunkte. Der Behälter lässt sich mit der Maus drehen.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was kostet die Stützbedingung, und ändert sie den besten Schlüssel?")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)

zeilen = ["| Schlüssel \\ Mindest-Stützfläche | " + " | ".join(C.S_MIN_KURZ[si] for si in S_LISTE) + " |", "|---|" + "---|" * len(S_LISTE)]
for k in SCHLUESSEL_LISTE:
    zellen = []
    for si in S_LISTE:
        wert = str(a.tabelle[k][si])
        zellen.append(f"**{wert}**" if (k, si) == (settings.schluessel, settings.s_index) else wert)
    zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(zellen) + " |")
st.markdown("Behälterzahl der ganzen Packung für alle 16 Kombinationen (mit der gewählten Schwerpunktregel; die gewählte ist fett):\n\n" + "\n".join(zeilen))
kind, text = verdict_tabelle(a)
getattr(st, kind)(text)

st.markdown("### ⚠️ Stehen die Quader sicher?")
kind, text = verdict_stuetz(a)
getattr(st, kind)(text)

st.markdown("### ⚖️ Liegt der Schwerpunkt im Fenster?")
kind, text = verdict_schwerpunkt(a)
getattr(st, kind)(text)
tab_sp = ["| Behälter | Füllung | Schwerpunkt x | Schwerpunkt y | im Fenster |", "|---|---|---|---|---|"]
for b, (cx, cy, fuell, ok) in enumerate(a.sp_ganz):
    tab_sp.append(f"| {b + 1} | {100 * fuell:.0f} % | {cx:.1f} | {cy:.1f} | {'ja' if ok else 'nein'} |")
st.markdown("\n".join(tab_sp))
st.caption(f"Schwerpunkt je Behälter der ganzen Packung (nach dem Verschieben, wenn es an ist); Mitte der Grundfläche: {a.inst.cap / 2:g}. Dieses Stück liefert **keinen harten** Schwerpunkt, siehe Experimente 3 bis 5.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Gilt das für viele Instanzen?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Behälter {C.CAP} mal {C.CAP} mal {C.CAP}, ganzzahlige Maße der Quader ohne Drehung, Massen zufällig. "
    "Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
verteilung = e1.selectbox("Verteilung der Quader", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
ni = e2.selectbox("Zahl der Quader n", list(range(len(C.MESS_N))), index=1, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(verteilung), int(ni))

st.markdown("### Experiment 1: Was kostet die Stützbedingung?")
st.plotly_chart(build_messung(z["mittel"], "Behälter über der Schranke (Mittel)"), width="stretch", key="exp_chart")
tab = ["| Schlüssel | " + " | ".join(C.S_MIN_KURZ[si] for si in S_LISTE) + " |", "|---|" + "---|" * len(S_LISTE)]
for k in SCHLUESSEL_LISTE:
    tab.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(f"{z['mittel'][k][si]:.2f}" for si in S_LISTE) + " |")
st.markdown("\n".join(tab))
st.caption("Mittlere Behälter über der Schranke (Schlüssel in den Zeilen, Mindest-Stützfläche in den Spalten), Mittel über die Instanzen der Zelle. Bei 20 bis 80 Quadern fehlt das Optimum, die Schranke ist vermutlich locker: Lesen Sie die Unterschiede, nicht den Abstand.")
kind, text = verdict_kosten(z)
getattr(st, kind)(text)

st.markdown("### Experiment 2: Ändert die Bedingung den besten Schlüssel?")
kind, text = verdict_messung(z)
getattr(st, kind)(text)
tab_m = ["| Schlüssel | 50 % | 80 % | 100 % |", "|---|---|---|---|"]
for k in SCHLUESSEL_LISTE:
    tab_m.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(str(z["mehr"][k][si]) for si in S_LISTE[1:]) + " |")
st.markdown("\n".join(tab_m))
st.caption(f"Zahl der Instanzen (von {z['instanzen']}), in denen die Mindest-Stützfläche mehr Behälter braucht als ohne Bedingung (gleicher Schlüssel).")

st.markdown("### Experiment 3: Wie weit kommt man beim Schwerpunkt?")
tab3 = ["| Variante | Behälter über Schranke | im Fenster ±5 | im Fenster ±10 |", "|---|---|---|---|"]
for name in ("keine", "keine_verschoben", "nah", "nah_verschoben", "nah_masse"):
    r = z["schwerpunkt"][name]
    tab3.append(f"| {C.VARIANTEN_NAME[name]} | {r['ueber']:.2f} | {r['im5']:.0f} % | {r['im10']:.0f} % |")
st.markdown("\n".join(tab3))
st.caption("Mindest-Stützfläche 80 %, Schlüssel Grundfläche (bei „schwere zuerst“ nach Masse sortiert). Anteil der **Behälter** im Fenster (nicht der Instanzen); der letzte Behälter ist meist nur teilweise gefüllt.")
kind, text = verdict_schwerpunkt_raster(z)
getattr(st, kind)(text)

st.markdown("### Experiment 4: Was wäre im besten Fall möglich? (Orakel)")
fz = fenster_zeilen()
tab4 = ["| Quader | Optimum ohne Fenster | Optimum mit Fenster ±5 | gleich viele Behälter | mehr Behälter |", "|---|---|---|---|---|"]
for r in fz:
    offen = f", {r['offen']} offen" if r["offen"] else ""
    tab4.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} {r['n']}{offen} | {r['ohne']:.2f} | {r['mit']:.2f} | {r['gleich']} von {r['entschieden']} | {r['mehr']} |")
st.markdown("\n".join(tab4))
st.caption("Optimum mit CP-SAT bei freier Platzierung, **ohne Stützbedingung** (sie lässt sich nicht linear ausdrücken); Mittel über die entschiedenen Instanzen. Eigene Instanzen, 40 je Verteilung bei 12 und 20 je Verteilung bei 20 Quadern.")
kind, text = verdict_fenster(fz)
getattr(st, kind)(text)

st.markdown("### Experiment 5: Warum kein harter Schwerpunkt? (Gegenbeispiel)")
tab5 = ["| Variante | Behälter über Schranke | im Fenster ±5 | Behälter über der Schwelle |", "|---|---|---|---|"]
for name in ("nah", "hart_50", "hart_75"):
    r = z["schwerpunkt"][name]
    tab5.append(f"| {C.VARIANTEN_NAME[name]} | {r['ueber']:.2f} | {r['im5']:.0f} % | " + (f"{r['schwelle']:.0f} %" if name != "nah" else "-") + " |")
st.markdown("\n".join(tab5))
st.caption("Die harte Regel macht jeden Eckpunkt unzulässig, der den Schwerpunkt aus dem Fenster zieht, sobald der Behälter mehr als die Schwelle seines Volumens füllt. Die Garantie gilt nur für Behälter über der Schwelle.")
kind, text = verdict_hart(z)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Kein harter Schwerpunkt** | Die weiche Regel und das Verschieben helfen oft, garantieren aber nichts: Füllt die Ladung die ganze Breite oder Tiefe oder liegt sie schon an einer Wand, bleibt wenig oder nichts zu verschieben. Die harte Regel ab einer Füllschwelle ist teuer und schützt nur Behälter über der Schwelle (Experiment 5). |
| **Kein Optimum mit Stützbedingung** | Die Stützfläche lässt sich in CP-SAT nicht linear ausdrücken; die Demo vergleicht nur Kombinationen und den Abstand zur Schranke. Das Orakel mit hartem Fenster gilt ohne Stützbedingung. |
| **Massen sind zufällig** | Die Massen sind Volumen mal eine zufällige Dichte; echte Ladungen können schwere Teile bündeln. Praxisdaten sind nicht gemessen. |
| **Keine Drehung, keine Stapellast** | Dürfen die Quader gedreht werden oder tragen sie nur begrenzt Last, ändert sich die Aufgabe; die Demo misst es nicht. |
| **Der Dekodierer ist Extreme Points mit Projektionen (eigene Lesart)** | Mit einem anderen Dekodierer können Kosten und Fensteranteile anders ausfallen. |
| **Alle Quader sind vor dem Packen bekannt** | Wer jeden Quader sofort einsortieren muss, kann nicht sortieren. Das ist Online-Packen. Mehr dazu: [Online](https://sebastianhanisch.net/konzepte-online-algorithmen.html). |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    # erklaerseite:lesehilfe:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/packen-stuetzflaeche-erklaert.json, nicht von Hand ändern)
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind $n$ Quader mit ganzzahliger Breite, Tiefe und Höhe und einer Masse sowie Behälter der Größe $C \times C \times C$. Gesucht ist eine überlappungsfreie Platzierung aller Quader in möglichst wenigen Behältern, bei der jeder Quader auf mindestens dem Anteil $s$ seiner Grundfläche aufliegt und der Schwerpunkt jedes Behälters möglichst nahe der Mitte liegt.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Quader |
| $w_i$, $d_i$, $h_i$, $m_i$ | Breite, Tiefe, Höhe und Masse von Quader $i$ |
| $C$ | Kantenlänge eines Behälters |
| $(x_i, y_i, z_i)$ | linke hintere untere Ecke von Quader $i$ |
| $s$ | Mindest-Stützfläche (Anteil der Grundfläche, der aufliegen muss) |
| $f$ | Fenster: halbe Breite um die Mitte $C/2$, in der der Schwerpunkt liegen soll |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Behältern über alle Platzierungen |

[Schritt für Schritt erklärt, mit Herleitung und Literatur](https://sebastianhanisch.net/packen-stuetzflaeche-erklaert.html#fachleute)
        """
    )
    # erklaerseite:lesehilfe:end
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Quader mit ganzzahliger Breite, Tiefe und Höhe, Massen und Behälter der Größe $C \times C \times C$. *Gesucht:* eine überlappungsfreie Platzierung aller Quader in möglichst wenigen Behältern, bei der jeder Quader auf mindestens $s$ seiner Grundfläche aufliegt und der Schwerpunkt jedes Behälters möglichst nahe der Mitte liegt.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Quader |
| $w_i$, $d_i$, $h_i$, $m_i$ | Breite, Tiefe, Höhe und Masse von Quader $i$ |
| $C$ | Kantenlänge eines Behälters |
| $(x_i, y_i, z_i)$ | linke hintere untere Ecke von Quader $i$ |
| $s$ | Mindest-Stützfläche (Anteil der Grundfläche) |
| $f$ | Fenster: halbe Breite um die Mitte $C/2$ |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Behältern über alle Platzierungen |

**Reihenfolge und Dekodierer.** Wie in Stück 9: Schlüssel $w_i d_i h_i$, $w_i d_i$ oder $h_i$ (absteigend, Gleichstände in der Lieferreihenfolge) oder die Lieferreihenfolge; jeder Quader kommt in den ersten Behälter, in dem ein Eckpunkt ihn aufnimmt, an den zulässigen Eckpunkt mit kleinstem $(z, y, x)$; die Eckpunkte entstehen aus den Ecken rechts, hinten und oben und ihren Projektionen auf die nächste Fläche.

**Stützfläche.** Die Stützfläche von Quader $i$ mit $z_i > 0$ ist $\sigma_i = \dfrac{1}{w_i d_i} \sum_j |\,[x_i, x_i + w_i) \cap [x_j, x_j + w_j)\,| \cdot |\,[y_i, y_i + d_i) \cap [y_j, y_j + d_j)\,|$ über die Quader $j$ desselben Behälters mit $z_j + h_j = z_i$; am Boden ist $\sigma_i = 1$. Ein Eckpunkt ist nur zulässig, wenn $\sigma_i \ge s$.

**Schwerpunkt.** Für einen Behälter $B$ ist $c_x = \dfrac{\sum_{i \in B} m_i (x_i + w_i/2)}{\sum_{i \in B} m_i}$ und ebenso $c_y$. Der Schwerpunkt liegt im Fenster, wenn $|c_x - C/2| \le f$ und $|c_y - C/2| \le f$. Die Regel *nah* wählt unter den zulässigen Eckpunkten den, der $(c_x - C/2)^2 + (c_y - C/2)^2$ nach dem Setzen minimiert (bei Gleichstand den mit kleinstem $(z, y, x)$). Die harte Regel ab der Schwelle $\theta$ lässt einen Eckpunkt nur zu, wenn der Behälter danach höchstens $\theta C^3$ füllt oder $(c_x, c_y)$ im Fenster liegt.

**Starres Verschieben.** Mit der Hüllbox $[x_{\min}, x_{\max}] \times [y_{\min}, y_{\max}]$ der Ladung eines Behälters wird jeder Quader um $\Delta_x = \max(-x_{\min},\ \min(C - x_{\max},\ \mathrm{rund}(C/2 - c_x)))$ in $x$ und entsprechend $\Delta_y$ in $y$ verschoben. Die Lage der Quader zueinander und alle Stützflächen bleiben; der Schwerpunkt wandert um $\Delta_x$ und $\Delta_y$.

**Schranken.** $L_{\mathrm{Vol}} = \left\lceil \tfrac{1}{C^3} \sum_i w_i d_i h_i \right\rceil \le \mathrm{OPT}$; $L_{\mathrm{gr}} = |\{ i : w_i, d_i, h_i > C/2 \}| \le \mathrm{OPT}$; $L = \max(L_{\mathrm{Vol}}, L_{\mathrm{gr}})$. Die Schranken gelten ohne Stützbedingung; mit Bedingung ist das Optimum nicht kleiner.

**Exaktes Optimum** (nur Generator und Tests, nicht diese App). CP-SAT wie in Stück 9; mit dem Schwerpunktfenster kommen je Behälter zwei lineare Bedingungen hinzu: $\left|\sum_i m_i (2 x_i + w_i - C)\, [i \in B]\right| \le 2 f \sum_i m_i [i \in B]$ und ebenso in $y$, mit Hilfsvariablen $t_i = x_i$ falls $i$ im Behälter liegt, sonst 0. Die Stützbedingung lässt sich nicht linear ausdrücken und fehlt dort.

**Literatur.** Keine Zahl und keine Aussage der Literatur ist in diese Demo übernommen; alle Zahlen sind selbst gemessen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
