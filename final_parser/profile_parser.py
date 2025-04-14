import time
import json
import re
from bs4 import BeautifulSoup


def get_profile_url(username):
    """Создает URL для профиля пользователя."""
    return f"https://www.instagram.com/{username}/"


def extract_ld_json(soup):
    """Извлекает данные из ld+json для имени и описания."""
    try:
        ld_json = soup.find("script", type="application/ld+json")
        if ld_json:
            data = json.loads(ld_json.string)
            full_name = data.get("name", "")
            bio = data.get("description", "")
            return full_name, bio
    except Exception:
        return "", ""
    return "", ""


def filter_bio(bio):
    """Фильтрует ненужную информацию из bio (например, подписчики, подписки)."""
    lines = bio.split("\n")
    filtered_lines = []
    for line in lines:
        # Убираем информацию о подписчиках и подписках
        if "подписчиков" in line.lower() or "подписок" in line.lower():
            continue
        # Оставляем остальные строки
        filtered_lines.append(line)
    return "\n".join(filtered_lines)

def extract_bio_and_external_url(soup):
    """Извлекает bio и внешнюю ссылку из секции профиля, фильтруя ненужную информацию."""
    bio_lines = []
    external_url = ""
    try:
        section = soup.find("section")
        if section:
            for tag in section.find_all(["span", "a"]):
                text = tag.get_text(strip=True)
                if not text:
                    continue
                lower = text.lower()
                if any(x in lower for x in [
                        "значок", "meta", "помощь", "блог", "вакансии", "условия",
                        "информация", "конфиденциальность", "загрузка контактов",
                        "threads", "instagram lite", "русский", "api", "публикац", "отметки", "места",
                        "reels"
                ]):
                    continue
                if text.isdigit():
                    continue
                if tag.name == "a":
                    href = tag.get("href", "")
                    if any(href.startswith(p) for p in
                           ["http://", "https://", "t.me", "vk.com", "linktr.ee", "taplink.cc", "github.com"]):
                        if not any(bad in href for bad in ["facebook.com", "instagram.com"]):
                            external_url = href
                else:
                    bio_lines.append(text)
        bio = "\n".join(dict.fromkeys(bio_lines))
        bio = filter_bio(bio)  # Фильтруем информацию из bio
        return bio, external_url
    except Exception:
        return "", ""


def extract_followers_and_posts(soup):
    """Извлекает количество подписчиков, подписок и постов."""
    followers = following = posts = ""
    try:
        for li in soup.find_all("li"):
            txt = li.text.lower()
            if " подписчиков" in txt or "followers" in txt:
                followers = li.text.split(" ")[0]
            elif " подписок" in txt or "following" in txt:
                following = li.text.split(" ")[0]
            elif " публикаций" in txt or "posts" in txt:
                posts = li.text.split(" ")[0]
    except Exception:
        pass
    return followers, following, posts


def extract_email_from_bio(bio):
    """Извлекает email из bio."""
    email_candidates = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", bio)
    return email_candidates[0] if email_candidates else "-"


def extract_phone_from_bio(bio):
    """Извлекает телефонный номер из bio."""
    digits = re.findall(r"[+()\d\s-]{6,}", bio)
    for d in digits:
        clean = re.sub(r"[^\d]", "", d)
        if len(clean) >= 9:
            return clean
    return "-"


def is_private_account(driver):
    """Определяет, является ли аккаунт приватным."""
    return "Да" if "Это закрытый аккаунт" in driver.page_source else "Нет"


def parse_profile(driver, username):
    """Основная функция для парсинга профиля."""
    url = get_profile_url(username)
    driver.get(url)
    time.sleep(5)

    result = {
        "username": username,
        "full_name": "",
        "bio": "",
        "external_url": "",
        "followers": "",
        "following": "",
        "posts": "",
        "is_private": "",
        "email": "-",
        "phone": "-",
        "profile_url": url
    }

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # === 1. ld+json
    result["full_name"], result["bio"] = extract_ld_json(soup)

    # === 2. BIO и внешняя ссылка
    result["bio"], result["external_url"] = extract_bio_and_external_url(soup)

    # === 3. Подписчики, подписки, посты
    result["followers"], result["following"], result["posts"] = extract_followers_and_posts(soup)

    # === 4. Приватность
    result["is_private"] = is_private_account(driver)

    # === 5. Email
    result["email"] = extract_email_from_bio(result["bio"])

    # === 6. Телефон
    result["phone"] = extract_phone_from_bio(result["bio"])

    return result
