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

    # Rimuovi tutte le funzioni on_*select esistenti e sostituisci con:

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

    def update_single_selection(field, listbox, is_dict=False, key=None):
        current_selections = listbox.curselection()

        if not current_selections:
            return  # Non cancellare se non c'è interazione

        if is_dict:
            if not key:
                return
            controller.object_attrs_selection[key] = [
                listbox.get(i) for i in current_selections]
        else:
            setattr(controller, field, [listbox.get(i)
                    for i in current_selections])

        # Stampa di debug
        print("\nAggiornamento parziale:")
        print(f"Campo modificato: {field}")
        _print_current_state()

    def _print_current_state():
        print("\nCurrent Selections:")
        print(f"Activity: {controller.activity_selection}")
        print(f"Timestamp: {controller.timestamp_selection}")
        print(f"Object Types: {controller.object_types_selection}")
        print(f"Event Attributes: {controller.events_attrs_selection}")
        print(f"Object Attributes: {controller.object_attrs_selection}\n")

    # Funzioni specifiche per ogni dropdown
    def on_activity_select(event):
        update_single_selection('activity_selection', activity_listbox)

    def on_timestamp_select(event):
        update_single_selection('timestamp_selection', timestamp_listbox)

    def on_object_types_select(event):
        update_single_selection('object_types_selection', object_types_listbox)

    def on_events_attrs_select(event):
        update_single_selection('events_attrs_selection', events_attrs_listbox)

    def on_object_type_select(event):
        # Aggiorna solo la lista delle colonne disponibili
        selected_type = object_type_attrs_listbox.get(tk.ACTIVE)
        if selected_type and controller.model.df_normalized is not None:
            object_columns_attrs_listbox.delete(0, tk.END)
            for col in controller.model.df_normalized.columns:
                object_columns_attrs_listbox.insert(tk.END, col)

            # Ripristina selezioni precedenti per questo tipo
            if selected_type in controller.object_attrs_selection:
                for idx, col in enumerate(controller.model.df_normalized.columns):
                    if col in controller.object_attrs_selection[selected_type]:
                        object_columns_attrs_listbox.selection_set(idx)

    def on_object_columns_select(event):
        selected_type = object_type_attrs_listbox.get(tk.ACTIVE)
        if selected_type:
            update_single_selection(
                'object_attrs_selection',
                object_columns_attrs_listbox,
                is_dict=True,
                key=selected_type
            )

    # Binding degli eventi
    activity_listbox.bind('<<ListboxSelect>>', on_activity_select)
    timestamp_listbox.bind('<<ListboxSelect>>', on_timestamp_select)
    object_types_listbox.bind('<<ListboxSelect>>', on_object_types_select)
    events_attrs_listbox.bind('<<ListboxSelect>>', on_events_attrs_select)
    object_type_attrs_listbox.bind('<<ListboxSelect>>', on_object_type_select)
    object_columns_attrs_listbox.bind(
        '<<ListboxSelect>>', on_object_columns_select)

    # Funzione aggiornamento colonne modificata
    def update_columns(columns):
        if not columns:
            print("Warning: No columns to update.")
            return

        # Salva lo stato precedente
        prev_activity = controller.activity_selection
        prev_timestamp = controller.timestamp_selection
        prev_object_types = controller.object_types_selection.copy()
        prev_event_attrs = controller.events_attrs_selection.copy()
        prev_object_attrs = controller.object_attrs_selection.copy()

        # Aggiorna tutte le listbox
        for listbox in [activity_listbox, timestamp_listbox,
                        object_types_listbox, events_attrs_listbox,
                        object_type_attrs_listbox]:
            listbox.delete(0, tk.END)
            for col in columns:
                listbox.insert(tk.END, col)

        # Ripristina selezioni solo se esistono nelle nuove colonne
        def restore_selection(listbox, prev_selection):
            for item in prev_selection:
                try:
                    idx = columns.index(item)
                    listbox.selection_set(idx)
                except ValueError:
                    continue

        restore_selection(activity_listbox, prev_activity)
        restore_selection(timestamp_listbox, prev_timestamp)
        restore_selection(object_types_listbox, prev_object_types)
        restore_selection(events_attrs_listbox, prev_event_attrs)

        # Aggiorna object_attrs_listbox mantenendo le relazioni
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
