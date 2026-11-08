# Nebenbedingungen: Stützfläche und Schwerpunkt – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-stuetzflaeche-schwerpunkt-demo.streamlit.app/)**

Stück 10 der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Stück 9 hat Quader ohne Stützbedingung gepackt und gezählt, wie viele nicht sicher stehen. Diese Demo macht daraus **Nebenbedingungen**: Eine **Mindest-Stützfläche** ist hart (kein Eckpunkt, an dem ein Quader zu wenig aufliegt), und der **Schwerpunkt** jedes Behälters wird als Kennzahl, mit einer weichen Regel und durch starres Verschieben der Ladung behandelt. Die Fall-Demos zu Beladeplan und Gewicht (ULD) zeigen die Anwendung samt Kostenmodell; diese Demo erklärt den Mechanismus davor.

## Warum dieses Problem

Eine Stützbedingung ist für die meisten Beladungen selbstverständlich, und sie verändert das Packen mehr, als man erwartet: Sie kostet im Mittel über diese Zellen und mit diesem Dekodierer Behälter, und sie **ändert den besten Sortierschlüssel**. Bei zwölf Quadern, die ohne Bedingung in einen Behälter passen, braucht das Volumen als Schlüssel mit 80 % Stützfläche zwei, die Grundfläche bleibt bei einem. Beim Schwerpunkt gibt es eine ehrliche Antwort: Eine weiche Regel und das starre Verschieben helfen oft, aber **einen harten Schwerpunkt liefert dieses Verfahren nicht**; das Orakel (CP-SAT) zeigt, dass ohne Stützbedingung und bei 12 und 20 Quadern die Aufgabe selbst das Fenster ohne Mehrkosten erlaubt; die Heuristik erreicht es dort oft nicht. Mit Stützbedingung und bei mehr Quadern ist das nicht gemessen.

## Modell

