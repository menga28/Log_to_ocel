import tkinter as tk


def create_dropdown(window, controller, label_text, is_multiple=True, x_position=280,  y_position=370):
    dropdown_frame = tk.Frame(window, bg="#86b2cc", relief="flat", bd=1)
    dropdown_frame.place(x=x_position, y=y_position, width=400)

    dropdown_label = tk.Label(
        dropdown_frame,
        text=label_text,
        bg="#86b2cc",
        fg="#000000",
        font=("Inter", 12, "bold"),
        anchor="w"
    )
    dropdown_label.pack(fill="x", pady=5, padx=5)

    listbox_frame = tk.Frame(dropdown_frame, bg="#ffffff")
    listbox_frame.pack(fill="both", expand=False, padx=10, pady=5)
    listbox_frame.pack_forget()

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

    is_expanded = [False]

    def toggle_dropdown(event=None):
        if is_expanded[0]:
            listbox_frame.pack_forget()
            is_expanded[0] = False
        else:
            listbox_frame.pack(fill="both", expand=True)
            is_expanded[0] = True

    dropdown_label.bind("<Button-1>", toggle_dropdown)

    return dropdown_frame, listbox
