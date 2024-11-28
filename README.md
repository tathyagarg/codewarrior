# CodeWarrior
CodeWarrior is a discord bot to view CodeWars questions on discord.

## New feature!!
- More commands, including one to get a random question of specified ranking
- Command that displays a given user's information

## Upcoming features
- Option to store questions on disk, making the bot slower but taking up less RAM.

## Running the Bot
To run the bot:
- Clone this repository
- `cd` into the cloned repo
- Install the dependencies
- Rename .env.example to .env, and fill in real values. (Refer to the [setting up the .env file](#env) section of this file for details)
- Run the main.py file
```
git clone https://github.com/tathyagarg/codewarrior && cd codewarrior
python -m pip install -r requirements.txt
python main.py
```

<h2 id="env">Setting up the .env file</h2>
The `.env.example` file holds the variables you need to fill in.
1. `TOKEN` - Your discord bot's token. You can find this in the `Bot` page of your Discord Application on the [Discord Developer Portal](https://discord.com/developers/applications)
2. `SIGMA` - The username of a codewars user. To have a better experience with the bot, choose the username of a user who has completed a large number of katas. You can find such users on [Code Wars' kata leaderboard page](https://www.codewars.com/users/leaderboard/kata)
3. `LIMIT` - When you select a user with a large number of katas solved, the bot will take a while to initialize and store all the katas in memory. The `LIMIT` variable limits the number of katas fetched from all katas the user has solved to `200 * LIMIT` questions.


