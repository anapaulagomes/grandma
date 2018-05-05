import network
import socket
import machine
import time


# MicroPython module

# TODO esconder variaveis IP, PORT, SSID e PASSWORD
# TODO configuravel PIN

def connect():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('cantinho', 'c@ntinhosemf10')
    # print(sta_if.active())
    # print(sta_if.isconnected())
    print(sta_if.ifconfig())
    return sta_if


def http_get():
    localhost = '192.168.0.25'
    api_host = '192.168.0.24'
    addr = socket.getaddrinfo(api_host, 5000)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % localhost, 'utf8'))
    data = s.recv(100)
    s.close()
    return data


def blink_led(number_of_blinks=1):
    led = machine.Pin(15, machine.Pin.OUT)

    for i in range(number_of_blinks):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)


if connect():
    try:
        response = http_get()
        if '200' in response:
            blink_led()
        else:
            blink_led(number_of_blinks=3)
    except:
        blink_led(number_of_blinks=5)

###
import machine
import time
button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
pin = machine.Pin(15, machine.Pin.OUT)

while True:
    first = button.value()
    time.sleep(0.01)
    second = button.value()

    if first and not second:
        pin.on()
        http_get()
        print('Button pressed!')
    elif not first and second:
        pin.off()
        print('Button released!')
