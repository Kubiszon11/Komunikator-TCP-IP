# server.py
import asyncio
import websockets

connected = {}  # Słownik połączeń: identyfikator -> websocket

async def handler(websocket, path):
    identyfikator = await websocket.recv()  # Oczekiwanie na identyfikator od klienta
    if identyfikator in connected:
        # Jeśli identyfikator jest już używany, odmów połączenia
        await websocket.send("Ten identyfikator jest już używany. Proszę spróbować innego.")
        await websocket.close(reason="Identyfikator jest już używany")
        return
    else:
        connected[identyfikator] = websocket
        print(f"{identyfikator} dołączył.")

    try:
        async for message in websocket:
            print(f"Odebrano od {identyfikator}: {message}")
            if message.startswith('do:'):
                _, dest_id, *msg_parts = message.split(' ')
                msg = ' '.join(msg_parts)
                if dest_id in connected:
                    await connected[dest_id].send(f"Od {identyfikator}: {msg}")
                else:
                    await websocket.send(f"Użytkownik {dest_id} nie jest dostępny.")
            else:
                for dest_id, conn in connected.items():
                    if conn != websocket:
                        await conn.send(f"Od {identyfikator}: {message}")
    finally:
        if identyfikator in connected:
            del connected[identyfikator]
            print(f"{identyfikator} opuścił.")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Uruchom serwer na zawsze

asyncio.run(main())
