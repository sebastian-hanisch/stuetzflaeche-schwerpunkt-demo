"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jeder Hilfetext stimmt mit der Rechnung überein."""

import stz_algorithm as A
import stz_constants as C
import stz_evaluation as ev
import stz_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    schluessel = ("quelle_select", "n_select", "seed_input", "schluessel_select", "smin_select", "regel_select", "verschieben_select", "fenster_input", "schritt_input", "behaelter_input", "farbe_select")
    assert [P.SETTING_SPECS[k].default for k in schluessel] == [s.quelle, s.n_index, s.seed, s.schluessel, s.s_index, s.regel, s.verschieben, s.fenster, s.schritt, s.behaelter, s.farbe]


def _a(name, **aender):
    return ev.analyse(ev.Settings(**{**{k: v for k, v in zip(("quelle", "n_index", "seed", "schluessel", "s_index", "regel", "verschieben", "fenster", "schritt", "behaelter", "farbe"),
                                                        (C.PRESETS[name][key] for key in P.PRESET_KEYS))}, **aender}))


def test_presets_behaupten_nur_was_stimmt():
    eins = _a("Beispiel 1, Volumen, ohne Stützbedingung")
    assert eins.count == 1 == eins.opt and eins.stuetz_min < 0.5 and "Sie passen alle in einen Behälter, das Optimum." in C.PRESET_HELP["Beispiel 1, Volumen, ohne Stützbedingung"]
    assert "Einige liegen auf weniger als der Hälfte" in C.PRESET_HELP["Beispiel 1, Volumen, ohne Stützbedingung"]
    zwei = _a("Beispiel 1, Volumen, 80 % Stützfläche")
    assert zwei.count == 2 and zwei.ohne == 1 and zwei.stuetz_min >= 0.8 and "sind es jetzt zwei Behälter" in C.PRESET_HELP["Beispiel 1, Volumen, 80 % Stützfläche"]
    drei = _a("Beispiel 1, Grundfläche, 80 % Stützfläche")
    assert drei.count == 1 and drei.ohne == 1 and "Es bleibt bei einem Behälter" in C.PRESET_HELP["Beispiel 1, Grundfläche, 80 % Stützfläche"]
    vier = _a("Beispiel 2, Schwerpunkt: nah und verschoben")
    assert vier.count == 1 and [ok for *_x, ok in vier.sp_ganz] == [True]
    nackt = _a("Beispiel 2, Schwerpunkt: nah und verschoben", regel=0, verschieben=0)
    assert [ok for *_x, ok in nackt.sp_ganz] == [False]                                    # ohne Regel und ohne Verschieben außerhalb des Fensters
    fuenf = _a("Flache Quader, 40 Stück, 80 % Stützfläche")
    assert (fuenf.count, fuenf.ohne, fuenf.inst.n) == (6, 4, 40) and fuenf.tabelle[C.GRUNDFLAECHE][2] == 5
    hilfe = C.PRESET_HELP["Flache Quader, 40 Stück, 80 % Stützfläche"]
    assert "sechs statt vier Behälter, mit der Grundfläche fünf" in hilfe
    assert all(A.packung_pruefen(x.inst.kisten, A.pack(x.inst.kisten, x.inst.masse, list(x.order), x.inst.cap, ev.s_min(x.settings), x.settings.regel)[1], x.inst.cap) for x in (eins, zwei, drei, vier, fuenf))


def test_beispiel_1_nur_volumen_kippt_mit_der_bedingung():
    """Die Aussage „die Bedingung ändert den besten Schlüssel“ im Handbeispiel: ohne Bedingung sind Volumen und Grundfläche gleich gut, mit 80 % nur noch die Grundfläche."""
    a = _a("Beispiel 1, Volumen, 80 % Stützfläche")
    assert ev.beste_schluessel(a.tabelle, 0) == [C.VOLUMEN, C.GRUNDFLAECHE] and ev.beste_schluessel(a.tabelle, 2) == [C.GRUNDFLAECHE] and ev.beste_schluessel(a.tabelle, 3) == [C.GRUNDFLAECHE]
