"""Konstanten: Regler-Grenzen, feste Beispiele, Messraster, Farben und Presets."""

CAP = 100                 # Behälter 100 x 100 x 100 (Breite, Tiefe, Höhe)

# Beispiel 1 (Zufallsinstanz mittlere Quader, n = 12, Seed 5000034): Optimum 1 (CP-SAT, ohne Stützbedingung). Behälterzahl für die Mindest-Stützfläche 0 / 50 / 80 / 100 %: Volumen 1 / 1 / 2 / 2,
# Grundfläche 1 / 1 / 1 / 1, Lieferung 2 / 2 / 2 / 2, Höhe 2 / 2 / 2 / 2 (Phase 0, in den Tests nachgerechnet).
# Beispiel 2 (breit gestreute Quader, n = 12, Seed 5001173): Optimum 1; Volumen 1 / 1 / 1 / 1, Grundfläche 1 / 1 / 1 / 1; mit 80 % Stützfläche und Schlüssel Grundfläche liegt der Schwerpunkt ohne Regel bei
# (47,0 | 40,0), mit der Regel „nah“ bei (47,3 | 41,6), beides außerhalb des Fensters ±5; „nah“ und verschoben: (47,3 | 49,6), im Fenster; ohne Regel verschoben: (47,0 | 42,0), außerhalb.
BEISPIELE = {
    0: ((53, 31, 28), (59, 53, 43), (20, 33, 24), (26, 21, 45), (35, 21, 38), (41, 22, 24), (20, 20, 38), (22, 52, 58), (23, 55, 29), (23, 26, 42), (26, 22, 57), (33, 37, 41)),
    1: ((57, 23, 14), (66, 47, 22), (50, 19, 67), (34, 29, 52), (47, 19, 37), (58, 35, 19), (20, 16, 14), (6, 27, 28), (30, 10, 15), (8, 19, 14), (19, 62, 70), (62, 27, 22)),
}
BEISPIEL_MASSEN = {
    0: (43.3, 168.5, 28.3, 37.7, 27.9, 35.3, 24.0, 53.9, 72.1, 31.8, 20.3, 88.5),
    1: (14.1, 83.0, 82.9, 47.4, 33.6, 65.6, 4.0, 8.6, 5.8, 3.7, 146.6, 62.9),
}
BEISPIEL_OPTIMUM = {0: 1, 1: 1}           # Optimum ohne Stützbedingung (CP-SAT); mit Stützbedingung gibt es kein Optimum

QUELLEN = {0: "Beispiel 1 (zwölf Quader)", 1: "Beispiel 2 (zwölf andere Quader)", 2: "zufällig, mittlere Quader", 3: "zufällig, breit gestreute Quader",
           4: "zufällig, kleine Quader", 5: "zufällig, flache Quader"}
ZUFALL_QUELLEN = (2, 3, 4, 5)
N_WERTE = (12, 20, 40)                    # Zahl der Quader der Zufallsinstanzen in der App

VERTEILUNGEN = (
    ("mittel", "mittlere Quader (alle Kanten 20 bis 60)", ((20, 60), (20, 60), (20, 60))),
    ("breit", "breit gestreute Quader (alle Kanten 5 bis 70)", ((5, 70), (5, 70), (5, 70))),
    ("klein", "kleine Quader (alle Kanten 10 bis 40)", ((10, 40), (10, 40), (10, 40))),
    ("flach", "flache Quader (Breite und Tiefe 30 bis 80, Höhe 5 bis 30)", ((30, 80), (30, 80), (5, 30))),
)
VERTEILUNG_KURZ = ("mittel", "breit", "klein", "flach")
VERTEILUNG_LANG = ("mittlere Quader", "breit gestreute Quader", "kleine Quader", "flache Quader")
VERTEILUNG_DAT = ("mittleren Quadern", "breit gestreuten Quadern", "kleinen Quadern", "flachen Quadern")

SCHLUESSEL = {0: "Lieferreihenfolge (nicht sortiert)", 1: "nach Volumen (größtes zuerst)", 2: "nach Grundfläche (größte zuerst)", 3: "nach Höhe (höchster zuerst)"}
SCHLUESSEL_KURZ = {0: "Lieferung", 1: "Volumen", 2: "Grundfläche", 3: "Höhe"}
SCHLUESSEL_MIT = {0: "der Lieferreihenfolge", 1: "dem Volumen", 2: "der Grundfläche", 3: "der Höhe"}
LIEFERUNG, VOLUMEN, GRUNDFLAECHE, HOEHE = 0, 1, 2, 3

