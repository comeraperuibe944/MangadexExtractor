# Mangadex Image Extractor
This Python script uses Selenium to automatically extract images from MangaDex chapters and save them locally by chapter.

## Features

- Automatically waits for all chapter images to load
- Handles both normal and blob images (using base64 extraction)
- Saves images in folders named after the chapter title
- Can extract multiple URLs from `urls.txt`

## Requirements

- Python 3.8+
- Google Chrome installed

## How to Use

On cmd:
```
pip install selenium webdriver-manager requests
```

Create a folder anywhere and insert ```main.py``` inside.

Create a file named ```urls.txt``` inside the same directory.

Edit ```urls.txt``` and paste any MangaDex chapter URL per line.

Run the script (open folder in terminal, and type ```python main.py```)
