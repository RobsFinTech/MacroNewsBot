import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup
import datetime

TOKEN = ''
CHANNEL_ID =   # Replace with your channel ID

intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    check_events.start()

def get_upcoming_events():
    url = "https://www.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract forex events
    events = soup.find_all('tr', class_='js-event-item')
    upcoming_events = []

    for event in events:
        event_datetime_str = event['data-event-datetime']
        event_datetime = datetime.datetime.strptime(event_datetime_str, '%Y/%m/%d %H:%M:%S')
        time_diff = event_datetime - datetime.datetime.now()

        # If the event is 5 minutes away
        if 0 < time_diff.total_seconds() <= 300:
            time = event.find('td', class_='time').get_text().strip()
            country = event.find('td', class_='flagCur').get_text().strip()
            event_name = event.find('td', class_='event').get_text().strip()

            # # Extracting volatility (counting the number of bull icons)
            volatility_bulls = event.find_all('td', class_='grayFullBullishIcon')
            volatility_count = len(volatility_bulls)
            
            if volatility_count == 3:
                volatility = "<:red_circle:>"  # Red dot for high volatility
            elif volatility_count == 2:
                volatility = ':yellow_circle:'  # Yellow dot for medium volatility
            elif volatility_count == 1:
                volatility = ':green_circle:'  # Green dot for low volatility
            else:
                volatility = ""  # Empty for no volatility

            upcoming_events.append(f'{volatility} - {time} - {country} - {event_name}')

    return upcoming_events

@tasks.loop(minutes=5)
async def check_events():
    channel = client.get_channel(CHANNEL_ID)
    events = get_upcoming_events()
    
    for event in events:
        embed = discord.Embed(title="Upcoming Economic Event in 5 Minutes", url="https://google.com", description=event, color=0xFF9900)
        #embed.add_field(name="Actual", value=f"{event['actual']}", inline=True)
        #embed.add_field(name="Forecast", value=f"{event['forecast']}", inline=True)
        embed.set_footer(icon_url="https://yt3.googleusercontent.com/9rB5TtR3DcGfXC5dJbhmc1nPIPaOeZl33viPEWBn-MjbqCFAOzW18DhcqQnD_r8YHCVAzOgePA=s176-c-k-c0x00ffffff-no-rj" ,text="© 2023, AdexTrades LLC | Not a Financial Advisor | #Playbothsides")
        await channel.send(embed=embed)

client.run(TOKEN)