Quader mit ganzzahliger Breite, Tiefe und Höhe und einer Masse, ohne Drehung, in Behältern der Größe 100 mal 100 mal 100, alle vorab bekannt. **Dekodierer:** Extreme Points mit Projektionen aus Stück 9 (eigene Lesart): jeder Quader kommt in den ersten Behälter, in dem ein Eckpunkt ihn aufnimmt, an den zulässigen Eckpunkt mit kleinstem (z, y, x). **Mindest-Stützfläche** s: Ein Eckpunkt ist nur zulässig, wenn der Quader dort auf mindestens dem Anteil s seiner Grundfläche aufliegt (auf dem Boden oder auf Oberseiten anderer Quader desselben Behälters); s = 0, 50, 80 oder 100 %. **Masse:** Volumen durch 1000 mal eine zufällige Dichte von 0,5 bis 2,0. **Schwerpunkt** eines Behälters: Mittelwert der Mittelpunkte seiner Quader, gewichtet mit der Masse, in x und y; das **Fenster** ist die halbe Breite um die Mitte der Grundfläche (±5 oder ±10). **Regel „nah“:** unter den zulässigen Eckpunkten der, bei dem der Schwerpunkt der Mitte am nächsten liegt. **Verschieben:** je Behälter alle Quader gemeinsam um dieselbe ganze Zahl in x und y, so nahe an die Mitte, wie die Hüllbox der Ladung erlaubt (Lage zueinander und Stützflächen bleiben). **Harte Regel ab einer Füllschwelle:** wie „nah“, aber ein Eckpunkt ist unzulässig, wenn der Behälter danach mehr als die Schwelle seines Volumens füllt und der Schwerpunkt außerhalb des Fensters läge. **Schranken:** das Volumen aller Quader durch das Behältervolumen, aufgerundet, und die Zahl der Quader, die in allen drei Maßen über die Hälfte reichen; das Größere von beiden (sie gelten ohne Stützbedingung). **Optimum** über alle Packungen mit CP-SAT (nur Generator und Tests; mit dem Schwerpunktfenster, ohne Stützbedingung). **Vier Verteilungen:** *mittel* (alle Kanten 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *flach* (Breite und Tiefe 30 bis 80, Höhe 5 bis 30). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`stz_algorithm.py`): `reihenfolge`, `pack` (Extreme Points mit Projektionen, Mindest-Stützfläche und Schwerpunktregel; liefert Behälter, Platzierungen und die Eckpunkte je Behälter; ein Anfang der Reihenfolge liefert den Zustand nach so vielen Schritten), `stuetzflaeche`, `schwerpunkt_behaelter`, `schwerpunkte`, `verschieben`, `schranken`, `packung_pruefen` (unabhängiger Prüfer).
- **Handbeispiele:** zwei feste Mengen von je zwölf Quadern mit Massen. Die App zeichnet einen gewählten Behälter in 3D (Farbe nach Stützfläche oder Reihenfolge, Schwerpunkt als Kreuz, Fenster am Boden, Eckpunkte) und zeigt alle 16 Kombinationen aus Schlüssel und Mindest-Stützfläche.
- **Messraster:** vier Verteilungen × drei Quaderzahlen (20, 40, 80) × **100 feste Instanzen** je Zelle × vier Schlüssel × vier Werte der Mindest-Stützfläche, dazu die Schwerpunkt-Varianten (Mindest-Stützfläche 80 %, Schlüssel Grundfläche). Maßstab ist die Schranke (vermutlich locker, wie in Stück 9 bei 12 und 20 Quadern gemessen; ein Optimum mit Stützbedingung gibt es nicht). Die Summen stehen als ganze Zahlen in `stz_precomputed.json` (erzeugt von `generate_precomputed.py`).
- **Orakel mit hartem Schwerpunktfenster:** bei 12 Quadern 40, bei 20 Quadern 20 Instanzen je Verteilung (eigene Seeds), CP-SAT mit 20 beziehungsweise 30 Sekunden Zeitlimit je Instanz, Fenster ±5, **ohne Stützbedingung** (sie lässt sich nicht linear ausdrücken).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_stuetzflaeche_schwerpunkt.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Schranke); die Anteile im Fenster zählen **Behälter**, nicht Instanzen.

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf Quader, Optimum 1) | Ohne Bedingung braucht das Volumen **1** Behälter, mit 80 % Stützfläche **2**; die Grundfläche bleibt bei **1** (Tabelle unten). Lieferung und Höhe brauchen mit jeder Bedingung 2 |
| Beispiel 2 (zwölf andere Quader, Optimum 1) | Mit 80 % Stützfläche und Grundfläche liegt der Schwerpunkt ohne Regel bei (47,0 / 40,0), mit „nah“ bei (47,3 / 41,6), ohne Regel verschoben bei (47,0 / 42,0): überall außerhalb des Fensters ±5. **Mit „nah“ und Verschieben** liegt er bei (47,3 / 49,6): im Fenster |
| Was kostet die Stützbedingung? | Im Mittel über die zwölf Zellen mit dem Volumen **+0,42 / +1,23 / +2,69** Behälter bei einer Mindest-Stützfläche von 50 / 80 / 100 %, mit der Grundfläche **+0,36 / +0,50 / +1,15**. Flache Quader zahlen am meisten (n = 80, Volumen: 2,19 → 3,69 / 6,33 / 12,58) |
| Ändert die Bedingung den besten Schlüssel? | **Ja.** Ohne Bedingung ist das Volumen in **10** von 12 Zellen allein der beste Schlüssel (zwei Zellen mit kleinen Quadern gleichauf mit anderen); mit 80 % und mit 100 % ist es die **Grundfläche in allen 12** Zellen. Bei 50 % ist es gemischt (Volumen allein in 8) |
| Instanz für Instanz | Von 1200 Instanzen braucht die Mindest-Stützfläche 80 % mit dem Volumen in **814** mehr Behälter als ohne Bedingung, mit der Grundfläche in **512**; bei 100 % in 1073 beziehungsweise 746 |
| Hilft die weiche Regel „nah“? | Sie bringt **1 bis 95 %** der Behälter ins Fenster ±5 (ohne Regel 1 bis 50 %): am meisten bei kleinen Quadern (n = 20: 38 → 95 %), kaum bei flachen (1 bis 3 %). Sie ändert die Behälterzahl um −0,22 bis +0,07 |
| Hilft das starre Verschieben? | Es kostet **keinen** Behälter. Mit „nah“ und Verschieben liegen **44 bis 100 %** der Behälter im Fenster ±5 und **69 bis 100 %** im Fenster ±10; **eine Garantie ist es nicht** (wo die Ladung die ganze Breite oder Tiefe füllt oder schon an einer Wand anliegt, bleibt wenig oder nichts zu verschieben) |
| Hilft „schwere zuerst“? | **Nein:** Der Schlüssel Masse (mit „nah“) braucht in allen 12 Zellen mehr Behälter als die Grundfläche (+0,16 bis +2,55) und bringt den Anteil im Fenster nirgends um mehr als 1 Prozentpunkt nach oben |
| Geht ein harter Schwerpunkt mit einer Füllschwelle? | **Nur teuer (ab 50 %) oder lückenhaft (ab 75 %):** Ab 50 % Füllung kostet die harte Regel bis zu **+1,89** Behälter gegenüber „nah“ (mittlere Quader, n = 80), und die Garantie gilt nur für die 0 bis 46 % der Behälter über der Schwelle; ab 75 % sind es höchstens +0,05 und 0 bis 20 % der Behälter |
| Was wäre im besten Fall möglich? | Das **Orakel** (freie Platzierung, ohne Stützbedingung, bei 12 und 20 Quadern): Das harte Fenster ±5 braucht in **236 von 236** entschiedenen Instanzen genauso viele Behälter wie ohne Fenster (4 von 240 nicht entschieden); die Heuristik erreicht das Fenster dort oft nicht. Mit Stützbedingung und bei mehr Quadern ist das nicht gemessen |

