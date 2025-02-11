import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import glob
import pickle
import json
import matplotlib.pyplot as plt
import io
import csv
from datetime import datetime
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import math

# Load environment variables
load_dotenv()

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Alliance ID to name mapping
ALLIANCE_NAMES = {
    "0": "Dragon Fire",
    "1": "Dragon Claw",
    "2": "Demons",
    "3": "Free Time Fun",
    "4": "44444",
    "5": "55555",
    "6": "Zible Believers",
    # Add more alliances as needed
}


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    await bot.change_presence(activity=discord.Game(name="processing Zalenia data!"))


@bot.command(
    name="ping",
    description="Check bot's latency",
    brief="Check bot latency",
    usage="!ping",
    help="Returns the bot's current latency in milliseconds.\n\n"
         "Example: !ping"
)
async def ping(ctx):
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")


@bot.command(
    name="inteladd",
    description="Add intel about a city",
    brief="Add intel for coordinates",
    usage="<x> <y> <message>",
    help="Adds intel information for a city at the specified coordinates.\n\n"
         "Parameters:\n"
         "- x: X coordinate of the city\n"
         "- y: Y coordinate of the city\n"
         "- message: The intel information to store\n\n"
         "Example: !inteladd 100 200 Strong castle with T5 troops"
)
async def inteladd(ctx, xcoord: int, ycoord: int, *, message: str):
    intel_file = "D:/ZaleniaData/cityintel.json"

    # Load existing intel
    try:
        with open(intel_file, "r") as f:
            cityintel = json.load(f)
    except FileNotFoundError:
        cityintel = {}

    # Create key from coordinates
    key = f"{xcoord},{ycoord}"

    # Add new intel with timestamp
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cityintel[key] = {
        "message": message,
        "added_on": current_datetime,
        "added_by": str(ctx.author),
    }

    # Save updated intel
    with open(intel_file, "w") as f:
        json.dump(cityintel, f, indent=4)

    await ctx.send(f"Intel added for coordinates ({xcoord}, {ycoord}): {message}")


@bot.command(
    name="intel",
    description="Get intel about a city at specific coordinates",
    brief="Get intel for a city",
    usage="<x> <y>",
    help="Retrieves stored intel information for a city at the specified coordinates.\n\n"
         "Parameters:\n"
         "- x: X coordinate of the city\n"
         "- y: Y coordinate of the city\n\n"
         "Example: !intel 100 200"
)
async def intel(ctx, xcoord: int, ycoord: int):
    intel_file = "D:/ZaleniaData/cityintel.json"

    # Load existing intel
    try:
        with open(intel_file, "r") as f:
            cityintel = json.load(f)
    except FileNotFoundError:
        await ctx.send("No intel data found.")
        return

    # Create key from coordinates
    key = f"{xcoord},{ycoord}"

    if key in cityintel:
        intel_data = cityintel[key]
        message = intel_data["message"]
        added_on = intel_data["added_on"]
        added_by = intel_data["added_by"]

        response = f"Intel for coordinates ({xcoord}, {ycoord}):\n"
        response += f"Message: {message}\n"
        response += f"Added on: {added_on}\n"
        response += f"Added by: {added_by}"

        await ctx.send(response)
    else:
        await ctx.send(f"No intel found for coordinates ({xcoord}, {ycoord}).")


@bot.command(
    name="inteldelete",
    description="Delete intel about a city at specific coordinates",
    brief="Delete intel for a city",
    usage="<x> <y>",
    help="Deletes stored intel information for a city at the specified coordinates.\n\n"
         "Parameters:\n"
         "- x: X coordinate of the city\n"
         "- y: Y coordinate of the city\n\n"
         "Example: !inteldelete 100 200"
)
async def inteldelete(ctx, xcoord: int, ycoord: int):
    intel_file = "D:/ZaleniaData/cityintel.json"

    # Load existing intel
    try:
        with open(intel_file, "r") as f:
            cityintel = json.load(f)
    except FileNotFoundError:
        await ctx.send("No intel data found.")
        return

    # Create key from coordinates
    key = f"{xcoord},{ycoord}"

    if key in cityintel:
        del cityintel[key]

        # Save updated intel
        with open(intel_file, "w") as f:
            json.dump(cityintel, f, indent=4)

        await ctx.send(f"Intel for coordinates ({xcoord}, {ycoord}) has been deleted.")
    else:
        await ctx.send(f"No intel found for coordinates ({xcoord}, {ycoord}).")


