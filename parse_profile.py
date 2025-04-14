import json
import time
from bs4 import BeautifulSoup
from parser import setup_driver, login_phase
import re
import pandas as pd
import os


def parse_profile(driver, username):
    url = f"https://www.instagram.com/{username}/"
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
    try:
        ld_json = soup.find("script", type="application/ld+json")
        if ld_json:
            data = json.loads(ld_json.string)
            result["full_name"] = data.get("name", "")
            desc = data.get("description", "")
            result["bio"] = desc if desc and "@" not in desc else ""  # bio будет дополняться ниже
    except:
        pass

    # === 2. BIO и внешняя ссылка (section)
    try:
        section = soup.find("section")
        bio_lines = []
        if section:
            for tag in section.find_all(["span", "a"]):
                text = tag.get_text(strip=True)
                if not text:
                    continue
                lower = text.lower()
                # фильтруем мусор
                if any(x in lower for x in [
                    "значок", "meta", "помощь", "блог", "вакансии", "условия",
                    "информация", "конфиденциальность", "загрузка контактов",
                    "threads", "instagram lite", "русский", "api", "публикац", "отметки", "места"
                ]):
                    continue
                if text.isdigit():
                    continue
                if tag.name == "a":
                    href = tag.get("href", "")
                    if any(href.startswith(p) for p in
                           ["http://", "https://", "t.me", "vk.com", "linktr.ee", "taplink.cc", "github.com"]):
                        if not any(bad in href for bad in ["facebook.com", "instagram.com"]):
                            result["external_url"] = href
                else:
                    bio_lines.append(text)
        if bio_lines:
            result["bio"] = "\n".join(dict.fromkeys(bio_lines))
    except:
        pass

    # === 3. Подписчики, подписки, посты
    try:
        for li in soup.find_all("li"):
            txt = li.text.lower()
            if " подписчиков" in txt or "followers" in txt:
                result["followers"] = li.text.split(" ")[0]
            elif " подписок" in txt or "following" in txt:
                result["following"] = li.text.split(" ")[0]
            elif " публикаций" in txt or "posts" in txt:
                result["posts"] = li.text.split(" ")[0]
    except:
        pass

    # === 4. Приватность
    result["is_private"] = "Да" if "Это закрытый аккаунт" in driver.page_source else "Нет"

    # === 5. Email
    email_candidates = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", result["bio"])
    if email_candidates:
        result["email"] = email_candidates[0]

    # === 6. Телефон — простая проверка на 6+ цифр
    digits = re.findall(r"[+()\d\s-]{6,}", result["bio"])
    for d in digits:
        clean = re.sub(r"[^\d]", "", d)
        if len(clean) >= 6:
            result["phone"] = clean
            break

    return result


def save_single_profile_to_excel(profile_data):
    os.makedirs("data/output", exist_ok=True)

    df = pd.DataFrame([profile_data])
    column_order = [
        "username", "full_name", "bio", "external_url", "followers",
        "following", "posts", "is_private", "email", "phone", "profile_url"
    ]
    df = df[column_order]
    df.to_excel("data/output/single_profile.xlsx", index=False)
    print("✅ Профиль успешно сохранён в data/output/single_profile.xlsx")


if __name__ == "__main__":
    driver = setup_driver()
    login_phase(driver)

    username = input("Введите username для анализа: ").strip()
    profile_data = parse_profile(driver, username)

    print("📋 Данные профиля:")
    for k, v in profile_data.items():
        print(f"{k}: {v}")

    save_single_profile_to_excel(profile_data)

