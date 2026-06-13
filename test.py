import asyncio
from playwright.async_api import async_playwright
import sys
sys.stdout.reconfigure(encoding='utf-8')

async def main():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            errors = []
            page.on('pageerror', lambda e: errors.append(f'PageError: {e}'))
            
            def handle_console(msg):
                if msg.type == 'error':
                    errors.append(f'ConsoleError: {msg.text}')
            page.on('console', handle_console)
            
            await page.goto('file:///C:/Desktop/projects/stlw%20hackthon/udan/UDAAN%20AI%20(standalone).html')
            await page.wait_for_timeout(2000)
            
            display_login = await page.evaluate('window.getComputedStyle(document.getElementById("view-login")).display')
            display_landing = await page.evaluate('window.getComputedStyle(document.getElementById("view-landing")).display')
            active_classes = await page.evaluate('Array.from(document.querySelectorAll(".spa-view.active")).map(el => el.id)')
            hash_val = await page.evaluate('location.hash')
            
            print('Errors:', errors)
            print('Login display:', display_login)
            print('Landing display:', display_landing)
            print('Active classes:', active_classes)
            print('Location hash:', hash_val)
            
            await browser.close()
    except Exception as e:
        print('EXCEPTION:', e)

asyncio.run(main())
