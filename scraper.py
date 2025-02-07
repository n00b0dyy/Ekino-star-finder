import asyncio
import aiohttp
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse_movies(html):
    """ Parsowanie HTML w osobnym wątku """
    soup = BeautifulSoup(html, "html.parser")
    movies = soup.find_all("div", class_="movies-list-item")

    movies_list = []
    for movie in movies:
       
        title_tag = movie.find("div", class_="title")
        title = title_tag.get_text(strip=True) if title_tag else "Brak tytułu"

      
        link = title_tag.find("a")["href"] if title_tag and title_tag.find("a") else "Brak linku"
        full_link = f"https://ekino-tv.pl{link}" if link.startswith("/") else link

       
        vote_tag = movie.find("div", class_="sum-vote")
        rating = vote_tag.get_text(strip=True) if vote_tag else "Brak oceny"

        movies_list.append((title, rating, full_link))

    return movies_list


async def fetch(session, url):
    """ Asynchroniczne pobieranie strony """
    try:
        async with session.get(url, headers=HEADERS) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"❌ Błąd podczas pobierania strony {url}: {e}")
        return None


async def get_movies(category_url, max_pages=1):
    """ Pobiera filmy z danej kategorii i przeszukuje do max_pages stron """
    movies_list = []
    tasks = []
    urls = []


    for page in range(1, max_pages + 1):
        if page == 1:  
            page_url = category_url if category_url.endswith("+") else category_url + "+"
        else:  
            page_url = category_url.rstrip("+") + f"+strona[{page}]+"
        urls.append(page_url)

    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch(session, url))

        responses = await asyncio.gather(*tasks)


    with ThreadPoolExecutor() as executor:
        for html in responses:
            if html:
                movies = executor.submit(parse_movies, html).result()
                movies_list.extend(movies)

    return movies_list


async def get_categories():
    """ Pobiera kategorie filmowe z ekino-tv.pl """
    url = "https://ekino-tv.pl/movie/cat/+"
    categories = {}

    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            menu_wrap = soup.find("div", class_="col-md-4 menu-wrap")
            if not menu_wrap:
                raise ValueError("Nie znaleziono kategorii!")

            for a in menu_wrap.find_all("a"):
                name = a.get_text(strip=True)
                link = f"https://ekino-tv.pl{a['href']}" if a['href'].startswith("/") else a['href']
                categories[name] = link

    return categories


def main():
    """ Główna funkcja """
    loop = asyncio.get_event_loop()
    categories = loop.run_until_complete(get_categories())
    print("Kategorie:", categories)

    first_category_url = list(categories.values())[0]
    movies = loop.run_until_complete(get_movies(first_category_url, max_pages=3))
    print("\nFilmy:")
    for movie in movies:
        print(movie)


if __name__ == "__main__":
    main()