@bot.command(
    name="intelcsv",
    description="Export all intel data to a CSV file",
    brief="Export intel to CSV",
    usage="!intelcsv",
    help="Exports all stored intel data to a CSV file, including city coordinates, owners, and intel information.\n\n"
         "Example: !intelcsv"
)
async def intelcsv(ctx):
    intel_file = "D:/ZaleniaData/cityintel.json"
    csv_file = "D:/ZaleniaData/cityintel_export.csv"

    try:
        # Load existing intel
        with open(intel_file, "r") as f:
            cityintel = json.load(f)

        # Load the latest world data
        latest_data_file = max(
            glob.glob("D:/ZaleniaData/WorldData/*"), key=os.path.getctime
        )
        with open(latest_data_file, "rb") as fp:
            latest_world_data = pickle.load(fp)

        # Load the latest player data
        latest_player_data_file = max(
            glob.glob("D:/ZaleniaData/PlayerData/*"), key=os.path.getctime
        )
        with open(latest_player_data_file, "rb") as fp:
            player_data = pickle.load(fp)

        # Create a dictionary to map playerGuid to username
        if isinstance(player_data, list):
            player_guid_to_name = {
                player["playerGuid"]: player["username"]
                for player in player_data
                if "playerGuid" in player and "username" in player
            }
        elif isinstance(player_data, dict) and "players" in player_data:
            player_guid_to_name = {
                player["playerGuid"]: player["username"]
                for player in player_data["players"]
                if "playerGuid" in player and "username" in player
            }
        else:
            player_guid_to_name = {}

        # Create dictionaries to map coordinates to city owner and continent
        city_owner_map = {}
        city_continent_map = {}
        for continent in latest_world_data["continents"]:
            cont_id = continent["continentIdentifier"]  # Get the continent ID
            for city in continent["cities"]:
                coords = f"{city['locationX']},{city['locationY']}"
                owner_guid = city["playerGuid"]
                owner_name = player_guid_to_name.get(owner_guid, owner_guid)
                city_owner_map[coords] = owner_name
                city_continent_map[coords] = cont_id  # Store just the continent ID

        # Prepare CSV file
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["X", "Y", "Coordinates", "Continent", "City Owner", "Intel", "Timestamp", "Added By"]
            )

            # Write data
            for key, value in cityintel.items():
                x, y = key.split(",")
                formatted_coords = f"({x}:{y})"
                continent = city_continent_map.get(key, "Unknown")  # This should now be just the continent number
                owner = city_owner_map.get(key, "Unknown")
                
                if isinstance(value, dict):
                    writer.writerow(
                        [
                            x,
                            y,
                            formatted_coords,
                            continent,  # This should now show correctly
                            owner,
                            value.get("message", ""),
                            value.get("added_on", ""),
                            value.get("added_by", ""),
                        ]
                    )
                elif isinstance(value, list):
                    for intel_entry in value:
                        if isinstance(intel_entry, dict):
                            writer.writerow(
                                [
                                    x,
                                    y,
                                    formatted_coords,
                                    continent,
                                    owner,
                                    intel_entry.get("intel", intel_entry.get("message", "")),
                                    intel_entry.get("timestamp", intel_entry.get("added_on", "")),
                                    intel_entry.get("added_by", ""),
                                ]
                            )
                        else:
                            print(f"Skipping invalid intel entry for {key}: {intel_entry}")
                else:
                    print(f"Skipping invalid value for {key}: {value}")

        # Send the CSV file
        await ctx.send("Intel data exported to CSV.", file=discord.File(csv_file))

    except FileNotFoundError:
        await ctx.send("No intel data found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        print(f"Error details: {e}")


# TODO, add in a way to see total monuments for each alliance etc
@bot.command(
    name="monuments",
    description="Count total monuments",
    brief="Count of all monuments",
    usage="[continent]",
    help="Displays a count of monuments by type for the specified continent or all continents.\n\n"
         "Parameters:\n"
         "- continent: (Optional) Specific continent to check. Defaults to 'All Conts'\n\n"
         "Example: !monuments\n"
         "Example: !monuments C1"
)
async def monuments(ctx, contaskedfor="All Conts"):
    data_file_list = []
    for name in glob.glob("D:/ZaleniaData/WorldData/*"):
        data_file_list.append(name)
    data_file_list.sort(reverse=True)

    with open(data_file_list[0], "rb") as fp:
        world_data = pickle.load(fp)

    monument_counts = {
        "Type 0": 0,
        "Type 1": 0,
        "Type 2": 0,
        "Type 3": 0,
        "Type 4": 0,
        "Type 5": 0,
    }
    for cont_data in world_data["continents"]:
        if (
            contaskedfor == "All Conts"
            or cont_data["continentIdentifier"] == contaskedfor
        ):
            for city_data in cont_data["cities"]:
                if city_data["hasMonument"]:
                    monument_type = city_data["monumentType"]
                    if monument_type == 0:
                        monument_counts["Fire"] += 1
                    elif 1 <= monument_type <= 5:
                        monument_counts[f"Type {monument_type}"] += 1

    total_monuments = sum(monument_counts.values())

    embed = discord.Embed(
        title=f"Monument Count on {contaskedfor}",
        description=f"Total Monuments: {total_monuments}",
        color=discord.Color.blue(),
    )

    for monument_name, count in monument_counts.items():
        embed.add_field(
            name=f"{monument_name} Monuments", value=str(count), inline=True
        )

    file = discord.File("images-files/boticon.png")
    embed.set_thumbnail(url="attachment://boticon.png")

    await ctx.send(embed=embed, file=file)


@bot.command(
    name="citiesflipped",
    description="Check cities that have changed ownership",
    brief="Cities that have flipped",
    aliases=["flipped"],
    usage="[days]",
    help="Shows cities that have changed ownership within the specified number of days.\n\n"
         "Parameters:\n"
         "- days: (Optional) Number of days to look back. Defaults to 1\n\n"
         "Example: !citiesflipped\n"
         "Example: !citiesflipped 3"
)
async def citiesflipped(ctx, days=1):
    try:
        # Load the latest world data
        latest_data_file = max(
            glob.glob("D:/ZaleniaData/WorldData/*"), key=os.path.getctime
        )
        with open(latest_data_file, "rb") as fp:
            latest_world_data = pickle.load(fp)

        # Load the world data from 'days' ago (4 files per day)
        files_to_go_back = 4 * int(days)
        all_data_files = sorted(
            glob.glob("D:/ZaleniaData/WorldData/*"), key=os.path.getctime, reverse=True
        )
        if len(all_data_files) <= files_to_go_back:
            await ctx.send(
                f"Not enough historical data available for {days} day(s) ago."
            )
            return
        past_data_file = all_data_files[files_to_go_back]
        with open(past_data_file, "rb") as fp:
            past_world_data = pickle.load(fp)

        # Load the latest player data
        latest_player_data_file = max(
            glob.glob("D:/ZaleniaData/PlayerData/*"), key=os.path.getctime
        )
        with open(latest_player_data_file, "rb") as fp:
            player_data = pickle.load(fp)

        # Create dictionaries to map playerGuid to username and alliance
        player_guid_to_name = {}
        player_guid_to_alliance = {}
        if isinstance(player_data, list):
            for player in player_data:
                if "playerGuid" in player and "username" in player:
                    player_guid_to_name[player["playerGuid"]] = player["username"]
                    player_guid_to_alliance[player["playerGuid"]] = player.get(
                        "allianceId", -1
                    )
        elif isinstance(player_data, dict) and "players" in player_data:
            for player in player_data["players"]:
                if "playerGuid" in player and "username" in player:
                    player_guid_to_name[player["playerGuid"]] = player["username"]
                    player_guid_to_alliance[player["playerGuid"]] = player.get(
                        "allianceId", -1
                    )

        flipped_cities = []

        # Compare the two datasets
        for latest_cont, past_cont in zip(
            latest_world_data["continents"], past_world_data["continents"]
        ):
            for latest_city, past_city in zip(
                latest_cont["cities"], past_cont["cities"]
            ):
                if (
                    latest_city["cityGuid"] == past_city["cityGuid"]
                    and latest_city["playerGuid"] != past_city["playerGuid"]
                ):
                    old_alliance_id = player_guid_to_alliance.get(
                        past_city["playerGuid"], -1
                    )
                    new_alliance_id = player_guid_to_alliance.get(
                        latest_city["playerGuid"], -1
                    )
                    flipped_cities.append(
                        {
                            "name": latest_city["name"],
                            "continent": latest_cont["continentIdentifier"],
                            "coords": f"({latest_city['locationX']}, {latest_city['locationY']})",
                            "old_owner": player_guid_to_name.get(
                                past_city["playerGuid"], past_city["playerGuid"]
                            ),
                            "new_owner": player_guid_to_name.get(
                                latest_city["playerGuid"], latest_city["playerGuid"]
                            ),
                            "old_alliance": ALLIANCE_NAMES.get(
                                str(old_alliance_id), "Unknown Alliance"
                            ),
                            "new_alliance": ALLIANCE_NAMES.get(
                                str(new_alliance_id), "Unknown Alliance"
                            ),
                        }
                    )

        if flipped_cities:
            embed = discord.Embed(
                title=f"Cities Flipped in Last {days} Day(s)",
                description=f"Total: {len(flipped_cities)}",
                color=discord.Color.blue(),
            )
            city_lines = [
                f"{c['continent']} {c['coords']} {c['old_alliance']} > {c['new_alliance']}"
                for c in flipped_cities[:25]
            ]
            embed.add_field(
                name="Flipped Cities", value="\n".join(city_lines), inline=False
            )
            if len(flipped_cities) > 25:
                embed.set_footer(
                    text=f"Showing 25/{len(flipped_cities)} flipped cities."
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No cities flipped in last {days} day(s).")

    except Exception as e:
        import traceback

        traceback.print_exc()
        await ctx.send(f"An error occurred: {str(e)}")


@bot.command(
    name="playerscore",
    description="Chart player scores over time",
    brief="Chart player scores",
    usage="<player1> [player2] [player3] ...",
    help="Generates a chart showing score progression for specified players over the last 3 days.\n\n"
         "Parameters:\n"
         "- player1: Name of first player to track\n"
         "- player2, player3, etc: (Optional) Additional players to compare\n\n"
         "Example: !playerscore PlayerOne\n"
         "Example: !playerscore PlayerOne PlayerTwo PlayerThree"
)
async def playerscore(ctx, *player_names):
    try:
        if not player_names:
            await ctx.send("Please specify at least one player name.")
            return

        # Convert all input player names to lowercase
        player_names = [name.lower() for name in player_names]

        player_data_files = sorted(
            glob.glob("D:/ZaleniaData/PlayerData/*"), key=os.path.getmtime, reverse=True
        )

        days = 3
        # Calculate the number of files to use (4 times per day)
        files_to_use = min(days * 4, len(player_data_files))
        player_data_files = player_data_files[:files_to_use]

        player_scores = {name: [] for name in player_names}
        dates = []

        for file_path in reversed(player_data_files):
            with open(file_path, "rb") as fp:
                player_data = pickle.load(fp)

            file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            dates.append(file_date)

            if isinstance(player_data, list):
                players = player_data
            elif isinstance(player_data, dict) and "players" in player_data:
                players = player_data["players"]
            else:
                continue

            for player in players:
                # Convert player username to lowercase for comparison
                if player["username"].lower() in player_names:
                    player_scores[player["username"].lower()].append(player["score"])

        plt.figure(figsize=(15, 10))
        players_with_data = []
        for name, scores in player_scores.items():
            if scores:  # Only plot if we have data for this player
                plt.plot(dates, scores, label=name, marker="o")
                players_with_data.append(name)
            else:
                await ctx.send(f"No data found for player: {name}")

        plt.title(
            f"Player Scores Over the Last {days} Days ({len(players_with_data)}/{len(player_names)} players)"
        )
        plt.xlabel("Date and Time")
        plt.ylabel("Score")

        # Calculate percentage increase and update legend labels
        legend_labels = []
        for name, scores in player_scores.items():
            if scores:
                first_score = scores[0]
                last_score = scores[-1]
                percent_increase = ((last_score - first_score) / first_score) * 100
                legend_labels.append(f"{name} (+{percent_increase:.2f}%)")
            else:
                legend_labels.append(name)

        plt.legend(
            legend_labels, loc="upper left"
        )  # Place legend in the upper left corner
        plt.grid(True)

        # Format y-axis to show full numbers
        def format_func(value, tick_number):
            return f"{int(value):,}"

        plt.gca().yaxis.set_major_formatter(FuncFormatter(format_func))

        # Format x-axis to show full date and time
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))

        # Rotate and align the tick labels so they look better
        plt.gcf().autofmt_xdate(rotation=45)

        # Use a tight layout
        plt.tight_layout()

        # Save the plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        # Send the plot as a file
        await ctx.send(file=discord.File(buf, filename="player_scores.png"))

    except Exception as e:
        import traceback

        traceback.print_exc()
        await ctx.send(f"An error occurred: {str(e)}")


