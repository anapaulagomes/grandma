# Grandma

She will let you know when there is coffee. 👵🏼 ☕️

***

## Available commands

``

## Running

### Server

`FLASK_APP=grandma/server.py flask run --host=0.0.0.0`

The param `--host=0.0.0.0` is important to keep visible externally.

### ESP 8266 + MicroPython

**TODO**

**Server**
[ ] endpoint coffee is over

**ESP8266**
[ ] tests loading the script into the pyboard
[ ] add tests
[ ] new button (coffee is over)
[ ] turn the light according with status code

**Security**
[ ] remove from history ssid + password
[ ] use environment variables

**Refactoring**

[ ] check db persistancy
[ ] maybe using an orm? http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#quickstart
[ ] brain

Nice to have:

[ ] IA lib instead of hard coded messages
