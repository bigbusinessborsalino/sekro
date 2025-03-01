import aiohttp
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    BASE_URL = ""
    
    def __init__(self):
        self.session = aiohttp.ClientSession()
    
    @abstractmethod
    async def search(self, query: str) -> list:
        pass
    
    @abstractmethod
    async def get_episodes(self, anime_url: str) -> list:
        pass
    
    @abstractmethod
    async def get_qualities(self, episode_url: str) -> list:
        pass
    
    @abstractmethod
    async def get_download_link(self, episode_url: str, quality_id: str) -> dict:
        pass
    
    async def close(self):
        await self.session.close()
