from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from View.gui import Gui
from datetime import datetime
from pathlib import Path
import easygui
import getpass


class GuiController:

    def __init__(self, view: Gui):
        self.view = view
        self.gui = self.view.guis["singleinsectgui"]
        self._bind()

    def _bind(self):
        self.gui.upload_button.config(command=self.file_dialog)

    def file_dialog(self):
        self.path = easygui.fileopenbox(msg="Choose file", title="InsectaCam",  filetypes=[
            "*.png", "*.jpg"], multiple=False, default="//*.png")
        self.process_file(self.path)
        self.update_image(self.path)

    def process_file(self,file_path):
        start_time = datetime.now()
        _, _, probs = learn.predict(PILImage.create(file_path))
        end_time = datetime.now()
        self.generate_csv(file_path, probs, start_time, end_time)
        self.update_probs(probs)

    def generate_csv(self, file_path, probs, start_time, end_time, csv_file_path="output_data.csv"):
        self.user_name = getpass.getuser()
        fieldnames = [
            "File selected",
            "Probability for Lucila", "Probability for Mosca Domestica", "Probability for Piofila",
            "User Name", "Start Time", "End Time"
        ]
        with open(csv_file_path, mode="a", newline="", encoding="utf-8") as csv_file:
            self.csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if csv_file.tell() == 0:
                self.csv_writer.writeheader()
            self.csv_writer.writerow({
                "File selected": file_path,
                "Probability for Lucila": f"{probs[0]:.4f}",
                "Probability for Mosca Domestica": f"{probs[1]:.4f}",
                "Probability for Piofila": f"{probs[2]:.4f}",
                "User Name": self.user_name,
                "Start Time": start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            }
        )
    
    def update_image(self, path):
        global img
        self.img = PilImage.open(path).resize((200, 200))
        self.img = ImageTk.PhotoImage(self.img)
        self.gui.itemconfig(tagOrId=self.gui.upload_frame, image=self.img)

    def update_probs(self, probs):
        self.gui.itemconfig(tagOrId=self.gui.lsPercentage, text=f"{100*probs[0]:.1f}%")
        self.gui.itemconfig(tagOrId=self.gui.mdPercentage, text=f"{100*probs[1]:.1f}%")
        self.gui.itemconfig(tagOrId=self.gui.pcPercentage, text=f"{100*probs[2]:.1f}%")
        if (100*probs[0] > 50):
            self.gui.itemconfig(tagOrId=self.gui.speciesDetected, text="Lucilia Sericata Detected")
        if (100*probs[1] > 50):
            self.gui.itemconfig(tagOrId=self.gui.speciesDetected, text="Musca Domestica Detected")
        if (100*probs[2] > 50):
            self.gui.itemconfig(tagOrId=self.gui.speciesDetected, text="Piophila Casei Detected")


    

