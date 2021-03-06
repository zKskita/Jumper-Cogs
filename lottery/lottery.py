#  Lottery.py was created by Redjumpman for Redbot
#  This will create a data folder with 2 JSON files
import os
import asyncio
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
from random import choice as randchoice


class Lottery:
    """Starts a lottery on the server"""

    def __init__(self, bot):
        self.bot = bot
        self.players = fileIO("data/lottery/players.json", "load")
        self.system = fileIO("data/lottery/system.json", "load")
        self.funny = ["Rigging the system...",
                      "Removing tickets that didn't pay me off...",
                      "Adding fake tickets...", "Throwing out the bad names..",
                      "Switching out the winning ticket...",
                      "Picking from highest bribe...",
                      "Looking for a marked ticket...",
                      "Eeny, meeny, miny, moe...",
                      "I lost the tickets so...",
                      "Stop messaging me, I'm picking...",
                      "May the odds be ever in your favor...",
                      "I'm going to ban that guy who keeps spamming me, 'please!'... ",
                      "Winner winner, chicken dinner...",
                      "Can someone tell the guy who keeps yelling 'Bingo!' that he is playing the wrong game..."]

    @commands.group(name="lottery", pass_context=True)
    async def _lottery(self, ctx):
        """Lottery Commands."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @_lottery.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def fun(self, ctx):
        """Add/Removes some fun text to picking the winner"""
        if self.system["funny"] == "Off":
            self.system["funny"] = "On"
            fileIO("data/lottery/system.json", "save", self.system)
            await self.bot.say("Fun text for the lottery is now ON!")

        elif self.system["funny"] == "On":
            self.system["funny"] = "Off"
            fileIO("data/lottery/system.json", "save", self.system)
            await self.bot.say("Fun text for the lottery is now OFF!")
        else:
            await self.bot.say("Missing funny parameter. Delete your " +
                               "system.json file in your lottery folder.")

    @_lottery.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def prize(self, ctx, credits: int):
        """Adds an optional point prize for the lottery winner"""
        self.system["Prize"] = True
        self.system["Prize Amount"] = credits
        fileIO("data/lottery/system.json", "save", self.system)
        await self.bot.say("I have set a prize for the winner, in the amount of " +
                           str(credits) + " credits.")

    @_lottery.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def start(self, ctx):
        """Begins the lottery until you enter a stop command"""
        user = ctx.message.author
        if self.system["lottery_start"] == "Inactive":
            self.system["lottery_start"] = "Active"
            self.system["lotteries_played"] = self.system[
                                                             "lotteries_played"
                                                             ] + 1
            fileIO("data/lottery/system.json", "save", self.system)
            await self.bot.say("A lottery has been started by " +
                               user.mention + "\n" +
                               "To enter type, !lottery play." +
                               " Make sure to sign up or you can't play!!")
        else:
            await self.bot.say("You cannot start another lottery while one" +
                               " is active." + "\n" + "End the current" +
                               " lottery to start another.")

    @_lottery.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def end(self, ctx):
        """This will stop the lottery and pick a winner"""
        server = ctx.message.server
        if self.system["lottery_start"] == "Active":
            self.system["lottery_start"] = "Inactive"
            fileIO("data/lottery/system.json", "save", self.system)
            results = []
            for subdict in self.players.values():
                results.append(subdict['current_ticket'])
            for subdict in self.players.values():
                subdict['ticket_played'] = "No"
            fileIO("data/lottery/players.json", "save", self.players)
            f = list(filter(None, results))
            names = randchoice(f)
            a = self.discord_id(names, ctx)
            b = self.discord_check(names, ctx)
            winner = b[0]
            winner_id = a[0]
            funny = randchoice(self.funny)
            await self.bot.say("The winner is...")
            await asyncio.sleep(2)
            if self.system["funny"] == "On":
                await self.bot.say(str(funny))
                await asyncio.sleep(5)
                await self.bot.say(winner + "!!!" +
                                   "\n" + "Congratulations " + winner)
                if self.system["Prize"]:
                    prize = self.system["Prize Amount"]
                    await self.bot.say("The prize of " + str(prize) + " credits has been deposited into your account.")
                    mobj = server.get_member(winner_id)
                    bank = self.bot.get_cog("Economy").bank
                    bank.deposit_credits(mobj, prize)
                    self.system["Prize"] = False
                    self.system["Prize Amount"] = 0
                    fileIO("data/lottery/system.json", "save", self.system)
                lookup = self.which_dict_key(names, self.players)
                extract = lookup[0]
                self.players[extract]["lotteries_won"] = self.players[
                                                                     extract
                                                        ]["lotteries_won"] + 1
                fileIO("data/lottery/players.json", "save", self.players)
                for subdict in self.players.values():
                    subdict['current_ticket'] = ""
                    fileIO("data/lottery/players.json", "save", self.players)
            else:
                await self.bot.say(str(winner) + "!!!" +
                                   "\n" + "Congratulations " + str(winner))
                if self.system["Prize"]:
                    prize = self.system["Prize Amount"]
                    await self.bot.say("The prize of " + str(prize) + " credits has been deposited into your account.")
                    userid = str(winner).replace("<", "").replace("@", "").replace(">", "")
                    mobj = server.get_member(userid)
                    bank = self.bot.get_cog("Economy").bank
                    bank.deposit_credits(mobj, prize)
                    self.system["Prize"] = False
                    self.system["Prize Amount"] = 0
                    fileIO("data/lottery/system.json", "save", self.system)
                lookup = self.which_dict_key(names, self.players)
                extract = lookup[0]
                self.players[extract]["lotteries_won"] = self.players[
                                                                      extract
                                                          ]["lotteries_won"
                                                            ] + 1
                fileIO("data/lottery/players.json", "save", self.players)
                for subdict in self.players.values():
                    subdict['current_ticket'] = ""
                    fileIO("data/lottery/players.json", "save", self.players)

        else:
            await self.bot.say("You can't end a lottery that I have"
                               " not started.")

    @_lottery.command(pass_context=True, no_pm=True)
    async def signup(self, ctx):
        """This allows a user to sign-up to play lotteries"""
        user = ctx.message.author
        if user.id not in self.players:
            self.players[user.id] = {"name": user.name,
                                     "lotteries_played": 0,
                                     "lotteries_won": 0,
                                     "current_ticket": "",
                                     "ticket_played": "No"}
            fileIO("data/lottery/players.json", "save", self.players)
            await self.bot.say("You have joined the lottery system " +
                               user.mention + ". You can now participate in" +
                               " all future lotteries")
        else:
            await self.bot.say("You are already a lottery member")

    @_lottery.command(pass_context=True, no_pm=True)
    async def play(self, ctx):
        """This let's a user play in an on-going lottery"""
        user = ctx.message.author
        userid = user.id
        if self.system["lottery_start"] == "Active":
            if user.id in self.players:
                if self.players[userid]["ticket_played"] == "No":
                    self.players[userid]["ticket_played"] = "Yes"
                    self.players[userid]["current_ticket"] = user.name
                    self.players[userid]["lotteries_played"] = self.players[userid][
                        "lotteries_played"
                        ] + 1
                    fileIO("data/lottery/players.json", "save", self.players)
                    await self.bot.say(user.mention + " has been entered into the" +
                                       " lottery")
                else:
                    await self.bot.say("You have already been entered into " +
                                       "this lottery.")
            else:
                await self.bot.say("You need to sign-up to play in an " +
                                   "ongoing lottery")
        else:
            await self.bot.say("There is currently no on-going lottery")

    @_lottery.command(pass_context=True, no_pm=True)
    async def stats(self, ctx):
        """Retrieves a user's lottery stats"""
        user = ctx.message.author
        userid = user.id
        if user.id in self.players:
            total = self.system["lotteries_played"]
            played = self.players[userid]["lotteries_played"]
            wins = self.players[userid]["lotteries_won"]
            await self.bot.say("\n" + "```" + "Lotteries Ran: " + str(total) +
                               "\n" + "Lotteries Played: " + str(played) +
                               "\n" + "Lotteries Won: " + str(wins) + "```")
        else:
            await self.bot.say("You need to sign-up for lotteries first.")

    def discord_check(self, names, ctx):
        return [m.mention for m in ctx.message.server.members if m.name in names]

    def discord_id(self, names, ctx):
        return [m.id for m in ctx.message.server.members if m.name in names]

    def which_dict_key(self, value, dicts):
        '''
        Return a list of keys for a dictionary where the value dictionary
        for that key includes the value provided.
        '''
        return [key for key in dicts if value in dicts[key].values()]


def check_folders():
    if not os.path.exists("data/lottery"):
        print("Creating data/lottery folder...")
        os.makedirs("data/lottery")


def check_files():
    system = {"lotteries_played": 0, "lottery_start": "Inactive",
              "funny": "Off", "Prize": False, "Prize Amount": 0}

    f = "data/lottery/players.json"
    if not fileIO(f, "check"):
        print("Adding lottery player.json...")
        fileIO(f, "save", {})

    f = "data/lottery/system.json"
    if not fileIO(f, "check"):
        print("Creating default lottery system.json...")
        fileIO(f, "save", system)
    else:  # consistency check
        current = fileIO(f, "load")
        if current.keys() != system.keys():
            for key in system.keys():
                if key not in current.keys():
                    current[key] = system[key]
                    print("Adding " + str(key) +
                          " field to lottery system.json")
            fileIO(f, "save", current)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Lottery(bot))
