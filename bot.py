import discord
from discord.ext import commands, tasks
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# ============ LOAD TOKEN ============
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN not found!")
    print("Please add DISCORD_TOKEN as a Secret in Replit")
    exit(1)

print(f"✅ Token loaded successfully")

# ============ BOT SETUP ============
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

CHANNEL_ID = None
DB_FILE = 'posted_opportunities.json'

# ============ DATABASE FUNCTIONS ============
def load_posted():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_opportunity(title, link, opp_type, deadline=None):
    posted = load_posted()
    posted.append({
        'title': title,
        'link': link,
        'type': opp_type,
        'deadline': deadline,
        'posted_at': datetime.now().isoformat()
    })
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(posted, f, indent=2)

def is_new_opportunity(link):
    posted = load_posted()
    return not any(opp.get('link') == link for opp in posted)

# ============ SCRAPING FUNCTIONS ============
def scrape_unstop():
    """Scrape from Unstop - Most reliable for Indian opportunities"""
    opportunities = []
    try:
        print("  🔍 Scraping Unstop...")
        url = "https://unstop.com/hackathons"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all opportunity cards
        cards = soup.find_all('div', {'class': re.compile('.*challenge.*|.*opportunity.*')})

        for card in cards[:15]:
            try:
                title_tag = card.find(['h2', 'h3', 'h4', 'a'])
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                link_tag = card.find('a', href=True)
                if link_tag:
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = 'https://unstop.com' + link
                else:
                    continue

                if link and title:
                    opportunities.append({
                        'title': title[:150],
                        'link': link,
                        'type': 'Hackathon/Competition',
                        'source': 'Unstop',
                        'deadline': None
                    })
            except Exception as e:
                continue

        print(f"  ✅ Found {len(opportunities)} on Unstop")
    except Exception as e:
        print(f"  ❌ Error scraping Unstop: {e}")

    return opportunities

def scrape_devpost():
    """Scrape from Devpost - Global hackathons"""
    opportunities = []
    try:
        print("  🔍 Scraping Devpost...")
        url = "https://devpost.com/hackathons?category=upcoming"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        hackathons = soup.find_all('div', {'class': re.compile('.*challenge.*')})

        for hack in hackathons[:15]:
            try:
                title_tag = hack.find(['h2', 'h3', 'a'])
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                link_tag = hack.find('a', href=True)
                if link_tag:
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = 'https://devpost.com' + link
                else:
                    continue

                if link and title and 'devpost' in link:
                    opportunities.append({
                        'title': title[:150],
                        'link': link,
                        'type': 'Hackathon',
                        'source': 'Devpost',
                        'deadline': None
                    })
            except Exception as e:
                continue

        print(f"  ✅ Found {len(opportunities)} on Devpost")
    except Exception as e:
        print(f"  ❌ Error scraping Devpost: {e}")

    return opportunities

def scrape_internshala():
    """Scrape from Internshala - Best for Indian internships"""
    opportunities = []
    try:
        print("  🔍 Scraping Internshala...")
        url = "https://internshala.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        listings = soup.find_all(['div', 'article'], {'class': re.compile('.*internship.*|.*listing.*')})

        for listing in listings[:15]:
            try:
                title_tag = listing.find(['h2', 'h3', 'h4', 'a'])
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                link_tag = listing.find('a', href=True)
                if link_tag:
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = 'https://internshala.com' + link
                else:
                    continue

                if link and title:
                    opportunities.append({
                        'title': title[:150],
                        'link': link,
                        'type': 'Internship',
                        'source': 'Internshala',
                        'deadline': None
                    })
            except Exception as e:
                continue

        print(f"  ✅ Found {len(opportunities)} on Internshala")
    except Exception as e:
        print(f"  ❌ Error scraping Internshala: {e}")

    return opportunities

def scrape_angel_list():
    """Scrape from AngelList - Startups & jobs"""
    opportunities = []
    try:
        print("  🔍 Scraping AngelList...")
        url = "https://wellfound.com/jobs"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        jobs = soup.find_all(['div', 'article'], {'class': re.compile('.*job.*|.*listing.*')})

        for job in jobs[:10]:
            try:
                title_tag = job.find(['h2', 'h3', 'h4', 'a'])
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                link_tag = job.find('a', href=True)
                if link_tag:
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = 'https://wellfound.com' + link
                else:
                    continue

                if link and title:
                    opportunities.append({
                        'title': title[:150],
                        'link': link,
                        'type': 'Job/Startup',
                        'source': 'AngelList',
                        'deadline': None
                    })
            except Exception as e:
                continue

        print(f"  ✅ Found {len(opportunities)} on AngelList")
    except Exception as e:
        print(f"  ❌ Error scraping AngelList: {e}")

    return opportunities

