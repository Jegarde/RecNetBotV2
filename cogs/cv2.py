import functions
import requests
import discord
import random
import json
from difflib import SequenceMatcher
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from discord.ext import commands


class Cv2(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session_message = {}
        self.buttons = {
            "default": [
                [
                    Button(style=ButtonStyle.red, label="Yes")
                ],
            ],
            "disabled": [
                [
                    Button(style=ButtonStyle.red, label="Yes", disabled=True)
                ]
            ]
        }

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_cv2_json(self):
        circuits = requests.get(
            "https://raw.githubusercontent.com/tyleo-rec/CircuitsV2Resources/master/misc/circuitsv2.json").json()[
            'Nodes']
        return circuits

    def get_chip_filter_str(self, chip_name):
        chip = self.get_chip_data(chip_name)

        if not chip:
            return False
        if chip['Similar']:
            return False

        filter_str = ""
        for path in chip['NodeFilters']:
            filters = path['FilterPath']
            filter = "`Circuits V2\\" + '\\'.join(filters) + "`"
            filter_str += filter + "\n"

        return filter_str

    def get_all_chips(self):
        circuits = self.filter_chips("all")
        return circuits

    def get_chip_data(self, chip_name):
        circuits = self.get_all_chips()

        chip_name = chip_name.lower()
        for chip in circuits:
            if chip['ReadonlyName'].lower() == chip_name:
                chip['Similar'] = False
                return chip

        # if wasn't found, find a similar one
        similar_chip = {'chip': '', 'player_data': None, 'similarity': 0.0}
        for chip in circuits:
            name = chip['ReadonlyName'].lower()
            similarity = self.similar(name, chip_name)
            if similarity > similar_chip['similarity']:
                similar_chip = {'chip': '', 'player_data': chip, 'similarity': similarity}

        if similar_chip['similarity']:  # if a similar one was found
            chip = similar_chip['player_data']
            chip['Similar'] = True
            return chip

        return False  # not found at all.

    def input_output_emoji(self, input_output):
        emojis = {
            "float": "🟦",  # blue
            "exec": "🟧",  # orange
            "bool": "🟥",  # red
            "int": "🟩",  # green
            "AI": "🟨",  # yellow
            "Combatant": "🟨",  # yellow
            "Player": "🟨",  # yellow
            "Rec Room Object": "🟨",  # yellow
            "Quaternion": "🟨",  # yellow
            "Vector3": "🟨",  # yellow
            "string": "🟪"  # purple
        }

        if input_output not in emojis:
            if input_output[:4] == "List":
                return "[]"
            return "⬜"
        else:
            return emojis[input_output]

    def get_chip_inputs_str(self, chip_name):
        chip = self.get_chip_data(chip_name)
        if not chip:
            return False
        if chip['Similar']:
            return False
        if not chip['NodeDescs']:
            return False

        node_descs = chip['NodeDescs'][0]
        if not node_descs:
            return ""

        #nodes = node_descs[list(chip['NodeDescs'].keys())[0]]
        nodes = node_descs

        emoji = ""
        input_str = ""
        input_ports = nodes['Inputs']
        for input_port in input_ports:
            emoji = ""
            port_data = input_port
            if not port_data['Name']:
                name = 'Null'
            else:
                name = port_data['Name']
                if name == "Target":
                    emoji = "🟨"

            if port_data['ReadonlyType'] == "T":
                type = nodes["ReadonlyTypeParams"]["T"]
            else:
                type = port_data['ReadonlyType']

            if not emoji:
                emoji = self.input_output_emoji(type)
            input_str += f"{emoji} `{name} - {type}`\n"

        return input_str

    def get_chip_outputs_str(self, chip_name):
        chip = self.get_chip_data(chip_name)
        if not chip:
            return False
        if chip['Similar']:
            return False
        if not chip['NodeDescs']:
            return False

        node_descs = chip['NodeDescs'][0]
        if not node_descs:
            return ""

        #nodes = node_descs[list(chip['NodeDescs'].keys())[0]]
        nodes = node_descs

        emoji = ""
        output_str = ""
        output_ports = nodes['Outputs']
        for output_port in output_ports:
            port_data = output_port
            if not port_data['Name']:
                name = 'Null'
            else:
                name = port_data['Name']
                if name == "Target":
                    emoji = "🟨"

            if port_data['ReadonlyType'] == "T":
                type = nodes["ReadonlyTypeParams"]["T"]
            else:
                type = port_data['ReadonlyType']

            if not emoji:
                emoji = self.input_output_emoji(type)

            output_str += f"`{name} - {type}` {emoji}\n"

        return output_str

    def filter_chips(self, filter="all", categories=[]):
        circuits = self.get_cv2_json()

        filters = [
            "all",
            "beta",
            "non-beta"
        ]

        filter = filter.lower()
        if filter not in filters:
            filter = "all"

        filtered_chips = []
        for key in circuits:
            chip = circuits[key]
            is_beta = chip['IsBetaChip']
            if is_beta and filter == "non-beta":
                continue
            elif not is_beta and filter == "beta":
                continue

            filtered_chips.append(chip)

        return filtered_chips

    @commands.command()
    async def chips(self, ctx):
        circuits = self.get_cv2_json()

        em = discord.Embed(
            title="Circuits V2 Chip Count",
            colour=discord.Colour.orange()
        )

        all_count = len(self.filter_chips("all", []))
        beta_count = len(self.filter_chips("beta", []))

        em.add_field(name="Total Counts", value=f"""
            Chips in total: `{all_count}`
            Beta chips: `{beta_count}`
            Non-beta chips: `{all_count - beta_count}`
            """,
                     inline=False)
        functions.embed_footer(ctx, em)  # get default footer from function
        await ctx.send(embed=em)

    @chips.error
    async def clear_error(self, ctx, error):
        raise error

    @commands.command()
    async def cvresources(self, ctx):
        circuits = self.get_cv2_json()

        em = discord.Embed(
            title="Circuits V2 Resources",
            colour=discord.Colour.orange(),
            url="https://tyleo-rec.github.io/CircuitsV2Resources/"
        )

        em.add_field(name="Official Resources", value="""
            [How To Circuits V2 Blog Post](https://recroom.com/developer-blog/2020/8/3/how-2-circuits-2)
            [Circuits V2 Happy Fox Documentation](https://recroom.happyfox.com/kb/section/65/)
            [Circuits V2 Canny](https://recroom.canny.io/creative-tools?category=circuits-v2-feedback)
            [Circuits V2 Official YouTube Tutorial](https://www.youtube.com/watch?v=J_vGEe5-rc8)
            [Creative Classes and Events](https://recroom.com/creative)
            [Releases](https://tyleo-rec.github.io/CircuitsV2Resources/releases/)
            [Chip Json](https://github.com/tyleo-rec/CircuitsV2Resources/blob/master/misc/circuitsv2.json)
            """, inline=False)

        em.add_field(name="Unofficial Resources", value="""
                **YouTube**
                [How To Use Circuits V2 (Beginner Tutorial, Events, and Variables) - Rec Room VR](https://youtu.be/Ow2CCZPedb0)
                [Rec Room - Circuits V2 Tutorial](https://youtu.be/sQ4GuOyiink)
                [Rec Room - Circuits V2 Tutorial - List based calculator.](https://youtu.be/3pD_gLHelTs)
                
                **Circuits V2 Community Tutorial Rooms**
                [^CircuitV2Documentation](https://rec.net/room/CircuitV2Documentation/)
                [^CircuitsV2Tutorials](https://rec.net/room/CircuitsV2Tutorials)
                [^CircuitsVersionTwoTutorial](https://rec.net/room/CircuitsVersionTwoTutorial)
                [^YoesCircuitsV2](https://rec.net/room/YoesCircuitsV2)
                """, inline=False)

        functions.embed_footer(ctx, em)  # get default footer from function
        await ctx.send(embed=em)

    @cvresources.error
    async def clear_error(self, ctx, error):
        raise error


    @commands.command()
    async def chip(self, ctx, *chip):
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        chip = ' '.join(chip)
        if not chip:
            em = functions.error_msg(
                ctx,
                "Please enter a chip!"
            )
            functions.embed_footer(ctx, em)  # get default footer from function
            return await ctx.send(embed=em)

        data = self.get_chip_data(chip)
        if data:
            if data['Similar']:
                similar_chip = data['ReadonlyName']
                em = functions.error_msg(
                    ctx,
                    f"`{chip}` chip couldn't be found, did you mean `{similar_chip}`?"
                )
                m = await ctx.send(embed=em, components=self.buttons['default'])

                def check(res):
                    return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                        ctx.author.id] == m_session

                try:
                    res = await self.client.wait_for("button_click", check=check, timeout=30)
                    await res.respond(type=6)
                except:
                    return await m.edit(components=self.buttons['disabled'])

                if res.component.label == "Yes":
                    await m.edit(
                        components=self.buttons['disabled']
                    )
                    await self.chip(ctx, similar_chip)
            else:
                em = discord.Embed(
                    title=data['ReadonlyName'] + " chip",
                    colour=discord.Colour.orange()
                )

                description = data['Description']
                if description:
                    em.add_field(name="Description", value=f"```{description}```", inline=False)

                if data['IsBetaChip']:
                    is_beta = "✅"
                else:
                    is_beta = "❌"

                if data['DeprecationStage']:
                    is_deprecated = "✅"
                else:
                    is_deprecated = "❌"

                em.add_field(name="Information", value=f"{is_beta} Beta?\n{is_deprecated} Deprecated?", inline=False)

                inputs = self.get_chip_inputs_str(chip)
                if inputs:
                    em.add_field(name="Inputs", value=inputs, inline=True)

                outputs = self.get_chip_outputs_str(chip)
                if outputs:
                    em.add_field(name="Outputs", value=outputs, inline=True)

                filters = self.get_chip_filter_str(chip)
                if filters:
                    em.add_field(name="Filters", value=filters, inline=False)

                functions.embed_footer(ctx, em)  # get default footer from function
                await ctx.send(embed=em)
        else:
            em = functions.error_msg(
                ctx,
                f"`{chip}` chip couldn't be found!"
            )
            functions.embed_footer(ctx, em)  # get default footer from function
            return await ctx.send(embed=em)

    @chip.error
    async def clear_error(self, ctx, error):
        raise error


def setup(client):
    client.add_cog(Cv2(client))
