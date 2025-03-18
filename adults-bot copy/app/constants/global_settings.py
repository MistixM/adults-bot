# --
# Change text, system and bot settings in this file
# Feel free to use HTML tags like: <b>, <i>, <code>, etc.
# Tokens and credentials must be changed in the config.ini file
# --

# VARIABLES
PHOTO_HASHTAG_TRIGGER = '#зустріч'
MIN_VOTES = 12
POLL_CLOSE_TIME = 24 # in hours
REVOTE_POLL_CLOSE_TIME = 48 # in hours
FOLDER_ID = "folder_id" # stable ID
OWNER_ID = 12345678

# TEXTS
# /start
GROUP_START_MESSAGE = """👋 Ласкаво просимо в Adults

Колись я бачив, як українці за кордоном намагалися збиратися – і щоразу ці зустрічі розвалювалися. Ковід, війна, страх соціалізації… Люди приходили один-два рази – і зникали.

Я вирішив зробити спільноту, яка не розвалиться. Так почався Adults Porto, який за два роки і понад 100 зустрічей став місцем, де люди не просто приходять, а залишаються.

Тепер Adults є в різних містах – і ти став(-ла) частиною цього руху.

🗓 Як це працює?

Ми збираємось щотижня. День та час зустрічей визначаємо голосуванням. Локації обираємо з пулу місць, куди додаються перевірені варіанти.

Зустрічі – це привід побачити своїх, познайомитись, поговорити і провести час так, як хочеться саме тобі. Можеш прийти на годину або засидітися допізна – ніяких зобов’язань.

Хочеш впливати на зустрічі? Користуйся командами:

📍 /add_place {назва місця} – почати голосування за нове місце в пулі
📍 /remove_place {назва місця} – почати голосування за виключення місця
📅 /revote_day – переголосувати день зустрічей
⏰ /revote_time – переголосувати час зустрічей

📸 Фотографії з зустрічей

У нас є традиція – загальні фото на кожній зустрічі. Бот нагадає про це. Використовуй #зустріч, щоб їх було легко знайти.

🤔 Що робити, якщо прийшов(-ла) перший(-а)?

Вітаю, пунктуальність – це сила!
- Займи класне місце, скинь фотку/локацію в чат
- Подивись меню, зроби замовлення
- Налаштуйся на спілкування

Ще жодного разу не було, щоб ніхто не прийшов. І ти це тільки що підтвердив(-ла).

⚠️ Чат без спаму та трешу
🚫 Заборонені репости без коментаря
🚫 Широко відома інфа (ми всі читаємо новини)
🚫 18+ контент та реклама

Ми тут не про театр і не про рекламу. Ми тут про людей.

Ти тут – отже, це твоє місце
Ласкаво просимо в Adults 🚀

Створив усе це @alex4arkin – якщо є питання або ідеї, пиши
"""

DM_START_MESSAGE = "Hello! Please add me to the group to get started!"
START_VIDEO_PATH = 'app/assets/adults-porto.png'

# /add_place
ADD_PLACE_ERR = 'Будь ласка проголосуйте за місце та час.'
ADD_PLACE_DIGIT_ERR = "Місце не повинно бути числом"
ADD_PLACE_ARG_ERR = "Будь ласка, вкажи місце для зустрічі. Приклад /add_place Cafe XYZ"
ADD_PLACE_EXIST_ERR = 'Таке місце вже є в списку зустрічей.'

ADD_PLACE_CHANGE = "було додано до списку зустрічей!" # {місце} було додано...
ADD_PLACE_DECLINE = "не буде додано до списку зустрічей!" # {місце} не буде додано...

ADD_PLACE_QUESTION = "додамо до списку зустрічей?" 

# /remove_place
RM_PLACE_ERR = 'Будь ласка проголосуйте за місце та час.'
RM_PLACE_DIGIT_ERR = "Місце не повинно бути числом."
RM_PLACE_ARG_ERR = "Будь ласка вкажи місце для видалення. Приклад /remove_place Cafe XYZ"
RM_PLACE_EXIST_ERR = "Такого місця немає в списку зустрічей. Будь ласка виберіть інше або додайте використовуючи /add_place [назва місця]"

REMOVE_PLACE_CHANGE = "було видалено зі списку зустрічей!" 
REMOVE_PLACE_DECLINE = "не буде видалено зі списку зустрічей!"

RM_PLACE_QUESTION = "видалимо зі списку зустрічей?"

# /revote_day
RV_DAY_ERR = 'Будь ласка проголосуйте за місце та час.'
RV_DAY_QUESTION = "На який день тижня змінимо зустрічі?"
RV_DAY_OPTIONS = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']

REVOTE_DAY_CHANGE = "День для зустріч було змінено на"
REVOTE_TIME_CHANGE = "Час для зустріч було змінено на"

# /revote_time
RV_TIME_ERR = 'Будь ласка проголосуйте за місце та час.'
RV_TIME_QUESTION = 'Який новий час виберем?'
RV_TIME_OPTIONS = ['16', '17', '18', '19', '20', '21', '22', '23']

# POLLS (initial start)
POLL_DAY_QUESTION = "В який день тижня?"
POLL_DAY_OPTIONS = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']
POLL_TIME_QUESTION = "Який час для зустрічі?"
POLL_TIME_OPTIONS = ['16', '17', '18', '19', '20', '21', '22', '23'] # keep time in this format (do not use e.g '18:30')

# MEETING CYCLE
# It means that 5 days before meeting it will send the poll
# For other variables – same logic.
WAITING_POLL_STATUS_DELAY = 5 # in days. 
POLL_ACTIVE_STATUS_DELAY = 3 # in days.
NOTIFYING_USERS_STATUS_DELAY = 1 # in days.
MEETING_DAY_STATUS_DELAY = 2 # in hours. Remind to make a photo

# Adjust place limit to vote (be careful when changing this. 
# Always check logs and ensure that the bot didn't catch 
# IndexError or index out of range)
PLACES_LIMIT = 6 

PLACE_REMIND_MESSAGE = """📍 Голосування за місце відкрите!
Де збираємось цього разу – вирішуєш ти. Голосуй, поки є час"""
PHOTO_REMIND_MESSAGE = """📸 Фото або не було! 
Не забудьте скинути загальне фото з зустрічі  з хештегом – це вже традиція"""

# PROCESS_POLL
TIE_MESSAGE = "Нічия. Будь ласка, проведіть переголосування."