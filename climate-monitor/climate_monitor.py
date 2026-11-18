import os
import random
import time
import sys
import select
import datetime
import json

# Лимиты Минздрава
TEMP_MIN = 10.0
TEMP_MAX = 30.0
HUMIDITY_MAX = 70.0

# шаги суперцикла
BASE_STEP = 100   # 100 мс — базовый шаг
LOG_EVERY = 10    # журнал каждые 10 тиков
SAMPLE_EVERY = 5  # опрос датчика каждые 5 тиков
TIME_CYCLE = 20   # длина полного цикла суперцикла

# стартовые значения датчика
t = 22.0
h = 45.0

# сигнал тревоги — включена/выключена
alarm = False
# запомненное состояние светодиода (чтобы печатать только при смене)
led = None
count = 1

# Кнопка BOOT доступна только когда есть клавиатура (локальный запуск).
# В Docker-контейнере клавиатуры нет, поэтому кнопку отключаем через
# переменную окружения BUTTON_ENABLED (в compose/Dockerfile ставим "0").
BUTTON_ENABLED = os.getenv("BUTTON_ENABLED", "1") == "1"


def is_any_key_pressed():
    # проверка клавиши без блокировки цикла
    if sys.platform.startswith("win"):
        return _win_nonblocking_key()
    else:
        # на линуксе/маке ждём stdin с таймаутом 0
        if select.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.readline()
            return True
        return False


def _win_nonblocking_key():
    # для винды: kbhit() не блокирует
    try:
        import msvcrt
        return msvcrt.kbhit()
    except ImportError:
        return False


def print_alarm_message():
    # вывести, что именно нарушено
    print()
    print("!!! ВНИМАНИЕ: ОШИБКА !!!")
    if t < TEMP_MIN or t > TEMP_MAX:
        print(f"Критическая T: {t:.1f} C")
    if h > HUMIDITY_MAX:
        print(f"Критическая H: {h:.1f} proc")
    print("=" * 45)


def setup():
    # старт и напоминание о лимитах
    print('START!')
    print(f"=== Климат-монитор склада ===")
    print(f"Лимиты : T {TEMP_MIN:.1f}..{TEMP_MAX:.1f} C, "
          f"влажность <= {HUMIDITY_MAX} proc")


def read_sensor():
    # имитация датчика: данные «плавают», влажность тянем вверх,
    # чтобы доходить до аварии, а не болтаться у 45 всё время
    global t, h
    t = t + random.uniform(-1.0, 1.0)
    # Медленный рост влажности + небольшое блуждание: стабильно уводим
    # показание вверх, чтобы порог 70% рано или поздно был достигнут.
    h = h + random.uniform(-1.0, 3.0)


def check_limits():
    # если что-то вылезло за лимит — включаем тревогу
    global alarm
    if t < TEMP_MIN or t > TEMP_MAX or h > HUMIDITY_MAX:
        alarm = True
        print_alarm_message()


def update_leds():
    global led
    text = "Красный горит" if alarm else "Зеленый горит"
    # печатаем только когда состояние поменялось, а не каждый тик
    if text != led:
        print(f"[LED] {text}")
        led = text


def handle_button():
    # кнопка BOOT: показать текущее состояние
    if not BUTTON_ENABLED:
        return  # в докере кнопки нет
    if is_any_key_pressed():
        if alarm:
            print_alarm_message()
        else:
            print("BOOT PRESS: Климат в норме")


def superloop():
    # главный цикл: читаем датчик, проверяем, обновляем светодиод
    global count
    while True:
        handle_button()

        # Чтение датчика и проверка — раз в цикл на 5-м шаге.
        if count == SAMPLE_EVERY:
            read_sensor()
            check_limits()

        # Светодиод — на каждом тике, печатается при смене.
        update_leds()

        if alarm:
            break

        # Журнал в JSON — раз в цикл на 10-м шаге.
        if count == LOG_EVERY:
            data = {
                "temp": round(t, 1),
                "humidity": round(h, 1),
                "time": str(datetime.datetime.now())
            }
            print(json.dumps(data))

        count += 1
        if count > TIME_CYCLE:
            count = 1

        time.sleep(BASE_STEP / 1000.0)


if __name__ == "__main__":
    setup()
    superloop()