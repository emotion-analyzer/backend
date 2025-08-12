import asyncio

from analyzer.config import config
from analyzer.core.queue_middleware import process_posts
from analyzer.model.initialization import load_emotions_model
from analyzer.result_storage.initialization import initialize_mappings


async def initialize():
    """Initialize database, model and necessary queues."""
    elasticsearch_client = initialize_mappings()
    tokenizer, model = load_emotions_model()
    await process_posts(tokenizer,
                        model,
                        elasticsearch_client,
                        config)

def main():
    """Main function."""
    asyncio.run(initialize())

if __name__ == "__main__":
    main()
