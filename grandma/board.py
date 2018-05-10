import network
import socket
import machine
import time
import access


def connect():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(access.NETWORK_NAME, access.NETWORK_PASSWORD)
    ip = sta_if.ifconfig()[0]
    return ip


def http_get(localhost):
    api_host = access.API_URL
    api_port = access.API_PORT

    endpoint = 'coffee/done'
    addr = socket.getaddrinfo(api_host, api_port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    request = 'GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (endpoint, localhost)
    s.send(bytes(request, 'utf8'))
    data = s.recv(100)
    s.close()
    return data


def run():
    button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
    led = machine.Pin(15, machine.Pin.OUT)

    ip = connect()

    while True:
        pressed = not button.value()
        if pressed:
            led.on()
            http_get(ip)
            led.off()

run()
