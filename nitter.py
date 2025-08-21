# cogs/nitter_rss.py
import os
import json
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

import discord
from discord.ext import tasks, commands
import feedparser

log = logging.getLogger(__name__)

DEFAULT_RSS_URL = "https://nitter.kuuro.net/nenewatch52681/rss"

def _load_state(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text("utf-8"))
        except Exception:
            log.warning("State file corrupted; starting fresh.")
    return {"seen_ids": [], "etag": None, "modified": None, "channel_id": None}

def _save_state(path: Path, state: Dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), "utf-8")
    tmp.replace(path)

def _format_embed(entry: Any) -> discord.Embed:
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()
    published = entry.get("published", "")
    # Basic embed; tweak as you like
    emb = discord.Embed(title="New Tweet", description=title)
    if published:
        emb.set_footer(text=published)
    if link:
        emb.url = link
    return emb

class NitterRSSCog(commands.Cog):
    """Poll a Nitter RSS feed and emit events / post to a channel."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # --- Config via env (or override by commands) ---
        self.rss_url: str = os.getenv("RSS_URL", DEFAULT_RSS_URL)
        self.poll_seconds: int = int(os.getenv("POLL_SECONDS", "60"))
        self.state_file = Path(os.getenv("STATE_FILE", "nitter_state.json"))

        # --- State ---
        self.state = _load_state(self.state_file)
        self.seen_ids = set(self.state.get("seen_ids", []))
        self._etag: Optional[str] = self.state.get("etag")
        self._modified = self.state.get("modified")

        # Optional preconfigured channel id
        self.channel_id: Optional[int] = self.state.get("channel_id") or (
            int(os.getenv("CHANNEL_ID", "0")) or None
        )

        # Task
        self.poll_feed.start()

    def cog_unload(self):
        self.poll_feed.cancel()

    @tasks.loop(seconds=1.0)  # replaced at runtime in before_loop
    async def poll_feed(self):
        """Main polling loop."""
        try:
            # Respect conditional GET using feedparser
            parsed = feedparser.parse(
                self.rss_url,
                etag=self._etag,
                modified=self._modified,
                request_headers={"User-Agent": "nitter-rss-discord-cog/1.0"},
            )

            status = getattr(parsed, "status", None)

            # Update etag/modified if present
            new_etag = getattr(parsed, "etag", None)
            new_modified = getattr(parsed, "modified", None)

            if status == 304:
                # Not modified
                return

            if status and status >= 400:
                log.warning(f"HTTP {status} from RSS feed; will retry later.")
                return

            entries: List[Any] = parsed.entries or []
            fresh = [e for e in entries if e.get("id") not in self.seen_ids]

            if fresh:
                # Process oldest first so your channel reads top-down in time
                for e in reversed(fresh):
                    # Mark as seen
                    if e.get("id"):
                        self.seen_ids.add(e["id"])

                    # Dispatch custom event for other cogs / listeners
                    self.bot.dispatch("nitter_tweet", e)

                    # Optionally post to a configured channel
                    if self.channel_id:
                        channel = self.bot.get_channel(self.channel_id)
                        if channel and isinstance(channel, (discord.TextChannel, discord.Thread)):
                            try:
                                await channel.send(embed=_format_embed(e))
                            except Exception as ex:
                                log.warning(f"Failed to post to channel {self.channel_id}: {ex}")

                # Persist trimmed state
                self.state["seen_ids"] = list(self.seen_ids)[-1000:]
                self.state["etag"] = new_etag
                self.state["modified"] = new_modified
                _save_state(self.state_file, self.state)
                self._etag, self._modified = new_etag, new_modified

        except Exception as ex:
            log.warning(f"Error polling RSS: {ex}")

    @poll_feed.before_loop
    async def before_poll(self):
        # Reconfigure the loop interval dynamically
        self.poll_feed.change_interval(seconds=self.poll_seconds)
        await self.bot.wait_until_ready()
        log.info(f"NitterRSSCog polling {self.rss_url} every {self.poll_seconds}s.")

    # ----- Commands -----

    @commands.command(name="nitterset")
    @commands.has_guild_permissions(manage_guild=True)
    async def nitter_set_channel(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        """
        Set the channel for automatic tweet posts.
        Usage: !nitterset #some-channel
        If omitted, uses the current channel.
        """
        target = channel or ctx.channel
        self.channel_id = target.id
        self.state["channel_id"] = self.channel_id
        _save_state(self.state_file, self.state)
        await ctx.send(f"✅ Tweets will be posted in {target.mention}")

    @commands.command(name="nittersource")
    @commands.has_guild_permissions(manage_guild=True)
    async def nitter_set_source(self, ctx: commands.Context, rss_url: str):
        """
        Change the RSS URL (e.g., switch Nitter instance or user).
        Usage: !nittersource https://nitter.net/<user>/rss
        """
        self.rss_url = rss_url.strip()
        await ctx.send(f"🔁 RSS source set to: {self.rss_url}")

    @commands.command(name="nitterping")
    async def nitter_ping(self, ctx: commands.Context):
        """Quick health check."""
        await ctx.send(f"NitterRSSCog is alive. Polling: {self.rss_url} every {self.poll_seconds}s.")

async def setup(bot: commands.Bot):
    await bot.add_cog(NitterRSSCog(bot))