**Beispiel 1** (Behälterzahl je Schlüssel und Mindest-Stützfläche):

| Schlüssel | 0 % | 50 % | 80 % | 100 % |
|---|---|---|---|---|
| Lieferung | 2 | 2 | 2 | 2 |
| Volumen | 1 | 1 | 2 | 2 |
| Grundfläche | 1 | 1 | 1 | 1 |
| Höhe | 2 | 2 | 2 | 2 |

**Beispiel 2:**

| Schlüssel | 0 % | 50 % | 80 % | 100 % |
|---|---|---|---|---|
| Lieferung | 2 | 2 | 2 | 2 |
| Volumen | 1 | 1 | 1 | 1 |
| Grundfläche | 1 | 1 | 1 | 1 |
| Höhe | 1 | 2 | 2 | 2 |

**Behälter über der Schranke** (Mittel über 100 Instanzen je Zelle; Mindest-Stützfläche 0 / 50 / 80 / 100 %; kein Optimum, die Schranke ist vermutlich locker, dort zählt nur der Vergleich der Kombinationen):

| Verteilung | n | Volumen 0 / 50 / 80 / 100 % | Grundfläche 0 / 50 / 80 / 100 % |
|---|---|---|---|
| mittel | 20 | 0,61 / 0,73 / 0,95 / 1,32 | 0,75 / 0,88 / 0,92 / 1,05 |
| mittel | 40 | 1,16 / 1,46 / 1,75 / 2,34 | 1,46 / 1,63 / 1,67 / 1,85 |
| mittel | 80 | 1,98 / 2,32 / 2,62 / 3,42 | 2,24 / 2,47 / 2,54 / 2,64 |
| breit | 20 | 0,80 / 1,00 / 1,32 / 1,81 | 0,90 / 1,01 / 1,12 / 1,32 |
| breit | 40 | 1,21 / 1,40 / 1,89 / 2,83 | 1,46 / 1,56 / 1,63 / 1,95 |
| breit | 80 | 1,60 / 2,01 / 2,73 / 4,27 | 2,15 / 2,28 / 2,35 / 2,69 |
| klein | 20 | 0,00 / 0,01 / 0,21 / 0,68 | 0,00 / 0,00 / 0,06 / 0,42 |
| klein | 40 | 0,22 / 0,36 / 0,86 / 1,08 | 0,39 / 0,59 / 0,82 / 0,99 |
| klein | 80 | 0,03 / 0,21 / 0,91 / 1,24 | 0,07 / 0,21 / 0,48 / 0,93 |
| flach | 20 | 0,63 / 1,32 / 2,75 / 4,70 | 0,65 / 1,32 / 1,66 / 3,16 |
| flach | 40 | 1,19 / 2,12 / 4,04 / 7,57 | 1,21 / 2,18 / 2,33 / 4,25 |
| flach | 80 | 2,19 / 3,69 / 6,33 / 12,58 | 2,35 / 3,86 / 4,01 / 6,22 |

