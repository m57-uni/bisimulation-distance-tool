import numpy as np
import scipy.optimize
import time
import datetime

def erstelle_labels(dimension, label_anzahl):
# return [0, 0, 1]                                      ### Zum Testen Entkommentieren
   return np.random.randint(0, label_anzahl, dimension) ## Zur manuellen Eingabe auskommentieren ---------------------------------


def erstelle_wsk_matrix(dimension):
#    P = [[0, 1, 0], [0.5, 0, 0.5], [0, 0, 1]]          ### Zum Testen Entkommentieren
    P = np.random.rand(dimension, dimension)            ## Zur manuellen Eingabe auskommentieren ---------------------------------
    P /= P.sum(axis=1)[:, np.newaxis]                   ## Zur manuellen Eingabe auskommentieren ---------------------------------
    return P                                            # Summe = 1 bei jeder Zeile;
                                                        # axis=1 -> horizontal
                                                        # [:, np.newaxis] -> 1D zu 2D-Form
                                                        # P /= ... -> Sicherstellen, dass P eine Wsk-Matrix ist, bei der jede Zeile die Summe gleich 1 ist

def get_input(aufforderung, cast_type=int, bedingung=None, error_message="Ungültige Eingabe. Bitte versuchen Sie es erneut.", standard_wert_enter=None):
    while True:
        try:
            nutzer_eingabe = input(aufforderung)
            if nutzer_eingabe == "":
                if standard_wert_enter is not None:
                    return standard_wert_enter
                else:
                    print("Eingabe kann nicht leer sein.")
                    continue
            nutzer_eingabe = cast_type(nutzer_eingabe)
            if bedingung and not bedingung(nutzer_eingabe):
                print(error_message)
                continue
            return nutzer_eingabe
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine Nummer ein.")


def get_dimension():
    return get_input("Gebe die Dimension bzw. die Anzahl der Zustände ein: ",
                     bedingung=lambda x: x > 0,
                     error_message="Die Dimension bzw. die Anzahl der Zustände muss größer als 0 sein.")


def get_label_anzahl():
    return get_input("Gebe die Anzahl der Labels ein: ",
                     bedingung=lambda x: x > 0,
                     error_message="Die Anzahl der Labels muss größer als 0 sein.")


def get_epsilon():
    return get_input("Gebe den Schwellenwert Epsilon in wissenschaftlicher Notation ein (z.B. 1e-10, Default = 1e-10): ",
                     cast_type=float,
                     bedingung=lambda x: x > 0,
                     error_message="Der Schwellenwert Epsilon muss größer als 0 sein.",
                     standard_wert_enter=1e-10)

def get_lambdaa():
    return get_input("Gebe den Discount-Faktor Lambda an: ",
                     cast_type=float,
                     bedingung=lambda x: 0 <= x <= 1,
                     error_message="Der Discount-Faktor Lambda muss zwischen 0.0 und 1.0 liegen.")



def get_system_anzahl():
    return get_input("Gebe die Anzahl der Systeme ein (Enter = 100): ",  # Enter = 100 -> Das ist der Standardwert, wenn man Enter drückt. Man spart Zeit bei Evaluierung
                     bedingung=lambda x: x > 0,
                     error_message="Die Anzahl der Systeme muss größer als 0 sein.",
                     standard_wert_enter=100)


def get_kleene_verfahren():
    while True:
        verfahren_input = input(
            "Wähle das Iterationsverfahren aus \n1 - Delta, \n2 - Groß Lambda, \n"
            "3 - Delta Dach, \n4 - Delta Klein Lambda (Discount-Faktor)). \n"
            "Mehrere Verfahren mit Komma trennen. Für alle Verfahren Enter drücken (Enter = 1,2,3,4): ")
        if verfahren_input == "":
            return [1, 2, 3, 4]
        else:
            try:
                verfahren_liste = [int(x) for x in verfahren_input.split(",") if x.isdigit() and int(x)
                                in [KLEENE_DELTA, KLEENE_GROSS_LAMBDA,
                                    KLEENE_DELTA_DACH, KLEENE_DISCOUNT_FACTOR]]
                if len(verfahren_liste) == 0:
                    print("Ungültige(s) Verfahren ausgewählt. Bitte wähle aus 1, 2, 3 und/oder 4.")
                else:
                    return verfahren_liste
            except ValueError:
                print("Ungültige Eingabe. Bitte geben Sie gültige Werte ein.")