S_MIN_WERTE = (0.0, 0.5, 0.8, 1.0)        # Mindest-Stützfläche; Regler und Raster nehmen diese vier Werte
S_MIN_TEXT = {0: "keine Bedingung", 1: "mindestens 50 %", 2: "mindestens 80 %", 3: "100 % (volle Auflage)"}
S_MIN_KURZ = {0: "0 %", 1: "50 %", 2: "80 %", 3: "100 %"}

REGELN = {0: "keine (tiefster, hinterster, linkester Punkt)", 1: "nah (Schwerpunkt möglichst in die Mitte)"}
REGEL_KURZ = {0: "keine", 1: "nah"}
FENSTER_STANDARD = 5                      # halbe Breite des Schwerpunktfensters (von 100)
FENSTER_MIN, FENSTER_MAX = 2, 20

FARBEN = {0: "Reihenfolge des Setzens", 1: "Stützfläche"}

SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Messraster ---------------------------------------------------------------------------------------------------------------------------
INSTANZEN = 100                           # Instanzen je Zelle; der Wert steht neben jeder Zahl
MESS_N = (20, 40, 80)
SCHWERPUNKT_SMIN_INDEX = 2                # im Schwerpunkt-Raster gilt die Mindest-Stützfläche 80 %
SCHWERPUNKT_SCHLUESSEL = GRUNDFLAECHE     # und der Schlüssel Grundfläche (der beste bei 80 %)
FENSTER_RASTER = (5, 10)                  # die zwei Fenster, nach denen das Raster zählt
SCHWELLEN = (0.5, 0.75)                   # Füllschwellen der harten Regel
# Varianten des Schwerpunkt-Rasters: Name -> (Regel, verschieben, Schwelle, Schlüssel-Art); Schlüssel-Art "masse" sortiert nach fallender Masse
VARIANTEN = {
    "keine": (0, False, None, "flaeche"),
    "keine_verschoben": (0, True, None, "flaeche"),
    "nah": (1, False, None, "flaeche"),
    "nah_verschoben": (1, True, None, "flaeche"),
    "nah_masse": (1, False, None, "masse"),
    "hart_50": (2, False, 0.5, "flaeche"),
    "hart_75": (2, False, 0.75, "flaeche"),
}
VARIANTEN_NAME = {"keine": "keine Regel", "keine_verschoben": "keine Regel, verschoben", "nah": "nah", "nah_verschoben": "nah, verschoben", "nah_masse": "nah, schwere zuerst",
                  "hart_50": "hart ab 50 % Füllung", "hart_75": "hart ab 75 % Füllung"}
FENSTER_OPT_N = {12: 40, 20: 20}          # Quaderzahl -> Instanzen je Verteilung für das CP-SAT-Orakel mit hartem Schwerpunktfenster
FENSTER_OPT_ZEIT = {12: 20.0, 20: 30.0}   # Sekunden je Instanz
CPSAT_ZEIT = 30.0
STICHPROBE_J = (0, 1, 2)                  # Instanzen jeder Zelle, die einzeln gespeichert und in den Tests frisch nachgerechnet werden

COLOR_LINE = "#c0392b"
COLOR_PUNKT = "#2F6B65"
COLOR_SCHWERPUNKT = "#000000"
COLOR_FENSTER = "#2F6B65"
KISTEN_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")
# Farben der Stützfläche: (untere Grenze, Farbe, Beschriftung), von oben nach unten; 0 Prozent = schwebend
STUETZ_FARBEN = ((1.0, "#54a24b", "100 %"), (0.8, "#b5cf6b", "80 bis unter 100 %"), (0.5, "#eeca3b", "50 bis unter 80 %"), (1e-12, "#f58518", "über 0 bis unter 50 %"), (0.0, "#e45756", "0 % (schwebt)"))
VERFAHREN_FARBEN = {0: "#9d755d", 1: "#4c78a8", 2: "#2F6B65", 3: "#b279a2"}