**Anteil der Behälter im Schwerpunktfenster** (Mindest-Stützfläche 80 %, Schlüssel Grundfläche):

| Verteilung | n | keine Regel ±5 | nah ±5 | keine, verschoben ±5 | nah, verschoben ±5 | nah, verschoben ±10 |
|---|---|---|---|---|---|---|
| mittel | 20 | 11 % | 19 % | 62 % | 68 % | 97 % |
| mittel | 40 | 20 % | 28 % | 57 % | 64 % | 96 % |
| mittel | 80 | 27 % | 39 % | 55 % | 64 % | 97 % |
| breit | 20 | 7 % | 12 % | 50 % | 56 % | 86 % |
| breit | 40 | 13 % | 19 % | 47 % | 50 % | 88 % |
| breit | 80 | 23 % | 30 % | 48 % | 52 % | 92 % |
| klein | 20 | 38 % | 95 % | 57 % | 100 % | 100 % |
| klein | 40 | 33 % | 51 % | 78 % | 91 % | 98 % |
| klein | 80 | 50 % | 69 % | 75 % | 89 % | 100 % |
| flach | 20 | 1 % | 1 % | 62 % | 64 % | 78 % |
| flach | 40 | 1 % | 2 % | 46 % | 50 % | 70 % |
| flach | 80 | 1 % | 3 % | 42 % | 44 % | 69 % |

**Die harte Regel ab einer Füllschwelle** (Mindest-Stützfläche 80 %, Schlüssel Grundfläche, Fenster ±5; „davon über der Schwelle“ = Anteil der Behälter, die über der Füllschwelle liegen und für die die Garantie gilt):

| Verteilung | n | nah: Behälter über Schranke | hart ab 50 %: Behälter über Schranke | davon über der Schwelle | hart ab 75 %: Behälter über Schranke | davon über der Schwelle |
|---|---|---|---|---|---|---|
| mittel | 20 | 0,90 | 1,24 | 15 % | 0,91 | 1 % |
| mittel | 40 | 1,70 | 2,51 | 23 % | 1,71 | 8 % |
| mittel | 80 | 2,44 | 4,33 | 31 % | 2,49 | 20 % |
| breit | 20 | 1,08 | 1,24 | 6 % | 1,08 | 0 % |
| breit | 40 | 1,61 | 2,16 | 11 % | 1,61 | 3 % |
| breit | 80 | 2,33 | 4,05 | 19 % | 2,34 | 14 % |
| klein | 20 | 0,05 | 0,05 | 0 % | 0,05 | 0 % |
| klein | 40 | 0,80 | 0,83 | 46 % | 0,80 | 0 % |
| klein | 80 | 0,55 | 0,84 | 35 % | 0,55 | 13 % |
| flach | 20 | 1,61 | 1,62 | 0 % | 1,61 | 0 % |
| flach | 40 | 2,31 | 2,52 | 0 % | 2,31 | 0 % |
| flach | 80 | 3,79 | 4,64 | 2 % | 3,79 | 0 % |

**Orakel mit hartem Schwerpunktfenster** (CP-SAT, ohne Stützbedingung, Mittel über die entschiedenen Instanzen):

| Verteilung | n | entschiedene Instanzen | Optimum ohne Fenster | Optimum mit Fenster ±5 | gleich viele Behälter |
|---|---|---|---|---|---|
| mittel | 12 | 39 von 40, 1 offen | 1,49 | 1,49 | 39 von 39 |
| breit | 12 | 40 von 40 | 1,43 | 1,43 | 40 von 40 |
| klein | 12 | 40 von 40 | 1,00 | 1,00 | 40 von 40 |
| flach | 12 | 40 von 40 | 1,57 | 1,57 | 40 von 40 |
| mittel | 20 | 19 von 20, 1 offen | 2,05 | 2,05 | 19 von 19 |
| breit | 20 | 20 von 20 | 2,15 | 2,15 | 20 von 20 |
| klein | 20 | 20 von 20 | 1,00 | 1,00 | 20 von 20 |
| flach | 20 | 18 von 20, 2 offen | 2,22 | 2,22 | 18 von 18 |

## Ehrliche Grenzen

