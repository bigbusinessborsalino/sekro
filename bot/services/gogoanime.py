import aiohttp
from bs4 import BeautifulSoup

class GogoAnimeScraper:
    BASE_URL = "https://gogoanime.hianime"
    
    async def search(self, query: str) -> list:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}/search.html?keyword={query}") as res:
                    soup = BeautifulSoup(await res.text(), 'lxml')
                    return [{
                        'title': item.select_one('p.name a').text.strip(),
                        'link': self.BASE_URL + item.select_one('a')['href']
                    } for item in soup.select('ul.items li')]
        except:
            return []
