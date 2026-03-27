import asyncio
from bleak import BleakClient
from pynput import keyboard

ADDRESS = "0A:C0:31:24:F9:C1"
CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"

# key state
keys = {
    "w": False,
    "a": False,
    "s": False,
    "d": False
}


def build_packet():
    packet = bytearray(16)
    packet[1:4] = b"CTL"

    packet[1] = 1 if keys["w"] else 0  # forward
    packet[2] = 1 if keys["s"] else 0  # reverse
    packet[3] = 1 if keys["a"] else 0  # left
    packet[4] = 1 if keys["d"] else 0  # right

    return packet


def on_press(key):
    try:
        if key.char in keys:
            keys[key.char] = True
    except:
        pass


def on_release(key):
    try:
        if key.char in keys:
            keys[key.char] = False
    except:
        pass


async def control_loop(client):
    while True:
        packet = build_packet()
        await client.write_gatt_char(CHAR_UUID, packet, response=False)
        await asyncio.sleep(0.05)  # ~20Hz


async def main():
    async with BleakClient(ADDRESS) as client:
        print("Connected:", client.is_connected)

        # start keyboard listener
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        listener.start()

        print("Use WASD to control the car. Ctrl+C to exit.")

        await control_loop(client)


if __name__ == "__main__":
    asyncio.run(main())