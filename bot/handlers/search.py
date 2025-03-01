from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.services import ZoroScraper, GogoAnimeScraper, NyaaScraper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎌 Welcome to Anime Download Bot!\n"
        "Use /search <anime_name> to find content."
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Please provide a search query!")
        return

    try:
        # Initialize scrapers
        scrapers = [ZoroScraper(), GogoAnimeScraper(), NyaaScraper()]
        
        # Search all sources
        results = []
        for scraper in scrapers:
            results += await scraper.search(query)
            
        # Store results and show first page
        context.user_data['search_results'] = results
        await show_search_page(update, context, page=1)
        
    except Exception as e:
        await update.message.reply_text("Error searching for anime. Please try again.")

async def show_search_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    # Implementation remains same as previous version
    pass
