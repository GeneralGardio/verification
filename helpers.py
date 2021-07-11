import asyncpraw as praw
import os
from asyncpraw.util.token_manager import FileTokenManager
import random
import time
import asyncio
import json

f2=open('config.json','r')
settings=json.load(f2)
f2.close()

f=open('ref.txt','w')
f.write(os.environ.get('reftoken'))
f.close()
reddit = praw.Reddit(client_id=os.environ.get('client_id'),
                     client_secret=os.environ.get('client_secret'),
                     user_agent="repl:www.reddit.com:v1 (by u/rules-rule8)"
                     ,
                     redirect_uri="https://localhost/",
                     token_manager=FileTokenManager("ref.txt")
)

open('ref.txt','w').close()

async def test():
    # print(reddit.auth.url(["*"], "...", "permanent"))
    # print(await reddit.auth.authorize(""))
    return

global lasttime
lasttime=0

async def dmcode(username,code):
    f=open('ref.txt','w')
    f.write(os.environ.get('reftoken'))
    f.close()
    try:
        user = await reddit.redditor(username,fetch=True)
        user.id
    except:
        open('ref.txt','w').close()
        return None
    if not user:
        open('ref.txt','w').close()
        return None
    global lasttime
    if lasttime+4 >= time.time():
        await asyncio.sleep(3)
    lasttime=time.time()
    # await user.message(subject="Verification code for MayMayAid",message=f"{str(code)}\n\n^^(Ignore this message if you did not request verification)")
    sublist=['r/dankmemes/','r/memes/','r/meme/','r/wholesomememes/']
    huv=[0,0]
    uvlist=[]
    if user.submissions:
        async for i in user.top():
            if not i:
                break
            if i.score > 100000 and i.subreddit._path in sublist:
                uvlist=[i.id,settings['100k'],settings['75k'],settings['50k']]
                break
            if i.score > 75000 and i.subreddit._path in sublist:
                uvlist=[i.id,settings['75k'],settings['50k']]
                break
            if i.score > 50000 and i.subreddit._path in sublist:
                uvlist=[i.id,settings['50k']]
                break
            if i.score > huv[1]:
                huv=[i.id,i.score]
    for i in await user.moderated():
        if i._path in sublist[:3]:
            uvlist.append(settings[i._path])
    open('ref.txt','w').close()
    return (user.name,uvlist,huv)


def randomcode():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','1','2','3','4','5','6','7','8','9','0']
    result_str = ''
    for i in range(8):
        result_str=result_str+random.choice(letters)
    return str(result_str)


