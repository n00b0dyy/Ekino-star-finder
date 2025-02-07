import sys
import asyncio
from PyQt5.QtWidgets import QApplication
from gui import EkinoScraperGUI


def main():
    app = QApplication(sys.argv)


    loop = asyncio.get_event_loop()
    window = EkinoScraperGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
