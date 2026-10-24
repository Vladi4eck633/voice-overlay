from pynput import keyboard


def on_press(key):
    print("press:", repr(key))


def on_release(key):
    print("release:", repr(key))
    if key == keyboard.Key.esc:
        return False  # Esc stops the test


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("Press keys (Esc to quit)...")
    listener.join()