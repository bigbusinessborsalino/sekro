from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from bot.services import ZoroScraper, GogoAnimeScraper, NyaaScraper
from bot.utils.helpers import format_anime_details, create_pagination_buttons

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎌 Welcome to Anime Download Bot!\n"
        "Use /search <anime_name> to find anime content."
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Please provide a search query!")
        return

    # Search all sources
    zoro = ZoroScraper()
    gogo = GogoAnimeScraper()
    nyaa = NyaaScraper()
    
    results = []
    results += await zoro.search(query)
    results += await gogo.search(query)
    results += await nyaa.search(query)
    
    # Store results and show first page
    context.user_data['search_results'] = results
    await show_search_page(update, context, page=1)

async def show_search_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    results = context.user_data['search_results']
    items_per_page = 10
    total_pages = (len(results) + items_per_page - 1) // items_per_page
    
    # Paginate results
    start_idx = (page-1)*items_per_page
    page_results = results[start_idx:start_idx+items_per_page]
    
    # Format message
    response = f"🔍 Search Results (Page {page}/{total_pages}):\n\n"
    for idx, item in enumerate(page_results, 1):
        response += f"{start_idx+idx}. {item['title']}\n   └─ Source: {item['source'].upper()}\n\n"
    
    # Create keyboard
    keyboard = []
    # Number buttons
    number_buttons = [
        InlineKeyboardButton(str(start_idx+i+1), callback_data=f"select_{start_idx+i}")
        for i in range(len(page_results))
    ]
    keyboard += [number_buttons[i:i+5] for i in range(0, len(number_buttons), 5)]
    
    # Pagination controls
    pagination = []
    if page > 1:
        pagination.append(InlineKeyboardButton("◀ Prev", callback_data=f"page_{page-1}"))
    if page < total_pages:
        pagination.append(InlineKeyboardButton("Next ▶", callback_data=f"page_{page+1}"))
    
    if pagination:
        keyboard.append(pagination)
    
    await update.message.reply_text(
        response,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
