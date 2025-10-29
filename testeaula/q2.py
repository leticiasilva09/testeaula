import requests
from bs4 import BeautifulSoup
import pandas as pd

# Função para obter o número total de páginas
def get_total_pages(base_url):
    response = requests.get(base_url)
    response.encoding = "utf-8"
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        pager = soup.find("li", class_="current")
        if pager:
            last_page = pager.text.strip().split()[-1]
            return int(last_page)
    return 1

# Função para extrair os dados dos livros
def scrape_books(base_url):
    total_pages = get_total_pages(base_url)
    book_list = []

    for page in range(1, total_pages + 1):
        if page == 1:
            url = f"{base_url}/index.html"
        else:
            url = f"{base_url}/catalogue/page-{page}.html"

        response = requests.get(url)
        response.encoding = "utf-8"
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            # Título
            title = book.h3.a.attrs["title"]

            # Preço
            price = book.find("p", class_="price_color").text.strip()

            # Classificação (ex: "Three", "Five", etc.)
            rating = book.p.attrs["class"][1]

            # Link da página do livro (para pegar categoria)
            book_url = book.h3.a["href"]
            if "catalogue/" not in book_url:
                book_url = "catalogue/" + book_url
            full_url = f"{base_url}/{book_url}"

            # Acessa a página do livro para extrair a categoria
            book_response = requests.get(full_url)
            book_response.encoding = "utf-8"
            book_soup = BeautifulSoup(book_response.text, "html.parser")
            category = book_soup.find("ul", class_="breadcrumb").find_all("a")[2].text.strip()

            # Adiciona os dados à lista
            book_list.append([title, price, rating, category])

        print(f"Página {page} concluída ({len(book_list)} livros até agora)")

    return book_list


# URL base
base_url = "https://books.toscrape.com"

# Extrair dados
books_data = scrape_books(base_url)

# Criar um DataFrame
df = pd.DataFrame(books_data, columns=["Título", "Preço", "Classificação", "Categoria"])

# Salvar em CSV
df.to_csv("books.csv", index=False, encoding="utf-8")

print("Dados extraídos e salvos com sucesso em 'books.csv'!")
