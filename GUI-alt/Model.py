import numpy as np
import scipy.optimize


class BisimulationsModel:
    def __init__(self, dimension, label_anzahl, epsilon, lambda_wert):
        self.dimension = dimension
        self.label_anzahl = label_anzahl
        self.epsilon = epsilon
        self.lambda_wert = lambda_wert
        self.labels = self.erstelle_labels()
        self.P = self.erstelle_wsk_matrix()
        self.verhaltens_metriken = self.berechne_verhaltens_metriken()
        self.bisimulation_relation = self.pruefe_bisimulationsrelation()

    def erstelle_labels(self):
        # return [0, 0, 1]                                              # zum Testen Entkommentieren
        return np.random.randint(0, self.label_anzahl, self.dimension)  # Zur manuellen Eingabe auskommentieren

    # def erstelle_labels(self, benutzer_labels):
    #     if benutzer_labels is not None:
    #         return benutzer_labels


    def erstelle_wsk_matrix(self):
        #    P = [[0, 1, 0], [0.5, 0, 0.5], [0, 0, 1]]      # Zum Testen Entkommentieren
        P = np.random.rand(self.dimension, self.dimension)  # Zur manuellen Eingabe auskommentieren
        P /= P.sum(axis=1)[:, np.newaxis]  # Zur manuellen Eingabe auskommentieren

        # Erklärung darüberliegende Zeile:
        # Summe = 1 bei jeder Zeile;
        # axis=1 -> horizontal
        # [:, np.newaxis] -> 1D zu 2D-Form
        # P /= ... -> Sicherstellen, dass P eine Wsk-Matrix ist,
        # bei der jede Zeile die Summe gleich 1 ist
        return P

    def berechne_verhaltens_metriken(self):  # Lambda Wert hier (vllt später wichtig)
        d = np.zeros((self.dimension, self.dimension))
        delta_d = self.kleene_discount_factor(d)

        d_prev = d.copy()  # tiefe-Kopie der Matrix d^(n-1)
        d = delta_d.copy()  # d^(n)

        while np.linalg.norm(d - d_prev) >= self.epsilon:  # ||d^(n) - d^(n-1)|| < Epsilon
            d_prev = d.copy()
            d = self.kleene_discount_factor(d)  # d^(n)
        return d

    ###----------------------------------------------------------
    # Fixpunktiterationen
    # 1. Kleene-Iteration von unten
    # 2. Kleene-Iteration von oben, wobei bisimulare Zustände Abstand 0 haben
    # 3. Mit Aufrunden auf 1, wenn Abstand größer 0
    # 4. Iteration von oben (FEHLT NOCH)

    def kleene_delta(self, d):
        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.labels[i] != self.labels[j]:
                    d[i, j] = 1
                    d[j, i] = 1                                                 # Symmetrie einhalten, auch in else-verzweigung eingebaut mit d[j, i] = d[i, j]
                else:
                    d[i, j] = self.berechne_kantorovich_abstand(self.P[i], self.P[j], d)       # P[i] Zeile der Wsk-Verteilung für Zustand mue
                                                                                # d fungiert hier als Übertrager der Dimension
                    d[j, i] = d[i, j]                                           # P[j] Zeile der Wsk-Verteilung für Zustand nue

        return d


    def kleene_gross_lambda(self, d):
        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.labels[i] != self.labels[j]:
                    d[i, j] = 1
                    d[j, i] = 1
                else:
                    kantorovich_abstand = self.berechne_kantorovich_abstand(self.P[i], self.P[j], d)
                    if kantorovich_abstand == 0:
                        d[i, j] = 0
                        d[j, i] = 0
                    else:
                        d[i, j] = kantorovich_abstand
                        d[j, i] = kantorovich_abstand
        return d


    #Anpassung mit Aufrundung auf 1, wenn Abstand größer 0
    def kleene_delta_dach(self, d):
        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.labels[i] != self.labels[j]:
                    d[i, j] = 1
                    d[j, i] = 1                                                         # Symmetrie einhalten, auch in else-verzweigung eingebaut mit d[j, i] = d[i, j]
                else:
                    kantorovich_abstand = self.berechne_kantorovich_abstand(self.P[i], self.P[j], d)
                    if kantorovich_abstand > 0:
                        d[i, j] = 1
                        d[j, i] = 1
                    else:
                        d[i, j] = kantorovich_abstand                                   # P[i] Zeile der Wsk-Verteilung für Zustand mue
                        d[j, i] = kantorovich_abstand                                   # P[j] Zeile der Wsk-Verteilung für Zustand nue
                                                                                        # d fungiert hier als Übertrager der Dimension

        return d

    def kleene_discount_factor(self, d):
        #lambdaa = get_lambdaa()  # den Discount-Faktor Lambda anfordern

        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.labels[i] != self.labels[j]:
                    d[i, j] = 1
                    d[j, i] = 1
                else:
                    kantorovich_abstand = self.berechne_kantorovich_abstand(self.P[i], self.P[j], d)
                    d[i, j] = self.lambda_wert * kantorovich_abstand
                    d[j, i] = self.lambda_wert * kantorovich_abstand

        return d


    def berechne_kantorovich_abstand(self, mue, nue, d_matrix):
        c_vektor = d_matrix.flatten()  # distanz-Matrix zu einer Kostenmatrix umwandeln
        A_eq_mue = np.zeros((self.dimension, self.dimension ** 2))  # Matrix vorbereiten
        A_eq_nue = np.zeros((self.dimension, self.dimension ** 2))  # -> Spalten quadriert, damit alle Konstellationen für mue und nue berücksichtigt werden

        for k in range(self.dimension):
            A_eq_mue[k, k * self.dimension:(k + 1) * self.dimension] = 1  # Verkettung der benachbarten 1-en führen zum entsprechend gewählten Wert von mue
            A_eq_nue[k, k::self.dimension] = 1                                              # Verkettung von 1-en und 0-en führen zum entsprechend gewählten Wert von nue

        A_eq = np.vstack((A_eq_mue, A_eq_nue))  # Zusammenfügen der beiden Hälften mue und nue um die Matrix A zu vervollständigen
        print(mue)
        # print(nue)
        b_eq = np.concatenate((mue, nue))  # b (von Ax=b)
        bounds = [(0, 1) for _ in range(self.dimension ** 2)]  # bounds zwischen 0 und 1

        result = scipy.optimize.linprog(c_vektor, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if result.success:  # Überprüfung, ob Optimierung eine Lösung gefunden hat
            return result.fun
        #        print("Der Kantorovich-Abstand ist: ", result.fun)  # Ausgabe vom minimalstem Wert
        #        print("Die dazugehörigen Unbekannten sind: ", result.x)
        else:
            raise ValueError(
                "Es gab ein Problem bei der Optimierung: " + result.message)  # Infos über Erfolg/Misserfolg der Optimierung

    def pruefe_bisimulationsrelation(self):
        dimension = self.verhaltens_metriken.shape[0]
        bisimulation_relation = np.zeros((dimension, dimension), dtype=bool)

        for i in range(dimension):
            for j in range(dimension):
                if self.verhaltens_metriken[i, j] <= self.epsilon:
                    bisimulation_relation[i, j] = True
        return bisimulation_relation

    def drucke_bisimulare_zustaende(self):
        bisimulare_zustaende = ""
        for i in range(self.dimension):
            for j in range(self.dimension):
                if i != j and self.bisimulation_relation[i, j]:
                    bisimulare_zustaende += f"Zustände {i} und {j} sind bisimular (d[{i}, {j}] = 0).\n"
        return bisimulare_zustaende
