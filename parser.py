from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os


def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def login_phase(driver):
    print("[~] Открой браузер и войди в Instagram вручную.")
    driver.get("https://www.instagram.com/")
    input("🔑 После входа нажми Enter, чтобы продолжить...")


def scroll_followers(driver, target_username, scroll_limit=100):
    print(f"[~] Открываю профиль {target_username}...")
    driver.get(f"https://www.instagram.com/{target_username}/")
    time.sleep(5)

    try:
        followers_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/')]"))
        )
        followers_button.click()
    except Exception as e:
        print("⚠️ Не удалось найти кнопку подписчиков.")
        print(f"Ошибка: {e}")
        return []

    time.sleep(3)

    # Пытаемся дождаться контейнер
    try:
        scroll_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//div[@class='_aano']"))
        )
    except Exception as e:
        print("⚠️ Контейнер не появился автоматически. Проверь, что модалка открыта.")
        input("🔎 Открой список подписчиков вручную, если он не открылся, и нажми Enter...")
        with open("debug/page_debug_final.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("debug/screenshot_final.png")

        try:
            scroll_box = driver.find_element(By.XPATH, "//div[@role='dialog']//div[@class='_aano']")
        except:
            print("❌ Не удалось найти контейнер даже вручную.")
            return []

    # Скроллим
    last_height, height = 0, 1
    scrolls = 0
    while scrolls < scroll_limit and last_height != height:
        last_height = height
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
        time.sleep(1.5)
        height = driver.execute_script("return arguments[0].scrollTop", scroll_box)
        scrolls += 1
        print(f"↧ Прокручено: {scrolls}")

    # Сбор логинов
    followers = scroll_box.find_elements(By.XPATH, ".//a[contains(@href, '/') and not(contains(@href, 'following'))]")
    usernames = set()
    for el in followers:
        href = el.get_attribute("href")
        if href and href.count("/") == 4:
            usernames.add(href.split("/")[-2])

    print(f"[✓] Собрано логинов: {len(usernames)}")
    return list(usernames)



def save_to_csv(usernames, filename="followers_list.csv"):
    os.makedirs("data/output", exist_ok=True)
    with open("data/output/" + filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username"])
        for username in usernames:
            writer.writerow([username])
    print(f"[✓] Сохранено в data/output/{filename}")


if __name__ == "__main__":
    print("=== Instagram Followers Parser  ===")
    driver = setup_driver()
    login_phase(driver)

    target = input("Введите username аккаунта для сбора подписчиков: ").strip()
    followers = scroll_followers(driver, target, scroll_limit=50)
    save_to_csv(followers)
