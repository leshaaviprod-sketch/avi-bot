# 🦅 AVI Bot — Telegram Bot для движения творцов

Красивый Telegram бот с кнопками для подписки и доступа к закрытому каналу.

---

## 🚀 Деплой на Render (5 минут)

### Шаг 1: Создай репозиторий на GitHub

1. Открой [github.com/new](https://github.com/new)
2. **Repository name:** `avi-bot`
3. **Public** (или Private)
4. **НЕ** отмечай "Add a README file"
5. Нажми **Create repository**

### Шаг 2: Загрузи файлы в GitHub

**Способ 1 (через GitHub website — проще):**

1. На странице нового репозитория нажми **uploading an existing file**
2. Перетащи ВСЕ файлы из папки `deploy_avi_bot`:
   - `avi_bot.py`
   - `requirements.txt`
   - `.env.example`
   - `README.md` (этот файл)
3. Нажми **Commit changes**

**Способ 2 (через Git — для продвинутых):**

```bash
cd deploy_avi_bot
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/ТВОЙ_ЮЗЕРНЕЙМ/avi-bot.git
git push -u origin main
```

### Шаг 3: Разверни на Render

1. Открой [dashboard.render.com](https://dashboard.render.com)
2. Войди или зарегистрируйся
3. Нажми **New +** → **Web Service**
4. Нажми **Connect GitHub** (если ещё не)
5. Выбери репозиторий: `avi-bot`
6. Настрой:

| Поле | Значение |
|------|----------|
| **Name** | `avi-bot` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python avi_bot.py` |

7. Нажми **Advanced** → **Add Environment Variable**:

```
Key: BOT_TOKEN
Value: 8782289644:AAGXOYPiHeOVe_kyglbmAs3AbQ0AbIxcaI8
```

```
Key: PUBLIC_CHANNEL_ID
Value: @avi_channel
```

```
Key: PRIVATE_CHANNEL_ID
Value: @avi_private
```

```
Key: ADMIN_ID
Value: 000000000
```

8. Нажми **Create Web Service**

### Шаг 4: Готово!

Через 2-3 минуты бот запустится и будет работать 24/7! 🎉

---

## 📋 Что умеет бот

- 🦅 Главное меню с красивыми кнопками
- 💎 Подписки (месяц/год)
- 🔒 Закрытый канал (проверка доступа)
- 💬 Обратная связь
- 🎵 Музыка и контент

---

## 🔧 Локальный запуск (для тестирования)

```bash
pip install -r requirements.txt
python avi_bot.py
```

---

## 📞 Поддержка

Вопросы? Пиши @avi

---

🦅 **AVI — Создавай. Не будь зрителем.**
