import os
import sys
import tkinter as tk
from utils.ui_utils import create_dropdown


def load_asset(path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")
    return os.path.join(assets, path)


def create_parameter_selection(parent, controller):
    window = tk.Frame(parent, bg="#ffffff")

    # Canvas e elementi grafici originali
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

    # Caricamento immagini
    image_12 = tk.PhotoImage(file=load_asset("frame_4/1.png"))
    image_13 = tk.PhotoImage(file=load_asset("frame_4/2.png"))
    image_14 = tk.PhotoImage(file=load_asset("frame_4/3.png"))
    image_15 = tk.PhotoImage(file=load_asset("frame_4/4.png"))
    image_16 = tk.PhotoImage(file=load_asset("frame_4/5.png"))
    image_17 = tk.PhotoImage(file=load_asset("frame_4/8.png"))

    # Posizionamento immagini
    window.canvas.create_image(721, 78, image=image_12)
    window.canvas.create_image(158, 73, image=image_13)
    window.canvas.create_image(720, 154, image=image_14)
    window.canvas.create_image(719, 534, image=image_15)
    window.canvas.create_image(713, 569, image=image_16)
    window.canvas.create_image(79, 269, image=image_17)

    # Testi descrittivi
    window.canvas.create_text(
        87, 342,
        anchor="nw",
        text="Activity column:\n\n\n\nTimestamp column:\n\n\n\nObject types columns:\n\n\n\nAdditional event attributes:\n\n\n\nAdditional object attributes \n",
        fill="#000000",
        font=("Inter", 16 * -1)
    )

    window.canvas.create_text(
        111, 257,
        anchor="nw",
        text="Ocel parameter selection",
        fill="#1e1e1e",
        font=("Inter", 24 * -1)
    )

    # Dropdowns principali

    # Dropdowns accoppiati per Object Attributes
    object_type_attrs_frame, object_type_attrs_listbox = create_dropdown(
        window, controller, "Select Object Type",
        is_multiple=False, y_position=618, x_position=300
    )

    object_columns_attrs_frame, object_columns_attrs_listbox = create_dropdown(
        window, controller, "Select Columns",
        is_multiple=True, y_position=618, x_position=720
    )

    events_attrs_frame, events_attrs_listbox = create_dropdown(
        window, controller, "Select Event Attributes",
        is_multiple=True, y_position=548, x_position=300
    )

    object_types_frame, object_types_listbox = create_dropdown(
        window, controller, "Select Object Types",
        is_multiple=True, y_position=478, x_position=300
    )

    timestamp_frame, timestamp_listbox = create_dropdown(
        window, controller, "Select Timestamp",
        is_multiple=False, y_position=408, x_position=300
    )

    activity_frame, activity_listbox = create_dropdown(
        window, controller, "Select Activity",
        is_multiple=False, y_position=338, x_position=300
    )

    # Funzioni di selezione
    def on_activity_select(event):
        controller.activity_selection = [activity_listbox.get(
            i) for i in event.widget.curselection()]

    def on_timestamp_select(event):
        controller.timestamp_selection = [
            timestamp_listbox.get(i) for i in event.widget.curselection()]

    def on_object_types_select(event):
        controller.object_types_selection = [
            object_types_listbox.get(i) for i in event.widget.curselection()]

    def on_events_attrs_select(event):
        controller.events_attrs_selection = [
            events_attrs_listbox.get(i) for i in event.widget.curselection()]

    def on_object_type_select(event):
        # Aggiorna colonne quando si seleziona un tipo
        selected_type = object_type_attrs_listbox.get(tk.ACTIVE)
        columns = controller.model.df_normalized.columns.tolist(
        ) if controller.model.df_normalized else []
        object_columns_attrs_listbox.delete(0, tk.END)
        for col in columns:
            object_columns_attrs_listbox.insert(tk.END, col)

    def on_object_columns_select(event):
        # Aggiorna dizionario nel controller
        selected_type = object_type_attrs_listbox.get(tk.ACTIVE)
        selected_columns = [object_columns_attrs_listbox.get(
            i) for i in event.widget.curselection()]
        if selected_type:
            controller.object_attrs_selection[selected_type] = selected_columns

    # Binding eventi
    activity_listbox.bind('<<ListboxSelect>>', on_activity_select)
    timestamp_listbox.bind('<<ListboxSelect>>', on_timestamp_select)
    object_types_listbox.bind('<<ListboxSelect>>', on_object_types_select)
    events_attrs_listbox.bind('<<ListboxSelect>>', on_events_attrs_select)
    object_type_attrs_listbox.bind('<<ListboxSelect>>', on_object_type_select)
    object_columns_attrs_listbox.bind(
        '<<ListboxSelect>>', on_object_columns_select)

    # Funzione aggiornamento colonne
    def update_columns(columns):
        for listbox in [activity_listbox, timestamp_listbox, object_types_listbox,
                        events_attrs_listbox, object_type_attrs_listbox]:
            listbox.delete(0, tk.END)
            for col in columns:
                listbox.insert(tk.END, col)
        # Aggiorna anche le colonne per gli object attributes
        object_columns_attrs_listbox.delete(0, tk.END)
        for col in columns:
            object_columns_attrs_listbox.insert(tk.END, col)

    controller.update_columns = update_columns

    # Pulsanti con immagini originali
    button_5_image = tk.PhotoImage(file=load_asset("frame_4/6.png"))
    button_5 = tk.Button(
        image=button_5_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_show_ocel_preview
    )
    button_5.place(x=1129, y=858, width=267, height=76)

    button_6_image = tk.PhotoImage(file=load_asset("frame_4/7.png"))
    button_6 = tk.Button(
        image=button_6_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_set_file
    )
    button_6.place(x=854, y=858, width=242, height=76)

    # Mantieni riferimenti alle immagini
    window.image_refs = [
        image_12, image_13, image_14, image_15,
        image_16, image_17, button_5_image, button_6_image
    ]

    return window
