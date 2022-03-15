# from _typeshed import NoneType
# import discord
from discord.ext import commands
from aternosapi import AternosAPI
from os import getcwd
from json import load, dumps

with open(getcwd()+"/credentials.json") as creds:
    credentials = load(creds)

with open(getcwd()+"/servers.json") as srvs:
    servers = load(srvs)

bot = commands.Bot(command_prefix='$')

@bot.command(name="list-servers", pass_context=True, help="Lists available servers")
async def list_servers(ctx):
    global servers
    resp = []
    api = AternosAPI(credentials["common_cookies"])

    servers = api.ServerUpdate()
    for i, server in enumerate(list(servers.keys())):
        resp.append(str(i+1)+": "+server)
    api.driver.quit()

    dump_data = dumps(servers, indent=4)
    with open(getcwd()+"/servers.json", "w") as outfile:
        outfile.write(dump_data)
    
    await ctx.send("The registered servers are: \n"+"\n".join(resp))

@bot.command(pass_context=True, help="Shows the current status of the mentioned server")
async def status(ctx, srv_no):
    try:
        srv_name = list(servers.keys())[int(srv_no)-1]
        api = AternosAPI(credentials["common_cookies"], servers[srv_name]["server_cookie"])
        await ctx.send(srv_name+" server is curently "+api.GetStatus())
        api.driver.quit()
    except IndexError:
        await ctx.send("Such a entry do not exist")

@bot.command(pass_context=True, help="Starts the mentioned server")
async def start(ctx, srv_no):
    try:
        srv_name = list(servers.keys())[int(srv_no)-1]
        api = AternosAPI(credentials["common_cookies"], servers[srv_name]["server_cookie"])
        sresp = api.StartServer()
        if sresp != "Something went wrong":
            await ctx.send(srv_name+" "+sresp)
        else :
            await ctx.send(sresp)
        api.driver.quit()
    except IndexError:
        await ctx.send("Such an entry does not exist")
    except TypeError:
        await ctx.send("Something went wrong")

@bot.command(pass_context=True, help="Stops the mentioned server (`REQUIRED ROLE: Admin`)")
@commands.has_role("Admin")
async def stop(ctx, srv_no):
    try:
        srv_name = list(servers.keys())[int(srv_no)-1]
        api = AternosAPI(credentials["common_cookies"], servers[srv_name]["server_cookie"])
        sresp = api.StopServer()
        if sresp != "Something went wrong":
            await ctx.send(srv_name+" "+sresp)
        else :
            await ctx.send(sresp)
        api.driver.quit()
    except IndexError:
        await ctx.send("Such an entry does not exist")
    except TypeError:
        await ctx.send("Something went wrong")

@bot.command(pass_context=True, help="Shows the information about the mentioned server")
async def getinfo(ctx, srv_no):
    try:
        srv_name = list(servers.keys())[int(srv_no)-1]
        api = AternosAPI(credentials["common_cookies"], servers[srv_name]["server_cookie"])
        sresp = api.GetServerInfo()
        await ctx.send(sresp["ip"].split(".")[0]+"\nIP: "+sresp["ip"]+"\nPort: "+sresp["port"]+"\nSoftware: "+sresp["software"]+"\nVersion: "+sresp["version"]+"\nPlayers: "+sresp["players"]+"\nStatus: "+sresp["status"])
        api.driver.quit()
    except IndexError:
        await ctx.send("Such an entry does not exist")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        await ctx.send("You are laking proper roles to run this command")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Such a command do not exist")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention a server number e.g. 1")
    else:
        print(error)

bot.run(credentials["secret_key"])
