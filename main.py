import os
from discord.ext import commands
from helpers import dmcode, randomcode, test
from tinydb import TinyDB, Query
from web import dummy
import time
import discord
import json

bot = commands.Bot(command_prefix='!')
db = TinyDB('database.json').table("_default", cache_size=30)
# Syntax: {'id':user.id,'username':reddit username, 'timeofverify': time said person verified,'code': code used in verification,'verified': bool on whether verified,'roles': upv role ids in list ['10k id','25k id'] etc,'highest': highest submission, [id,score],"msgid": log msg id}

f2 = open('config.json', 'r')
settings = json.load(f2)
f2.close()



@bot.event
async def on_ready():
    await test()
    print("Started")


@bot.command(name='verify', help='Server verification')
async def verify(ctx, code: str):
    search = db.search(Query().id == ctx.author.id)
    if len(search) == 0:
        return await ctx.reply(
            "You have no running verification! Use `!start <username>` to start verifying"
        )
    else:
        if not search[0]['verified'] and code != search[0]['code']:
            await ctx.reply(
                "Invalid code! Resetting verification. Use `!start <username>` to restart verification."
            )
            db.remove(Query().id == ctx.author.id)
        if search[0]['verified']:
            return await ctx.reply("You have already verified.")
        if code == search[0]['code']:
            try:
                await ctx.author.edit(nick=search[0]['username'])
            except:
                await ctx.reply("I am missing permissions to change your nickname")
            try:
                if len(search[0]['roles']) != 0:
                    for n,i in enumerate(search[0]['roles']):
                        if n!=0:
                            role = ctx.guild.get_role(i)
                            await ctx.author.add_roles(role)
            except:
                await ctx.reply("I am missing permissions to give you roles")
            await ctx.reply("You have successfuly verified.")
            log = ctx.guild.get_channel(settings['verification_channel'])
            try:
                m = await log.fetch_message(search[0]['msgid'])
                roles = ""
                if len(search[0]['roles']) != 0:
                    roles = f"[Link to post](https://www.reddit.com/{search[0]['roles'][0]})\n"
                    for n,i in enumerate(search[0]['roles']):
                        if n != 0:
                            roles = roles + "\n" + "<@&" + str(i) + ">"
                else:
                    roles= "No roles."
                await m.edit(embed=discord.Embed(
                    title="Verified.", color=0x00FF00
                ).add_field(
                    name="Discord account: ",
                    value=f"{ctx.author.mention}\n**ID:** {ctx.author.id}"
                ).add_field(
                    name="Reddit account: ",
                    value=
                    f"[u/{search[0]['username']}](https://www.reddit.com/user/{search[0]['username']}/)"
                ).add_field(name="Roles: ", value=roles))
                db.update({'verified':True},Query().id==ctx.author.id)
            except:
                pass
    pass


@bot.command(name='start', help='Server verification start')
async def start(ctx, username: str = None):
    if not username:
        return await ctx.reply("Enter a username. Format: `!start <username>`")
    search = db.search(Query().id == ctx.author.id)
    if len(search) == 0:
        code = randomcode()
        check = await dmcode(username, code)
        if not check:
            return await ctx.reply("Invalid reddit username provided!")
        else:
            await ctx.reply(
                "A verification code has been DM'd to you. Use `!verify <code>` to verify your account."
            )
            await ctx.send(code)

            log = ctx.guild.get_channel(settings['verification_channel'])
            roles = ""
            if len(check[1]) != 0:
                roles = f"[Link to post](https://www.reddit.com/{check[1][0]})\n"
                for n,i in enumerate(check[1]):
                    if n != 0:
                        roles = roles + "\n" + "<@&" + str(i) + ">"
            else:
                roles= "No roles."
            m = await log.send(embed=discord.Embed(
                title="New verification requested", color=0xFFFF00
            ).add_field(
                name="Discord account: ",
                value=f"{ctx.author.mention}\n**ID:** {ctx.author.id}"
            ).add_field(
                name="Reddit account: ",
                value=f"[u/{check[0]}](https://www.reddit.com/user/{check[0]}/)"
            ).add_field(name="Roles: ", value=roles))
            db.insert({
                'id': ctx.author.id,
                'username': check[0],
                'timeofverify': time.time(),
                'code': code,
                'verified': False,
                'roles': check[1],
                'highest': check[2],
                "msgid": m.id
            })
    else:
        if not search[0]['verified']:
            await ctx.reply("You already have a running verification!")
        else:
            await ctx.reply("You have already verified!")


