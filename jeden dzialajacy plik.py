import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QCheckBox, QLabel, QScrollArea, QMessageBox

class EkinoScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Ekino Kategorie")
        self.setGeometry(100, 100, 400, 500)

        # Layout główny
        layout = QVBoxLayout()

        # Scroll area dla checkboxów
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.checkboxes_layout = QVBoxLayout(scroll_content)

        # Pobieranie kategorii z ekino-tv
        self.categories = self.get_categories()

        # Tworzenie checkboxów dla kategorii
        self.checkboxes = {}
        for name, link in self.categories.items():
            checkbox = QCheckBox(name)
            self.checkboxes_layout.addWidget(checkbox)
            self.checkboxes[name] = (checkbox, link)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Przycisk pobierania filmów
        search_btn = QPushButton("Pobierz filmy", self)
        search_btn.clicked.connect(self.scrape_movies)
        layout.addWidget(search_btn)

        self.setLayout(layout)

    def get_categories(self):
        """ Pobiera kategorie filmowe ze strony ekino-tv.pl """
        url = "https://ekino-tv.pl/movie/cat/+"
        headers = {"User-Agent": "Mozilla/5.0"}
        categories = {}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Znalezienie menu kategorii
            menu_wrap = soup.find("div", class_="col-md-4 menu-wrap")
            if not menu_wrap:
                raise ValueError("Nie znaleziono kategorii!")

            # Pobranie wszystkich linków z menu
            for a in menu_wrap.find_all("a"):
                name = a.get_text(strip=True)
                link = f"https://ekino-tv.pl{a['href']}" if a['href'].startswith("/") else a['href']
                categories[name] = link

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się pobrać kategorii: {e}")

        return categories

    def scrape_movies(self):
        """ Pobiera filmy z wybranej kategorii i wyświetla wyniki w konsoli """
        selected_categories = [name for name, (cb, link) in self.checkboxes.items() if cb.isChecked()]

        if not selected_categories:
            QMessageBox.warning(self, "Uwaga", "Nie wybrano żadnej kategorii!")
            return

        for category in selected_categories:
            category_link = self.categories[category]
            print(f"\n🎬 Filmy w kategorii: {category}\n")

            try:
                response = requests.get(category_link, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Pobranie wszystkich filmów
                movies = soup.find_all("div", class_="movies-list-item")

                if not movies:
                    print("Brak filmów w tej kategorii.")
                    continue

                for movie in movies:
                    # Pobranie tytułu
                    title_tag = movie.find("div", class_="title")
                    title = title_tag.get_text(strip=True) if title_tag else "Brak tytułu"

                    # Pobranie linku do filmu
                    link = title_tag.find("a")["href"] if title_tag and title_tag.find("a") else "Brak linku"
                    full_link = f"https://ekino-tv.pl{link}" if link.startswith("/") else link

                    # Pobranie oceny (liczba gwiazdek)
                    vote_tag = movie.find("div", class_="sum-vote")
                    rating = vote_tag.get_text(strip=True) if vote_tag else "Brak oceny"

                    print(f"{title} ({rating}⭐)\n{full_link}\n")

            except requests.exceptions.RequestException as e:
                print(f"Błąd podczas pobierania filmów z kategorii {category}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EkinoScraperGUI()
    window.show()
    sys.exit(app.exec_())