@bot.command(
    name="logisticcalc",
    description="Calculate logistics capacity based on number of ships/carts and round-trip time",
    brief="Calculate logistics capacity",
    usage="<vehicles> <hours> <minutes>",
    help="Calculates the logistics capacity and resources per hour based on vehicle count and trip time.\n\n"
         "Parameters:\n"
         "- vehicles: Number of ships/carts\n"
         "- hours: Hours for one-way trip\n"
         "- minutes: Minutes for one-way trip\n\n"
         "Example: !logisticcalc 10 2 30"
)
async def logisticcalc(ctx, vehicles: int, hours: int, mins: int):
    try:
        # Convert time to hours for one-way trip
        one_way_hours = hours + (mins / 60)

        # Calculate total round-trip time
        total_hours = one_way_hours * 2

        # Calculate total resources that can be moved
        total_resources = vehicles * 1000

        # Calculate resources per hour (accounting for round trip)
        resources_per_hour = total_resources / total_hours if total_hours > 0 else 0

        # Prepare the response message
        response = (
            f"With {vehicles} ships/carts over a {hours} hour and {mins} minute 1 way trip:\n"
            f"Total resources that can be moved: {total_resources:,}\n"
            f"Resources per hour (accounting for return trip time): {resources_per_hour:,.2f}"
        )

        await ctx.send(response)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


