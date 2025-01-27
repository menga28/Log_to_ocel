import os
import sys
import tkinter as tk


def load_asset(path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")
    return os.path.join(assets, path)


def create_ocel_preview(parent, controller):
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

    image_1 = tk.PhotoImage(file=load_asset("frame_5/1.png"))
    image_2 = tk.PhotoImage(file=load_asset("frame_5/2.png"))
    image_3 = tk.PhotoImage(file=load_asset("frame_5/3.png"))
    image_4 = tk.PhotoImage(file=load_asset("frame_5/4.png"))
    image_5 = tk.PhotoImage(file=load_asset("frame_5/5.png"))

    window.canvas.create_image(721, 78, image=image_1)
    window.canvas.create_image(158, 73, image=image_2)
    window.canvas.create_image(720, 154, image=image_3)
    window.canvas.create_image(719, 534, image=image_4)
    window.canvas.create_image(713, 569, image=image_5)

    text_ids = {
        "statistics_ocel": window.canvas.create_text(
            87,
            342,
            anchor="nw",
            text="Object-Centric Event Log statistics: Number of events: , number of objects: number of activities: , number of object types: , events-objects relationships: \n                                                             Activities occurrences: ",
            fill="#000000",
            font=("Inter", 16 * -1)
        )
    }

    controller.text_ids = {
        'ocel_preview': text_ids
    }

    window.canvas.create_text(
        111,
        257,
        anchor="nw",
        text="Ocel preview",
        fill="#1e1e1e",
        font=("Inter", 24 * -1)
    )

    # ocel export button
    button_1_image = tk.PhotoImage(file=load_asset("frame_5/6.png"))
    button_1 = tk.Button(
        image=button_1_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_ocel_export
    )
    button_1.place(x=1129, y=858, width=267, height=76)

    button_2_image = tk.PhotoImage(file=load_asset("frame_5/7.png"))
    button_2 = tk.Button(
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
