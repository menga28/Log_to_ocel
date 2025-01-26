# Code generated by TkForge <https://github.com/axorax/tkforge>
# Donate to support TkForge! <https://www.patreon.com/axorax>

import os
import sys
import tkinter as tk


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
        command=controller.handle_subkey_button1
    )
    button_1.place(x=1129, y=858, width=267, height=76)

    button_2_image = tk.PhotoImage(file=load_asset("frame_3/7.png"))
    button_2 = tk.Button(
        window,
        image=button_2_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_subkey_button2
    )
    button_2.place(x=854, y=858, width=242, height=76)

    window.image_refs = [
        image_1, image_2, image_3, image_4, image_5,
        button_1_image, button_2_image
    ]

    return window
