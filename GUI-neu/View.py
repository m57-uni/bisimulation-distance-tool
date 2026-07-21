import tkinter as tk
from tkinter import IntVar
# from tkinter import ttk
from tkinter import HORIZONTAL, Scrollbar, Text,filedialog
import json
import numpy as np
from random import randint


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


    def oeffne_datei(self):
        root = tk.Tk()
        root.withdraw()

        datei_pfad = filedialog.askopenfilename()

        if datei_pfad:

            with open(datei_pfad, 'r') as file:
                datei_inhalt = file.read()
                jsonr = json.loads(datei_inhalt)
                dimension = int(jsonr['dimension'])
                label_anzahl = int(jsonr['dimension'])
                epsilon = float(jsonr['ep'])
                lambda_wert = float(jsonr['lambda'])

                ergebnisse = self.controller.starte_berechnung(dimension, label_anzahl, epsilon, lambda_wert,
                                                               jsonr['values'], jsonr['labels'])
                startwerte = (dimension, label_anzahl, epsilon, lambda_wert)
                self.ergebnis_fenster(startwerte, ergebnisse)

    def checkbox_toggle(self, checkbox):
        checkbox_zustand = checkbox.var.get()
        checkbox.var.set(not checkbox_zustand)

    def checkboxen_validieren(self, checkbox_aktuell):
        if checkbox_aktuell.var.get() == False:
            if checkbox_aktuell in self.checkboxes:
                if sum(checkbox.var.get() for checkbox in self.checkboxes if checkbox != checkbox_aktuell) == 0:
                    checkbox_aktuell.var.set(True)
            elif checkbox_aktuell in self.checkboxes_ausgabe:
                if sum(checkbox.var.get() for checkbox in self.checkboxes_ausgabe if checkbox != checkbox_aktuell) == 0:
                    checkbox_aktuell.var.set(True)

    def lambda_status(self):
        if self.checkbox_delta_discount_factor.var.get():
            self.eingabe_lambda.configure(state='normal')
        else:
            self.eingabe_lambda.configure(state='disabled')

    def auswahl_fenster(self):
        aw_fenster = tk.Tk()
        aw_fenster.title("Auswahl-Fenster")
        aw_fenster.resizable(False, False)

        tk.Label(aw_fenster,
                 text="Möchtest du zur Berechnung der Transitionssysteme \n manuelle Eingaben machen oder eine Datei einlesen?").grid(
            row=0,
            column=0,
            columnspan=4,
            pady=10)

        # Buttons
        tk.Button(aw_fenster, text="Manuelle Eingabe",
                  command=lambda: [aw_fenster.destroy(), self.haupt_fenster()]).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(aw_fenster, text="Einlesen einer Datei",
                  command=self.oeffne_datei
            ).grid(row=1, column=1, padx=10, pady=10)

        # Eingabefelder für Epsilon und Lambda Eingaben
        tk.Label(aw_fenster, text="Schwellenwert Epsilon (z.B. 1e-10):").grid(row=2, column=0, sticky="w", padx=10,
                                                                              pady=10)
        self.eingabe_epsilon = tk.Entry(aw_fenster)
        self.eingabe_epsilon.grid(row=2, column=1, padx=10)
        self.eingabe_epsilon.insert(0, "1e-10")

        tk.Label(aw_fenster, text="Skalierungswert Lambda eingeben (z.B. 1.0):").grid(row=3, column=0, sticky="w",
                                                                                      padx=10, pady=10)
        self.eingabe_lambda = tk.Entry(aw_fenster)
        self.eingabe_lambda.grid(row=3, column=1, padx=10)
        self.eingabe_lambda.insert(0, "1.0")

        # Kontrollkästchen Kleene-Iterationen

        checkbox_frame = tk.Frame(aw_fenster)
        checkbox_frame.grid(row=4, column=0, rowspan=2, padx=10, pady=10)

        tk.Label(checkbox_frame, text="Welche Kleene-Iteration soll durchgeführt werden?").pack(anchor="w")

        self.checkboxes = []

        self.checkbox_delta = tk.Checkbutton(checkbox_frame, text="Delta")
        self.checkbox_delta.var = tk.BooleanVar()
        self.checkbox_delta.var.set(True)  
        self.checkbox_delta.config(variable=self.checkbox_delta.var,
                                   command=lambda: self.checkboxen_validieren(self.checkbox_delta))
        self.checkbox_delta.pack(anchor="w")

        self.checkbox_delta_dach = tk.Checkbutton(checkbox_frame, text="Delta Dach")
        self.checkbox_delta_dach.var = tk.BooleanVar()
        self.checkbox_delta_dach.config(variable=self.checkbox_delta_dach.var,
                                        command=lambda: self.checkboxen_validieren(self.checkbox_delta_dach))
        self.checkbox_delta_dach.pack(anchor="w")

        self.checkbox_grosses_lambda = tk.Checkbutton(checkbox_frame, text="Großes Lambda")
        self.checkbox_grosses_lambda.var = tk.BooleanVar()
        self.checkbox_grosses_lambda.config(variable=self.checkbox_grosses_lambda.var,
                                            command=lambda: self.checkboxen_validieren(self.checkbox_grosses_lambda))
        self.checkbox_grosses_lambda.pack(anchor="w")


        self.checkbox_delta_discount_factor = tk.Checkbutton(checkbox_frame, text="Delta + Discount Factor")
        self.checkbox_delta_discount_factor.var = tk.BooleanVar()
        self.checkbox_delta_discount_factor.config(variable=self.checkbox_delta_discount_factor.var,
                                                   command=lambda: [
                                                       self.checkboxen_validieren(self.checkbox_delta_discount_factor),
                                                       self.lambda_status()])
        self.checkbox_delta_discount_factor.pack(anchor="w")

        self.checkboxes.extend([self.checkbox_delta, self.checkbox_delta_dach, self.checkbox_grosses_lambda,
                                self.checkbox_delta_discount_factor])

        if self.checkbox_delta_discount_factor.var.get():
            self.eingabe_lambda.configure(state='normal')
        else:
            self.eingabe_lambda.configure(state='disabled')




        # Kontrollkästchen für die Ausgaben
        output_checkbox_frame = tk.Frame(aw_fenster)
        output_checkbox_frame.grid(row=4, column=1, rowspan=2, padx=10, pady=10)

        tk.Label(output_checkbox_frame, text="Welche Ausgaben sollen erfolgen?").pack(anchor="w")

        self.checkboxes_ausgabe = []

        self.checkbox_labels = tk.Checkbutton(output_checkbox_frame, text="erzeugte Labels")
        self.checkbox_labels.var = tk.BooleanVar()
        self.checkbox_labels.var.set(True)  
        self.checkbox_labels.config(variable=self.checkbox_labels.var,
                                    command=lambda: self.checkboxen_validieren(self.checkbox_labels))
        self.checkbox_labels.pack(anchor="w")

        self.checkbox_p_matrix = tk.Checkbutton(output_checkbox_frame, text="erzeugte P-Matrix")
        self.checkbox_p_matrix.var = tk.BooleanVar()
        self.checkbox_p_matrix.config(variable=self.checkbox_p_matrix.var,
                                      command=lambda: self.checkboxen_validieren(self.checkbox_p_matrix))
        self.checkbox_p_matrix.pack(anchor="w")

        self.checkbox_verhaltensmetrik = tk.Checkbutton(output_checkbox_frame, text="Verhaltensmetriken")
        self.checkbox_verhaltensmetrik.var = tk.BooleanVar()
        self.checkbox_verhaltensmetrik.config(variable=self.checkbox_verhaltensmetrik.var,
                                               command=lambda: self.checkboxen_validieren(
                                                   self.checkbox_verhaltensmetrik))
        self.checkbox_verhaltensmetrik.pack(anchor="w")

        self.checkbox_bisimulations = tk.Checkbutton(output_checkbox_frame, text="Bisimulationsrelationen")
        self.checkbox_bisimulations.var = tk.BooleanVar()
        self.checkbox_bisimulations.config(variable=self.checkbox_bisimulations.var,
                                           command=lambda: self.checkboxen_validieren(self.checkbox_bisimulations))
        self.checkbox_bisimulations.pack(anchor="w")

        self.checkbox_verfahrens_zeit_insgesamt = tk.Checkbutton(output_checkbox_frame,
                                                         text="insgesamte Laufzeit von Verfahren")
        self.checkbox_verfahrens_zeit_insgesamt.var = tk.BooleanVar()
        self.checkbox_verfahrens_zeit_insgesamt.config(variable=self.checkbox_verfahrens_zeit_insgesamt.var,
                                               command=lambda: self.checkboxen_validieren(
                                                   self.checkbox_verfahrens_zeit_insgesamt))
        self.checkbox_verfahrens_zeit_insgesamt.pack(anchor="w")

        self.checkbox_gesamte_berechnungszeit = tk.Checkbutton(output_checkbox_frame,
                                                              text="insgesamte Laufzeit aller Berechnungen")
        self.checkbox_gesamte_berechnungszeit.var = tk.BooleanVar()
        self.checkbox_gesamte_berechnungszeit.config(variable=self.checkbox_gesamte_berechnungszeit.var,
                                                    command=lambda: self.checkboxen_validieren(
                                                        self.checkbox_gesamte_berechnungszeit))
        self.checkbox_gesamte_berechnungszeit.pack(anchor="w")

        self.checkbox_anzahl_iterationen = tk.Checkbutton(output_checkbox_frame, text="Anzahl der Iterationen")
        self.checkbox_anzahl_iterationen.var = tk.BooleanVar()
        self.checkbox_anzahl_iterationen.config(variable=self.checkbox_anzahl_iterationen.var,
                                                  command=lambda: self.checkboxen_validieren(
                                                      self.checkbox_anzahl_iterationen))
        self.checkbox_anzahl_iterationen.pack(anchor="w")

        self.checkboxes_ausgabe.extend([self.checkbox_labels, self.checkbox_p_matrix, self.checkbox_verhaltensmetrik,
                                       self.checkbox_bisimulations, self.checkbox_verfahrens_zeit_insgesamt,
                                       self.checkbox_gesamte_berechnungszeit,
                                       self.checkbox_anzahl_iterationen])

        self.zentriere_fenster(aw_fenster)
        aw_fenster.mainloop()

    def haupt_fenster(self):
        h_fenster = tk.Tk()
        h_fenster.title("Wertevergabe für die Grundbausteine des Transitionssystems")
        h_fenster.resizable(False, False)

        self.options_var = tk.StringVar(value='manuell')

        def toggle_state():
            if self.options_var.get() == 'zufällig':
                self.eingabe_label_anzahl.configure(state='normal', bg='white')
                self.eingabe_system_anzahl.configure(state='normal', bg='white')
                self.zufall_button.configure(state='normal')
                self.manuell_button.configure(state='disabled')
            else:
                self.eingabe_label_anzahl.configure(state='disabled', bg='grey')
                self.eingabe_system_anzahl.configure(state='disabled', bg='grey')
                self.zufall_button.configure(state='disabled')
                self.manuell_button.configure(state='normal')

        tk.Label(h_fenster, text="Möchten Sie gleich die Übergangsmatrix und die jeweiligen Labels selber eintragen,\n "
                                 "oder sollen diese zufällig gewählt werden?").grid(row=0, column=2, columnspan=3)

        tk.Radiobutton(h_fenster, text="Manuell", variable=self.options_var, value='manuell',
                       command=toggle_state).grid(row=1, column=2)
        tk.Radiobutton(h_fenster, text="Zufällig", variable=self.options_var, value='zufällig',
                       command=toggle_state).grid(row=2, column=2)



        tk.Label(h_fenster, text="Dimension bzw. Anzahl der Zustände:").grid(row=0, column=0, sticky="w")
        self.eingabe_dimension = tk.Entry(h_fenster)
        self.eingabe_dimension.grid(row=0, column=1)

        tk.Label(h_fenster, text="Anzahl der Labels (Für randomisierte Berechnung):").grid(row=1, column=0, sticky="w")
        self.eingabe_label_anzahl = tk.Entry(h_fenster)
        self.eingabe_label_anzahl.grid(row=1, column=1)

        tk.Label(h_fenster, text="Anzahl der Systeme (Für randomisierte Evaluierung):").grid(row=2, column=0, sticky="w")
        self.eingabe_system_anzahl = tk.Entry(h_fenster)
        self.eingabe_system_anzahl.grid(row=2, column=1)
        self.eingabe_system_anzahl.insert(0, "100")

        self.manuell_button = tk.Button(h_fenster, text="manuelle Eingabe von P-Matrix & Labels",
                                        command=lambda: self.erstelle_berechnungs_fenster(self.eingabe_dimension,
                                                                                          self.eingabe_dimension))
        self.manuell_button.grid(row=5, column=2, padx=10, pady=10, sticky="w")

        self.zufall_button = tk.Button(h_fenster, text="randomisierte P-Matrix & Labels",
                                       command=lambda: self.starte_berechnung_zufall(
                                           self.eingabe_dimension, self.eingabe_label_anzahl,
                                           self.eingabe_epsilon, self.eingabe_lambda))
        self.zufall_button.grid(row=5, column=1, padx=10, pady=10)

        toggle_state()

        tk.Button(h_fenster, text="Zurück",
                  command=lambda: [h_fenster.destroy(), self.auswahl_fenster()]).grid(row=5, column=0, padx=10, pady=10,
                                                                                      sticky="e")

        self.zentriere_fenster(h_fenster)
        h_fenster.mainloop()

    def generate_random_distribution(self, dim):
        matrix = np.random.rand(dim, dim)
        matrix = matrix / matrix.sum(axis=1, keepdims=True)
        return matrix

    def fill_fields_with_random_distribution(self):
        self.matrix_dim = self.generate_random_distribution(int(self.eingabe_dimension.get()))
        for i in range(self.eingabe_dimension):
            for j in range(self.eingabe_dimension):
                self.matrix_eingaben[i][j].delete(0, tk.END)
                self.matrix_eingaben[i][j].insert(0, str(round(self.matrix_dim[i][j], 12)))
                self.feedback()

    def fill_labels_with_random_numbers(self):
        for label_eingabe_feld in self.label_eingaben:
            label_eingabe_feld.delete(0, tk.END)
            label_eingabe_feld.insert(0, str(randint(0, 9)))
    def erstelle_berechnungs_fenster(self, eingabe_dimension, eingabe_label_anzahl):
        dimension = int(eingabe_dimension.get())
        label_anzahl = int(eingabe_label_anzahl.get())
        self.matrix_dim =dimension
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
                                text="Gebe deine beliebigen Label ein:")
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

        self.matrix_eingaben = []
        hinweis_labels = []

        def begrenze_eingabe(P):
            if len(P) > 12:
                return False
            return True

        cmd = (b_fenster.register(begrenze_eingabe), '%P')

        for i in range(matrix_dim):
            zeile = []
            for j in range(matrix_dim):
                koordinaten = tk.Label(matrix_frame, text=f"({i + 1}, {j + 1})", font=("Helvetica", 8))
                koordinaten.grid(row=i * 2, column=j)
                var = tk.StringVar()
                var.trace("w", lambda name, index, mode, var=var: feedback())
                eingabe_feld = tk.Entry(matrix_frame, width=12, validate='key', validatecommand=cmd, textvariable=var)
                eingabe_feld.grid(row=i * 2 + 1, column=j, padx=2, pady=2)
                eingabe_feld.insert(0, "0.")
                zeile.append(eingabe_feld)
            self.matrix_eingaben.append(zeile)

        # Hinweis-Label-------------------------------------------------------------------------------------------------
        hinweis_label = tk.Label(b_fenster, text="Hinweise für die Akzeptanz der Matrix-Zeilen")
        hinweis_label.grid(row=3, column=matrix_dim + 1, padx=0, pady=(0, 0), sticky="w")

        for i in range(matrix_dim):
            my_string_var = tk.StringVar()

            my_string_var.set("Fülle die " + str(i + 1) + ". Matrix-Zeile aus")
            hinweis_label = tk.Label(b_fenster, textvariable=my_string_var, width=36, relief="groove")
            hinweis_label.grid(row=i + 4, column=matrix_dim + 1, padx=0, pady=0)
            hinweis_labels.append((my_string_var, hinweis_label))


        def feedback():
            for index, zeile_feedback in enumerate(self.matrix_eingaben):
                ergebnis = 0
                for spalte in zeile_feedback:
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

        # Buttons-------------------------------------------------------------------------------------------------------
        zuruck_button = tk.Button(b_fenster, text="Zurück",
                                  command=lambda: b_fenster.destroy())
        zuruck_button.grid(row=matrix_dim + 4, column=0, padx=10, pady=10, sticky="e")

        zufallige_werte_button = tk.Button(b_fenster, text="Zufällige Werte",
                                           command=self.fill_fields_with_random_distribution)
        zufallige_werte_button.grid(row=matrix_dim + 4, column=1, padx=10, pady=10)

        zufallige_label_werte_button = tk.Button(b_fenster, text="Zufällige Label Werte",
                                                 command=self.fill_labels_with_random_numbers)
        zufallige_label_werte_button.grid(row=matrix_dim + 5, column=1, padx=10, pady=10)

        eingaben_berechnen_button = tk.Button(b_fenster, text="Eingaben berechnen", command=self.starte_berechnung)
        eingaben_berechnen_button.grid(row=matrix_dim + 4, column=2, padx=10, pady=10, sticky="w")

        self.zentriere_fenster(b_fenster)



    def hole_labels(self):
        labelsarray = []
        for element in self.label_eingaben:
               labelsarray.append(element.get())
        return labelsarray

    def hole_matrix(self):
        matrix_eingaben = []
        for spalte in self.matrix_eingaben:
            zeile = []
            for wert in spalte:
                zeile.append(wert.get())
            matrix_eingaben.append(zeile)
        return matrix_eingaben

    def starte_berechnung(self):
        dimension = int(self.eingabe_dimension.get())
        label_anzahl = int(self.eingabe_dimension.get())
        epsilon = float(self.eingabe_epsilon.get())
        lambda_wert = float(self.eingabe_lambda.get())

        ergebnisse = self.controller.starte_berechnung(dimension, label_anzahl, epsilon, lambda_wert,
                                                       self.hole_matrix(), self.hole_labels(), [self.checkbox_delta.var.get(), self.checkbox_delta_dach.var.get(), self.checkbox_delta_discount_factor.var.get(), self.checkbox_grosses_lambda.var.get()], False)
        startwerte = (dimension, label_anzahl, epsilon, lambda_wert)
        self.ergebnis_fenster(startwerte, ergebnisse)

    # START-BUTTON-------------------------------------------------------------------------------------------------------
    def starte_berechnung_zufall(self, eingabe_dimension, eingabe_label_anzahl, eingabe_epsilon, eingabe_lambda):
        dimension = eingabe_dimension.get()
        label_anzahl = eingabe_label_anzahl.get()
        epsilon = eingabe_epsilon.get()
        lambda_wert = eingabe_lambda.get()

        ergebnisse = self.controller.starte_berechnung(dimension, label_anzahl, epsilon, lambda_wert, 0, 0, True)
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
        self.savevar = ergebnisse
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
        # Buttons-------------------------------------------------------------------------------------------------------
        tk.Button(unterer_frame, text="Zurück", command=lambda: ergebnis_fenster.destroy()).pack(side='left', padx=10,
                                                                                                 pady=10)
        tk.Button(unterer_frame, text="Neustart").pack(side='left', padx=10, pady=10)
        # Beenden muss noch korrigiert werden
        tk.Button(unterer_frame, text="Beenden", command=ergebnis_fenster.quit).pack(side='left', padx=10, pady=10)

        tk.Button(unterer_frame, text="Ergebnisse speichern", command=self.speichern).pack(side='left', padx=10, pady=10)
        tk.Label(oberer_frame, text="Startwerte", font=("Arial", 16)).grid(row=0, column=0, columnspan=4)
        tk.Label(oberer_frame, text="Dimension: " + str(dimension) + " " * 16).grid(row=1, column=0)
        tk.Label(oberer_frame, text="Label Anzahl: " + str(label_anzahl) + " " * 16).grid(row=1, column=1)
        tk.Label(oberer_frame, text="Epsilon: " + str(epsilon) + " " * 16).grid(row=1, column=2)
        tk.Label(oberer_frame, text="Lambda: " + str(lambda_wert) + " " * 16).grid(row=1, column=3)
        # gewählte Labels
        tk.Label(oberer_frame, text="Dies sind ihre ausgewählten Labels: " + ', '.join(map(str, labels)),
                 wraplength=500).grid(row=2, column=0, columnspan=4)
        bisimulation_relation = ergebnisse['bisimulation_relation']
        bisimulare_zustaende = ergebnisse['bisimulare_zustaende']

        tk.Label(mittlerer_frame, text="Ergebnis der Berechnungsfelder", font=("Arial", 16)).pack()
        ergebnis_feld = Text(mittlerer_frame)
        ergebnis_feld.pack(fill='both', expand=True)
        ergebnis_feld['wrap'] = 'none'

        scroll = Scrollbar(mittlerer_frame, orient=HORIZONTAL, command=ergebnis_feld.xview)
        scroll.pack(fill='x')
        ergebnis_feld['xscrollcommand'] = scroll.set
        for index,verhaltens_metriken in enumerate(ergebnisse['verhaltens_metriken']):
            print(verhaltens_metriken)
            ergebnis_feld.insert(tk.END, ergebnisse['namen'][index])
            ergebnis_feld.insert(tk.END, "Dies ist die gewählte Wahrscheinlichkeitsverteilung im Form der Matrix P:\n")

            ergebnis_feld.insert(tk.END, self.matrix_zu_string(P) + "\n\n\n")
            ergebnis_feld.insert(tk.END, "Die daraus resultierende Verhaltensmetriken sind folgende:\n")
            ergebnis_feld.insert(tk.END, self.matrix_zu_string(verhaltens_metriken) + "\n\n\n")
            ergebnis_feld.insert(tk.END, "Die Bisimulationsrelation ist wie folgt:\n")
            ergebnis_feld.insert(tk.END, self.matrix_zu_string(bisimulation_relation[index]) + "\n\n\n")
            ergebnis_feld.insert(tk.END, bisimulare_zustaende[index] + "\n\n\n")
            ergebnis_feld.insert(tk.END, bisimulare_zustaende[index] + "\n\n\n")

            formatierte_ausgabe = self.formatierte_zeilen(P, verhaltens_metriken, bisimulation_relation[index])
            ergebnis_feld.insert(tk.END, "Formatierte Ausgabe (M-P = Matrix-P; VM = Verhaltensmetriken;"
                                         " BSM = Bisimulationsrelation):\n")
            ergebnis_feld.insert(tk.END, formatierte_ausgabe)
            #ergebnis_feld['wrap'] = 'none'

        ergebnis_feld.config(state=tk.DISABLED)

            #.zentriere_fenster(ergebnis_fenster)
    def speichern(self):
        datei_pfad = 'export.txt'

        def ndarray_to_list(arr):
            if isinstance(arr, np.ndarray):
                return arr.tolist()
            raise TypeError(f"Unserializable object: {arr}")
        with open(datei_pfad, 'w') as file:
            file.write(json.dumps(self.savevar,default=ndarray_to_list))