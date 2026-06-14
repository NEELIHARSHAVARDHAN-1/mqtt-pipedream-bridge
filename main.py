import paho.mqtt.client as mqtt
import requests
import json
import ssl

MQTT_BROKER = "998559fd5537417097b01fa008399933.s1.eu.hivemq.cloud"  
MQTT_PORT = 8883                            
MQTT_USER = "dummy_dummy"            
MQTT_PASSWORD = "dummy_dummy+86D"        
PIPEDREAM_URL = "https://eoou7y49dewn8il.m.pipedream.net"

TOPIC_TELEMETRY = "factorysense/14C19F2DDFF4/telemetry"
TOPIC_STATUS = "factorysense/14C19F2DDFF4/status"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to HiveMQ Cloud over Port 8883 from Koyeb Container!")
        client.subscribe([(TOPIC_TELEMETRY, 1), (TOPIC_STATUS, 1)])
    else:
        print(f"Connection failed with code: {rc}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        incoming_json = json.loads(payload_str)
        outbound_data = {}

        if msg.topic == TOPIC_TELEMETRY:
            print(f"Relaying telemetry payload from {msg.topic}")
            outbound_data = incoming_json
            
        elif msg.topic == TOPIC_STATUS:
            print(f"Relaying status payload from {msg.topic}")
            outbound_data = {
                "device_id": "14C19F2DDFF4",
                "timestamp": "2026-06-14T10:13:22Z", 
                "wifi_status": incoming_json.get("wifi", "UNKNOWN"),
                "wifi_rssi_dbm": 0,
                "metrics": {
                    "temperature_c": 0.0,
                    "vibration_g": 0.0,
                    "current_a": 0.0
                }
            }

        if outbound_data:
            headers = {"Content-Type": "application/json"}
            response = requests.post(PIPEDREAM_URL, json=outbound_data, headers=headers)
            print(f"Forwarded to Pipedream. Status: {response.status_code}")
        
    except Exception as e:
        print(f"Error processing payload: {e}")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, transport="tcp")
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

client.on_connect = on_connect
client.on_message = on_message

print("Launching local multi-topic gateway bridge...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