# def kleene_gross_lambda(dimension, labels, P, epsilon):
#     def verfahren_case(mue, nue, d):
#         kantorovich_abstand = berechne_kantorovich_abstand(mue, nue, d)
#         return 0 if kantorovich_abstand == 0 else kantorovich_abstand
#
#     return kleene_iteration(dimension, labels, P, epsilon, verfahren_case)[0]


def kleene_iteration(dimension, labels, P, epsilon, update_rule):
    d = np.zeros((dimension, dimension))
    d_prev = d.copy()
    iterations = 0

    while True:
        iterations += 1
        for i in range(dimension):
            for j in range(dimension):
                if labels[i] != labels[j]:
                    d[i, j] = 1
                    d[j, i] = 1
                else:
                    d[i, j] = update_rule(P[i], P[j], d)
                    d[j, i] = d[i, j]

        if np.linalg.norm(d - d_prev) < epsilon:
            break
        d_prev = d.copy()

    return d, iterations


def kleene_delta(dimension, labels, P, epsilon):
    def verfahren_case(mue, nue, d):
        return berechne_kantorovich_abstand(mue, nue, d)

    return kleene_iteration(dimension, labels, P, epsilon, verfahren_case)[0]


def kleene_delta_dach(dimension, labels, P, epsilon):
    def verfahren_case(mue, nue, d):
        kantorovich_abstand = berechne_kantorovich_abstand(mue, nue, d)
        return 1 if kantorovich_abstand > 0 else kantorovich_abstand

    return kleene_iteration(dimension, labels, P, epsilon, verfahren_case)[0]


def kleene_gross_lambda(dimension, labels, P, epsilon):
    bisi_matrix = np.full((dimension, dimension), False, dtype=bool)

    def verfahren_case(i, j, d):
        if bisi_matrix[i, j]:
            return 0
        else:
            kantorovich_abstand = berechne_kantorovich_abstand(P[i], P[j], d)
            bisi_matrix[i, j] = kantorovich_abstand == 0
            return kantorovich_abstand

    return kleene_iteration(dimension, labels, P, epsilon, verfahren_case, bisi_matrix)[0]


def kleene_discount_factor(dimension, labels, P, epsilon, lambdaa=0.5):
    def verfahren_case(mue, nue, d):
        kantorovich_abstand = berechne_kantorovich_abstand(mue, nue, d)
        return lambdaa * kantorovich_abstand

    return kleene_iteration(dimension, labels, P, epsilon, verfahren_case)[0]


