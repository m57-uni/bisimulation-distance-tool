from Controller import BisimulationsController

if __name__ == "__main__":
    controller = BisimulationsController()
    controller.start()

# TODO AKTUELLER STAND: HIER HABE ICH DIE ERSTEN ZWEI FENSTER
# TODO ZUM FUNKTIONIEREN GEBRACHT + MVC + STRUKTUR DES DRITTEN FENSTERS

# TODO ERSTES FENSTER: AUSWAHL ZWISCHEN EINLESEN ODER MANUELLE NUTZEREINGABEN

# TODO ZWEITES FENSTER: MANUELLE NUTZEREINGABEN DER DIMENSION LABELANZAHL ETC. UND BERECHNUNG + FEHLERMELDUGNEN

# TODO  DRITTES FENSTER: STRUKTUR IST VORHANDEN,
# TODO  ABER NOCH KEINE FUNKTIONALITÄT BZW. WEITERVERARBEITUNG, WENN MAN EINGABEN MACHT

# TODO  VIERTES FENSTER: STRUKTUR IST VORHANDEN + AUSGABEN WERDEN ANGEZEIGT


# TODO  durchzuführende Verbesserungen
# TODO  A) Auswahl-Fenster:
# TODO  A.1 Ein- und Auslesen von Textdateien -> führt zum Ergebnisfenster (Format bestimmen)
# TODO  Fehler suchen, rumprobieren

# TODO  B) Hauptfenster:
# TODO  B.1 Start-Button umbenennen in "zufällige Werte" -> führt zu Ergebnisfenster mit zufälligen Werten
# TODO  Fehler suchen, rumprobieren


# TODO  C) Berechnungsfenster:
# TODO  C.1 Radio-Buttons -> Methode aussuchen
# TODO  C.2 Eingaben erkennen für Labels, Wsk-Matrix
# TODO  C.3 Grenzen bestimmen: Nachkommastellen für WSK-Matrix, Eingabe in Label- und WSK-Vert.-Feld
# TODO  C.4 Fehlermeldungen bei falschen Eingaben
# TODO  C.5 Hinweisfeld für WSK-Matrix -> dynamische Hinweise während Laufzeit
# TODO  C.6 Zufällige Werte in die Eingabefelder
# TODO  C.7 Scroll-Möglichkeit, wenn zu viele Eingabefelder für Labels und WSK-Matrix
# TODO  Fehler suchen, rumprobieren


# TODO  D) Ergebnisfenster:
# TODO  D.1 Beenden-Button muss man zwei Male aktuell drücken
# TODO D.2 Ergebnisse sollen besser und übersichtlicher angezeigt werden (in einer Linie)
# TODO  D.3 Startwerte etwas besser positionieren
# TODO  D.4 Ergebnisse speichern -> einlesen bzw. auslesen Evaluation
# TODO  D.5 Neustart-Button
# TODO  Fehler suchen, rumprobieren
