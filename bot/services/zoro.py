import aiohttp
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class ZoroScraper(BaseScraper):
    BASE_URL = "https://zoro.tv"
    
    async def search(self, query: str) -> list:
        try:
            async with self.session.get(
                f"{self.BASE_URL}/search",
                params={"keyword": query},
                headers=self.headers
            ) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                results = []
                for item in soup.select('div.film_list-wrap div.flw-item'):
                    try:
                        results.append({
                            'title': item.select_one('h2.film-name a').text.strip(),
                            'link': self.BASE_URL + item.select_one('h2.film-name a')['href'],
                            'year': item.select_one('span.film-infor span:nth-child(1)').text.strip(),
                            'duration': item.select_one('span.film-infor span:nth-child(3)').text.strip(),
                            'source': 'zoro'
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
                for item in soup.select('div.ss-list a'):
                    episodes.append({
                        'number': item['data-number'],
                        'title': item.select_one('div.ssli-title').text.strip(),
                        'link': self.BASE_URL + item['href']
                    })
                return sorted(episodes, key=lambda x: int(x['number']))
        except Exception as e:
            return []

    async def get_download_links(self, episode_url: str) -> dict:
        try:
            async with self.session.get(episode_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                qualities = []
                for item in soup.select('div.server-quality select option'):
                    if item['value'] != '0':
                        qualities.append({
                            'quality': item.text.strip(),
                            'id': item['value'],
                            'language': 'sub' if 'sub' in item.text.lower() else 'dub'
                        })
                
                return {
                    'qualities': qualities,
                    'download_base': f"{self.BASE_URL}/ajax/v2/episode/sources/"
                }
        except Exception as e:
            return {}
