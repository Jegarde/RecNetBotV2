import functions
import discord
from discord.ext import commands
from discord.ext import menus


class Test(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check(functions.is_it_me)
    async def test(self, ctx, x, y):
        global xy
        xy = [int(x),int(y)]
        m =  GameInstance()
        await m.start(ctx)


class GameInstance(menus.Menu):
    instance = None
    coords = [2,2]
    blocks = ['⬜', '🔳', '<:flushy:700195761765482496>', '<:RootBeer:825646217471983646>']
    map = {}

    async def send_initial_message(self, ctx, channel):
        global xy
        #self.map = await self.generate_map(xy[0], xy[1])
        self.map = {
            0: [1,1,1,1,1,1,1,1],
            1: [1,0,1,0,0,0,0,1],
            2: [1,0,1,0,0,0,0,1],
            3: [1,0,0,0,0,0,0,1],
            4: [1,0,0,0,0,3,0,1],
            5: [1,1,1,0,0,1,1,1],
            6: [1,1,1,0,0,1,1,1],
            7: [1,1,1,0,0,1,1,1],
            8: [1,1,1,1,1,1,1,1],
            9: [1,1,1,1,1,1,1,1],
        }
        render = await self.render_game(self.coords)
        return await channel.send(render)
        

    async def generate_map(self, x=7, y=7):
        print(f"Starting generation of map! x: {x}, y: {y}")
        gen_map = {}
        for layer in range(y):
            print(f"layer: {layer}")
            gen_map[layer] = []
            i = 0
            for tile in range(x):
                print(f"tile: {tile}")
                if layer == 0 or layer == y-1:
                    gen_map[layer].append(1)
                elif i == 0 or i == x-1:
                    gen_map[layer].append(1)
                else:
                    gen_map[layer].append(0)
                print(f"block: {gen_map[layer][len(gen_map[layer])-1]}")
                print("\r")
                i += 1
        return gen_map


    async def render_game(self, coordinates=None):
        render = f"x: {coordinates[0]}, y: {coordinates[1]}\n"
        print(f"To render: {self.map.keys()}")
        print(f"Player coords: {coordinates}")
        for layer in self.map:
            print(f"Rendering layer {layer}")
            i = 0
            for tile in self.map[layer]:
                print(f"Rendering tile {i} in {layer}")
                i += 1
                if coordinates and (coordinates[0], coordinates[1]-1) == (i, layer):
                    print(f"Player tile! {coordinates}")
                    render += str(self.blocks[2])
                else:
                    render += str(self.blocks[tile])
            print(f"Layer {layer} finished rendering!")
            render += "\n"
        print("Render complete!\n\n\n")
        return render

    async def check_collision(self, coordinates):
        if self.map[coordinates[1]-1][coordinates[0]-1] == 1:
            return True
        return False

    @menus.button('🔼')
    async def move_up(self, payload):
        if not await self.check_collision([self.coords[0], self.coords[1]-1]):
            self.coords[1] -= 1
            print(f"Move up! {self.coords}")
            render = await self.render_game(self.coords)
            await self.message.edit(content=render)
        else: print("Collided while moving up!")

    @menus.button('🔽')
    async def move_down(self, payload):
        if not await self.check_collision([self.coords[0], self.coords[1]+1]):
            self.coords[1] += 1
            print(f"Move down! {self.coords}")
            render = await self.render_game(self.coords)
            await self.message.edit(content=render)
        else: print("Collided while moving down!")

    @menus.button('◀️')
    async def move_left(self, payload):
        if not await self.check_collision([self.coords[0]-1, self.coords[1]]):
            self.coords[0] -= 1
            print(f"Move left! {self.coords}")
            render = await self.render_game(self.coords)
            await self.message.edit(content=render)
        else: print("Collided while moving left!")

    @menus.button('▶️')
    async def move_right(self, payload):
        if not await self.check_collision([self.coords[0]+1, self.coords[1]]):
            self.coords[0] += 1
            print(f"Move right! {self.coords}")
            render = await self.render_game(self.coords)
            await self.message.edit(content=render)
        else: print("Collided while moving left!")




def setup(client):
    client.add_cog(Test(client))
