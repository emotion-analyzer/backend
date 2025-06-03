import asyncio

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustChannel


async def initiate_connection(config):
    """Initialize the connection to the RabbitMQ server."""
    return await aio_pika.connect_robust(
        host=config.RABBIT_MQ.HOST,
        port=config.RABBIT_MQ.PORT,
        login=config.RABBIT_MQ.USERNAME,
        password=config.RABBIT_MQ.PASSWORD)


async def process_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        # FALTA: Procesar y mandar a guardar en la base de datos
        print(f"Message body is: {message.body!r}")


async def process_posts(config) -> None:
    connection = await initiate_connection(config)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(config.RABBIT_MQ.PROCESSING_QUEUE, durable=True)
        await queue.consume(process_message)
        await asyncio.Future()


async def initialize_channel(config)-> AbstractRobustChannel :
    connection = await initiate_connection(config)
    await connection.connect()
    channel = await connection.channel()
    await channel.declare_queue(config.RABBIT_MQ.PROCESSING_QUEUE, durable=True)
    return channel


async def send_message(message, channel, config) -> None:
    await channel.default_exchange.publish(message, routing_key=config.RABBIT_MQ.PROCESSING_QUEUE)