def berechne_kantorovich_abstand(mue, nue, d_matrix, dimension):
    c_vektor = d_matrix.flatten()                           #distanz-Matrix zu einer Kostenmatrix umwandeln
    A_eq_mue = np.zeros((dimension, dimension ** 2))        #Matrix vorbereiten
    A_eq_nue = np.zeros((dimension, dimension ** 2))        #-> Spalten quadriert, damit alle Konstellationen für mue und nue berücksichtigt werden

    for k in range(dimension):
        A_eq_mue[k, k * dimension:(k + 1) * dimension] = 1  #Verkettung der benachbarten 1-en führen zum entsprechend gewählten Wert von mue
        A_eq_nue[k, k::dimension] = 1                       #Verkettung der benachbarten 1-en führen zum entsprechend gewählten Wert von mue

    A_eq = np.vstack((A_eq_mue, A_eq_nue))                  #Zusammenfügen der beiden Hälften mue und nue um die Matrix A zu vervollständigen
    b_eq = np.concatenate((mue, nue))                       # b (von Ax=b)
    bounds = [(0, 1) for _ in range(dimension ** 2)]        # bounds zwischen 0 und 1

    result = scipy.optimize.linprog(c_vektor, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    if result.success:                                      # Überprüfung, ob Optimierung eine Lösung gefunden hat
        return result.fun
#        print("Der Kantorovich-Abstand ist: ", result.fun)  # Ausgabe vom minimalstem Wert
#        print("Die dazugehörigen Unbekannten sind: ", result.x)
    else:
        raise ValueError("Es gab ein Problem bei der Optimierung: " + result.message) # Infos über Erfolg/Misserfolg der Optimierung

#---------------------------------------------------------------------------------------------------
def pruefe_bisimulationsrelation(d, epsilon):
    dimension = d.shape[0]
    bisimulation_relation = np.zeros((dimension, dimension), dtype=bool)

    for i in range(dimension):
        for j in range(dimension):
            if d[i, j] <= epsilon:
                bisimulation_relation[i, j] = True

    return bisimulation_relation


KLEENE_DELTA = 1
KLEENE_GROSS_LAMBDA = 2
KLEENE_DELTA_DACH = 3
KLEENE_DISCOUNT_FACTOR = 4

def starte_kleene_iteration(verfahren, dimension, labels, P, epsilon):
    # Startzeitpunkt aufzeichnen
    start_zeit = time.time()

    if verfahren == KLEENE_DELTA:
        verfahren_case = lambda mue, nue, d: berechne_kantorovich_abstand(mue, nue, d, dimension)
    elif verfahren == KLEENE_GROSS_LAMBDA:
        verfahren_case = lambda mue, nue, d: 0 if berechne_kantorovich_abstand(mue, nue, d, dimension) == 0 \
            else berechne_kantorovich_abstand(mue, nue, d, dimension)
    elif verfahren == KLEENE_DELTA_DACH:
        verfahren_case = lambda mue, nue, d: 1 if berechne_kantorovich_abstand(mue, nue, d, dimension) > 0 \
            else berechne_kantorovich_abstand(mue, nue, d, dimension)
    elif verfahren == KLEENE_DISCOUNT_FACTOR:
        lambdaa = 1.0  # Kann durch Benutzereingabe ersetzt werden
        verfahren_case = lambda mue, nue, d: lambdaa * berechne_kantorovich_abstand(mue, nue, d, dimension)
    else:
        print("Ungültige(s) Verfahren ausgewählt.")
        return None, 0, 0

    ergebnis, iteration_anzahl = kleene_iteration(dimension, labels, P, epsilon, verfahren_case)

    # Zeit messen
    verstrichene_Zeit = time.time() - start_zeit

    return ergebnis, verstrichene_Zeit, iteration_anzahl


if __name__ == "__main__":
    # input Werte bekommen
    dimension = get_dimension()
    label_anzahl = get_label_anzahl()
    epsilon = get_epsilon()
    verfahren_menge = get_kleene_verfahren()
    system_anzahl = get_system_anzahl()

    start_datum = datetime.datetime.now()

    zeiten = [0, 0, 0, 0]
    iterationen = [0, 0, 0, 0]

    for i in range(system_anzahl):
        print(f"\n\nErzeuge System {i + 1} und führe Verfahren aus...\n")
        labels = erstelle_labels(dimension, label_anzahl)
        P = erstelle_wsk_matrix(dimension)
        print("Dies sind die folgenden Labels:\n", labels, "\n")                                                           #Auskommentieren wenn man nicht braucht
        print("Dies sind unsere Wahrscheinlichkeitsverteilungen im Form der Matrix P:\n", P, "\n")                         #Auskommentieren wenn man nicht braucht

        for verfahren in verfahren_menge:
            verhaltens_metriken, verstrichene_zeit, iterations_anzahl = starte_kleene_iteration(verfahren, dimension, labels, P,
                                                                                                epsilon)
            bisimulation_relation = pruefe_bisimulationsrelation(verhaltens_metriken, epsilon)
            zeiten[verfahren - 1] += verstrichene_zeit
            iterationen[verfahren - 1] += iterations_anzahl
            print(f"Verhaltensmetriken für System {i + 1} mit Verfahren {verfahren}:\n", verhaltens_metriken, "\n\n")        #Auskommentieren wenn man nicht braucht
            print(f"Bisimulationsrelation für System {i + 1} mit Verfahren {verfahren}:\n", bisimulation_relation, "\n\n")   #Auskommentieren wenn man nicht braucht

    end_zeitpunkt = datetime.datetime.now()
    gesamte_zeit = end_zeitpunkt - start_datum

    for i, (zeit, iterationen_insgesamt) in enumerate(zip(zeiten, iterationen)):
        print(f"\n\nGesamtzeit für Verfahren {i + 1}: {zeit} Sekunden")
        print(f"Anzahl der Iterationen für Verfahren {i + 1}: {iterationen_insgesamt}")

    print("\nStartzeitpunkt der Berechnung: ", start_datum.strftime("%d.%m.%Y, %H:%M:%S"))
    print("Endzeitpunkt der Berechnung: ", end_zeitpunkt.strftime("%d.%m.%Y, %H:%M:%S"))
    print(f"Gesamtlaufzeit der Berechnung: {gesamte_zeit.total_seconds()} Sekunden")