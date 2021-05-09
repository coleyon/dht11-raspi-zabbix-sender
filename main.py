from datetime import datetime
import os
from pyzabbix import ZabbixMetric, ZabbixSender
from time import sleep
from RPi import GPIO
import dht11
import logging
from logging import StreamHandler, DEBUG

SEND_FREQ = int(os.getenv("SEND_FREQ", default=60))
LOCAL_HOST = os.getenv("LOCAL_HOST", default="127.0.0.1")
ZABBIX_SERVER = os.getenv("ZABBIX_SERVER", default='172.0.0.1')
ZABBIX_PORT = int(os.getenv("ZABBIX_PORT", default=10051))
LOG_LEVEL = os.getenv("LOG_LEVEL", default="DEBUG")
GPIO_PIN_NUMBER = int(os.getenv("GPIO_PIN_NUMBER", 4))


# logger
logger = logging.getLogger("raspi_zabbix_sender")
fmtr = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
handler = StreamHandler()
handler.setFormatter(fmtr)
logger.addHandler(handler)
logger.setLevel(DEBUG)
zbx = ZabbixSender(zabbix_server=ZABBIX_SERVER, zabbix_port=ZABBIX_PORT)


def get_sensor_data(instance):
    '''
    '''
    result = instance.read()
    if result.is_valid():
        return {
            "temp": result.temperature,
            "humid": result.humidity
        }
    else:
        return None


if __name__ == '__main__':
    try:
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
        instance = dht11.DHT11(pin=GPIO_PIN_NUMBER)
        while True:
            result = None
            met = get_sensor_data(instance)
            if not met:
                continue
            try:
                result = zbx.send(metrics=[ZabbixMetric(LOCAL_HOST, k, v) for k, v in met.items()])
                logger.info("Sending metrics has successed. {res}".format(res=str(result)))
            except BaseException as e:
                logger.error("Sending metrics has failed, {m}".format(m=str(e)))
            sleep(SEND_FREQ)
    finally:
        GPIO.cleanup()
