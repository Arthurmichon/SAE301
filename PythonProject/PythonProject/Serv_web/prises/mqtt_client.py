import paho.mqtt.client as mqtt
import threading
import logging

logger = logging.getLogger(__name__)

BROKER = "127.0.0.1"
PORT = 1883
USERNAME = "akaza"
PASSWORD = "akaza"
TOPIC_LED1 = "esp1/led/control"
TOPIC_LED2 = "esp2/led/control"
TOPIC_ALL = "all/led/control"

TOPIC_TEMPERATURE = "esp1/temperature"

client = mqtt.Client(client_id="ESP8266-clta1-PythonClient")
client.username_pw_set(USERNAME,PASSWORD)



def envoyer_commande_toutes_les_leds(etat: bool):
    message = "ON" if etat else "OFF"
    try:
        logger.info(f"MQTT publish: {message} -> {TOPIC_ALL}")
        result = client.publish(TOPIC_ALL, message)
        result.wait_for_publish(timeout=1)
        return True
    except Exception as e:
        logger.exception("Erreur lors de l’envoi MQTT global")
        return False

def on_temperature_message(client, userdata, msg):
    try:
        value = float(msg.payload.decode())
        print(f"Température reçue : {value}°C")

        # Sauvegarde dans la base Django
        from .models import Temperature  # importer ici pour éviter les problèmes d'import circulaire
        temp, created = Temperature.objects.get_or_create(pk=1)
        temp.value = value
        temp.save()
    except Exception as e:
        print("Erreur en traitant le message MQTT :", e)


def envoyer_commande_prise(prise_id, etat: bool):
    message = "ON" if etat else "OFF"
    topic = TOPIC_LED1 if prise_id == 1 else TOPIC_LED2

    try:
        logger.info(f"MQTT publish: {message} -> {topic}")
        result = client.publish(topic, message)
        result.wait_for_publish(timeout=1)
        return True
    except Exception as e:
        logger.exception("Erreur lors de l’envoi MQTT")
        return False

def _mqtt_loop():
    logger.info("Démarrage du thread MQTT...")
    client.on_message = on_temperature_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC_TEMPERATURE)
    client.loop_forever()

# Lance le client MQTT au démarrage
thread = threading.Thread(target=_mqtt_loop, daemon=True)
thread.start()

