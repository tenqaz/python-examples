"""
@author: Jim
@file: async_consumer_producer.py
@time: 2019/12/21 17:43
@desc:

    使用协程完成生产者与消费者的例子。
"""

import asyncio
from asyncio.queues import Queue
import random


async def consumer(queue: Queue, id: str) -> None:
    while True:
        val = await queue.get()
        print('{} get a val: {}'.format(id, val))
        await asyncio.sleep(1)


async def producter(queue: Queue, id: str) -> None:
    for i in range(5):
        val = random.randint(1, 10)
        await queue.put(val)
        print('{} put a value: {}'.format(id, val))
        await asyncio.sleep(1)


async def main():
    queue = asyncio.Queue()

    consumer_1 = asyncio.create_task(consumer(queue, 'consumer_1'))
    consumer_2 = asyncio.create_task(consumer(queue, 'consumer_2'))

    producter_1 = asyncio.create_task(producter(queue, 'producter_1'))
    producter_2 = asyncio.create_task(producter(queue, 'producter_2'))
    await asyncio.sleep(10)
    consumer_1.cancel()
    consumer_2.cancel()

    await asyncio.gather(consumer_1, consumer_2, producter_1, producter_2,
                         return_exceptions=True)


if __name__ == '__main__':
    asyncio.run(main())
