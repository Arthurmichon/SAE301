import paho.mqtt.client as mqtt
from prises.models import Prise


BROKER = "127.0.0.1"
PORT = 1883
USERNAME = "akaza"
PASSWORD = "akaza"
TOPIC_LED1_STATE = "esp1/led/state"
TOPIC_LED2_STATE = "esp2/led/state"
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[MQTT] Connecté au broker (code {rc})")
    client.subscribe(TOPIC_LED1_STATE)
    client.subscribe(TOPIC_LED2_STATE)

def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip().lower()
    print(f"[MQTT] Reçu sur {msg.topic} : {payload}")

    if payload not in ["on", "off"]:
        print("Payload invalide :", payload)
        return

    # Identifier la LED concernée
    if msg.topic == TOPIC_LED1_STATE:
        prise = Prise.objects.filter(id=1).first()
        led=1
    elif msg.topic == TOPIC_LED2_STATE:
        prise = Prise.objects.filter(id=2).first()
        led=2

    if prise:
        prise.etat = (payload == "on")
        prise.save()
        print(f"[DB] LED {prise.id} mise à jour à : {prise.etat}")
    else:
        print(f"[DB] Pas de prises correspondante pour le topic {msg.topic}")

def start_listener():
    client = mqtt.Client(client_id="ESP8266-clta1-Listener")
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Serv_web.settings")
    django.setup()

    start_listener()

