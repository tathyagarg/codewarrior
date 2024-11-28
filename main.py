import os
import dotenv
import discord
import requests
import pandas as pd
import random

dotenv.load_dotenv()

TOKEN = os.getenv('TOKEN')
SIGMA = os.getenv('SIGMA')
CHALLENGE_ENDPOINT = 'https://www.codewars.com/api/v1/code-challenges/{challenge}'
SIGMA_USER_CHALLENGES_ENDPOINT = 'https://www.codewars.com/api/v1/users/{user}/code-challenges/completed?page={page}'
SIGMA_USER_COUNT_ENDPOINT = 'https://www.codewars.com/api/v1/users/{user}'
WHOIS_ENDPOINT = 'https://www.codewars.com/api/v1/users/{user}'

_lim = os.getenv('LIMIT')
if _lim:
    LIMIT = int(_lim)
else:
    LIMIT = -1 

bot = discord.Bot()

QUESTIONS = [] 
CACHE = {}

COLORS = {
    'white': 0xe6e6e6,
    'yellow': 0xecb613,
    'blue': 0x1f87e7,
    'purple': 0x866cc7,
    'black': 0x666666,
    'red': 0x993229
}
ERR = 0xcc0000 

LANGUAGES = {
    'c': '<:c_:1311363854265221160>',
    'clojure': '<:clojure:1311363859172560956>',
    'coffeescript': '<:coffeescript:1311363862368354354>',
    'cpp': '<:cpp:1311363864830410752>',
    'crystal': '<:crystal:1311363867246460958>',
    'csharp': '<:csharp:1311363870170021980>',
    'dart': '<:dart:1311363873827197021>',
    'elixir': '<:elixir:1311363877501403167>',
    'fsharp': '<:fsharp:1311363880219574363>',
    'go': '<:go:1311363883486679121>',
    'groovy': '<:groovy:1311363891443269662>',
    'haskell': '<:haskell:1311363894933192844>',
    'java': '<:java:1311363898808598620>',
    'javascript': '<:javascript:1311363901254013049>',
    'kotlin': '<:kotlin:1311363906714865664>',
    'lua': '<:lua:1311363911898890260>',
    'nasm': '<:nasm:1311363916454170636>',
    'php': '<:php:1311363921373958296>',
    'python': '<:python:1311363926432153681>',
    'racket': '<:racket:1311363930890965043>',
    'ruby': '<:ruby:1311364101561122869>',
    'rust': '<:rust:1311363943872200775>',
    'scala': '<:scala:1311363946208428064>',
    'shell': '<:bash:1311363846077939823>',
    'sql': '<:sql:1311363951639924769>',
    'swift': '<:swift:1311363954135535727>',
    'typescript': '<:typescript:1311363958782955570>',
}

def make_question_embed(data, desc):
    embed = discord.Embed(title=data['name'], description=desc, url=data['url'], color=COLORS.get(data['rank']['color'], 0xffffff))
    embed.add_field(name='Ranking', value=data['rank']['name'])

    languages = ''
    for lang in data['languages']:
        languages += LANGUAGES.get(lang, lang.capitalize()) + ' '

    embed.add_field(name='Languages', value=languages)
    return embed

@bot.event
async def on_ready():
    global QUESTIONS

    print(f'{bot.user} is logged in and ready to go!')
    print('Fetching sigma\'s challenges.')

    solved_questions = requests.get(SIGMA_USER_COUNT_ENDPOINT.format(user=SIGMA))
    count: int = solved_questions.json()['codeChallenges']['totalCompleted']
    
    lim = LIMIT if LIMIT > 0 else 10_000  # There's no way anybody is solving 2_000_000 questions
    for i in range(min(count // 200, lim)):
        print(f"Fetching page {i}")
        res = requests.get(SIGMA_USER_CHALLENGES_ENDPOINT.format(user=SIGMA, page=i+1))
        df = pd.DataFrame(res.json()['data'])['slug']

        QUESTIONS.extend(df)

@bot.command(description="Sends the bot's latency")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is {round(bot.latency * 1000)}ms")

@bot.command(description="Fetch a random Code Wars question")
async def question(ctx):
    await ctx.defer()
    
    while True:
        slug = random.choice(QUESTIONS)
        if slug in CACHE: continue

        data = requests.get(CHALLENGE_ENDPOINT.format(challenge=slug)).json()


        if data['rank']['name']:
            CACHE[slug] = data['rank']['name']
            break
    
    desc = data['description']
    if len(desc) > 4096:
        desc = desc[:4093] + '...'

    await ctx.respond(embed=make_question_embed(data, desc))

@bot.command(description="Fetch a random Code Wars question of a specified kyu ranking")
async def ranked_question(ctx, kyu: int):
    if kyu < 1 or kyu > 8:
        embed = discord.Embed(title="Invalid kyu", description="`kyu` in Code Wars can only range from `1` (hardest) to `8` (easiest). Please pick a kyu ranking within that range.", color=ERR)

        await ctx.respond(embed=embed)
        return

    await ctx.defer()

    while True:
        slug = random.choice(QUESTIONS)
        if slug in CACHE:
            if CACHE[slug] != f'{kyu} kyu': continue

        data = requests.get(CHALLENGE_ENDPOINT.format(challenge=slug)).json()

        if data['rank']['name']: CACHE[slug] = data['rank']['name']

        if data['rank']['name'] == f'{kyu} kyu': break

    desc = data['description']
    if len(desc) > 4096:
        desc = desc[:4093] + '...'

    await ctx.respond(embed=make_question_embed(data, desc))

@bot.command(description='Fetch data about a user')
async def whois(ctx, username: str):
    await ctx.defer()

    resp = requests.get(WHOIS_ENDPOINT.format(user=username))
    if resp.status_code == 404:
        embed = discord.Embed(title='Not a user', description=f'Code Wars tells us that there\'s no user by the name of {username}. Sure you got that right?', color=ERR)
        await ctx.respond(embed=embed)
        return
    
    data = resp.json()

    embed = discord.Embed(title=username, color=COLORS.get(data['ranks']['overall']['color']), url=f'https://www.codewars.com/users/{username}')
    embed.add_field(name='Name', value=data['name'], inline=False)
    embed.add_field(name='Honor', value=data['honor'], inline=False)
    embed.add_field(name='Leaderboard Position', value=data['leaderboardPosition'], inline=False)
    embed.add_field(name='Ranking', value=data['ranks']['overall']['name'], inline=False)

    langs = ''
    for lang, lang_data in data['ranks']['languages'].items():
        text = f'{LANGUAGES.get(lang, lang.capitalize())} - {lang_data["name"]} ({lang_data["score"]} points)\n'
        if len(langs + text) > 1024:
            break

        langs += text

    embed.add_field(name='Languages', value=langs, inline=False)
    embed.add_field(name='Challenges Completed', value=data['codeChallenges']['totalCompleted'], inline=False)

    await ctx.respond(embed=embed)

bot.run(TOKEN)

