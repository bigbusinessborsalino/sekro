import os
import aiohttp
import aiofiles
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.progress import DownloadProgress
from config import Config

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Get download info
    selected = context.user_data['selected_anime']
    quality_id = query.data.split("_")[1]
    ep_number = context.user_data['selected_episode']
    
    # Get download link
    scraper = selected['source']
    download_info = await scraper.get_download_link(
        selected['link'],
        ep_number,
        quality_id
    )
    
    # Initialize progress
    progress = DownloadProgress(
        update=update,
        context=context,
        total_size=download_info['size'],
        download_type="📥 Downloading"
    )
    
    # Download file
    temp_path = os.path.join(Config.TEMP_DIR, download_info['filename'])
    os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(download_info['url']) as response:
                async with aiofiles.open(temp_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024*1024):
                        await f.write(chunk)
                        await progress.update(chunk)
        
        # Upload to Telegram
        await handle_upload(update, context, temp_path)
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    upload_progress = DownloadProgress(
        update=update,
        context=context,
        total_size=os.path.getsize(file_path),
        download_type="📤 Uploading"
    )
    
    async with aiofiles.open(file_path, 'rb') as f:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f,
            filename=os.path.basename(file_path),
            progress=upload_progress.update,
            read_timeout=Config.DOWNLOAD_TIMEOUT
        )
