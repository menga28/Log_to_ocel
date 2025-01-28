import os
import sys
import tkinter as tk


def load_asset(path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")
    return os.path.join(assets, path)


def create_home(parent, controller):
    window = tk.Frame(parent, bg="#ffffff")

    canvas = tk.Canvas(
        window,
        bg="#ffffff",
        width=1440,
        height=1024,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)

    image_6 = tk.PhotoImage(file=load_asset("frame_1/1.png"))
    image_7 = tk.PhotoImage(file=load_asset("frame_1/2.png"))
    image_8 = tk.PhotoImage(file=load_asset("frame_1/3.png"))
    image_9 = tk.PhotoImage(file=load_asset("frame_1/4.png"))
    image_10 = tk.PhotoImage(file=load_asset("frame_1/5.png"))
    image_11 = tk.PhotoImage(file=load_asset("frame_1/8.png"))
    image_12 = tk.PhotoImage(file=load_asset("frame_1/9.png"))

    canvas.create_image(720, 160, image=image_6)
    canvas.create_image(459, 658, image=image_7)
    canvas.create_image(719, 158, image=image_8)
    canvas.create_image(720, 317, image=image_9)
    canvas.create_image(459, 550, image=image_10)
    canvas.create_image(121, 514, image=image_11)
    canvas.create_image(1193, 661, image=image_12)

    canvas.create_text(
        142,
        499,
        anchor="nw",
        text="Log file selection to map to Ocel2",
        fill="#1e1e1e",
        font=("Inter", 24 * -1)
    )

    canvas.create_text(
        114,
        625,
        anchor="nw",
        text="Select a file that you want to map to ocel2 ",
        fill="#1e1e1e",
        font=("Inter", 16 * -1)
    )

    button_3_image = tk.PhotoImage(file=load_asset("frame_1/6.png"))
    button_3 = tk.Button(
        window,
        image=button_3_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_set_file
    )
    button_3.place(x=123, y=724, width=193, height=76)

    button_4_image = tk.PhotoImage(file=load_asset("frame_1/7.png"))
    button_4 = tk.Button(
        window,
        image=button_4_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_set_default_file
    )
    button_4.place(x=361, y=724, width=242, height=76)

    window.image_refs = [
        image_6, image_7, image_8, image_9,
        image_10, button_3_image, button_4_image,
        image_11, image_12
    ]

    return window
