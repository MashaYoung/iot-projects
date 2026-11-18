"""
Система динамического освещения на ESP32 и протоколе MQTT.

Python-симуляция узла-подписчика. В оригинальной прошивке микроконтроллер:

    1) подключался к MQTT-брокеру (локальному Mosquitto или облачному);
    2) подписывался на топик команд lamp/cmd;
    3) по команде '1' включал светодиод (нагрузку), по '0' — выключал.

Здесь ту же роль «осветительного узла» выполняет Python-скрипт, который
использует библиотеку paho-mqtt. Подключение настраивается через переменные
окружения, поэтому один и тот же код работает и с локальным брокером
Mosquitto (в Docker), и с облачным брокером — без зашитых в исходник паролей.
"""

import os
import sys

try:
    import paho.mqtt.client as mqtt
except ImportError:
    sys.exit(
        "Библиотека paho-mqtt не установлена. Выполните: "
        "pip install paho-mqtt python-dotenv"
    )

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Настройки из переменных окружения (секреты не хардкодим!)
MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "lamp/cmd")
MQTT_USER = os.getenv("MQTT_USER", "")
PASS = os.getenv("MQTT_PASS", "")


def on_connect(client, userdata, flags, rc):
    """Вызывается при подключении к брокеру."""
    if rc == 0:
        print(f"Подключено к брокеру {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
    else:
        print("Ошибка подключения", rc)


def on_message(client, userdata, msg):
    """
    Вызывается при получении команды. msg.payload — байты.

    В прошивке: '1' -> свет ВКЛ, '0' -> свет ВЫКЛ.
    """
    command = msg.payload.decode().strip()
    print(f"Пришла команда: {command}")

    if command == "1":
        print("Статус: СВЕТ ВКЛЮЧЕН")
    elif command == "0":
        print("Статус: СВЕТ ВЫКЛЮЧЕН")
    else:
        print("Неизвестная команда:", command)


def main():
    """Точка входа: подключаемся к брокеру и слушаем команды."""
    print("=== Система динамического освещения (MQTT node) ===")
    print(f"Топик команд: {MQTT_TOPIC}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    if MQTT_USER:
        client.username_pw_set(MQTT_USER, PASS)

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    print(f"Подключение к брокеру {MQTT_HOST}:{MQTT_PORT}...")
    print("Ожидание команд. Для выхода — Ctrl+C.")

    client.loop_forever()


if __name__ == "__main__":
    main()