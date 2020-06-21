def add_screen(items, func):
    for item in items:
        if item.url.startswith('https://t.me'):
            continue
        func(id=item.id, url=item.url)
        print(f'{item.url} ---- DONE!')
    print('All screens added!')