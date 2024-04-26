import asyncio
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import websockets
from threading import Thread

class ChatClient(tk.Tk):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop

        self.user_id = simpledialog.askstring("Identyfikator", "Podaj swój identyfikator:", parent=self)
        if self.user_id:
            self.title(self.user_id)  # Ustawienie tytułu okna na identyfikator użytkownika
        else:
            self.destroy()  # Zamknij aplikację, jeśli nie podano identyfikatora

        self.geometry("400x500")

        self.text_area = scrolledtext.ScrolledText(self, state='disabled')
        self.text_area.pack(padx=20, pady=5, expand=True, fill='both')

        self.msg_entry = tk.Entry(self)
        self.msg_entry.pack(padx=20, pady=5, fill='x')
        self.msg_entry.bind("<Return>", self.send_message)

        self.websocket = None
        if self.user_id:
            asyncio.run_coroutine_threadsafe(self.setup_websocket(), self.loop)

    async def setup_websocket(self):
        self.websocket = await websockets.connect('ws://localhost:8765')
        await self.websocket.send(self.user_id)
        self.loop.create_task(self.receive_messages())

    async def receive_messages(self):
        while True:
            message = await self.websocket.recv()
            self.display_message(message)
            if message == "Ten identyfikator jest już używany. Proszę spróbować innego.":
                self.websocket = None
                self.loop.call_soon_threadsafe(self.connect_to_server)

    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert('end', message + '\n')
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message and self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.send(message), self.loop)
            self.msg_entry.delete(0, 'end')

def run_app(loop):
    app = ChatClient(loop)
    app.mainloop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    chat_thread = Thread(target=run_app, args=(loop,))
    chat_thread.start()
    loop.run_forever()
