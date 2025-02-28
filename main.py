import os
import logging
import aiohttp
import random
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
SITES = {
    "zoro": {
        "url": "https://zoro.tv/search?keyword=",
        "selectors": {
            "container": "div.film_list-wrap div.flw-item",
            "title": "h2.film-name a",
            "link": "h2.film-name a"
        }
    },
    "gogoanime": {
        "url": "https://gogoanime.hianime/search.html?keyword=",
        "selectors": {
            "container": "ul.items li",
            "title": "p.name a",
            "link": "p.name a"
        }
    },
    "nyaa": {
        "url": "https://nyaa.si/?q=",
        "selectors": {
            "container": "table.torrent-list tbody tr",
            "title": "td:nth-of-type(1) a:not(.comments)",
            "link": "td:nth-of-type(1) a:not(.comments)"
        }
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        "🎌 Anime Search Bot\n\n"
        "Use /search <anime_name> to find anime across multiple sites!\n"
        "Example: /search Attack on Titan"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search command"""
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a search query!")
        return

    query = " ".join(context.args)
    user_id = update.effective_user.id
    logging.info(f"New search from {user_id}: {query}")

    try:
        results = await fetch_all_results(query)
        if not results:
            await update.message.reply_text("❌ No results found across all sites")
            return

        response = format_response(query, results)
        keyboard = create_keyboard(results)
        
        await update.message.reply_text(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        await update.message.reply_text("🔧 Temporary server error. Please try again later.")

async def fetch_all_results(query: str):
    """Fetch results from all sites concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_site_results(session, "zoro", query),
            fetch_site_results(session, "gogoanime", query),
            fetch_site_results(session, "nyaa", query)
        ]
        results = await asyncio.gather(*tasks)
    return {site: data for site, data in zip(SITES.keys(), results)}

async def fetch_site_results(session: aiohttp.ClientSession, site: str, query: str):
    """Fetch results from a single site"""
    try:
        url = f"{SITES[site]['url']}{query.replace(' ', '%20')}"
        async with session.get(url, headers=HEADERS) as response:
            text = await response.text()
            return parse_results(site, text)
    except Exception as e:
        logging.error(f"{site} fetch error: {str(e)}")
        return []

def parse_results(site: str, html: str):
    """Parse HTML results for a specific site"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    for item in soup.select(SITES[site]['selectors']['container']):
        try:
            title = item.select_one(SITES[site]['selectors']['title']).text.strip()
            link = item.select_one(SITES[site]['selectors']['link'])['href']
            
            if site == "zoro":
                link = f"https://zoro.tv{link}"
            elif site == "nyaa":
                link = f"https://nyaa.si{link}"
            elif site == "gogoanime":
                link = f"https://gogoanime.hianime{link}"
            
            results.append((title, link))
        except Exception as e:
            logging.warning(f"{site} parse error: {str(e)}")
    
    return results[:3]  # Return top 3 results

def format_response(query: str, results: dict):
    """Format the response message"""
    response = f"🔍 *Results for* `{query}`:\n\n"
    for site, items in results.items():
        if items:
            response += f"🏮 *{site.capitalize()}*:\n"
            response += "\n".join([f"• [{title}]({link})" for title, link in items])
            response += "\n\n"
    return response

def create_keyboard(results: dict):
    """Create inline keyboard markup"""
    keyboard = []
    for site, items in results.items():
        if items:
            site_buttons = [
                InlineKeyboardButton(title, url=link)
                for title, link in items
            ]
            keyboard.append(site_buttons)
    return keyboard

if __name__ == "__main__":
    # Validate token
    if not TOKEN:
        raise ValueError("No BOT_TOKEN found in environment variables!")
    
    # Create application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    
    # Start bot
    application.run_polling()
