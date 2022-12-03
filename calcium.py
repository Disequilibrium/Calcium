import os
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.utils import get
from youtube_dl import YoutubeDL
import requests

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

def search(query):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
        try: requests.get(query)
        except: info = ydl.extract_info(f"ytsearch:{query}", download = False)['entries'][0]
        else: info = ydl.extract_info(query, download = False)
    return (info, info['formats'][0]['url'])

async def join(ctx, voice):
    channel = ctx.author.voice.channel
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

@bot.command(pass_context=True)
async def help(ctx):
    await ctx.send("```\n
                    !play <youtube-link> OR <youtube-search-term>\n
                    !stop\n
                    !disconnect\n
                    ```")

@bot.command(pass_context=True)
async def play(ctx, *, query):
    FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    video, source = search(query)
    voice = get(bot.voice_clients, guild = ctx.guild)

    await join(ctx, voice)
    #await ctx.send(f"Now playing {info['title']}")
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice.is_playing():
        voice.stop()
    voice.play(FFmpegPCMAudio(source, **FFMPEG_OPTS, executable="D:/ffmpeg/bin/ffmpeg.exe"), after=lambda e: print('done', e))

@bot.command(pass_context=True)
async def stop(ctx):
    voice = get(bot.voice_clients, guild = ctx.guild)
    voice.stop()

@bot.command(pass_context=True)
async def disconnect(ctx):
    voice = get(bot.voice_clients, guild = ctx.guild)
    await voice.disconnect(force = True)

@bot.event
async def on_ready():
    print('Bot initialized')
    await bot.change_presence(activity=discord.Game('!play !stop !disconnect'))

# -- MAIN --

if os.path.exists("src/token.txt"):
    f = open("src/token.txt", "r")
    TOKEN = f.readline()
else:
    f = open("src/token.txt", "w")
    TOKEN = input("Please input Bot API Token: ")
    TOKEN = TOKEN.strip()
    f.write(TOKEN)
    f.close()

try:
    bot.run(TOKEN)
except:
    print("[!] Authentication failed!")
    print("[!] Please check the correctness of your API Token in token.txt.")
    print("[!] Terminating program . . .")