- Alle Aussagen gelten für Quader ohne Drehung, vier Verteilungen mit festen Bereichen, Quaderzahlen 20, 40 und 80 im Raster (12 und 20 beim Orakel), eine Behältergröße, **zufällige Massen** (keine Praxisdaten), **einen** Dekodierer (Extreme Points mit Projektionen, eigene Lesart) mit der Wahl „tiefster, hinterster, linkester Eckpunkt“ beziehungsweise den Schwerpunktregeln. Stapellast, Gewichtsgrenzen je Behälter und Drehung kommen nicht vor.
- **Ein harter Schwerpunkt wird nicht geliefert.** Die Regeln und das Verschieben verbessern ihn, garantieren ihn aber nicht; die harte Regel ab einer Füllschwelle ist ein Gegenbeispiel. Das Orakel zeigt, was bei freier Platzierung möglich wäre.
- Ein **Optimum mit Stützbedingung** fehlt: CP-SAT kann die Stützfläche nicht linear ausdrücken. Das Orakel gilt ohne sie; die Schranken sind mit Bedingung nur eine untere Grenze.
- Die Anteile im Fenster zählen Behälter; der letzte Behälter einer Packung ist meist nur teilweise gefüllt und liegt ohne Verschieben häufiger außerhalb (mit Verschieben dagegen seltener, vermutlich weil die dünn gefüllte Ladung Spielraum hat).
- Die Projektionen der Eckpunkte sind nach eigener Lesart umgesetzt (Stück 9); es wird keine Zahl und keine Aussage der Literatur übernommen.
- Zur **Laufzeit** macht die Demo keine Aussage.

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Quader mit ganzzahligen Maßen (Breite, Tiefe, Höhe), ohne Drehung; Behälter 100 mal 100 mal 100; alle Quader sind vor dem Packen bekannt; jeder Quader kommt in den ersten Behälter, in dem ein Eckpunkt ihn aufnimmt (Stück 9, Extreme Points mit Projektionen). Die Masse jedes Quaders ist sein Volumen durch 1000 mal eine zufällige Dichte von 0,5 bis 2,0. **Mindest-Stützfläche:** Ein Eckpunkt ist nur zulässig, wenn der Quader dort auf mindestens diesem Anteil seiner Grundfläche aufliegt. **Schwerpunkt:** der Mittelwert der Mittelpunkte der Quader eines Behälters, gewichtet mit der Masse, in x und y; das Fenster ist die halbe Breite um die Mitte der Grundfläche.

**Grenzen.** Das Messraster deckt vier Verteilungen der Kanten und drei Quaderzahlen (20, 40, 80) ab, jeweils mit 100 Instanzen je Zelle, vier Schlüssel und vier Werte der Mindest-Stützfläche. Die Wahl unter den Eckpunkten ist ohne Schwerpunktregel immer der mit kleinstem (z, y, x). **Ein harter Schwerpunkt wird nicht geliefert:** Die Regeln „nah“ und „harte Regel ab einer Füllschwelle“ und das starre Verschieben gelten nur für diese Packungen, und die Anteile im Fenster stehen je Behälter. Ein Optimum mit Stützbedingung fehlt (CP-SAT kann sie nicht linear ausdrücken); das Orakel mit hartem Schwerpunktfenster (CP-SAT, 30 Sekunden Zeitlimit je Instanz) gilt ohne Stützbedingung und nur bei 12 und 20 Quadern. Die Projektionen der Eckpunkte sind nach eigener Lesart umgesetzt (Stück 9). Dichten sind zufällig, keine Praxisdaten; Stapellast, Drehung und Gewichtsgrenzen je Behälter kommen nicht vor.

