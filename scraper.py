import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_categories():
    """ Pobiera kategorie filmowe z ekino-tv.pl """
    url = "https://ekino-tv.pl/movie/cat/+"
    categories = {}

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        menu_wrap = soup.find("div", class_="col-md-4 menu-wrap")
        if not menu_wrap:
            raise ValueError("Nie znaleziono kategorii!")

        for a in menu_wrap.find_all("a"):
            name = a.get_text(strip=True)
            link = f"https://ekino-tv.pl{a['href']}" if a['href'].startswith("/") else a['href']
            categories[name] = link

    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania kategorii: {e}")

    return categories

def get_movies(category_url, max_pages=1):
    """ Pobiera filmy z danej kategorii i przeszukuje do max_pages stron """
    movies_list = []

    for page in range(1, max_pages + 1):
        # Generowanie URL dla paginacji
        if page == 1:  # Pierwsza strona bez parametru "strona"
            page_url = category_url if category_url.endswith("+") else category_url + "+"
        else:  # Kolejne strony z parametrem "strona[X]"
            page_url = category_url.rstrip("+") + f"+strona[{page}]+"

        try:
            print(f"Przeszukuję stronę: {page_url}")  # Debugowanie
            response = requests.get(page_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Znajdź filmy na stronie
            movies = soup.find_all("div", class_="movies-list-item")

            if not movies:
                print(f"⚠ Brak filmów na stronie {page}.")
                continue

            for movie in movies:
                # Pobierz tytuł filmu
                title_tag = movie.find("div", class_="title")
                title = title_tag.get_text(strip=True) if title_tag else "Brak tytułu"

                # Pobierz link do filmu
                link = title_tag.find("a")["href"] if title_tag and title_tag.find("a") else "Brak linku"
                full_link = f"https://ekino-tv.pl{link}" if link.startswith("/") else link

                # Pobierz liczbę gwiazdek
                vote_tag = movie.find("div", class_="sum-vote")
                rating = vote_tag.get_text(strip=True) if vote_tag else "Brak oceny"

                movies_list.append((title, rating, full_link))

        except requests.exceptions.RequestException as e:
            print(f"❌ Błąd podczas pobierania filmów z {page_url}: {e}")

    return movies_list
