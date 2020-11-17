from PIL import Image, ImageOps, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import discord

headerMessage = "Welcome!"
headerFont = "LEMONMILK-Bold.ttf"
userFont = "LEMONMILK-Medium.ttf"
memberFont = "LEMONMILK-Medium.ttf"

#Text outline
def outline(draw,x,y,text,font):
    draw.text((x-1, y), text, font=font, fill="black")
    draw.text((x+1, y), text, font=font, fill="black")
    draw.text((x, y-1), text, font=font, fill="black")
    draw.text((x, y+1), text, font=font, fill="black")

#Make welcome banner
def bannerMake(avUrl,userName, userCount):
    #get profile picture
    url = avUrl
    name = userName.upper()
    memberCount = str(userCount)
    print(name+ " : "+memberCount)
    response = requests.get(url)
    pfpImg = Image.open(BytesIO(response.content))
    pfpImg = pfpImg.resize((128, 128));
    outlinesize= (132,132)
    #crop circular pfp
    bigsize = (pfpImg.size[0] * 3, pfpImg.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    pfpmask = mask.resize(pfpImg.size, Image.ANTIALIAS)
    outlinemask = mask.resize(outlinesize, Image.ANTIALIAS)
    pfpImg.putalpha(pfpmask)

    pfpoutline = Image.new('RGBA',outlinesize,(255,255,255,255))
    pfpoutline.putalpha(outlinemask)
    #add pfp to background
    background = Image.open('banner.png')
    x,y = (38,36)
    background.paste(pfpoutline,(x-2,y-2),pfpoutline)
    background.paste(pfpImg,(x, y), pfpImg)
    #Text

    W, H = (background.width,background.height)
    draw = ImageDraw.Draw(background)

    #Header
    header = headerMessage
    font = ImageFont.truetype('Fonts/%s'%headerFont, 40)
    x, y = (170,34)
    outline(draw,x,y,header,font)
    draw.text((x, y), header, font=font, fill="white")

    #Discord Name
    font = ImageFont.truetype('Fonts/%s'%userFont, 22)
    x, y = (180,85)
    outline(draw,x,y,name,font)
    draw.text((x, y), name, font=font, fill="white")

    #Member count
    message = "You are the %sth Member"%memberCount
    font = ImageFont.truetype('Fonts/%s'%memberFont, 10)
    x, y = (180,120)
    outline(draw,x,y,message,font)
    draw.text((x, y), message, font=font, fill="white")

    #background.show()
    #banner output
    if os.path.exists('output.png'):
        os.remove('output.png')
        background.save('output.png')
    else:
        background.save('output.png')

#Discord Py
client = discord.Client()

#Config
"""
discordToken = ""
channel_id =
count_channel_id =
guild_id =
"""
#Heroku
discordToken = os.environ['TOKEN']
channel_id = os.environ['CHANNELID']
count_channel_id = os.environ['COUNTID']
guild_id = os.environ['GUILDID']

#Bot ready
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    guild = client.get_guild(int(guild_id))
    print("Serving Guild:")
    print(guild)
    members = guild.member_count
    print("Server Member Count: ")
    print(members)
    count_channel = client.get_channel(int(count_channel_id))
    print("Count Channel: ")
    print(count_channel)
    await count_channel.edit(name="Member Count: %d"%members)
    print("Count Channel Updated to: %d"%members)
#Member Join event
@client.event
async def on_member_join(member):
    await client.wait_until_ready()
    url = member.avatar_url
    name = member.name + "#" + member.discriminator
    guild = client.get_guild(int(guild_id))
    total_members = guild.member_count
    count_channel = client.get_channel(int(count_channel_id))
    print("User %s Joined"%name)
    try:
        bannerMake(url,name,total_members)
    except:
        print("Banner Make Error")
    channel = client.get_channel(int(channel_id))
    try:
        message = await channel.send(content="Welcome <@%d>, make sure to read <#734008100050305114>"%member.id,file=discord.File('output.png'), delete_after = 360)
    except:
        print("Banner Send Error")

    #Delete output file for welcome banner
    if os.path.exists('output.png'):
        os.remove('output.png')
    else:
        print('No output file')
    try:
        await count_channel.edit(name="Member Count: %d"%total_members)
        print("Updating Count Channel")
    except:
        print("Channel Update Error")
#Member Leave event
@client.event
async def on_member_remove(member):
    await client.wait_until_ready()
    name = member.name
    print("User %s Left"%name)
    guild = client.get_guild(int(guild_id))
    total_members = guild.member_count
    count_channel = client.get_channel(int(count_channel_id))
    try:
        await count_channel.edit(name="Member Count: %d"%total_members)
        print("Updating Count Channel")
    except:
        print("Channel Update Error")
#Run bot
client.run(discordToken)