@bot.command(
    name="alliancescore",
    description="Compare the total score of the top 5 alliances",
    brief="Compare top 5 alliance scores",
    usage="[continent]",
    help="Shows total score, member count, and average score for the top 5 alliances.\n\n"
         "Parameters:\n"
         "- continent: (Optional) Specific continent to analyze\n\n"
         "Example: !alliancescore\n"
         "Example: !alliancescore C1"
)
async def alliancescore(ctx, continent: str = None):
    try:
        # Load the latest player data
        latest_player_data_file = max(
            glob.glob("D:/ZaleniaData/PlayerData/*"), key=os.path.getctime
        )
        with open(latest_player_data_file, "rb") as fp:
            player_data = pickle.load(fp)

        # Load the latest world data
        latest_world_data_file = max(
            glob.glob("D:/ZaleniaData/WorldData/*"), key=os.path.getctime
        )
        with open(latest_world_data_file, "rb") as fp:
            world_data = pickle.load(fp)

        alliance_score = {}
        alliance_members = {}

        if isinstance(player_data, list):
            players = player_data
        elif isinstance(player_data, dict) and "players" in player_data:
            players = player_data["players"]
        else:
            await ctx.send("Unable to process player data.")
            return

        player_alliance_dict = {
            player["playerGuid"]: str(player.get("allianceId", -1))
            for player in players
        }

        for cont_data in world_data["continents"]:
            if continent is None or cont_data["continentIdentifier"] == continent:
                for city_data in cont_data["cities"]:
                    player_guid = city_data["playerGuid"]
                    alliance_id = player_alliance_dict.get(player_guid, "-1")
                    if alliance_id != "-1":
                        if alliance_id not in alliance_score:
                            alliance_score[alliance_id] = 0
                            alliance_members[alliance_id] = set()
                        alliance_score[alliance_id] += city_data.get("score", 0)
                        alliance_members[alliance_id].add(player_guid)

        # Sort alliances by total score and get top 5
        sorted_alliances = sorted(
            alliance_score.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Create embed
        embed = discord.Embed(
            title=f"Top 5 Alliance Score Comparison{' on Continent ' + continent if continent else ''}",
            color=discord.Color.blue(),
        )

        for alliance_id, total_score in sorted_alliances:
            alliance_name = ALLIANCE_NAMES.get(alliance_id, f"Alliance {alliance_id}")
            member_count = len(alliance_members[alliance_id])
            avg_score = total_score / member_count if member_count > 0 else 0

            embed.add_field(
                name=alliance_name,
                value=f"Total Score: {total_score:,}\n"
                f"Members: {member_count}\n"
                f"Avg Score: {avg_score:,.2f}",
                inline=False,
            )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


@bot.command(
    name="attackplanner",
    description="List castles of the same alliance as the city at given coordinates",
    brief="List alliance castles near coordinates",
    usage="<x> <y>",
    help="Generates a CSV file listing all castles belonging to the same alliance as the target coordinates.\n\n"
         "Parameters:\n"
         "- x: X coordinate of the target city\n"
         "- y: Y coordinate of the target city\n\n"
         "Example: !attackplanner 100 200"
)
async def attackplanner(ctx, xcoord: int, ycoord: int):
    try:
        # Load the latest world data
        latest_world_data_file = max(
            glob.glob("D:/ZaleniaData/WorldData/*"), key=os.path.getctime
        )
        with open(latest_world_data_file, "rb") as fp:
            world_data = pickle.load(fp)

        # Load the latest player data
        latest_player_data_file = max(
            glob.glob("D:/ZaleniaData/PlayerData/*"), key=os.path.getctime
        )
        with open(latest_player_data_file, "rb") as fp:
            player_data = pickle.load(fp)

        # Create player_alliance_dict and player_name_dict
        if isinstance(player_data, list):
            players = player_data
        elif isinstance(player_data, dict) and "players" in player_data:
            players = player_data["players"]
        else:
            await ctx.send("Unable to process player data.")
            return

        player_alliance_dict = {
            player["playerGuid"]: str(player.get("allianceId", -1))
            for player in players
        }
        
        player_name_dict = {
            player["playerGuid"]: player["username"]
            for player in players
        }

        # Calculate total score for each player
        player_total_score = {}
        for cont_data in world_data["continents"]:
            for city_data in cont_data["cities"]:
                player_guid = city_data["playerGuid"]
                if player_guid not in player_total_score:
                    player_total_score[player_guid] = 0
                player_total_score[player_guid] += city_data.get("score", 0)

        # Find the continent and alliance of the given coordinates
        target_continent = None
        target_alliance = None
        for cont_data in world_data["continents"]:
            for city_data in cont_data["cities"]:
                if (
                    city_data["locationX"] == xcoord
                    and city_data["locationY"] == ycoord
                ):
                    target_continent = cont_data
                    player_guid = city_data["playerGuid"]
                    target_alliance = player_alliance_dict.get(player_guid)
                    break
            if target_continent:
                break

        if not target_continent or not target_alliance:
            await ctx.send(f"No city found at coordinates ({xcoord}, {ycoord})")
            return

        castles = []
        for city_data in cont_data["cities"]:
            if (
                city_data["isCastle"]
                and player_alliance_dict.get(city_data["playerGuid"]) == target_alliance
            ):
                player_guid = city_data["playerGuid"]
                distance = (
                    (city_data["locationX"] - xcoord) ** 2
                    + (city_data["locationY"] - ycoord) ** 2
                ) ** 0.5
                
                # Determine special features
                features = []
                if city_data.get("hasMonument", False):
                    monument_type = city_data.get("monumentType", "Unknown")
                    features.append(f"Monument Type {monument_type}")
                if city_data.get("isWaterCity", False):
                    features.append("Water Castle")
                
                features_str = ", ".join(features) if features else ""
                
                castles.append(
                    [
                        city_data["locationX"],
                        city_data["locationY"],
                        f"({city_data['locationX']}:{city_data['locationY']})",
                        cont_data["continentIdentifier"],
                        city_data["name"],
                        player_name_dict.get(player_guid, "Unknown"),
                        city_data["score"],
                        player_total_score.get(player_guid, 0),
                        round(distance, 2),
                        features_str
                    ]
                )

        if not castles:
            await ctx.send(
                f"No castles from the same alliance found near ({xcoord}, {ycoord})"
            )
            return

        # Sort castles by distance
        castles.sort(key=lambda x: x[8])

        # Create and save CSV file
        filename = f"alliance_castles_{target_continent['continentIdentifier']}.csv"
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "X", "Y", "Coordinates", "Continent", "City Name", 
                "Owner Name", "City Score", "Owner Total Score", "Distance", "Special Features"
            ])
            writer.writerows(castles)

        # Send the CSV file
        file = discord.File(filename)
        await ctx.send(
            f"Castles of the same alliance on continent {target_continent['continentIdentifier']}, sorted by distance from ({xcoord}, {ycoord}):",
            file=file,
        )

        # Clean up the file
        os.remove(filename)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