def get_all_opportunities():
    """Fetch from all sources"""
    print("📡 Fetching opportunities...")
    all_opps = []

    try:
        all_opps.extend(scrape_unstop())
    except:
        pass

    try:
        all_opps.extend(scrape_devpost())
    except:
        pass

    try:
        all_opps.extend(scrape_internshala())
    except:
        pass

    try:
        all_opps.extend(scrape_angel_list())
    except:
        pass

    # Remove duplicates based on link
    seen = set()
    unique_opps = []
    for opp in all_opps:
        if opp['link'] not in seen:
            seen.add(opp['link'])
            unique_opps.append(opp)

    print(f"📊 Total: {len(unique_opps)} unique opportunities found\n")
    return unique_opps

# ============ BOT EVENTS ============
@bot.event
async def on_ready():
    print(f'\n{"="*50}')
    print(f'✅ Bot is ONLINE!')
    print(f'Bot Name: {bot.user}')
    print(f'Connected to {len(bot.guilds)} server(s)')
    print(f'{"="*50}\n')

    if not check_opportunities.is_running():
        check_opportunities.start()
        print('✅ Scheduled checker started (checks every 2 hours)')

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {str(error)}")

# ============ SCHEDULED TASK ============
@tasks.loop(hours=2)
async def check_opportunities():
    if CHANNEL_ID is None:
        return

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    print("⏰ Scheduled check running...")
    opportunities = get_all_opportunities()
    new_count = 0

    for opp in opportunities:
        if is_new_opportunity(opp['link']):
            try:
                embed = discord.Embed(
                    title=f"🎯 {opp['title']}",
                    url=opp['link'],
                    description=f"**Type:** {opp['type']}\n**Source:** {opp['source']}",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Apply now!")

                await channel.send(embed=embed)
                save_opportunity(opp['title'], opp['link'], opp['type'])
                new_count += 1
            except:
                pass

@check_opportunities.before_loop
async def before_check():
    await bot.wait_until_ready()

# ============ BOT COMMANDS ============
@bot.command(name='setchannel')
async def set_channel(ctx):
    global CHANNEL_ID
    CHANNEL_ID = ctx.channel.id
    embed = discord.Embed(
        title="✅ Channel Set!",
        description=f"Opportunities will be posted in {ctx.channel.mention}",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name='fetch')
async def fetch_opportunities(ctx):
    await ctx.send("🔍 Searching for opportunities... (This may take a moment)")
    opps = get_all_opportunities()

    if not opps:
        await ctx.send("❌ No opportunities found. Please try again later.")
        return

    sent_count = 0
    max_show = min(15, len(opps))

    for opp in opps[:max_show]:
        try:
            embed = discord.Embed(
                title=f"🎯 {opp['title']}",
                url=opp['link'],
                description=f"**Type:** {opp['type']}\n**Source:** {opp['source']}",
                color=discord.Color.purple()
            )
            embed.set_footer(text="Click the title to apply!")
            await ctx.send(embed=embed)
            sent_count += 1
        except:
            pass

    await ctx.send(f"\n✅ Displayed {sent_count} opportunities!")

@bot.command(name='status')
async def status(ctx):
    embed = discord.Embed(title="🤖 Bot Status", color=discord.Color.gold())
    embed.add_field(
        name="Alert Channel",
        value=f"<#{CHANNEL_ID}>" if CHANNEL_ID else "❌ Not set - Use !setchannel",
        inline=False
    )
    embed.add_field(
        name="Opportunities Tracked",
        value=str(len(load_posted())),
        inline=True
    )
    embed.add_field(
        name="Bot Status",
        value="🟢 Online and Running",
        inline=True
    )
    embed.add_field(
        name="Sources",
        value="Unstop, Devpost, Internshala, AngelList",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_cmd(ctx):
    embed = discord.Embed(title="📚 Available Commands", color=discord.Color.blue())
    embed.add_field(name="!fetch", value="Show all current opportunities", inline=False)
    embed.add_field(name="!setchannel", value="Set channel for automatic alerts", inline=False)
    embed.add_field(name="!status", value="Check bot status", inline=False)
    embed.add_field(name="!help", value="Show this message", inline=False)
    embed.set_footer(text="Bot checks every 2 hours automatically")
    await ctx.send(embed=embed)

# ============ RUN BOT ============
if __name__ == "__main__":
    try:
        print("Starting bot...\n")
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Error: {e}")
