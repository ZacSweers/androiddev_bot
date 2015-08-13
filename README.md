# androiddev_bot

Any command must start with `postbot`

Actions are as follows

* `rm` <postid>
  * Spam
    * -s 
    * --spam
  * Message
    * -m '<My message>'
    * --message='<My message>'
  * Canned responses
    * -c responseName
    * --canned=responseName
* `flair` <postid> '<My message>'
* `approve` <postid>
* `ban` <userid>
  * Temp
    * -t 
    * --temp
  * Message
    * -m '<My message>'
    * --message='<My message>'
  * Note (for mods)
    * -n '<My note>'
    * --note='<My note>'
* `running`
  * Bot will respond if it's running
* `help`
  * Bot will respond with available commands