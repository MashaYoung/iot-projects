# Узел-подписчик для управления освещением по MQTT.
# Подключается к брокеру, подписывается на топик lamp/cmd,
# по команде "1" включает свет, по "0" — выключает.

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
    # при подключении подписываемся на топик
    if rc == 0:
        print(f"Подключено к брокеру {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
    else:
        print("Ошибка подключения", rc)


def on_message(client, userdata, msg):
    # пришла команда — понять, что от нас хотят
    command = msg.payload.decode().strip()
    print(f"Пришла команда: {command}")

    if command == "1":
        print("Статус: СВЕТ ВКЛЮЧЕН")
    elif command == "0":
        print("Статус: СВЕТ ВЫКЛЮЧЕН")
    else:
        print("Неизвестная команда:", command)


def main():
    # подключиться и слушать команды
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