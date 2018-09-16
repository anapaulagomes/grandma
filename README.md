# Grandma

She will let you know when the coffee is done. 👵🏼 ☕️

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
API_URL = '192.168.0.24'  # be careful it may change
API_PORT = 5000
NETWORK_NAME = 'yyyy'
NETWORK_PASSWORD = 'xxxxxx'
```

To keep it running as soon as it is connected to an energy source run `make deploy-to-board`. This command will copy the needed files to the board.

If you'd like running it from your machine:

```
ampy run -n grandma/board.py
```

## Troubleshooting

- SlackLoginError

**API**

```
Traceback (most recent call last):
  File "/Users/ana.gomes/.pyenv/versions/3.6.4/lib/python3.6/site-packages/slackclient/client.py", line 52, in rtm_connect
    self.server.rtm_connect(use_rtm_start=with_team_state, **kwargs)
  File "/Users/ana.gomes/.pyenv/versions/3.6.4/lib/python3.6/site-packages/slackclient/server.py", line 151, in rtm_connect
    raise SlackLoginError(reply=reply)
slackclient.server.SlackLoginError
```

You must set `SLACK_BOT_TOKEN` as environment variable.

**Board**

- Missing option "--port"

```
ampy run -n grandma/board.py
Usage: ampy [OPTIONS] COMMAND [ARGS]...

Error: Missing option "--port" / "-p".
```

You must set `AMPY_PORT` as environment variable like `AMPY_PORT=/dev/tty.SLAB_USBtoUART`. Or adding it as an argument:

```
ampy run -n grandma/board.py -p /dev/tty.SLAB_USBtoUART
```

-n / --no-output

- I pressed the button, the light is on and nothing happens...

Houston, we have a problem. Check the variable `API_URL` on `secrets.py`. Either you don't have it or the IP is wrong.

If the problem persists could be a MicroPython [issue that happens when reopening WiFi connection](https://github.com/micropython/micropython-esp32/issues/167). You may reset and check it again.
