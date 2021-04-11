import sys

from moodle_scrapper import *
from bs4 import BeautifulSoup
from requests import session
import requests
from datetime import datetime
import random

import discord
import asyncio
import os

STUDENT_ID = os.getenv("USERNAME")
LOGIN_PASSWORD = os.getenv('PASSWORD')
CHANNEL_ID = os.getenv('CHANNEL_ID')  # don't use double quote
imgur_key = os.getenv("IMAGURKEY")


def album(parameter):
    r = requests.get(
        f"https://api.imgur.com/3/gallery/t/{parameter}/?client_id={imgur_key}")
    json_data = r.json()
    return json_data


def imageFromAlbum(album_id):
    r = requests.get(
        f"https://api.imgur.com/3/album/{album_id}/images/?client_id={imgur_key}")
    json_data = r.json()
    return json_data


def getLink(parameter):
    jdata = album(parameter)
    if len(jdata['data']) == 11:
        return -1
    indexmax = len(jdata['data']['items']) - 1
    print(indexmax)
    size = random.randrange(0, indexmax, 1)
    obj = jdata['data']['items'][size]
    objlink = obj['link']
    album_id = objlink[20:]
    print(album_id)
    images = imageFromAlbum(album_id)
    indexmax = len(images['data'])
    size = random.randrange(0, indexmax, 1)
    thisImage = images['data'][size]
    imageLink = thisImage['link']
    return imageLink


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        if message.author == self.user.name:
            return
        if "send" in message.content.lower():
            tag = message.content.lower().split()
            keyword = tag[tag.index("send") + 1]
            print(keyword)
            link = getLink(keyword)
            if link == -1:
                await message.channel.send("Nice try, but I don't want FBI at my home.")
            else:
                await message.channel.send(link)

        if "cursed" in message.content.lower():
            link = getLink("cursed_images")
            await message.channel.send(link)

        if "hi bot" in message.content.lower():
            print(message.author.name)
            hatemsg = "Hi {0.author.name}, you're a retard.".format(message)
            goodmsg = "Hi {0.author.name}, oh dear gorgeous, you're the best.".format(
                message)
            if message.author.name == "zarifikram":
                await message.channel.send(hatemsg)
            else:
                await message.channel.send(goodmsg)

    async def autocursed(self):
        await self.wait_until_ready()
        while not self.is_closed():
            link = getLink("cursed_images")
            await self.get_channel(829927515442511915).send(link)
            await asyncio.sleep(4*60*60)

    async def my_background_task(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)  # channel ID goes here

        count = 0

        while not self.is_closed():

            count += 1
            print("Count :", count)

            # dd/mm/YY H:M:S
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("date and time =", dt_string)

            '''
            FORUMS
            '''
            print("getiing Old Forum Links ... \n")
            old_forum_links = get_old_forum_links(course_dict)
            # print(old_forum_links)

            print("getiing New Forum Posts ... \n")
            new_forum_posts = get_new_forum_posts(
                course_dict, old_forum_links, session)
            # print(new_forum_posts)

            '''
            ACTIVITY
            '''
            print("getiing Old Activity Links ... \n")
            old_activity_links = get_old_activity_links(course_dict)
            # print(old_forum_links)

            print("getiing New Activity Posts ... \n")
            new_activity_posts = get_new_activity_posts(
                course_dict, old_activity_links, session)
            # print(new_activity_posts)

            # for testing only
            for c_name, post_ara in new_forum_posts.items():

                if(len(post_ara) == 0):
                    continue

                for p in post_ara:
                    print(p)
                    embedVar = discord.Embed(
                        title="Forum Post ( " + c_name+" ) :rotating_light: ", description=p.title, color=0xb331bd)
                    embedVar.add_field(name="Link :paperclips: ",
                                       value=p.link, inline=False)
                    embedVar.add_field(name="Teacher :person_fencing: ",
                                       value="`"+p.author+"`", inline=False)
                    await channel.send(embed=embedVar)
                    await asyncio.sleep(30)  # 30 seconds

            for c_name, post_ara in new_activity_posts.items():

                if(len(post_ara) == 0):
                    continue

                for p in post_ara:
                    print(p)
                    embedVar = discord.Embed(
                        title="New Activity ( " + c_name + " ) :boom: ", description=p.title, color=0xfc9803)
                    embedVar.add_field(name="Link :paperclips: ",
                                       value=p.link, inline=False)
                    await channel.send(embed=embedVar)
                    await asyncio.sleep(30)  # 30 seconds

            await asyncio.sleep(20*60)  # check after 20 minutes


if __name__ == "__main__":

    # logging in
    print("logging in...\n")
    session = login(STUDENT_ID, LOGIN_PASSWORD)

    # get courses
    print("getting Courses...\n")
    course_dict = getCourses(session)
    print(course_dict)

    write_old_forum_posts(course_dict, session)
    write_old_activities(course_dict, session)

    print("OLD FORUM AND ACTIVITIES UPDATED")

    client = MyClient()

    client.run(os.getenv('TOKEN'))
