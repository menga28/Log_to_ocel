import os
import sys
import tkinter as tk


def load_asset(path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")
    return os.path.join(assets, path)


def create_row_info(parent, controller):
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

    image_13 = tk.PhotoImage(file=load_asset("frame_2/1.png"))
    image_14 = tk.PhotoImage(file=load_asset("frame_2/2.png"))
    image_15 = tk.PhotoImage(file=load_asset("frame_2/3.png"))
    image_16 = tk.PhotoImage(file=load_asset("frame_2/4.png"))
    image_17 = tk.PhotoImage(file=load_asset("frame_2/5.png"))
    image_18 = tk.PhotoImage(file=load_asset("frame_2/6.png"))
    image_19 = tk.PhotoImage(file=load_asset("frame_2/7.png"))
    image_20 = tk.PhotoImage(file=load_asset("frame_2/8.png"))
    image_21 = tk.PhotoImage(file=load_asset("frame_2/9.png"))
    image_22 = tk.PhotoImage(file=load_asset("frame_2/12.png"))
    image_23 = tk.PhotoImage(file=load_asset("frame_2/13.png"))
    image_24 = tk.PhotoImage(file=load_asset("frame_2/14.png"))

    window.canvas.create_image(721, 78, image=image_13)
    window.canvas.create_image(158, 73, image=image_14)
    window.canvas.create_image(720, 154, image=image_15)
    window.canvas.create_image(719, 341, image=image_16)
    window.canvas.create_image(713, 375, image=image_17)
    window.canvas.create_image(719, 612, image=image_18)
    window.canvas.create_image(713, 646, image=image_19)
    window.canvas.create_image(411, 857, image=image_20)
    window.canvas.create_image(891, 895, image=image_22)
    window.canvas.create_image(78, 784, image=image_23)
    window.canvas.create_image(78, 537, image=image_24)
    window.canvas.create_image(410, 891, image=image_21)

    text_ids = {
        "keys": window.canvas.create_text(
            87,
            342,
            anchor="nw",
            text="Key:",
            fill="#000000",
            font=("Inter", 16 * -1)
        ),
        "subkeys": window.canvas.create_text(
            75,
            613,
            anchor="nw",
            text="Sub-key:",
            fill="#000000",
            font=("Inter", 16 * -1)
        ),
        "statistics_df": window.canvas.create_text(
            67,
            858,
            anchor="nw",
            text="Number of logs, number of keys and sub-keys, size, median ",
            fill="#000000",
            font=("Inter", 16 * -1)
        )
    }

    controller.text_ids = {
        'row_info': text_ids
    }

    window.canvas.create_text(
        111,
        771,
        anchor="nw",
        text="Statistics of selected file",
        fill="#1e1e1e",
        font=("Inter", 24 * -1)
    )

    window.canvas.create_text(
        111,
        526,
        anchor="nw",
        text="Detected sub-keys in supported file formats",
        fill="#1e1e1e",
        font=("Inter", 24 * -1)
    )

    window.canvas.create_text(
        111,
        257,
        anchor="nw",
        text="Detected keys in supported file formats",
        fill="#1e1e1e",
        font=("Inter", 24 * -1)
    )

    button_5_image = tk.PhotoImage(file=load_asset("frame_2/10.png"))
    button_5 = tk.Button(
        image=button_5_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_row_button5
    )
    button_5.place(x=1129, y=858, width=267, height=76)

    button_6_image = tk.PhotoImage(file=load_asset("frame_2/11.png"))
    button_6 = tk.Button(
        image=button_6_image,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        command=controller.handle_set_file
    )
    button_6.place(x=854, y=858, width=242, height=76)

    window.image_refs = [
        image_13, image_14, image_15, image_16, image_17,
        image_18, image_19, image_20, image_21, image_22,
        image_23, image_24, button_5_image, button_6_image
    ]

    return window
