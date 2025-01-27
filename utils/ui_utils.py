import tkinter as tk

def create_dropdown(window, controller, label_text, is_multiple=True, x_position = 280,  y_position=370):
    # Frame del dropdown
    dropdown_frame = tk.Frame(window, bg="#86b2cc", relief="flat", bd=1)
    dropdown_frame.place(x=x_position, y=y_position, width=400)

    # Label del dropdown (intestazione cliccabile)
    dropdown_label = tk.Label(
        dropdown_frame,
        text=label_text,
        bg="#86b2cc",
        fg="#000000",
        font=("Inter", 12, "bold"),
        anchor="w"
    )
    dropdown_label.pack(fill="x", pady=5, padx=5)

    # Contenitore per la lista (inizialmente nascosto)
    listbox_frame = tk.Frame(dropdown_frame, bg="#ffffff")
    listbox_frame.pack(fill="both", expand=False, padx=10, pady=5)
    listbox_frame.pack_forget()  # Nasconde il frame inizialmente

    # Listbox per selezione
    listbox = tk.Listbox(
        listbox_frame,
        selectmode=tk.MULTIPLE if is_multiple else tk.SINGLE,
        bg="#648599",
        fg="#000000",
        font=("Inter", 12),
        relief="flat",
        highlightthickness=0
    )
    listbox.pack(fill="both", expand=True)

    # Stato aperto/chiuso
    is_expanded = [False]  # Usa una lista mutabile per preservare lo stato

    # Funzione per espandere/collassare la tendina
    def toggle_dropdown(event=None):
        if is_expanded[0]:
            # Collassa la tendina
            listbox_frame.pack_forget()
            is_expanded[0] = False
        else:
            # Espande la tendina
            listbox_frame.pack(fill="both", expand=True)
            is_expanded[0] = True

    # Associa il clic sull'etichetta al toggle
    dropdown_label.bind("<Button-1>", toggle_dropdown)

    return dropdown_frame, listbox