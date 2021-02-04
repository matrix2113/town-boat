# Town Boat
Town Boat is made for a gaming discord server to fit certain needs. The bot is public if you are creating any discord server in general.

# Selfhosting
Documentation for self-hosting will be coming out soon. We recommend `Python 3.8` running the bot through `pipenv`.

# Install Python

### Windows

You can install Python 3.8 [here](https://www.python.org/downloads/). Recommended is `3.8.7`. Make sure you install to PATH ![PATH](https://docs.python.org/3/_images/win_installer.png)

### Linux

You can either compile python yourself or use [pyenv](https://github.com/pyenv/pyenv).

```bash
1. Download the source using "wget"
2. Unzip the source using "tar"
3. run "./configure"
4. run "make"
5. run "make install"
```

After you are complete, open terminal and double check that Python and Pip is correctly installed. Note that if you are using Python/Linux, it would be `python3` as `python` would point to 2.7 (EOL October 2nd 2019)

```bash
> python --version
Python 3.8.7
> pip --version 
pip 20.2.3 from /Dir/ (python3.8)
```


### Pipenv

You will need pipenv as the bot requires environmental variables to start the bot.

```bash
> pip install pipenv
```
Unless you have sudo privledges, you will need to add `--user` at the end of the command above.

### Starting the Bot

```bash
cp .env.example .env
pipenv install
pipenv run townboat```

Fill in the environmental variables in the `.env` file and you should be able to start.
