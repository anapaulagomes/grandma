# Grandma

She will let you know when there is coffee. 👵🏼 ☕️

***

## Running

Make sure your file `.env` is updated with all the environment variable needed:

```
SLACK_BOT_TOKEN='xxx'
DEFAULT_CHANNEL='random'
AMPY_PORT=/dev/tty.SLAB_USBtoUART
```

### Server

```
FLASK_APP=grandma/server.py flask run --host=0.0.0.0
```

The param `--host=0.0.0.0` is important to keep visible externally.

### ESP 8266 + MicroPython

Check the name of your board on `/dev/` directory (for MacOS users) e.g. `/dev/tty.SLAB_USBtoUART`.

Secrets: `access.py`

```
API_URL = '192.168.0.24'  # be careful, it may change
API_PORT = 5000
NETWORK_NAME = 'yyyy'
NETWORK_PASSWORD = 'xxxxxx'
```

```
ampy run -n grandma/board.py
```

**TODO**

**Bot**

- [ ] check private messages
- [ ] Refactor (grandma, brain, coffee)
- [ ] check db persistancy
- [ ] maybe using an orm? http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#quickstart

Nice to have:

[ ] IA lib instead of hard coded messages
