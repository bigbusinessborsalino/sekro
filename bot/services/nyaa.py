import aiohttp
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class NyaaScraper(BaseScraper):
    BASE_URL = "https://nyaa.si"
    
    async def search(self, query: str) -> list:
        try:
            async with self.session.get(
                f"{self.BASE_URL}/",
                params={"q": query, "s": "seeders", "o": "desc"},
                headers=self.headers
            ) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                results = []
                for row in soup.select('table.torrent-list tbody tr'):
                    try:
                        results.append({
                            'title': row.select_one('td:nth-child(2) a').text.strip(),
                            'link': self.BASE_URL + row.select_one('td:nth-child(2) a')['href'],
                            'size': row.select_one('td:nth-child(4)').text.strip(),
                            'seeders': int(row.select_one('td:nth-child(6)').text),
                            'source': 'nyaa'
                        })
                    except Exception as e:
                        continue
                return sorted(results, key=lambda x: -x['seeders'])
        except Exception as e:
            return []

    async def get_episodes(self, anime_url: str) -> list:
        # Nyaa doesn't have episodes, return single "episode"
        return [{
            'number': 1,
            'title': 'Torrent Download',
            'link': anime_url
        }]

    async def get_download_links(self, episode_url: str) -> dict:
        try:
            async with self.session.get(episode_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                return {
                    'qualities': [{
                        'quality': 'Torrent',
                        'link': soup.select_one('a.card-footer-item[href$=".torrent"]')['href']
                    }],
                    'source': 'nyaa'
                }
        except Exception as e:
            return {}