**Bekannte Probleme und Unsicherheiten.** Die Anteile im Schwerpunktfenster zählen Behälter, nicht Instanzen; der letzte Behälter einer Packung ist meist nur teilweise gefüllt und liegt ohne Verschieben häufiger außerhalb (mit Verschieben dagegen seltener, vermutlich weil die dünn gefüllte Ladung Spielraum hat). Das starre Verschieben setzt Spielraum voraus: Füllt die Ladung die ganze Breite oder Tiefe oder liegt sie schon an einer Wand, bleibt wenig oder nichts zu verschieben. Zur Laufzeit macht die Demo keine Aussage. Die App wurde im Browser bedient (Presets, Würfel-Button, Regler und die 3D-Ansicht auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** alle Regeln an einer von Hand gerechneten Mini-Instanz (vier Quader mit Massen, Behälter 10 mal 10 mal 10: Eckpunkte nach jedem Schritt, die Stützfläche 43,75 / 87,5 / 100 % und die drei Packungen, der Schwerpunkt, das Verschieben, die Regel „nah“ und die harte Regel); Stützfläche (genau 80 %, 60 %, schwebend, anderer Behälter, andere Höhe); beide Handbeispiele mit allen 16 Behälterzahlen und den vier Schwerpunkt-Varianten von Beispiel 2; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein Quader, Quader gleich Behälter, Verschieben ohne Spielraum und an den Rändern, Fensterrand, Gleichstände, ungültige Eingaben, Grenzen der Regler).
- **Orakel** (`tests/test_oracle_stuetzflaeche_schwerpunkt.py`): der Dekodierer mit Mindest-Stützfläche und allen drei Schwerpunktregeln gegen eine Umsetzung, die die Eckpunkte nach jedem Quader neu erzeugt und die Stützfläche aus einem Voxelraster liest (7 Kombinationen, je 80 Läufe, mit mehreren Behältern und mit Wirkung der Bedingung); der Schwerpunkt gegen die Summe über alle Zellen eines Voxelrasters; das Verschieben gegen eine Suche über alle ganzzahligen Verschiebungen; jede Stützfläche mindestens s und nach dem Verschieben unverändert; das Optimum mit Fenster nie unter dem ohne Fenster; gemeinsames Skalieren.
- **Messraster:** jede Zelle bei n = 20 wird frisch gerechnet und exakt mit `stz_precomputed.json` verglichen, bei allen Zellen die ersten drei Instanzen einzeln (Stichprobe in der Datei); alle Zellen zusammen prüft `python generate_precomputed.py --check` (parallel). Das Orakel mit Fenster wird an einer Stichprobe der Instanzen mit CP-SAT nachgerechnet; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **3D-Darstellung:** Die zwölf Dreiecke je Quader decken jede der sechs Seitenflächen lückenlos und ohne Überlappung ab; die Farbe folgt der Stützfläche (`tests/test_visualization.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, jeder Hilfetext stimmt mit der Rechnung überein; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Zahlenfelder an den Grenzen) und Footer-Test.
- **Tests gesamt:** 155 (Stand 2026-11-08, alle grün; ohne ortools werden die CP-SAT-Proben übersprungen).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/opt.py` | exaktes Optimum mit CP-SAT, mit und ohne Schwerpunktfenster (nur für Generator und Tests) |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Messzellen und dem Text der Annahmen zusammen |
| `generate_precomputed.py` | erzeugt `stz_precomputed.json` (Messraster, Orakel mit CP-SAT, Stichprobe); `--check` vergleicht, `--keep-fenster` behält das gespeicherte Orakel, `--nur-stichprobe` ergänzt die Stichprobe |
| `requirements-dev.txt` | Laufzeit plus pytest und ortools |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `stz_algorithm.py` | Kern: Schlüssel, Dekodierer mit Stützfläche und Schwerpunktregeln, Verschieben, Schranken, Packungsprüfer |
| `stz_constants.py` | Beispiele, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `stz_evaluation.py` | Analyse, Verdikte, Messzellen |
| `stz_layout.py` | Fester Kopf (Stylesheet) und Tabellen auf dem Telefon |
| `stz_precomputed.json` | vorberechnete Summen, Orakel und Stichprobe des Messrasters |
| `stz_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `stz_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit Massen und festen Seeds |
| `stz_visualization.py` | Plotly-Abbildungen (3D-Behälter mit Farbe nach Stützfläche, Schwerpunkt und Fenster; Balken mit gesperrten Achsen) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, 3D-Darstellung, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Ein harter Schwerpunkt als Konstruktion:** Phase 0 zeigt, dass die Heuristik ihn nicht liefert; die Demo zeigt die Grenze und das Orakel.
- **Optimum mit Stützbedingung:** nicht linear ausdrückbar; kein Optimum, nur Schranke und Vergleich.
- **Stapellast, Gewichtsgrenzen, Drehung, Entladereihenfolge:** nicht Gegenstand dieses Stücks (Entladereihenfolge: gelbes Stück 11).
- **Laufzeitvergleich:** hängt an der Umsetzung, keine Aussage.
- **Gütegarantien und Zahlen aus der Literatur:** keine übernommen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
