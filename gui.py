import sys
import asyncio
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QCheckBox, QScrollArea,
    QLineEdit, QLabel, QMessageBox, QDoubleSpinBox, QLabel, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
from scraper import get_categories, get_movies


class EkinoScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.categories = {}  
        self.checkboxes = {} 
        self.initUI()

        self.load_categories()

    def load_categories(self):
        """ Uruchamia asynchroniczne pobieranie kategorii w PyQt5 """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.categories = loop.run_until_complete(get_categories())
        self.populate_categories()

    def populate_categories(self):
        """ Aktualizuje listę checkboxów po pobraniu kategorii """
        category_layout = self.category_layout
        row, col = 0, 0
        for name, link in self.categories.items():
            checkbox = QCheckBox(name)
            checkbox.setFont(QFont("Arial", 16))
            checkbox.setStyleSheet("color: white;")
            category_layout.addWidget(checkbox, row, col)
            self.checkboxes[name] = (checkbox, link)

            row += 1
            if row >= 10:  
                row = 0
                col += 1

    def initUI(self):
        self.setWindowTitle("Ekino Scraper")
        self.showMaximized()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)

        layout = QVBoxLayout()

        
        self.pages_label = QLabel("Ile stron przeszukać?", self)
        self.pages_label.setFont(QFont("Arial", 18))
        self.pages_label.setStyleSheet("color: white;")
        layout.addWidget(self.pages_label)

        self.pages_input = QLineEdit(self)
        self.pages_input.setPlaceholderText("Podaj liczbę stron (np. 3)")
        self.pages_input.setFont(QFont("Arial", 16))
        self.pages_input.setStyleSheet("color: black; background-color: white;")
        layout.addWidget(self.pages_input)

        
        self.stars_label = QLabel("Minimalna liczba gwiazdek:", self)
        self.stars_label.setFont(QFont("Arial", 18))
        self.stars_label.setStyleSheet("color: white;")
        layout.addWidget(self.stars_label)

        self.stars_input = QDoubleSpinBox(self)
        self.stars_input.setRange(0.0, 10.0)
        self.stars_input.setSingleStep(0.1)
        self.stars_input.setValue(0.0)
        self.stars_input.setFont(QFont("Arial", 16))
        self.stars_input.setStyleSheet("color: black; background-color: white;")
        layout.addWidget(self.stars_input)

        category_scroll = QScrollArea()
        category_scroll.setWidgetResizable(True)
        category_widget = QWidget()
        self.category_layout = QGridLayout(category_widget)
        category_scroll.setWidget(category_widget)
        layout.addWidget(category_scroll)

      
        search_btn = QPushButton("Pobierz filmy", self)
        search_btn.setFont(QFont("Arial", 18, QFont.Bold))
        search_btn.setStyleSheet("background-color: white; color: black; padding: 10px;")
        search_btn.clicked.connect(self.scrape_movies)
        layout.addWidget(search_btn)

    
        self.movies_scroll = QScrollArea()
        self.movies_scroll.setWidgetResizable(True)
        self.movies_widget = QWidget()
        self.movies_layout = QVBoxLayout(self.movies_widget)
        self.movies_scroll.setWidget(self.movies_widget)
        layout.addWidget(self.movies_scroll)

        self.setLayout(layout)

    def scrape_movies(self):
        """ Pobiera filmy z wybranej kategorii asynchronicznie """
        selected_categories = [name for name, (cb, link) in self.checkboxes.items() if cb.isChecked()]
        max_pages = self.pages_input.text()
        min_stars = self.stars_input.value()

        if not selected_categories:
            QMessageBox.warning(self, "Uwaga", "Nie wybrano żadnej kategorii!")
            return

        if not max_pages.isdigit() or int(max_pages) < 1:
            QMessageBox.warning(self, "Błąd", "Podaj poprawną liczbę stron!")
            return

        max_pages = int(max_pages)

    
        for i in reversed(range(self.movies_layout.count())):
            self.movies_layout.itemAt(i).widget().setParent(None)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_movies(selected_categories, max_pages, min_stars))

    async def fetch_movies(self, selected_categories, max_pages, min_stars):
        """ Asynchroniczne pobieranie filmów z wybranych kategorii """
        tasks = []
        for category in selected_categories:
            category_link = self.categories[category]
            tasks.append(get_movies(category_link, max_pages))

        all_movies = await asyncio.gather(*tasks)  

        for movies in all_movies:
            for title, rating, link in movies:
                try:
                    rating_value = float(rating)  
                except ValueError:
                    continue

                if rating_value < min_stars:
                    continue

                film_html = f"""
                    <p style="color: white; font-size: 20px;">
                        <b>{title} ({rating}⭐)</b><br>
                        <a href="{link}" style="color: #00BFFF;">{link}</a>
                    </p>
                """
                film_label = QLabel(film_html)
                film_label.setTextFormat(Qt.RichText)
                film_label.setOpenExternalLinks(True)
                film_label.setWordWrap(True)
                self.movies_layout.addWidget(film_label)
                spacer = QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
                self.movies_layout.addSpacerItem(spacer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EkinoScraperGUI()
    window.show()
    sys.exit(app.exec_())