@bot.command(
    name="altar",
    description="List cities and castles by distance from provided altar coordinates",
    brief="List cities/castles near altar",
    usage="<x> <y> [radius]",
    help="Generates a CSV file listing all cities and castles within the specified radius of the altar.\n\n"
         "Parameters:\n"
         "- x: X coordinate of the altar\n"
         "- y: Y coordinate of the altar\n"
         "- radius: (Optional) Search radius in tiles. Defaults to 6\n\n"
         "Example: !altar 100 200\n"
         "Example: !altar 100 200 10"
)
async def altar(ctx, x: int, y: int, radius: int = 6):
    try:
        # Load the latest world data
        latest_world_data_file = max(
            glob.glob("D:/ZaleniaData/WorldData/*"), key=os.path.getctime
        )
        with open(latest_world_data_file, "rb") as fp:
            world_data = pickle.load(fp)

        # Load the latest player data
        latest_player_data_file = max(
            glob.glob("D:/ZaleniaData/PlayerData/*"), key=os.path.getctime
        )
        with open(latest_player_data_file, "rb") as fp:
            player_data = pickle.load(fp)

        # Create dictionaries to map playerGuid to alliance
        player_guid_to_alliance = {}
        if isinstance(player_data, list):
            for player in player_data:
                if "playerGuid" in player and "allianceId" in player:
                    player_guid_to_alliance[player["playerGuid"]] = ALLIANCE_NAMES.get(
                        str(player["allianceId"]), "Unknown"
                    )
        elif isinstance(player_data, dict) and "players" in player_data:
            for player in player_data["players"]:
                if "playerGuid" in player and "allianceId" in player:
                    player_guid_to_alliance[player["playerGuid"]] = ALLIANCE_NAMES.get(
                        str(player["allianceId"]), "Unknown"
                    )

        # Find the continent of the given coordinates
        target_continent = None
        for cont_data in world_data["continents"]:
            for city in cont_data["cities"]:
                if city["locationX"] == x and city["locationY"] == y:
                    target_continent = cont_data
                    break
            if target_continent:
                break

        if not target_continent:
            await ctx.send(f"No continent found for altar coordinates ({x}, {y})")
            return

        # Generate surroundings data (only cities and castles)
        surroundings_data = []
        for city in target_continent["cities"]:
            dx = city["locationX"] - x
            dy = city["locationY"] - y
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= radius:
                tile_type = "Castle" if city["isCastle"] else "City"
                alliance = player_guid_to_alliance.get(city["playerGuid"], "Unknown")
                surroundings_data.append(
                    [
                        city["locationX"],
                        city["locationY"],
                        tile_type,
                        city["name"],
                        alliance,
                        round(distance, 2),
                    ]
                )

        # Sort by distance
        surroundings_data.sort(key=lambda x: x[5])

        # Create and save CSV file
        filename = f"altar_surroundings_{x}_{y}_r{radius}.csv"
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["X", "Y", "Type", "Name", "Alliance", "Distance"])
            writer.writerows(surroundings_data)

        # Send the CSV file
        file = discord.File(filename)
        await ctx.send(
            f"Cities and castles within radius {radius} of altar at ({x}, {y}):",
            file=file,
        )

        # Clean up the file
        os.remove(filename)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))