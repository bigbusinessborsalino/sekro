import time
from telegram import Update
from telegram.ext import ContextTypes

class DownloadProgress:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                 total_size: int, download_type: str):
        self.update = update
        self.context = context
        self.total_size = total_size
        self.download_type = download_type
        self.start_time = time.time()
        self.last_update = 0
        self.downloaded = 0

    async def update(self, chunk):
        self.downloaded += len(chunk)
        now = time.time()
        
        if now - self.last_update > 1:
            progress = self.downloaded / self.total_size
            elapsed = now - self.start_time
            speed = self.downloaded / elapsed
            remaining = (self.total_size - self.downloaded) / speed
            
            bar = self._create_bar(progress)
            text = (
                f"{self.download_type}\n"
                f"{bar} {progress:.1%}\n"
                f"📦 {self._format_size(self.downloaded)}/{self._format_size(self.total_size)}\n"
                f"⏳ Remaining: {self._format_time(remaining)}"
            )
            
            try:
                await self.update.effective_message.edit_text(text)
            except Exception as e:
                self.context.logger.error(f"Progress update failed: {str(e)}")
            
            self.last_update = now

    def _create_bar(self, progress: float, width: int = 20) -> str:
        filled = int(width * progress)
        return "[" + "▓" * filled + "░" * (width - filled) + "]"

    def _format_size(self, bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024:
                break
            bytes /= 1024
        return f"{bytes:.2f} {unit}"

    def _format_time(self, seconds: float) -> str:
        return f"{int(seconds//3600):02}:{int((seconds%3600)//60):02}:{int(seconds%60):02}"
