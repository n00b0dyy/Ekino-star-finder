import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QCheckBox, QScrollArea,
    QLineEdit, QLabel, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
from scraper import get_categories, get_movies


class EkinoScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Ekino Scraper")
        self.setGeometry(100, 100, 900, 800)  # Większe okno

        # Zmiana kolorów GUI
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))  # Czarne tło
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))  # Białe napisy
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Pole do wpisania liczby stron
        self.pages_label = QLabel("Ile stron przeszukać?", self)
        self.pages_label.setFont(QFont("Arial", 18))  # Większa czcionka
        self.pages_label.setStyleSheet("color: white;")
        layout.addWidget(self.pages_label)

        self.pages_input = QLineEdit(self)
        self.pages_input.setPlaceholderText("Podaj liczbę stron (np. 3)")
        self.pages_input.setFont(QFont("Arial", 18))
        self.pages_input.setStyleSheet("color: black; background-color: white;")
        layout.addWidget(self.pages_input)

        # Scroll area dla kategorii filmowych
        category_scroll = QScrollArea()
        category_scroll.setWidgetResizable(True)
        category_widget = QWidget()
        category_layout = QGridLayout(category_widget)  # Grid dla kategorii

        # Pobranie kategorii z ekino-tv
        self.categories = get_categories()

        # Tworzenie checkboxów dla kategorii (max 10 na kolumnę, max 6 kolumn)
        self.checkboxes = {}
        row = 0
        col = 0
        for name, link in self.categories.items():
            checkbox = QCheckBox(name)
            checkbox.setFont(QFont("Arial", 18))  # Większa czcionka
            checkbox.setStyleSheet("color: white;")  # Białe napisy
            category_layout.addWidget(checkbox, row, col)
            self.checkboxes[name] = (checkbox, link)

            row += 1
            if row >= 10:  # Maksymalnie 10 kategorii w kolumnie
                row = 0
                col += 1
                if col >= 6:  # Maksymalnie 6 kolumn
                    break

        category_scroll.setWidget(category_widget)
        layout.addWidget(category_scroll)

        # Przycisk pobierania filmów
        search_btn = QPushButton("Pobierz filmy", self)
        search_btn.setFont(QFont("Arial", 18, QFont.Bold))
        search_btn.setStyleSheet("background-color: white; color: black; padding: 10px;")
        search_btn.clicked.connect(self.scrape_movies)
        layout.addWidget(search_btn)

        # Scroll area dla listy filmów
        self.movies_scroll = QScrollArea()
        self.movies_scroll.setWidgetResizable(True)
        self.movies_widget = QWidget()
        self.movies_layout = QVBoxLayout(self.movies_widget)
        self.movies_scroll.setWidget(self.movies_widget)
        layout.addWidget(self.movies_scroll)

        self.setLayout(layout)

    def scrape_movies(self):
        """ Pobiera filmy z wybranej kategorii i wyświetla wyniki w GUI """
        selected_categories = [name for name, (cb, link) in self.checkboxes.items() if cb.isChecked()]
        max_pages = self.pages_input.text()

        if not selected_categories:
            QMessageBox.warning(self, "Uwaga", "Nie wybrano żadnej kategorii!")
            return

        # Walidacja liczby stron
        if not max_pages.isdigit() or int(max_pages) < 1:
            QMessageBox.warning(self, "Błąd", "Podaj poprawną liczbę stron!")
            return

        max_pages = int(max_pages)

        # Czyszczenie poprzednich wyników
        for i in reversed(range(self.movies_layout.count())):
            self.movies_layout.itemAt(i).widget().setParent(None)

        for category in selected_categories:
            category_link = self.categories[category]
            print(f"\n🎬 Filmy w kategorii: {category} (Przeszukiwane strony: {max_pages})\n")

            movies = get_movies(category_link, max_pages)

            if not movies:
                print("⚠ Brak filmów w tej kategorii.")
                continue

            for title, rating, link in movies:
                # Tworzenie klikalnego linku w HTML
                film_html = f"""
                    <p style="color: white; font-size: 20px;">
                        <b>{title} ({rating}⭐)</b><br>
                        <a href="{link}" style="color: #00BFFF;">{link}</a>
                    </p>
                """
                film_label = QLabel(film_html)
                film_label.setTextFormat(Qt.RichText)
                film_label.setOpenExternalLinks(True)  # Link otwiera się w przeglądarce
                film_label.setWordWrap(True)
                self.movies_layout.addWidget(film_label)

                # Dodanie odstępu (30px) po każdym filmie
                spacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
                self.movies_layout.addSpacerItem(spacer)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EkinoScraperGUI()
    window.show()
    sys.exit(app.exec_())
