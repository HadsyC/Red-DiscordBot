import datetime
import heapq
import math
import random
from pathlib import Path

import discord
import lavalink
from red_commons.logging import getLogger

from redbot.core import commands
from redbot.core.i18n import Translator
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import humanize_number, pagify
from redbot.core.utils.menus import menu

from ..abc import MixinMeta
from ..cog_utils import CompositeMetaClass

log = getLogger("red.cogs.Audio.cog.Commands.miscellaneous")
_ = Translator("Audio", Path(__file__))

OPTIONS = {
        # "antena-sur": "Antena Sur",
        # "bethel": "Bethel",
        "comas": "Comas FM",
        # "folk": "Folk Radio",
        "generacion-kpop": "Generación KPOP",
        "inolvidable": "La Inolvidable",
        "kalle": "La Kalle",
        "la-karibena": "La Karibeña",
        "la-zona": "La Zona",
        "matucana": "Matucana",
        "la-mega-lima": "MegaMix (Lima)",
        "moda": "Moda",
        "magica-lima": "Mágica",
        "nueva-q": "Nueva Q",
        # "nuevo-tiempo-peru": "Nuevo Tiempo Perú",
        "onda": "Onda Cero",
        "oxigeno": "Oxígeno (Lima)",
        "panamericana": "Panamericana",
        # "cumbia-lima": "Perú Cumbia Radio (Lima)",
        "planeta": "Planeta",
        # "corazon": "Radio Corazón",
        # "mas-91-9": "Radio Cumbia Mix",
        # "elite": "Radio Elite (Huaral)",
        "exitosa-lima": "Radio Exitosa (Lima)",
        "felicidad": "Radio Felicidad",
        "inca": "Radio Inca (Lima)",
        # "maranon": "Radio Marañón (Jaén)",
        # "maria": "Radio María",
        "melodia-arequipa": "Radio Melodía (Arequipa)",
        "nacional": "Radio Nacional",
        # "nova-trujillo": "Radio Nova (Trujillo)",
        # "ovacion-lima": "Radio Ovación (Lima)",
        "rpp": "Radio RPP Noticias",
        # "san-borja": "Radio San Borja (San Borja)",
        # "uno": "Radio Uno (Tacna)",
        # "z-lima": "Radio Z Rock Pop (Lima)",
        "exito-lima": "Radio Éxito (Lima)",
        # "radiomar": "Radiomar",
        "romantica": "Ritmo Romántica",
        # "integridad-lima": "RRI",
        "studio": "Studio 92 (San Isidro)",
        # "turbo": "Turbo Mix",
        "viva": "Viva FM",
    }
SELECT_OPTIONS = [discord.SelectOption(label=v, value=k) for k, v in OPTIONS.items()]
print(len(SELECT_OPTIONS))
class RadioView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.radio_selected = None
    
    @discord.ui.select(placeholder="Choose a radio station", min_values=1, max_values=1, options=SELECT_OPTIONS)
    async def select_callback(self, interaction, select: discord.ui.Select):
        self.radio_selected = interaction.data["values"][0]
        self.stop()
        await interaction.message.delete()
    
