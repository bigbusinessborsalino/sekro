import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler
)
from config import Config
from bot.handlers import (
    start,
    search,
    show_episode_selection,
    handle_episode_pagination,
    handle_quality_selection,
    handle_download
)
from bot.utils import error_handler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    # Validate configuration
    Config.validate()

    # Create application
    application = ApplicationBuilder() \
        .token(Config.BOT_TOKEN) \
        .post_init(setup_health_check) \
        .build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search.search))

    # Episode selection flow
    application.add_handler(CallbackQueryHandler(
        show_episode_selection, 
        pattern=r"^select_\d+$"
    ))
    application.add_handler(CallbackQueryHandler(
        handle_episode_pagination,
        pattern=r"^ep_page_\d+$"
    ))

    # Quality selection flow
    application.add_handler(CallbackQueryHandler(
        handle_quality_selection,
        pattern=r"^ep_\d+$"
    ))

    # Download handling
    application.add_handler(CallbackQueryHandler(
        handle_download,
        pattern=r"^quality_"
    ))

    # Navigation handlers
    application.add_handler(CallbackQueryHandler(
        search.show_search_page,
        pattern=r"^page_\d+$"
    ))
    application.add_handler(CallbackQueryHandler(
        search.show_search_page,
        pattern="^back_search$"
    ))
    application.add_handler(CallbackQueryHandler(
        show_episode_selection,
        pattern="^back_episodes$"
    ))

    # Error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling(
        http_port=8080,
        health_check_path='/health',
        allowed_updates=Update.ALL_TYPES
    )

async def setup_health_check(application: Application):
    """Set up health check endpoint"""
    from aiohttp import web
    from bot.utils.health import health_check
    
    web_app = web.Application()
    web_app.add_routes([web.get('/health', health_check)])
    application.bot._web_app = web_app

if __name__ == "__main__":
    main()
