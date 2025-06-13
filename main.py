from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import base64
import requests
import time
import os
import re

# XPaths
XPATH_IMAGES = '//*[@id="__nuxt"]/div[1]/div[2]/div[3]/div/div[1]/div[2]/div[1]/div/div/img'
XPATH_FIRST_IMAGE = '//*[@id="__nuxt"]/div[1]/div[2]/div[3]/div/div[1]/div[2]/div[1]/div/div[1]/img'
XPATH_TITLE = '//*[@id="__nuxt"]/div[1]/div[2]/div[3]/div/div[1]/div[1]/div[2]/div[1]'

# Read URLs
def read_urls(file="urls.txt"):
    if not os.path.exists(file):
        print(f"File '{file}' not found.")
        return []
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_first_image(driver, timeout=20):
    print("⏳ Waiting for the first image to render...")
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, XPATH_FIRST_IMAGE))
        )
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("""
            const img = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            return img && img.complete && img.naturalWidth > 0;
        """, XPATH_FIRST_IMAGE))
        print("✅ First image loaded successfully.")
        return True
    except Exception as e:
        print("❌ Failed to load the first image:", e)
        return False

def find_image_elements(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, XPATH_IMAGES))
        )
        images = driver.find_elements(By.XPATH, XPATH_IMAGES)
        print(f"🔍 Found {len(images)} image(s).")
        return images
    except Exception as e:
        print("⚠️ Error locating images:", e)
        return []


def extract_title(driver):
    try:
        title_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATH_TITLE))
        )
        title = title_elem.text.strip()
        sanitized_title = re.sub(r'[\\/*?:"<>|]', '_', title)
        print(f"📂 Chapter detected: {sanitized_title}")
        return sanitized_title
    except:
        print("⚠️ Chapter title not found. Using 'Unknown_Chapter'")
        return "Unknown_Chapter"



def create_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)


def download_image(src_url, path):
    try:
        response = requests.get(src_url)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"✅ Saved: {path}")
        else:
            print("Error downloading image:", response.status_code)
    except Exception as e:
        print("Error saving image:", e)

def extract_base64_from_canvas(driver, element):
    script = """
    const img = arguments[0];
    const canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    return canvas.toDataURL('image/jpeg');
    """
    try:
        return driver.execute_script(script, element)
    except Exception as e:
        print("Error extracting base64:", e)
        return None


def save_base64_image(data_url, path):
    try:
        header, encoded = data_url.split(",", 1)
        data = base64.b64decode(encoded)
        with open(path, "wb") as f:
            f.write(data)
        print(f"✅ Saved (base64): {path}")
    except Exception as e:
        print("Error saving base64 image:", e)


def generate_filename(index):
    return f"page_{index:03d}.jpg"

def process_chapter(driver, url):
    print(f"\n🔗 Accessing: {url}")
    driver.get(url)
    time.sleep(2)

    if not wait_for_first_image(driver):
        print("⚠️ Skipping this chapter due to image load failure.")
        return

    chapter_title = extract_title(driver)
    create_folder(chapter_title)

    images = find_image_elements(driver)

    for i, img in enumerate(images, start=1):
        src = img.get_attribute("src")
        filename = generate_filename(i)
        full_path = os.path.join(chapter_title, filename)

        if src.startswith("blob:"):
            data_url = extract_base64_from_canvas(driver, img)
            if data_url:
                save_base64_image(data_url, full_path)
        elif src.startswith("http"):
            download_image(src, full_path)
        else:
            print("❌ Invalid SRC:", src)

if __name__ == "__main__":
    urls = read_urls("urls.txt")
    if not urls:
        print("No valid URLs found.")
        exit()

    driver = start_driver()

    for url in urls:
        process_chapter(driver, url)

    driver.quit()
    print("\n🎉 Done! All images were saved by chapter.")
