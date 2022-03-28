import asyncio
from asyncio import Task
from typing import Optional
from app.web.app import app
from app.store import Store
from app.base.decorators import errors_catching_async
from app.store.vk_api.dataclasses import Message
from app.store.vk_api.keyboard import START_KEY

class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: Optional[Task] = None
        self.dead_line_task: Optional[Task] = None
        self.queue = asyncio.Queue()
        self.tasks = []

    @errors_catching_async
    async def dead_time_chacker(self):
        "Отслеживает время жизни игры"
        MAX_LIFETIME = 3
        while self.is_running:
            await asyncio.sleep(60)
            games_for_del = []
            for game in app.games.values():
                game.dead_time_count += 1
                if game.dead_time_count > MAX_LIFETIME:
                    games_for_del.append(game)
        
            while len(games_for_del) > 0:
                game = games_for_del.pop()
                message_text = await app.store.games.stop_game(game.chat_id)
                message_text += "<br>Игра завершена по таймауту"
                await app.store.vk_api.send_message(
                    Message(
                        user_id=111111,
                        peer_id=game.chat_id,
                        text=message_text,
                        id=""
                    ),
                    START_KEY
                )


    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())
        self.dead_line_task = asyncio.create_task(self.dead_time_chacker())
        for i in range(3):
            task = asyncio.create_task(self.worker(f'worker-{i}', self.queue))
            self.tasks.append(task) 

    async def stop(self):
        self.is_running = False
        await self.poll_task
        await self.dead_line_task
        await self.queue.join()
        # Cancel our worker tasks.
        for task in self.tasks:
            task.cancel()
        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*self.tasks, return_exceptions=True)

    async def poll(self):
        while self.is_running:
            updates = await self.store.vk_api.poll()
            self.queue.put_nowait(updates)
            

    async def worker(self, name, queue):
        while True:
            # Получить  элемент вне очереди.
            updates = await queue.get()
            await self.store.bots_manager.handle_updates(updates)
            # Сообщение очереди, для обработки "рабочего элемента".
            queue.task_done()