# Instagram Profile Parser

Парсер Instagram-профилей на Python.:

- Получать список подписчиков с профиля 
- Собирать расширенные данные профиля: имя, биография, ссылки, количество подписчиков, почта, телефон и т.д.
- Сохранять результат в Excel-файл

---

## ✨ Возможности

- 🔢 Режим 1: Парсинг одного профиля по username (ручной)
- 📄 Выгрузка результата в `single_profile.xlsx` и `mass_profiles.xlsx`

---

## 🚀 Установка и запуск

1. **Клонировать репозиторий**
```
git clone https://github.com/Nick8927/IgParser/
```

2. **Создать и активировать виртуальное окружение**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate    # Linux/macOS
```

3. **Установить зависимости**
```bash
pip install -r requirements.txt
```

4. **Убедитесь, что установлен Chrome + ChromeDriver**
- Используется `webdriver_manager`, установка драйвера автоматическая

---

## 🔧 Использование

### Режим 1 — Парсинг одного профиля

```bash
python main.py
```

Программа:
- Откроет браузер
- Запросит логин (username)
- Позволит вручную залогиниться в Instagram
- Соберёт данные профиля
- Сохранит результат в `data/output/single_profile.xlsx`

---

## 📄 Поля, которые собираются:

- `username` — логин пользователя
- `full_name` — имя (если указано)
- `bio` — описание профиля (фильтруется от мусора)
- `external_url` — внешняя ссылка (например, Telegram, Linktree)
- `followers`, `following`, `posts` — числовые метрики
- `is_private` — приватный ли аккаунт
- `email`, `phone` — извлекаются из bio при наличии
- `profile_url` — ссылка на профиль

---

## 🛡️ Примечания

- Instagram может временно ограничивать сбор — используйте с задержками
- В случае режима сбора подписчиков: рекомендуется прокручивать список подписчиков вручную и сохранять HTML заранее

---

## 📄  Структура проекта

```
IgParser/
├── main.py                  # Ручной запуск
├── parser/
│   ├── profile_parser.py    # Логика сбора данных
│   ├── browser.py           # WebDriver и логин
│   └── writer.py            # Сохранение Excel
├── data/
│   └── output/
├── debug/
│   └── parser/              # Парсинг аккаунта IG
│   └── pre_parser/           
├── requirements.txt         # Зависимости
└── README.md
```

---

## 🙌 

