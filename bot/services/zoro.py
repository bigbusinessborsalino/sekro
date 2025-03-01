import aiohttp
from bs4 import BeautifulSoup

class ZoroScraper:
    BASE_URL = "https://zoro.tv"
    
    async def search(self, query: str) -> list:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}/search?keyword={query}") as res:
                    soup = BeautifulSoup(await res.text(), 'lxml')
                    return [{
                        'title': item.select_one('h2.film-name').text.strip(),
                        'link': self.BASE_URL + item.select_one('a')['href']
                    } for item in soup.select('div.flw-item')]
        except:
            return []