@bot.command(name='delete', help='Delte verfication')
@commands.has_permissions(manage_messages=True)
async def delete(ctx, member: discord.Member):
    if not member:
        return await ctx.reply("Format: `!delete <member>`")
    search=db.search(Query().id==member.id)
    if len(search)==0:
        return await ctx.reply("No ongoing verificaton.")    
    else:
        logs = ctx.guild.get_channel(settings['verification_channel'])
        roles = ""
        if len(search[0]['roles']) != 0:
            roles = f"[Link to post](https://www.reddit.com/{search[0]['roles'][0]})\n"
            for n,i in enumerate(search[0]['roles']):
                if n != 0:
                    roles = roles + "\n" + "<@&" + str(i) + ">"
            
        else:
            roles= "No roles."
        await logs.send(embed=discord.Embed(
            title="Verificaton deleted", color=0xFF0000
        ).add_field(
            name="Discord account: ",
            value=f"{member.mention}\n**ID:** {member.id}"
        ).add_field(
            name="Reddit account: ",
            value=
            f"[u/{search[0]['username']}](https://www.reddit.com/user/{search[0]['username']}/)"
        ).add_field(name="Roles: ", value=roles)
        .add_field(name="Deleted by: ",value=f"{ctx.author.mention}\n**ID:** {ctx.author.id}"))
        db.remove(Query().id==member.id)
        await ctx.reply("Deleted.")

@bot.command(name='reverify', help='reverify with new username')
async def reverify(ctx, username: str=None):
    if not username:
        return await ctx.reply("Format: `!reverify <username>`")
    search=db.search(Query().id==ctx.author.id)
    if len(search)==0:
        return await ctx.reply("No ongoing verificaton.")
    if search[0]['verified']==False:
        return await ctx.reply("No ongoing verificaton.")
    else:
        logs = ctx.guild.get_channel(settings['verification_channel'])
        m = await logs.fetch_message(search[0]['msgid'])
        roles = ""
        if len(search[0]['roles']) != 0:
            roles = f"[Link to post](https://www.reddit.com/{search[0]['roles'][0]})\n"
            for n,i in enumerate(search[0]['roles']):
                if n != 0:
                    roles = roles + "\n" + "<@&" + str(i) + ">"
        else:
            roles= "No roles."
        await m.edit(embed=discord.Embed(
            title="Reverification requested", color=0xFF0000
        ).add_field(
            name="Discord account: ",
            value=f"{ctx.author.mention}\n**ID:** {ctx.author.id}"
        ).add_field(
            name="Reddit account: ",
            value=
            f"[u/{search[0]['username']}](https://www.reddit.com/user/{search[0]['username']}/)"
        ).add_field(name="Roles: ", value=roles))
        db.remove(Query().id==ctx.author.id)
        await start(ctx,username)



@bot.command()
@commands.has_permissions(manage_messages=True)
async def info(ctx, member: discord.Member):
    if not member:
        return await ctx.reply("Format: `!delete <member>`")
    search=db.search(Query().id==member.id)
    if len(search)==0:
        return await ctx.reply("No ongoing verificaton.") 
    roles = ""
    if len(search[0]['roles']) != 0:
        roles = f"[Link to post](https://www.reddit.com/{search[0]['roles'][0]})\n"
        for n,i in enumerate(search[0]['roles']):
            if n != 0:
                roles = roles + "\n" + "<@&" + str(i) + ">"
    else:
        roles= "No roles."
    await ctx.send(embed=discord.Embed(
        title="Verificaton deleted", color=0x43A6C6
    ).add_field(
        name="Discord account: ",
        value=f"{member.mention}\n**ID:** {member.id}"
    ).add_field(
        name="Reddit account: ",
        value=
        f"[u/{search[0]['username']}](https://www.reddit.com/user/{search[0]['username']}/)"
    ).add_field(name="Roles: ", value=roles)
    .add_field(name="Requested by: ",value=f"{ctx.author.mention}\n**ID:** {ctx.author.id}"))
    db.remove(Query().id==member.id)


@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please input all required arguments.', delete_after=25)
    elif isinstance(error, commands.CommandNotFound):
        return 
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f'You are missing permissions to run this command. `{error}`')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Invalid user!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'You\'re on {str(error.cooldown.type).split(".")[-1]} cooldown for this command. Try again in {round(error.retry_after)} seconds.')
    else:
        print(error)

dummy()
bot.run(os.environ.get('token'))
