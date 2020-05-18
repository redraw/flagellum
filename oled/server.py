#!/usr/bin/env python3
import os
import signal
import asyncio

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher

from ui import Screen

OSC_HOST = os.getenv("OSC_HOST", "127.0.0.1")
OSC_PORT = os.getenv("OSC_PORT", 4001)

serial = i2c(port=1, address=0x3c)
oled = ssd1306(serial)
print("OLED connected!")

screen = Screen(oled, fps=25)

def oled_handler(address, *args):
    #print("{}: {}".format(address, args))
    global screen
    line = address.split("/")[-1]
    if line in screen.data.keys():
        screen.data[line] = " ".join(str(arg) for arg in args)


dispatcher = Dispatcher()
dispatcher.map("/oled/line*", oled_handler)
dispatcher.set_default_handler(print)


async def display():
    while True:
        screen.draw()
        await asyncio.sleep(1/screen.fps)


async def main():
    address = (OSC_HOST, OSC_PORT)
    server = AsyncIOOSCUDPServer(address, dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    print(f"OSC server running at port {OSC_PORT}")
    await display()
    transport.close()


async def shutdown(s, loop):
    print(f"Received exit signal {s.name}...")
    
    print("Cleanup OLED")
    screen.device.cleanup()

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop))
        )
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

