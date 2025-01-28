import os
import sys
import tkinter as tk
from tkinter import ttk
import pandas as pd


def load_asset(path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")
    return os.path.join(assets, path)


def create_sub_key_norm(parent, controller):
    window = tk.Frame(parent, bg="#ffffff")

    window.canvas = tk.Canvas(
        window,
        bg="#ffffff",
        width=1440,
        height=1024,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    window.canvas.place(x=0, y=0)

    image_1 = tk.PhotoImage(file=load_asset("frame_3/1.png"))
    image_2 = tk.PhotoImage(file=load_asset("frame_3/2.png"))
    image_3 = tk.PhotoImage(file=load_asset("frame_3/3.png"))
    image_4 = tk.PhotoImage(file=load_asset("frame_3/4.png"))
    image_5 = tk.PhotoImage(file=load_asset("frame_3/5.png"))

    window.canvas.create_image(721, 78, image=image_1)
    window.canvas.create_image(158, 73, image=image_2)
    window.canvas.create_image(720, 154, image=image_3)
    window.canvas.create_image(719, 343, image=image_4)
    window.canvas.create_image(713, 375, image=image_5)

    text_ids_subkey = {
        "subkeys_normalization": window.canvas.create_text(
            87,
            342,
            anchor="nw",
            text="Columns to normalize",
            fill="#000000",
            font=("Inter", 16 * -1)
        )
    }

    controller.text_ids = {
        'sub_key_norm': text_ids_subkey
    }

    tree_frame = tk.Frame(window, bg="#ffffff")
    tree_frame.place(x=41, y=470, width=1351, height=300)

    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
    h_scrollbar.pack(side="bottom", fill="x")

    # Rendi tree un attributo della finestra
    window.tree = ttk.Treeview(
        tree_frame,
        columns=[],
        show="headings",
        xscrollcommand=h_scrollbar.set
    )
    window.tree.pack(fill="both", expand=True)

    h_scrollbar.config(command=window.tree.xview)

    # Funzione per aggiornare il Treeview con i dati del DataFrame

    def update_treeview(df):
        for row in window.tree.get_children():
            window.tree.delete(row)

        window.tree["columns"] = list(df.columns)
        for col in df.columns:
            window.tree.heading(col, text=col)

        for index, row in df.iterrows():
            window.tree.insert("", "end", values=list(row))

        window.tree.update_idletasks()
        h_scrollbar.pack(side="bottom", fill="x")

    # Collega l'aggiornamento del Treeview al controller
    controller.update_treeview = update_treeview

    dropdown_frame = tk.Frame(window, bg="#86b2cc", relief="flat", bd=1)
    dropdown_frame.place(x=80, y=370, width=400)

    # Label del dropdown (intestazione cliccabile)
    dropdown_label = tk.Label(
        dropdown_frame,
        text="Select columns to normalize",
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

    # Listbox per selezione multipla
    window.listbox = tk.Listbox(
        listbox_frame,
        selectmode=tk.MULTIPLE,
        bg="#648599",
        fg="#000000",
        font=("Inter", 12),
        relief="flat",
        highlightthickness=0
    )
    window.listbox.pack(fill="both", expand=True)

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

    # Funzione per aggiornare le colonne nella Listbox
    def update_columns(columns):
        window.listbox.delete(0, tk.END)  # Cancella tutte le voci esistenti
        for col in columns:
            window.listbox.insert(tk.END, col)  # Aggiungi ogni colonna alla Listbox
        # Collassa di default
        if is_expanded[0]:
            toggle_dropdown()

    # Collega l'aggiornamento delle colonne al controller
    controller.update_columns = update_columns

    window.canvas.create_text(
        111,
        257,
        anchor="nw",
        text="Select the subkeys you want to normalize",
        fill="#1e1e1e",
        font=("Inter", 24 * -1)
    )

    button_1_image = tk.PhotoImage(file=load_asset("frame_3/6.png"))
    button_1 = tk.Button(
        window,
        image=button_1_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_view_parameter_selection
    )
    button_1.place(x=1129, y=858, width=267, height=76)

    button_2_image = tk.PhotoImage(file=load_asset("frame_3/7.png"))
    button_2 = tk.Button(
        window,
        image=button_2_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_set_file
    )
    button_2.place(x=854, y=858, width=242, height=76)

    window.image_refs = [
        image_1, image_2, image_3, image_4, image_5,
        button_1_image, button_2_image
    ]

    return window
