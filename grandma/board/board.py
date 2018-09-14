import network
import socket
import machine
import time
import access


class CoffeeBoard(object):
    def __init__(self):
        self.api_host = access.API_URL
        self.api_port = access.API_PORT

    def run(self):
        done_button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
        over_button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
        led = machine.Pin(15, machine.Pin.OUT)

        self._connect()

        while True:
            done_pressed = not done_button.value()
            if done_pressed:
                led.on()
                self._has_coffee()
                led.off()
            over_pressed = not over_button.value()
            if over_pressed:
                led.on()
                self._coffee_is_over()
                led.off()

    def _connect(self):
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(access.NETWORK_NAME, access.NETWORK_PASSWORD)
        self.ip = sta_if.ifconfig()[0]

    def _has_coffee(self):
        self._get('coffee/done')

    def _coffee_is_over(self):
        self._get('coffee/over')

    def _get(self, endpoint):
        addr = socket.getaddrinfo(self.api_host, self.api_port)[0][-1]
        s = socket.socket()
        s.connect(addr)
        request = 'GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (endpoint, self.ip)
        print(request)
        s.send(bytes(request, 'utf8'))
        data = s.recv(100)
        s.close()
        print(data)
        return data
