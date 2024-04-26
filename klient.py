# client.py
import asyncio
import websockets
import aioconsole


async def send_messages(websocket):
    while True:
        message = await aioconsole.ainput("")
        await websocket.send(message)


async def receive_messages(websocket):
    while True:
        message = await websocket.recv()
        print(message)
        if message == "Ten identyfikator jest już używany. Proszę spróbować innego.":
            return "retry"


async def main():
    while True:
        identyfikator = input("Podaj swój identyfikator: ")
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            await websocket.send(identyfikator)  # Wyślij identyfikator na początku połączenia
            send_task = asyncio.create_task(send_messages(websocket))
            result = await receive_messages(websocket)

            if result == "retry":
                print("Proszę wybrać inny identyfikator.")
                continue  # Powrót do początku pętli, aby ponownie wybrać identyfikator

            # Oczekiwanie na zakończenie zadania wysyłania (co powinno nastąpić tylko przy zamknięciu połączenia)
            await send_task


asyncio.run(main())
