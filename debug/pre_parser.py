from bs4 import BeautifulSoup

file_path = 'page_debug_final.html'

def parse_followers(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Используем BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(content, 'html.parser')

    # Ищем имя пользователя (из тега title) и удаляем лишние символы
    title_tag = soup.find('title')
    if title_tag:
        username = title_tag.get_text().split('@')[-1].split(' ')[0].replace(')', '').strip()
    else:
        username = "Unknown"

    # Ищем все теги <span>, содержащие имена подписчиков
    follower_elements = soup.find_all('span', class_="_ap3a _aaco _aacw _aacx _aad7 _aade")
    followers = []

    for element in follower_elements:
        follower_name = element.get_text().strip()

        # Фильтруем ненужные имена (например, имя самого пользователя или аккаунт, который смотрит)
        if follower_name and follower_name != username:
            if follower_name not in followers:  # избегаем дубли
                followers.append(follower_name)

    return username, followers

# Извлекаем имя пользователя и список подписчиков
username, followers = parse_followers(file_path)

# Печатаем результат в консоль
print(f"Username: {username}")
print("Followers Names:")
for i, follower in enumerate(followers, 1):
    print(f"{i}. {follower}")

print(f"Profile Link: /{username}/")

# Сохраняем данные в txt файл
def save_to_txt(username, followers, output_file="followers.txt"):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(f"Username: {username}\n")
        file.write("Followers Names:\n")
        for i, follower in enumerate(followers, 1):
            file.write(f"{i}. {follower}\n")
        file.write(f"Profile Link: /{username}/\n")

# Сохраняем результат в файл
save_to_txt(username, followers)
