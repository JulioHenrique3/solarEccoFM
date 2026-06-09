# pyrefly: ignore [missing-import]
import discord
# pyrefly: ignore [missing-import]
from discord import app_commands
# pyrefly: ignore [missing-import]
from discord.ext import commands
# pyrefly: ignore [missing-import]
import asyncio
from yt_dlp import YoutubeDL


class music(commands.Cog):
    def __init__(self, client):
        self.client = client
    
        #all the music related stuff
        self.is_playing = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.current_song = None
        self.YDL_OPTIONS = {
            'format': 'bestaudio', 
            'noplaylist': False,
            'ignoreerrors': True,
            'cookiesfrombrowser': ('brave',),
            'remote_components': ['ejs:npm', 'ejs:github']
        }


        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""

     #searching the item on youtube
        #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                if item.startswith("http://") or item.startswith("https://"):
                    info = ydl.extract_info(item, download=False)
                else:
                    info = ydl.extract_info(f"ytsearch:{item}", download=False)
            except Exception as e:
                print(f"Erro no yt-dlp: {e}")
                return False

        # Se tiver a chave 'entries', pode ser uma busca ou uma playlist
        if 'entries' in info:
            # Se for uma pesquisa por texto (não URL), pegamos apenas o primeiro resultado
            if not (item.startswith("http://") or item.startswith("https://")):
                entry = info['entries'][0]
                return [{'source': entry['url'], 'title': entry['title']}]
            
            # Se for uma URL de playlist, adicionamos todos os vídeos
            songs = []
            for entry in info['entries']:
                if entry: # Ignora vídeos ocultos ou excluídos da playlist
                    songs.append({'source': entry['url'], 'title': entry['title']})
            return songs
        else:
            # Se for um único vídeo (URL direta que não é playlist)
            return [{'source': info['url'], 'title': info['title']}]

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            item = self.music_queue.pop(0)
            self.current_song = item[0]
            m_url = item[0]['source']

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
            self.current_song = None

    # infinite loop checking 
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            item = self.music_queue.pop(0)
            self.current_song = item[0]
            m_url = item[0]['source']
            voice_channel = item[1]
            
            #try to connect to voice channel if you are not already connected

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await voice_channel.connect()
            else:
                await self.vc.move_to(voice_channel)
            
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
            self.current_song = None
            if self.vc != "" and self.vc:
                await self.vc.disconnect()

    @app_commands.command(name="ajuda",description="Mostre um comando de ajuda.")
    async def help(self,interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        helptxt = "`/ajuda` - Veja esse guia!\n`/play` - Toque uma música do YouTube!\n`/fila` - Veja a fila de músicas na Playlist\n`/pular` - Pule para a próxima música da fila"
        embedhelp = discord.Embed(
            colour = 1646116,#grey
            title=f'Comandos do {self.client.user.name}',
            description = helptxt
        )
        try:
            embedhelp.set_thumbnail(url=self.client.user.avatar.url)
        except:
            pass
        await interaction.followup.send(embed=embedhelp)


    @app_commands.command(name="play",description="Toca uma música ou playlist do YouTube.")
    @app_commands.describe(
        busca = "Digite o nome da música ou o link (vídeo/playlist) no YouTube"
    )
    async def play(self, interaction:discord.Interaction,busca:str):
        await interaction.response.defer(thinking=True)
        query = busca
        
        try:
            voice_channel = interaction.user.voice.channel
        except:
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Para tocar uma música, primeiro se conecte a um canal de voz.'
            )
            await interaction.followup.send(embed=embedvc)
            return
        
        songs = await asyncio.to_thread(self.search_yt, query)
        if type(songs) == type(True): # Verifica se deu erro (retornou False)
            embedvc = discord.Embed(
                colour= 12255232,#red
                description = 'Algo deu errado! Tente mudar ou configurar a playlist/vídeo ou escrever o nome dele novamente!'
            )
            await interaction.followup.send(embed=embedvc)
        else:
            # Mensagem dependendo de ser uma única música ou playlist
            if len(songs) == 1:
                embedvc = discord.Embed(
                    colour= 32768,#green
                    description = f"Você adicionou a música **{songs[0]['title']}** à fila!"
                )
            else:
                embedvc = discord.Embed(
                    colour= 32768,#green
                    description = f"Você adicionou **{len(songs)} músicas** da playlist à fila!"
                )
            await interaction.followup.send(embed=embedvc)
            
            # Adiciona cada música retornada à fila de reprodução
            for song in songs:
                self.music_queue.append([song, voice_channel])
                
            if self.is_playing == False:
                await self.play_music()

    @app_commands.command(name="fila",description="Mostra as atuais músicas da fila.")
    async def q(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        retval = ""
        
        if self.current_song:
            retval += f"**Tocando agora:** {self.current_song['title']}\n\n"

        if len(self.music_queue) > 0:
            retval += "**Na fila:**\n"
            for i in range(0, len(self.music_queue)):
                retval += f"**{i+1} - ** " + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"{retval}"
            )
            await interaction.followup.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour= 1646116,
                description = 'Não existem músicas tocando ou na fila no momento.'
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="pular",description="Pula a atual música que está tocando.")
    @app_commands.default_permissions(manage_channels=True)
    async def pular(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.vc != "" and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music()
            embedvc = discord.Embed(
                colour= 1646116,#ggrey
                description = f"Você pulou a música."
            )
            await interaction.followup.send(embed=embedvc)

    @pular.error #Erros para kick
    async def skip_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, commands.MissingPermissions):
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"Você precisa da permissão **Gerenciar canais** para pular músicas."
            )
            await interaction.followup.send(embed=embedvc)     
        else:
            raise error

    @app_commands.command(name="pausar",description="Pausa a música atual.")
    async def pausar(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.vc != "" and self.vc and self.vc.is_playing():
            self.vc.pause()
            embedvc = discord.Embed(
                colour= 32768,
                description = f"Música **pausada**! ⏸️"
            )
            await interaction.followup.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"Não há nenhuma música tocando no momento."
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="retomar",description="Retoma a música pausada.")
    async def retomar(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.vc != "" and self.vc and self.vc.is_paused():
            self.vc.resume()
            embedvc = discord.Embed(
                colour= 32768,
                description = f"Música **retomada**! ▶️"
            )
            await interaction.followup.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"A música não está pausada."
            )
            await interaction.followup.send(embed=embedvc)

async def setup(client):
    await client.add_cog(music(client))
    