from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class ZoroScraper(BaseScraper):
    BASE_URL = "https://zoro.tv"
    
    async def search(self, query: str) -> list:
        async with self.session.get(f"{self.BASE_URL}/search?keyword={query}") as res:
            soup = BeautifulSoup(await res.text(), 'lxml')
            return [{
                'title': item.select_one('h2.film-name').text.strip(),
                'link': self.BASE_URL + item.select_one('a')['href'],
                'source': self,
                'year': item.select_one('.film-infor span').text.strip()
            } for item in soup.select('.film_list-wrap .flw-item')]
    
    async def get_episodes(self, anime_url: str) -> list:
        async with self.session.get(anime_url) as res:
            soup = BeautifulSoup(await res.text(), 'lxml')
            return [{
                'number': idx+1,
                'title': item.text.strip(),
                'link': self.BASE_URL + item['href']
            } for idx, item in enumerate(soup.select('.ss-list a'))]
    
    async def get_qualities(self, episode_url: str) -> list:
        async with self.session.get(episode_url) as res:
            soup = BeautifulSoup(await res.text(), 'lxml')
            return [{
                'id': item['data-quality'],
                'resolution': item.text.strip(),
                'language': 'sub' if 'sub' in item.text.lower() else 'dub'
            } for item in soup.select('.quality-item')]
    
    async def get_download_link(self, episode_url: str, quality_id: str) -> dict:
        # Implementation to fetch actual download URL
        return {
            'url': f"{episode_url}/download/{quality_id}",
            'filename': "episode.mp4",
            'size': 1024*1024*500  # Example 500MB
        }
