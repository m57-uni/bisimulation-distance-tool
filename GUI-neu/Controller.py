from Model import BisimulationsModel
from View import BisimulationsView
import tkinter as tk
import tkinter.messagebox


class BisimulationsController:
    def __init__(self):
        self.model = None
        self.view = BisimulationsView(self)

    def start(self):
        self.view.auswahl_fenster()

    def starte_berechnung(self, dimension, label_anzahl, epsilon, lambda_wert, p_matrix, labels,choose, random=False):
        dimension, label_anzahl, epsilon, lambda_wert = self.validiere_eingaben(dimension, label_anzahl, epsilon,
                                                                                lambda_wert)

        ergebnisse = {}
        if dimension is not None and label_anzahl is not None and epsilon is not None and lambda_wert is not None:
            self.model = BisimulationsModel(dimension, label_anzahl, epsilon, lambda_wert,labels,p_matrix,random,choose)
            if random:
                labels = self.model.labels_zufall
                p_matrix = self.model.p_matrix_zufall
            verhaltens_metriken = self.model.verhaltens_metriken
            bisimulation_relation = self.model.bisimulation_relation
            bisimulare_zustaende = self.model.drucke_bisimulare_zustaende()
            verfahren = self.model.verfahren
            ergebnisse['labels'] = labels
            ergebnisse['verfahren'] = verfahren
            ergebnisse['P'] = p_matrix
            ergebnisse['verhaltens_metriken'] = verhaltens_metriken
            ergebnisse['bisimulation_relation'] = bisimulation_relation
            ergebnisse['bisimulare_zustaende'] = bisimulare_zustaende

        return ergebnisse

    @staticmethod
    def validiere_eingaben(dimension, label_anzahl, epsilon, lambda_wert):
        try:
            dimension = int(dimension)
            label_anzahl = int(label_anzahl)
            epsilon = float(epsilon)
            lambda_wert = float(lambda_wert)

            if dimension <= 0 or label_anzahl <= 0 or epsilon <= 0 or lambda_wert <= 0:
                tk.messagebox.showerror("Fehler", "Bitte geben Sie Werte größer als 0 ein.")
                return None, None, None, None

            return dimension, label_anzahl, epsilon, lambda_wert

        except ValueError:
            tk.messagebox.showerror("Fehler", "Ungültige Eingabe. Bitte überprüfen Sie Ihre Eingaben."
                                              "\n\nFür jedes Eingabefeld werden "
                                              "\nNUR Zahlenwerte größer als 0 akzeptiert."
                                              "\n\nD.h. keine Buchstaben (A,B,C,...) und keine Symbole(!&/§$)")
            return None, None, None, None