class MiscellaneousCommands(MixinMeta, metaclass=CompositeMetaClass):

    @commands.command(name="playradio")
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def command_play_radio(self, ctx: commands.Context):
        """Play a radio station."""
        
        view = RadioView()
        await ctx.send("", view=view)
        await view.wait()
        radio = view.radio_selected

        if radio is None:
            return await self.send_embed_msg(ctx, title="Unable To Play Radio",description="No radio station selected.")
        await self.send_embed_msg(ctx, title=f"Playing radio station {OPTIONS[radio]}")

        from cloudscraper import create_scraper
        r = create_scraper().get('https://api.instant.audio/data/streams/13/'+radio).json()
        if r["success"] == False:
            return await self.send_embed_msg(
                ctx,
                title="Unable To Play Radio",
                description=f"Failed to get radio station {radio}. Maybe it's no longer available.",
            )
        radio_name = r['result']['station']['title']

        for stream in r['result']['streams']:
            if stream["mime"] in ["audio/mpeg", "audio/aac"]:
                url = stream["url"]
        
        await ctx.invoke(self.command_bumpplay, query=url, play_now=True, radio_name=radio_name)

    @commands.command(name="lyrics")
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def command_lyrics(self, ctx: commands.Context):
        """Get the lyrics of the current song."""
        player = lavalink.get_player(ctx.guild.id)
        if player.current:
            if player.current.is_stream:
                return await self.send_embed_msg(ctx, title=_("This is a live stream."))
            else:
                title=player.current.title
                # remove parenthesis content from title, e.g: "title (feat. artist) title" -> "title title"
                import re
                title = re.sub(r'\(.*?\)', '', title).strip() 
                artist=player.current.author
                artist=re.sub(r'VEVO', '', artist).strip()
                from lyricsgenius import Genius
                from pykakasi import kakasi

                # call set api genius access_token <access_token>
                genius_access_token = await self.bot.get_shared_api_tokens("genius")
                genius_access_token = genius_access_token.get("access_token",None)
                if not genius_access_token:
                    return await self.send_embed_msg(
                        ctx,
                        title=_("Invalid Environment"),
                        description=_(
                            "The owner needs to set Genius access token."
                        ).format(prefix=ctx.prefix),
                    )

                genius = Genius(genius_access_token,verbose=False)
                song = genius.search_song(title, artist)
                if song is None:
                    song = genius.search_song(title)
                    if song is None:
                        return await self.send_embed_msg(ctx, title=_("Lyrics not found."))
                lyrics = song.lyrics
                
                kks = kakasi()
                import warnings
                warnings.filterwarnings('ignore')
                kks.setMode("H", "a")  # Hiragana to ascii, default: no conversion
                kks.setMode("K", "a")
                kks.setMode("J", "a")
                kks.setMode("r", "Hepburn")
                kks.setMode("s", True)
                kks.setMode("C", True)
                converter = kks.getConverter()
                lyrics = converter.do(lyrics)
                warnings.filterwarnings('default')
                lyrics = lyrics.split("Lyrics")[1]
                lyrics = re.sub(r'\d+Embed$', '', lyrics).strip()

                return await self.send_embed_msg(ctx, title=f"Lyrics for {title} by {artist}",description=lyrics, url=song.url)

        return await self.send_embed_msg(ctx, title=_("Nothing playing."))

    @commands.command(name="sing")
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def command_sing(self, ctx: commands.Context):
        """Make Red sing one of her songs."""
        ids = (
            "zGTkAVsrfg8",
            "cGMWL8cOeAU",
            "vFrjMq4aL-g",
            "WROI5WYBU_A",
            "41tIUr_ex3g",
            "f9O2Rjn1azc",
        )
        url = f"https://www.youtube.com/watch?v={random.choice(ids)}"
        await ctx.invoke(self.command_play, query=url)

    @commands.command(name="audiostats")
    @commands.guild_only()
    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.bot_can_react()
    async def command_audiostats(self, ctx: commands.Context):
        """Audio stats."""
        server_num = len(lavalink.active_players())
        total_num = len(lavalink.all_connected_players())

        msg = ""
        async for p in AsyncIter(lavalink.all_connected_players()):
            connect_dur = (
                self.get_time_string(
                    int(
                        (
                            datetime.datetime.now(datetime.timezone.utc) - p.connected_at
                        ).total_seconds()
                    )
                )
                or "0s"
            )
            try:
                if not p.current:
                    raise AttributeError
                current_title = await self.get_track_description(
                    p.current, self.local_folder_current_path
                )
                msg += f"{p.guild.name} [`{connect_dur}`]: {current_title}\n"
            except AttributeError:
                msg += "{} [`{}`]: **{}**\n".format(
                    p.guild.name, connect_dur, _("Nothing playing.")
                )

        if total_num == 0:
            return await self.send_embed_msg(ctx, title=_("Not connected anywhere."))
        servers_embed = []
        pages = 1
        for page in pagify(msg, delims=["\n"], page_length=1500):
            em = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("Playing in {num}/{total} servers:").format(
                    num=humanize_number(server_num), total=humanize_number(total_num)
                ),
                description=page,
            )
            em.set_footer(
                text=_("Page {}/{}").format(
                    humanize_number(pages), humanize_number((math.ceil(len(msg) / 1500)))
                )
            )
            pages += 1
            servers_embed.append(em)

        await menu(ctx, servers_embed)

    @commands.command(name="percent")
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def command_percent(self, ctx: commands.Context):
        """Queue percentage."""
        if not self._player_check(ctx):
            return await self.send_embed_msg(ctx, title=_("Nothing playing."))
        player = lavalink.get_player(ctx.guild.id)
        queue_tracks = player.queue
        requesters = {"total": 0, "users": {}}

        async def _usercount(req_user_handle):
            if req_user_handle in requesters["users"]:
                requesters["users"][req_user_handle]["songcount"] += 1
                requesters["total"] += 1
            else:
                requesters["users"][req_user_handle] = {}
                requesters["users"][req_user_handle]["songcount"] = 1
                requesters["total"] += 1

        async for track in AsyncIter(queue_tracks):
            req_user_handle = str(track.requester)
            await _usercount(req_user_handle)

        try:
            req_user_handle = str(player.current.requester)
            await _usercount(req_user_handle)
        except AttributeError:
            return await self.send_embed_msg(ctx, title=_("There's nothing in the queue."))

        async for req_user_handle in AsyncIter(requesters["users"]):
            percentage = float(requesters["users"][req_user_handle]["songcount"]) / float(
                requesters["total"]
            )
            requesters["users"][req_user_handle]["percent"] = round(percentage * 100, 1)

        top_queue_users = heapq.nlargest(
            20,
            [
                (x, requesters["users"][x][y])
                for x in requesters["users"]
                for y in requesters["users"][x]
                if y == "percent"
            ],
            key=lambda x: x[1],
        )
        queue_user = ["{}: {:g}%".format(x[0], x[1]) for x in top_queue_users]
        queue_user_list = "\n".join(queue_user)
        await self.send_embed_msg(
            ctx, title=_("Queued and playing tracks:"), description=queue_user_list
        )
