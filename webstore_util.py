import asyncio

import keyboard


async def check_selector_exists(page, selector):
    elements = await page.query_selector_all(selector)
    return len(elements) > 0


# can use this to detect if the page changes order on me
async def wait_for_selectors(page, selector1, selector2):
    tasks = [
        asyncio.create_task(page.wait_for_selector(selector1)),
        asyncio.create_task(page.wait_for_selector(selector2))
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

    if tasks[0] in done:
        return selector1
    elif tasks[1] in done:
        return selector2


# use this if I see best buy survey again
async def watch_for_popup(page, popup_selector, close_button_selector):
    await page.wait_for_selector(popup_selector)
    print("Popup detected!")
    await page.wait_for_selector(close_button_selector)
    await page.click(close_button_selector)
    print("Popup dismissed")


async def wait_for_user_action():
    print("Waiting for user action... Press ` to continue")
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    def on_keypress(event):
        if event.name == '`':
            future.set_result(None)

    keyboard_hook = keyboard.on_press(on_keypress)
    await future
    keyboard.unhook(keyboard_hook)
    print("User action detected!")

# simple function but would be repeated a lot without it
async def wait_then_click(page, selector):
    await page.wait_for_selector(selector)
    await page.click(selector)