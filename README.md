A web interface for running Rust code built using [playpen][playpen]. It is
hosted at <https://play.rust-lang.org/>.

The interface can also be accessed in most Rust-related channels on
`irc.mozilla.org`.

To use Playbot in a public channel, address your message to it. Playbot
responds to both `playbot` and `rusti`: 

    <you> playbot: println!("Hello, World");
    -playbot:#rust-offtopic- Hello, World
    -playbot:#rust-offtopic- ()

You can also private message Playbot your code to have it evaluated. In a
private message, don't preface the code with playbot's nickname: 

    /msg playbot println!("Hello, World");

# Running your own Rust-Playpen

## System Requirements

Rust-Playpen currently needs to be run on an Arch Linux system that meets
[playpen's requirements][playpen]. 

The bot requires python 3, which is the default on Arch.

## IRC Bot Setup 

`playbot` on Mozilla IRC is run from a Rust-Playpen instance where Python
dependencies are installed system-wide. Get the latest versions of `pyyaml`,
`requests`, and `irc` from Pip. 

#### Create `shorten_key.py`

The bot uses [bitly](https://bitly.com) as a URL shortener. Get an OAuth access token, and put it
into a file called `shorten_key.py`, in the same directory as `bot.py`.
`shorten_key.py` just needs one line, of the form:

    key = "123abc123"

#### Create `irc.yaml`

You'll also need to create the file `irc.yaml` in the same directory as
`bot.py`. The IRC nick that the bot will use is hard-coded [in
bot.py][nickname]. This configuration assumes that the bot's nick is
registered, and includes the nick's password. The `irc.yaml` file will look
something like this:

```
   - server: irc.example.org
      port: 6667
      channels:
        - "#bots"
        - "#secret-clubhouse"
      keys: [null, "hunter2"]
      password: abc123abc
``` 

Note that the channel key is `null` for public channels. 

#### Registering and starting services

The working playpen has the IRC and Web services set up to automatically start at boot:

`/etc/systemd/system/rust-playpen-irc.service`

```
[Unit]
Description=Rust code evaluation sandbox (irc bots)
After=network.target

[Service]
ExecStart=/root/rust-playpen/bot.py

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/rust-playpen-web.service`

```
[Unit]
Description=Rust code evaluation sandbox (web frontend)
After=network.target 

[Service]
ExecStart=/root/rust-playpen/web.py

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/rust-playpen-update.service`

```
[Unit]
Description=Playpen sandbox root updater

[Service]
Type=oneshot
ExecStart=/root/rust-playpen/init.sh
Environment=HOME=/root
```

`/etc/systemd/system/rust-playpen-update.timer`

```
[Unit]
Description=Playpen sandbox root update scheduler

[Timer]
OnBootSec=10min
OnCalendar=daily
Persistent=true
Unit=rust-playpen-update.service

[Install]
WantedBy=multi-user.target
```

If the services fail to start, kick them:

```
$ systemctl restart rust-playpen-irc.service
$ systemctl restart rust-playpen-web.service
```

[playpen]: https://github.com/thestinger/playpen
[nickname]: https://github.com/rust-lang/rust-playpen/blob/master/bot.py#L140