PRESETS = {
    "Beispiel 1, Volumen, ohne Stützbedingung": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "s_index": 0, "regel": 0, "verschieben": 0, "fenster": FENSTER_STANDARD,
                                                 "schritt": 0, "behaelter": 1, "farbe": 1},
    "Beispiel 1, Volumen, 80 % Stützfläche": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "s_index": 2, "regel": 0, "verschieben": 0, "fenster": FENSTER_STANDARD,
                                              "schritt": 0, "behaelter": 1, "farbe": 1},
    "Beispiel 1, Grundfläche, 80 % Stützfläche": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": GRUNDFLAECHE, "s_index": 2, "regel": 0, "verschieben": 0,
                                                  "fenster": FENSTER_STANDARD, "schritt": 0, "behaelter": 1, "farbe": 1},
    "Beispiel 2, Schwerpunkt: nah und verschoben": {"quelle": 1, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": GRUNDFLAECHE, "s_index": 2, "regel": 1, "verschieben": 1,
                                                    "fenster": FENSTER_STANDARD, "schritt": 0, "behaelter": 1, "farbe": 1},
    "Flache Quader, 40 Stück, 80 % Stützfläche": {"quelle": 5, "n_index": 2, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "s_index": 2, "regel": 0, "verschieben": 0,
                                                  "fenster": FENSTER_STANDARD, "schritt": 0, "behaelter": 1, "farbe": 1},
}
PRESET_HELP = {
    "Beispiel 1, Volumen, ohne Stützbedingung": "Zwölf Quader nach dem Volumen sortiert, ohne Stützbedingung: Sie passen alle in einen Behälter, das Optimum. Die Farbe zeigt, wie viel Auflage jeder Quader hat: Einige liegen auf weniger als der Hälfte.",
    "Beispiel 1, Volumen, 80 % Stützfläche": "Dieselben Quader, aber jeder muss auf mindestens 80 % seiner Grundfläche aufliegen: Mit dem Volumen als Schlüssel sind es jetzt zwei Behälter.",
    "Beispiel 1, Grundfläche, 80 % Stützfläche": "Dieselbe Bedingung mit der Grundfläche als Schlüssel: Es bleibt bei einem Behälter. Die Bedingung ändert nicht nur die Zahl, sondern auch den besten Schlüssel.",
    "Beispiel 2, Schwerpunkt: nah und verschoben": "Zwölf andere Quader mit Massen: Mit der Regel „nah“ und dem starren Verschieben liegt der Schwerpunkt im Fenster ±5 der Mitte; ohne Regel und ohne Verschieben liegt er außerhalb.",
    "Flache Quader, 40 Stück, 80 % Stützfläche": "Vierzig flache Quader: Mit dem Volumen als Schlüssel braucht die Bedingung sechs statt vier Behälter, mit der Grundfläche fünf. Flache Quader zahlen für die Stützfläche am meisten.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Quader mit ganzzahligen Maßen (Breite, Tiefe, Höhe), ohne Drehung; Behälter {CAP} mal {CAP} mal {CAP}; alle Quader sind vor dem Packen bekannt; jeder Quader kommt in den ersten Behälter, in dem ein Eckpunkt ihn aufnimmt (Stück 9, Extreme Points mit Projektionen). Die Masse jedes Quaders ist sein Volumen durch 1000 mal eine zufällige Dichte von 0,5 bis 2,0. **Mindest-Stützfläche:** Ein Eckpunkt ist nur zulässig, wenn der Quader dort auf mindestens diesem Anteil seiner Grundfläche aufliegt. **Schwerpunkt:** der Mittelwert der Mittelpunkte der Quader eines Behälters, gewichtet mit der Masse, in x und y; das Fenster ist die halbe Breite um die Mitte der Grundfläche.

**Grenzen.** Das Messraster deckt vier Verteilungen der Kanten und drei Quaderzahlen (20, 40, 80) ab, jeweils mit {INSTANZEN} Instanzen je Zelle, vier Schlüssel und vier Werte der Mindest-Stützfläche. Die Wahl unter den Eckpunkten ist ohne Schwerpunktregel immer der mit kleinstem (z, y, x). **Ein harter Schwerpunkt wird nicht geliefert:** Die Regeln „nah“ und „harte Regel ab einer Füllschwelle“ und das starre Verschieben gelten nur für diese Packungen, und die Anteile im Fenster stehen je Behälter. Ein Optimum mit Stützbedingung fehlt (sie ist im CP-SAT-Modell nicht abgebildet); das Orakel mit hartem Schwerpunktfenster (CP-SAT, {int(CPSAT_ZEIT)} Sekunden Zeitlimit je Instanz) gilt ohne Stützbedingung und nur bei 12 und 20 Quadern. Die Projektionen der Eckpunkte sind nach eigener Lesart umgesetzt (Stück 9). Dichten sind zufällig, keine Praxisdaten; Stapellast, Drehung und Gewichtsgrenzen je Behälter kommen nicht vor.

**Bekannte Probleme und Unsicherheiten.** Die Anteile im Schwerpunktfenster zählen Behälter, nicht Instanzen; der letzte Behälter einer Packung ist meist nur teilweise gefüllt; ob er häufiger außerhalb des Fensters liegt, hängt von der Zelle ab und ist nicht getestet (mit Verschieben vermutlich seltener, weil die dünn gefüllte Ladung Spielraum hat). Das starre Verschieben setzt Spielraum voraus: Füllt die Ladung die ganze Breite oder Tiefe oder liegt sie schon an einer Wand, bleibt wenig oder nichts zu verschieben. Zur Laufzeit macht die Demo keine Aussage. Die App wurde im Browser bedient (Presets, Würfel-Button, Regler und die 3D-Ansicht auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
