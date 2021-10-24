import discord
from discord.ext import commands
from discord.ext.commands.core import command
from sqlalchemy.orm import Session
from sqlalchemy import insert
from utils import discord_utils, admin_utils, logging_utils, database_utils
import constants


class CustomCommandCog(commands.Cog, name="Custom Command"):
    """Create your own custom command!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.has_any_role(*constants.TRUSTED)
    @commands.command(name="addembedcommand", aliases=["addcustomcommand", "addccommand"])
    async def addembedcommand(self, ctx, command_name: str, *args):
        """Add your own custom command to the bot with an embed reply
        
        Usage: `~addembedcommand command_name \"This is my custom command!\""""
        logging_utils.log_command("addembedcommand", ctx.channel, ctx.author)

        if len(args) <= 0:
            discord_utils.create_no_argument_embed("Command Return")
        
        command_name = command_name.lower()
        command_return = " ".join(args)
        
        if command_name in constants.DEFAULT_COMMANDS:
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.FAILED}",
                            value=f"Command {command_name} is a default command. Please use a different name.")

            await ctx.send(embed=embed)
            return

        if command_name in constants.CUSTOM_COMMANDS[ctx.guild.id]:
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.FAILED}",
                            value=f"The command `{ctx.prefix}{command_name}` already exists in `{ctx.guild.name}` with value "
                                    f"`{constants.CUSTOM_COMMANDS[ctx.guild.id][command_name][0]}`. If you'd like to replace "
                                    f"`{ctx.prefix}{command_name}`, please use `{ctx.prefix}editcustomcommand {command_name} "
                                    f"{command_return}`")
            await ctx.send(embed=embed)
            return

        with Session(constants.DATABASE_ENGINE) as session:
            result = session.query(database_utils.CustomCommmands)\
                            .filter_by(server_id_command=f"{ctx.guild.id} {command_name}")\
                            .first()
            if result is None:
                stmt = insert(database_utils.CustomCommmands).values(server_id=ctx.guild.id, server_name=ctx.guild.name,
                                                                     server_id_command=f"{ctx.guild.id} {command_name}",
                                                                     command_name=command_name, command_return=command_return,
                                                                     image=False)
                session.execute(stmt)
                session.commit()
                
                embed = discord_utils.create_embed()
                embed.add_field(name=f"{constants.SUCCESS}",
                                value=f"Added `{ctx.prefix}{command_name}` with value `{command_return}`")
            # Command exists in the DB but not in our constants.
            else:
                command_return = result.command_return
            # update constants dict
            constants.CUSTOM_COMMANDS[ctx.guild.id][command_name] = (command_return, False)
                 
        await ctx.send(embed=embed)

    @commands.has_any_role(*constants.TRUSTED)
    @commands.command(name="addtextcommand", aliases=["addcustomimage", "addcimage"])
    async def addtextcommand(self, ctx, command_name: str, *args):
        """Add your own custom command to the bot with a text reply (good for images and pings)
        
        Usage: `~addtextcommand command_name Link_to_image"""
        logging_utils.log_command("addtextcommand", ctx.channel, ctx.author)

        if len(args) <= 0:
            discord_utils.create_no_argument_embed("Command Return")

        command_name = command_name.lower()
        command_return = " ".join(args)

        if command_name in constants.DEFAULT_COMMANDS:
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.FAILED}",
                            value=f"Command {command_name} is a default command. Please use a different name.")

            await ctx.send(embed=embed)
            return

        if command_name in constants.CUSTOM_COMMANDS[ctx.guild.id]:
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.FAILED}",
                            value=f"The command `{ctx.prefix}{command_name}` already exists in `{ctx.guild.name}` with value "
                                    f"`{constants.CUSTOM_COMMANDS[ctx.guild.id][command_name][0]}`. If you'd like to replace "
                                    f"`{ctx.prefix}{command_name}`, please use `{ctx.prefix}editcustomcommand {command_name} "
                                    f"{command_return}`")
            await ctx.send(embed=embed)
            return

        with Session(constants.DATABASE_ENGINE) as session:
            result = session.query(database_utils.CustomCommmands)\
                            .filter_by(server_id_command=f"{ctx.guild.id} {command_name}")\
                            .first()
            if result is None:
                stmt = insert(database_utils.CustomCommmands).values(server_id=ctx.guild.id, server_name=ctx.guild.name,
                                                                     server_id_command=f"{ctx.guild.id} {command_name}",
                                                                     command_name=command_name, command_return=command_return,
                                                                     image=True)
                session.execute(stmt)
                session.commit()
                
                embed = discord_utils.create_embed()
                embed.add_field(name=f"{constants.SUCCESS}",
                                value=f"Added `{ctx.prefix}{command_name}` with value `{command_return}`")
            # Command exists in the DB but not in our constants.
            else:
                command_return = result.command_return
            # update constants dict
            constants.CUSTOM_COMMANDS[ctx.guild.id][command_name] = (command_return, True)
                 
        await ctx.send(embed=embed)

    @commands.has_any_role(*constants.TRUSTED)
    @commands.command(name="lscustomcommands", aliases=["lscustomcommand",
                                                        "listcustomcommands",
                                                        "listcustomcommand", 
                                                        "lsccommands",
                                                        "lsccommand", 
                                                        "listccommands",
                                                        "listccommand"])
    async def lscustomcommands(self, ctx):
        """List custom commands in the server
        
        Usage: `~lscustomcommands`"""
        logging_utils.log_command("lscustomcommands", ctx.channel, ctx.author)

        custom_commands = "\n".join(constants.CUSTOM_COMMANDS[ctx.guild.id].keys())
        embed = discord.Embed(title=f"Custom Commands for {ctx.guild.name}",
                              description=custom_commands,
                              color=constants.EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.has_any_role(*constants.TRUSTED)
    @commands.command(name="editcustomcommand", aliases=["editccommand", "editcimage"])
    async def editcustomcommand(self, ctx, command_name: str, *args):
        """Edit an existing custom command, or adds the command if it doesn't exist.
        
        Usage: `~editcustomcommand potato My new return value`"""
        logging_utils.log_command("editcustomcommand", ctx.channel, ctx.author)

        command_name = command_name.lower()
        command_return = " ".join(args)

        if command_name in constants.CUSTOM_COMMANDS[ctx.guild.id]:
            # Update command in DB
            with Session(constants.DATABASE_ENGINE) as session:
                result = session.query(database_utils.CustomCommmands)\
                       .filter_by(server_id_command=f"{ctx.guild.id} {command_name}")\
                       .update({"command_return": command_return})
                session.commit()
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.SUCCESS}",
                            value=f"Edited command `{ctx.prefix}{command_name}` to have return value "
                                  f"`{command_return}`")
            constants.CUSTOM_COMMANDS[ctx.guild.id][command_name] = (command_return, constants.CUSTOM_COMMANDS[ctx.guild.id][command_name][1])
        else:
            # If the command does not exist yet, just add it to DB.
            with Session(constants.DATABASE_ENGINE) as session:
                stmt = insert(database_utils.CustomCommmands).values(server_id=ctx.guild.id, server_name=ctx.guild.name,
                                                                     server_id_command=f"{ctx.guild.id} {command_name}",
                                                                     command_name=command_name, command_return=command_return,
                                                                     image=False)
                session.execute(stmt)
                session.commit()
            constants.CUSTOM_COMMANDS[ctx.guild.id][command_name] = (command_return, False)
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.SUCCESS}",
                            value=f"Added command `{ctx.prefix}{command_name}` with return value "
                                  f"`{command_return}`")
        
        await ctx.send(embed=embed)

    @commands.has_any_role(*constants.TRUSTED)
    @commands.command(name="rmcustomcommand", aliases=["removecustomcommand", "rmccommand", "removeccommand"])
    async def rmcustomcommand(self, ctx, command_name: str):
        """Remove an existing custom command
        
        Usage: `~rmcustomcommand potato`"""
        logging_utils.log_command("rmcustomcommand", ctx.channel, ctx.author)

        command_name = command_name.lower()
        if command_name in constants.CUSTOM_COMMANDS[ctx.guild.id]:
            del constants.CUSTOM_COMMANDS[ctx.guild.id][command_name]
            with Session(constants.DATABASE_ENGINE) as session:
                session.query(database_utils.CustomCommmands)\
                       .filter_by(server_id_command=f"{ctx.guild.id} {command_name}")\
                       .delete()
                session.commit()
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.SUCCESS}",
                            value=f"Deleted custom command `{ctx.prefix}{command_name}`")
        else:
            embed = discord_utils.create_embed()
            embed.add_field(name=f"{constants.FAILED}",
                            value=f"Command `{ctx.prefix}{command_name}` does not exist in {ctx.guild.name}")
        await ctx.send(embed=embed)

    @admin_utils.is_owner_or_admin()
    @commands.command(name="reloadcommandcache", aliases=["reloadccache", "ccachereload"])
    async def reloadcommandcache(self, ctx):
        """Reloads the custom command cache. This is useful when we're editing commands or playing with the DB
        
        Usage: `~reloadcommandcache`"""
        logging_utils.log_command("reloadcommandcache", ctx.channel, ctx.author)

        constants.CUSTOM_COMMANDS = {}
        with Session(constants.DATABASE_ENGINE) as session:
            for guild in self.bot.guilds:
                constants.CUSTOM_COMMANDS[guild.id] = {}
                custom_command_result = session.query(database_utils.CustomCommmands)\
                                    .filter_by(server_id=guild.id)\
                                    .all()
                if custom_command_result is not None:
                    for custom_command in custom_command_result:
                        # Populate custom command dict
                        constants.CUSTOM_COMMANDS[guild.id][custom_command.command_name.lower()] = (custom_command.command_return, custom_command.image)
        embed = discord_utils.create_embed()
        embed.add_field(name=f"{constants.SUCCESS}",
                        value="Successfully reloaded command cache.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CustomCommandCog(bot))