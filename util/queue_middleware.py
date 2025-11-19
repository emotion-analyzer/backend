import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractRobustQueue, ExchangeType
from aio_pika.exceptions import (ChannelClosed, AMQPConnectionError,
                                 ConnectionClosed)

async def initiate_connection(config) -> AbstractRobustConnection:
    """Initialize the connection to the RabbitMQ server."""
    return await aio_pika.connect_robust(
        host=config.RABBIT_MQ.HOST,
        port=config.RABBIT_MQ.PORT,
        login=config.RABBIT_MQ.USERNAME,
        password=config.RABBIT_MQ.PASSWORD)

async def declare_queue(channel: AbstractRobustChannel,
                        name: str, logger) -> AbstractRobustQueue:
    try:
        return await channel.declare_queue(name, durable=True)
    except ChannelClosed:
        logger.error(f"Channel closed while declaring {name} queue.")
        raise
    except (AMQPConnectionError, ConnectionClosed):
        logger.error(f"Connection lost while declaring {name} queue.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while declaring {name} queue: {e}.")
        raise

async def send_message(exchange,
                       message, queue_name, logger):
    try:
        await exchange.publish(
            message, routing_key=queue_name)
    except ChannelClosed:
        logger.error(f"Channel closed during publishing at {queue_name}.")
        raise
    except (AMQPConnectionError, ConnectionClosed):
        logger.error(f"Connection lost during publishing at {queue_name}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during publishing at {queue_name}: {e}.")
        raise

async def initialize_exchange(channel, exchange_name, logger):
    """Initialize required exchange(s)."""
    results_exchange = await channel.declare_exchange(exchange_name,
                                                      ExchangeType.TOPIC)
    return results_exchange