from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Get selected episode
    ep_number = query.data.split("_")[1]
    selected_anime = context.user_data['selected_anime']
    
    # Fetch quality options
    scraper = selected_anime['source']
    qualities = await scraper.get_qualities(ep_number)
    
    # Create quality buttons
    keyboard = []
    for quality in qualities:
        btn_text = f"{quality['language'].upper()} {quality['resolution']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"quality_{quality['id']}")])
    
    # Add navigation
    keyboard.append([
        InlineKeyboardButton("🔙 Back", callback_data="back_episodes"),
        InlineKeyboardButton("🏠 Menu", callback_data="main_menu")
    ])
    
    await query.edit_message_text(
        f"📀 {selected_anime['title']}\n"
        f"📺 Episode {ep_number}\n\n"
        "Select quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
