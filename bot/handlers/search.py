from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from bot.services import ZoroScraper, GogoAnimeScraper, NyaaScraper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎌 Anime Download Bot\n"
        "Use /search <anime_name> to find content\n"
        "Example: /search Attack on Titan"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Please provide a search query!")
        return

    # Search all sources
    results = []
    for scraper in [ZoroScraper(), GogoAnimeScraper(), NyaaScraper()]:
        results += await scraper.search(query)
    
    # Store results and show first page
    context.user_data['search_results'] = results
    await show_search_page(update, context, page=1)

async def show_search_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    results = context.user_data['search_results']
    items_per_page = 10
    total_pages = (len(results) + items_per_page - 1) // items_per_page
    
    # Format message
    response = f"🔍 Search Results (Page {page}/{total_pages}):\n\n"
    for idx, item in enumerate(results[(page-1)*items_per_page : page*items_per_page], 1):
        response += f"{idx}. {item['title']}\n"
    
    # Create buttons
    buttons = [
        [InlineKeyboardButton(str(i), callback_data=f"select_{i}") 
        for i in range(1, len(results)+1)
    ]
    
    # Add pagination
    pagination = []
    if page > 1:
        pagination.append(InlineKeyboardButton("◀ Prev", callback_data=f"page_{page-1}"))
    if page < total_pages:
        pagination.append(InlineKeyboardButton("Next ▶", callback_data=f"page_{page+1}"))
    
    await update.message.reply_text(
        response,
        reply_markup=InlineKeyboardMarkup(buttons + [pination])
    )
