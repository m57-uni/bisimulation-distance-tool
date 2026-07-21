import tkinter as tk
from tkinter import IntVar
# from tkinter import ttk
from tkinter import HORIZONTAL, Scrollbar, Text


class BisimulationsView:
    def __init__(self, controller):
        self.eingabe_dimension = None
        self.eingabe_label_anzahl = None
        self.eingabe_epsilon = None
        self.eingabe_lambda = None
        self.controller = controller

    @staticmethod
    def zentriere_fenster(fenster):
        fenster.update_idletasks()
        breite = fenster.winfo_width()
        hoehe = fenster.winfo_height()
        x = (fenster.winfo_screenwidth() // 2) - (breite // 2)
        y = (fenster.winfo_screenheight() // 2) - (hoehe // 2)
        fenster.geometry(f'{breite}x{hoehe}+{x}+{y}')

    def auswahl_fenster(self):
        aw_fenster = tk.Tk()
        aw_fenster.title("Auswahl-Fenster")
        aw_fenster.resizable(False, False)

        tk.Label(aw_fenster,
                 text="Möchtest du eine manuelle Eingaben machen \noder eine Datei einlesen,"
                      "\nin welchem sich ein Transitionssystem zur Berechnung befindet?").grid(
            row=0,
            column=0,
            columnspan=2)

        tk.Button(aw_fenster, text="Manuelle Eingabe",
                  command=lambda: [aw_fenster.destroy(), self.haupt_fenster()]).grid(row=1, column=0)
        tk.Button(aw_fenster, text="Einlesen einer Datei mit Transitionssystem",
                  command=self.ergebnis_fenster).grid(row=1, column=1)

        self.zentriere_fenster(aw_fenster)
        aw_fenster.mainloop()

    def haupt_fenster(self):
        h_fenster = tk.Tk()
        h_fenster.title("Wertevergabe für die Grundbausteine des Transitionssystems")
        h_fenster.resizable(False, False)

        tk.Label(h_fenster, text="Dimension bzw. Anzahl der Zustände:").grid(row=0, column=0, sticky="w")
        self.eingabe_dimension = tk.Entry(h_fenster)
        self.eingabe_dimension.grid(row=0, column=1)

        tk.Label(h_fenster, text="Anzahl der Labels:").grid(row=1, column=0, sticky="w")
        self.eingabe_label_anzahl = tk.Entry(h_fenster)
        self.eingabe_label_anzahl.grid(row=1, column=1)

        tk.Label(h_fenster, text="Schwellenwert Epsilon in wissenschaftlicher Notation eingeben (z.B. 1e-10):").grid(
            row=2, column=0, sticky="w")
        self.eingabe_epsilon = tk.Entry(h_fenster)
        self.eingabe_epsilon.grid(row=2, column=1)
        self.eingabe_epsilon.insert(0, "1e-10")

        tk.Label(h_fenster, text="Skalierungswert Lambda eingeben (z.B. 1.0):").grid(row=3, column=0, sticky="w")
        self.eingabe_lambda = tk.Entry(h_fenster)
        self.eingabe_lambda.grid(row=3, column=1)
        self.eingabe_lambda.insert(0, "1.0")

        weiter_button = tk.Button(h_fenster, text="Weiter",
                                  command=lambda: self.erstelle_berechnungs_fenster(self.eingabe_dimension,
                                                                                    self.eingabe_label_anzahl))
        weiter_button.grid(row=4, column=2, padx=10, pady=10, sticky="w")

        start_button = tk.Button(h_fenster, text="Zufällige Wahrscheinlichkeitsverteilung & Labels",
                                 command=lambda: self.starte_berechnung_haupt(
                                     self.eingabe_dimension, self.eingabe_label_anzahl,
                                     self.eingabe_epsilon, self.eingabe_lambda))
        start_button.grid(row=4, column=1, padx=10, pady=10)

        tk.Button(h_fenster, text="Zurück",
                  command=lambda: [h_fenster.destroy(), self.auswahl_fenster()]).grid(row=4, column=0, padx=10, pady=10,
                                                                                      sticky="e")

        self.zentriere_fenster(h_fenster)
        h_fenster.mainloop()

    def erstelle_berechnungs_fenster(self, eingabe_dimension, eingabe_label_anzahl):
        dimension = int(eingabe_dimension.get())
        label_anzahl = int(eingabe_label_anzahl.get())
        self.berechnungs_fenster(self, dimension, label_anzahl)

    @staticmethod
    def berechnungs_fenster(self, matrix_dim, label_anzahl):
        b_fenster = tk.Toplevel()
        b_fenster.title("Wertevergabe der Wahrscheinlichkeitsverteilungen und der Labels")
        b_fenster.state('zoomed')
        b_fenster.resizable(True, True)

        # Spalten-Konf.-------------------------------------------------------------------------------------------------
        b_fenster.columnconfigure(matrix_dim, minsize=60)
        b_fenster.columnconfigure(0, weight=1)
        b_fenster.columnconfigure(1, weight=1)
        b_fenster.columnconfigure(2, weight=1)

        for j in range(matrix_dim):
            b_fenster.columnconfigure(j, weight=1, uniform="col")

        # Label-Eingabe-------------------------------------------------------------------------------------------------
        label_frame = tk.Frame(b_fenster)
        label_frame.grid(row=1, column=0, columnspan=matrix_dim)

        wunsch_label = tk.Label(b_fenster,
                                text="Gebe deine beliebigen Label an:")
        wunsch_label.grid(row=0, column=0, columnspan=matrix_dim)

        def begrenze_eingabe(P):
            if len(P) > 1:
                return False
            return True

        cmd = (b_fenster.register(begrenze_eingabe), '%P')

        self.label_eingaben = []
        for i in range(label_anzahl):
            label_eingabe_feld = tk.Entry(label_frame, width=5, validate='key', validatecommand=cmd)
            label_eingabe_feld.grid(row=0, column=i * 2)
            if i < label_anzahl - 1:
                trennzeichen = tk.Label(label_frame, text="|")
                trennzeichen.grid(row=0, column=i * 2 + 1)
            self.label_eingaben.append(label_eingabe_feld)



        # Matrix--------------------------------------------------------------------------------------------------------
        matrix_frame = tk.Frame(b_fenster)
        matrix_frame.grid(row=4, rowspan=matrix_dim, column=0, columnspan=matrix_dim, padx=0, pady=(0, 0))

        matrix_label_text = tk.Label(b_fenster, text="\n\n\nFülle die folgenden Felder mit Eingaben aus,\n"
                                                     "um eine Wahrscheinlichkeitsverteilung zu erstellen.\n"
                                                     "Beachte hierbei, dass jede Zeile "
                                                     "insgesamt 1.0 bzw. 100% ergeben muss.\n"
                                                     "Für jede Matrix-Zeile kannst du dich an die rechts parallel\n"
                                                     "befindende Spalte orientieren, in welchem hingewiesen wird,\n"
                                                     "um wie viel du deine Eingaben zur Akzeptanz anpassen solltest.")
        matrix_label_text.grid(row=3, column=0, columnspan=matrix_dim, padx=0, pady=(0, 0), sticky="ew")

        matrix_eingaben = []
        hinweis_labels = []

        def begrenze_eingabe(P):
            if len(P) > 12:
                return False
            return True


        def callback(var):
            for index, zeile in enumerate(matrix_eingaben):
                ergebnis = 0
                for spalte in zeile:
                    ergebnis = ergebnis + float(spalte.get())

                hinweis_string_var, hinweis_label = hinweis_labels[index]
                if ergebnis < 1:
                    hinweis_string_var.set("Hier fehlen dir noch " + str(round(1 - ergebnis, 12)) + " für 100%")
                    hinweis_label.config(fg="orange")
                elif ergebnis == 1:
                    hinweis_string_var.set("100% erreicht")
                    hinweis_label.config(fg="green")
                elif ergebnis > 1:
                    hinweis_string_var.set("Du bist hast " + str(round(ergebnis - 1, 12)) + " überschritten!!!")
                    hinweis_label.config(fg="red")

        cmd = (b_fenster.register(begrenze_eingabe), '%P')

        for i in range(matrix_dim):
            zeile = []
            for j in range(matrix_dim):
                koordinaten = tk.Label(matrix_frame, text=f"({i + 1}, {j + 1})", font=("Helvetica", 8))
                koordinaten.grid(row=i * 2, column=j)
                var = tk.StringVar()
                var.trace("w", lambda name, index, mode, var=var: callback(var))
                eingabe_feld = tk.Entry(matrix_frame, width=12, validate='key', validatecommand=cmd, textvariable=var)
                eingabe_feld.grid(row=i * 2 + 1, column=j, padx=2, pady=2)
                eingabe_feld.insert(0, "0.")

                zeile.append(eingabe_feld)
            matrix_eingaben.append(zeile)

        # Hinweis-Label-------------------------------------------------------------------------------------------------
        hinweis_label = tk.Label(b_fenster, text="Hinweise für die Akzeptanz der Matrix-Zeilen")
        hinweis_label.grid(row=3, column=matrix_dim + 1, padx=0, pady=(0, 0), sticky="w")

        for i in range(matrix_dim):
            my_string_var = tk.StringVar()

            my_string_var.set("Fülle die " + str(i + 1) + ". Matrix-Zeile aus")
            hinweis_label = tk.Label(b_fenster, textvariable=my_string_var, width=36, relief="groove")
            hinweis_label.grid(row=i + 4, column=matrix_dim + 1, padx=0, pady=0)
            hinweis_labels.append((my_string_var, hinweis_label))

        # Buttons-------------------------------------------------------------------------------------------------------
        zuruck_button = tk.Button(b_fenster, text="Zurück",
                                  command=lambda: b_fenster.destroy())
        zuruck_button.grid(row=matrix_dim + 4, column=0, padx=10, pady=10, sticky="e")

        zufallige_werte_button = tk.Button(b_fenster, text="Zufällige Werte")
        zufallige_werte_button.grid(row=matrix_dim + 4, column=1, padx=10, pady=10)

        eingaben_berechnen_button = tk.Button(b_fenster, text="Eingaben berechnen", command=self.starte_berechnung)
        eingaben_berechnen_button.grid(row=matrix_dim + 4, column=2, padx=10, pady=10, sticky="w")

        # Radio-Buttons-------------------------------------------------------------------------------------------------
        radiobutton_frame = tk.Frame(b_fenster)
        radiobutton_frame.grid(row=4, rowspan=matrix_dim, column=matrix_dim + 2, padx=10, pady=10)

        radiobutton_label = tk.Label(b_fenster, text="Welche Methode\n der Iteration soll erfolgen?")
        radiobutton_label.grid(row=3, column=matrix_dim + 2, padx=10, pady=(10, 0), sticky="w")

        radio_wahl = IntVar()

        radio_kleene_delta = tk.Radiobutton(radiobutton_frame, text="Delta", variable=radio_wahl, value=1)
        radio_kleene_delta.pack(anchor="w")

        radio_delta_dach = tk.Radiobutton(radiobutton_frame, text="Delta Dach", variable=radio_wahl, value=2)
        radio_delta_dach.pack(anchor="w")

        radio_gross_lambda = tk.Radiobutton(radiobutton_frame, text="Gross Lambda", variable=radio_wahl, value=3)
        radio_gross_lambda.pack(anchor="w")

        radio_discount_factor = tk.Radiobutton(radiobutton_frame, text="Delta Discount Factor", variable=radio_wahl, value=4)
        radio_discount_factor.pack(anchor="w")

        radio_wahl.set(1)

        self.zentriere_fenster(b_fenster)

    def hole_labels(self):
        labelsarray = []
        for element in self.label_eingaben:
               labelsarray.append(element.get())
        return labelsarray

    def starterechnen(self):
        print("TEST")
        dimension = int(self.eingabe_dimension.get())
        label_anzahl = int(self.eingabe_label_anzahl.get())
        epsilon = float(self.eingabe_epsilon.get())
        lambda_wert = float(self.eingabe_lambda.get())
        #labels = self.hole_labels()

        ergebnisse = self.controller.starte_berechnung(dimension, label_anzahl, epsilon, lambda_wert)#, labels)
        startwerte = (dimension, label_anzahl, epsilon, lambda_wert)#, labels)
        self.ergebnis_fenster(startwerte, ergebnisse)

    # START-BUTTON-------------------------------------------------------------------------------------------------------
    def starte_berechnung_haupt(self, eingabe_dimension, eingabe_label_anzahl, eingabe_epsilon, eingabe_lambda):
        dimension = eingabe_dimension.get()
        label_anzahl = eingabe_label_anzahl.get()
        epsilon = eingabe_epsilon.get()
        lambda_wert = eingabe_lambda.get()

        ergebnisse = self.controller.starte_berechnung(dimension, label_anzahl, epsilon, lambda_wert)
        startwerte = (dimension, label_anzahl, epsilon, lambda_wert)
        self.ergebnis_fenster(startwerte, ergebnisse)

    @staticmethod
    def matrix_zu_string(matrix):
        return '\n'.join(['\t\t\t'.join([str(feld) for feld in zeile]) for zeile in matrix])

    @staticmethod
    def formatierte_zeilen(matrix_p, verhaltens_metriken, bisimulation_relation):
        formatierte_zeilen = []
        for i in range(len(matrix_p)):
            for j in range(len(matrix_p[i])):
                formatierte_zeilen.append(f'({i + 1}, {j + 1})')
                formatierte_zeilen.append(f'M-P: {matrix_p[i][j]}')
                formatierte_zeilen.append(f'VM: {verhaltens_metriken[i][j]}')
                formatierte_zeilen.append(f'BSM: {bisimulation_relation[i][j]}')
                formatierte_zeilen.append('\n')
        return '\n'.join(formatierte_zeilen)

    def ergebnis_fenster(self, startwerte, ergebnisse):
        ergebnis_fenster = tk.Toplevel()
        ergebnis_fenster.title("Ergebnisse der Berechnung")
        ergebnis_fenster.state('zoomed')
        ergebnis_fenster.resizable(True, True)

        # Frames--------------------------------------------------------------------------------------------------------
        oberer_frame = tk.Frame(ergebnis_fenster)
        mittlerer_frame = tk.Frame(ergebnis_fenster)
        unterer_frame = tk.Frame(ergebnis_fenster)

        oberer_frame.pack(fill='x')
        mittlerer_frame.pack(fill='both', expand=True)
        unterer_frame.pack(fill='x')

        # Startwerte----------------------------------------------------------------------------------------------------
        dimension, label_anzahl, epsilon, lambda_wert = startwerte
        labels = ergebnisse['labels']
        P = ergebnisse['P']

        tk.Label(oberer_frame, text="Startwerte", font=("Arial", 16)).grid(row=0, column=0, columnspan=4)
        tk.Label(oberer_frame, text="Dimension: " + str(dimension) + " " * 16).grid(row=1, column=0)
        tk.Label(oberer_frame, text="Label Anzahl: " + str(label_anzahl) + " " * 16).grid(row=1, column=1)
        tk.Label(oberer_frame, text="Epsilon: " + str(epsilon) + " " * 16).grid(row=1, column=2)
        tk.Label(oberer_frame, text="Lambda: " + str(lambda_wert) + " " * 16).grid(row=1, column=3)
        # gewählte Labels
        tk.Label(oberer_frame, text="Dies sind ihre ausgewählten Labels: " + ', '.join(map(str, labels)),
                 wraplength=500).grid(row=2, column=0, columnspan=4)

        # Ergebnisse + P-Matrix-----------------------------------------------------------------------------------------
        verhaltens_metriken = ergebnisse['verhaltens_metriken']
        bisimulation_relation = ergebnisse['bisimulation_relation']
        bisimulare_zustaende = ergebnisse['bisimulare_zustaende']

        tk.Label(mittlerer_frame, text="Ergebnis der Berechnungsfelder", font=("Arial", 16)).pack()
        ergebnis_feld = Text(mittlerer_frame)
        ergebnis_feld.pack(fill='both', expand=True)
        ergebnis_feld['wrap'] = 'none'

        scroll = Scrollbar(mittlerer_frame, orient=HORIZONTAL, command=ergebnis_feld.xview)
        scroll.pack(fill='x')

        ergebnis_feld['xscrollcommand'] = scroll.set
        ergebnis_feld.insert(tk.END, "Dies ist die gewählte Wahrscheinlichkeitsverteilung im Form der Matrix P:\n")
        ergebnis_feld.insert(tk.END, self.matrix_zu_string(P) + "\n\n\n")
        ergebnis_feld.insert(tk.END, "Die daraus resultierende Verhaltensmetriken sind folgende:\n")
        ergebnis_feld.insert(tk.END, self.matrix_zu_string(verhaltens_metriken) + "\n\n\n")
        ergebnis_feld.insert(tk.END, "Die Bisimulationsrelation ist wie folgt:\n")
        ergebnis_feld.insert(tk.END, self.matrix_zu_string(bisimulation_relation) + "\n\n\n")
        ergebnis_feld.insert(tk.END, bisimulare_zustaende + "\n\n\n")
        ergebnis_feld.insert(tk.END, bisimulare_zustaende + "\n\n\n")

        formatierte_ausgabe = self.formatierte_zeilen(P, verhaltens_metriken, bisimulation_relation)
        ergebnis_feld.insert(tk.END, "Formatierte Ausgabe (M-P = Matrix-P; VM = Verhaltensmetriken;"
                                     " BSM = Bisimulationsrelation):\n")
        ergebnis_feld.insert(tk.END, formatierte_ausgabe)
        ergebnis_feld['wrap'] = 'none'
        ergebnis_feld.config(state=tk.DISABLED)

        # Buttons-------------------------------------------------------------------------------------------------------
        tk.Button(unterer_frame, text="Zurück", command=lambda: ergebnis_fenster.destroy()).pack(side='left', padx=10,
                                                                                                 pady=10)
        tk.Button(unterer_frame, text="Neustart").pack(side='left', padx=10, pady=10)
        # Beenden muss noch korrigiert werden
        tk.Button(unterer_frame, text="Beenden", command=ergebnis_fenster.quit).pack(side='left', padx=10, pady=10)

        tk.Button(unterer_frame, text="Ergebnisse speichern").pack(side='left', padx=10, pady=10)

        self.zentriere_fenster(ergebnis_fenster)
