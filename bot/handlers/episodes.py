from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.helpers import create_pagination_buttons

async def show_episode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Get selected anime
    selected_idx = int(query.data.split("_")[1])
    selected_anime = context.user_data['search_results'][selected_idx]
    
    # Fetch episodes
    scraper = selected_anime['source']  # Get appropriate scraper
    episodes = await scraper.get_episodes(selected_anime['link'])
    
    # Store context
    context.user_data['selected_anime'] = selected_anime
    context.user_data['episodes'] = episodes
    context.user_data['current_page'] = 1
    
    await show_episode_page(query, context)

async def show_episode_page(query, context: ContextTypes.DEFAULT_TYPE):
    page = context.user_data['current_page']
    episodes = context.user_data['episodes']
    items_per_page = 10
    
    # Paginate episodes
    start_idx = (page-1)*items_per_page
    page_episodes = episodes[start_idx:start_idx+items_per_page]
    
    # Format message
    anime = context.user_data['selected_anime']
    response = (
        f"📺 {anime['title']}\n"
        f"📅 {anime.get('year', '')} | {anime.get('episodes', '')} Episodes\n"
        f"⭐ Rating: {anime.get('rating', 'N/A')}\n\n"
        f"Select Episode (Page {page}/{(len(episodes)+items_per_page-1)//items_per_page}):\n"
    )
    
    # Create episode buttons
    keyboard = []
    for idx, ep in enumerate(page_episodes, 1):
        btn_text = f"Ep {ep['number']}: {ep['title'][:20]}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"ep_{ep['number']}")])
    
    # Add pagination controls
    pagination = []
    if page > 1:
        pagination.append(InlineKeyboardButton("◀ Prev", callback_data=f"ep_page_{page-1}"))
    if page < (len(episodes)/items_per_page):
        pagination.append(InlineKeyboardButton("Next ▶", callback_data=f"ep_page_{page+1}"))
    
    if pagination:
        keyboard.append(pagination)
    
    # Add navigation
    keyboard.append([
        InlineKeyboardButton("🔙 Back", callback_data="back_search"),
        InlineKeyboardButton("🏠 Menu", callback_data="main_menu")
    ])
    
    await query.edit_message_text(
        response,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_episode_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    page = int(query.data.split("_")[-1])
    context.user_data['current_page'] = page
    await show_episode_page(query, context)
