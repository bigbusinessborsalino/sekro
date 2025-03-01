from telegram import InlineKeyboardButton

def format_anime_details(anime: dict) -> str:
    return (
        f"🎬 Title: {anime['title']}\n"
        f"📅 Year: {anime.get('year', 'N/A')}\n"
        f"⭐ Rating: {anime.get('rating', 'N/A')}\n"
        f"📺 Episodes: {anime.get('episodes', 'N/A')}"
    )

def create_pagination_buttons(current_page: int, total_pages: int) -> list:
    buttons = []
    if current_page > 1:
        buttons.append(InlineKeyboardButton("◀ Prev", callback_data=f"page_{current_page-1}"))
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("Next ▶", callback_data=f"page_{current_page+1}"))
    return buttons
