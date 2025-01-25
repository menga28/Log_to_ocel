import os
import sys
import tkinter as tk
import easygui


def load_asset(path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(base, "assets")
    return os.path.join(assets, path)


window = tk.Tk()
window.geometry("1440x1024")
window.configure(bg="#ffffff")
window.title("Log")

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

image_1 = tk.PhotoImage(file=load_asset("frame_3/1.png"))

canvas.create_image(721, 78, image=image_1)

image_2 = tk.PhotoImage(file=load_asset("frame_3/2.png"))

canvas.create_image(158, 73, image=image_2)

image_3 = tk.PhotoImage(file=load_asset("frame_3/3.png"))

canvas.create_image(720, 154, image=image_3)

image_4 = tk.PhotoImage(file=load_asset("frame_3/4.png"))

canvas.create_image(719, 343, image=image_4)

image_5 = tk.PhotoImage(file=load_asset("frame_3/5.png"))

canvas.create_image(713, 375, image=image_5)

canvas.create_text(
    111,
    257,
    anchor="nw",
    text="Some sub-keys may need further normalization",
    fill="#1e1e1e",
    font=("Inter", 24 * -1)
)

button_1_image = tk.PhotoImage(file=load_asset("frame_3/6.png"))

button_1 = tk.Button(
    image=button_1_image,
    relief="flat",
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 has been pressed!")
)

button_1.place(x=1129, y=858, width=267, height=76)

button_2_image = tk.PhotoImage(file=load_asset("frame_3/7.png"))

button_2 = tk.Button(
    image=button_2_image,
    relief="flat",
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 has been pressed!")
)

button_2.place(x=854, y=858, width=242, height=76)

window.resizable(False, False)
window.mainloop()
