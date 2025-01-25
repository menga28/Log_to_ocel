from views.gui import Gui
from controller.controller import Controller


def main():
    view = Gui()
    controller = Controller(view)
    controller.start()


if __name__ == '__main__':
    main()
