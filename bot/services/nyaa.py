import aiohttp
from bs4 import BeautifulSoup

class NyaaScraper:
    BASE_URL = "https://nyaa.si"
    
    async def search(self, query: str) -> list:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}/?q={query}") as res:
                    soup = BeautifulSoup(await res.text(), 'lxml')
                    return [{
                        'title': row.select_one('td:nth-child(2) a').text.strip(),
                        'link': self.BASE_URL + row.select_one('a')['href']
                    } for row in soup.select('table.torrent-list tbody tr')]
        except:
            return []
