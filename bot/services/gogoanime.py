import aiohttp
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class GogoAnimeScraper(BaseScraper):
    BASE_URL = "https://gogoanime.hianime"
    
    async def search(self, query: str) -> list:
        try:
            async with self.session.get(
                f"{self.BASE_URL}/search.html",
                params={"keyword": query},
                headers=self.headers
            ) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                results = []
                for item in soup.select('ul.items li'):
                    try:
                        results.append({
                            'title': item.select_one('p.name a').text.strip(),
                            'link': self.BASE_URL + item.select_one('p.name a')['href'],
                            'year': item.select_one('p.released').text.strip().split(': ')[1],
                            'source': 'gogoanime'
                        })
                    except Exception as e:
                        continue
                return results
        except Exception as e:
            return []

    async def get_episodes(self, anime_url: str) -> list:
        try:
            async with self.session.get(anime_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                episodes = []
                for item in soup.select('#episode_related a'):
                    episodes.append({
                        'number': item['ep_end'],
                        'title': item.text.strip(),
                        'link': self.BASE_URL + item['href'].strip()
                    })
                return sorted(episodes, key=lambda x: int(x['number']))
        except Exception as e:
            return []

    async def get_download_links(self, episode_url: str) -> dict:
        try:
            async with self.session.get(episode_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                download_div = soup.select_one('div.anime_muti_link')
                return {
                    'qualities': [{
                        'quality': li.text.split('-')[1].strip(),
                        'link': li.select_one('a')['href']
                    } for li in download_div.select('li')],
                    'source': 'gogoanime'
                }
        except Exception as e:
            return {}
