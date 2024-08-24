import shiny
from shiny import App, ui, reactive, render
import os
import requests
import pandas as pd
from datetime import datetime, timezone

# Define the item IDs
ITEM_IDS = [19721, 19976, 24283, 24289, 19701]

# API Endpoints
ITEMS_ENDPOINT = "https://api.guildwars2.com/v2/items/"
PRICES_ENDPOINT = "https://api.guildwars2.com/v2/commerce/prices/"
HISTORY_ENDPOINT = "https://api.datawars2.ie/gw2/v1/history?itemID="


# Function to format price as G/S/C (Gold/Silver/Copper)
def format_price(price_in_copper):
    gold = price_in_copper // 10000
    silver = (price_in_copper % 10000) // 100
    copper = price_in_copper % 100
    return f"{gold}G {silver}S {copper}C"


# Function to fetch 30-entry average price from the historical data API
def fetch_30_entry_average(item_id):
    try:
        history_response = requests.get(f"{HISTORY_ENDPOINT}{item_id}").json()

        # Ensure the datetime is timezone-aware
        for entry in history_response:
            entry["date"] = datetime.strptime(
                entry["date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).replace(tzinfo=timezone.utc)

        # Sort entries by date and get the last 30 entries
        history_response = sorted(
            history_response, key=lambda x: x["date"], reverse=True
        )[:30]

        # Extract the minimum sell prices
        prices = [
            entry["sell_price_min"]
            for entry in history_response
            if "sell_price_min" in entry
        ]

        # Calculate and round the average price
        return round(sum(prices) / len(prices)) if prices else 0
    except Exception as e:
        print(f"Error fetching 30-entry average for item ID {item_id}: {e}")
        return 0


# Function to calculate and format profit/loss correctly
def calculate_price_difference(current_price, average_price_30d):
    difference = current_price - average_price_30d

    # Determine the sign of the difference
    sign = -1 if difference < 0 else 1
    difference = abs(difference)

    gold = difference // 10000
    silver = (difference % 10000) // 100
    copper = difference % 100

    # Adjust for negative profit/loss
    formatted_difference = f"{sign * gold}G {sign * silver}S {sign * copper}C"

    return formatted_difference


# Function to fetch item data from the GuildWars2 API
def fetch_item_data(item_id):
    try:
        item_response = requests.get(f"{ITEMS_ENDPOINT}{item_id}").json()
        price_response = requests.get(f"{PRICES_ENDPOINT}{item_id}").json()
        current_price = price_response.get("buys", {}).get("unit_price", 0)
        average_price_30d = fetch_30_entry_average(item_id)
        price_difference = calculate_price_difference(current_price, average_price_30d)

        item_data = {
            "ID": item_id,
            "Name": item_response.get("name", "Unknown"),
            "PriceRaw": current_price,
            "Price": format_price(current_price),
            "Average Price (30 Day Avg)": format_price(average_price_30d),
            "Profit": price_difference,
        }
        return item_data
    except Exception as e:
        print(f"Error fetching data for item ID {item_id}: {e}")
        return None


# Function to fetch data for all item IDs and sort by raw price (highest to lowest)
def get_sorted_items_data():
    data = [fetch_item_data(item_id) for item_id in ITEM_IDS]
    data = [d for d in data if d is not None]
    sorted_data = sorted(data, key=lambda x: x["PriceRaw"], reverse=True)
    for item in sorted_data:
        item.pop("PriceRaw")  # Remove raw price after sorting
    return pd.DataFrame(sorted_data)


# Shiny UI
static_dir = os.path.join(os.path.dirname(__file__), "static")

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.script(src="https://unpkg.com/react@17/umd/react.development.js"),
        ui.tags.script(src="https://unpkg.com/react-dom@17/umd/react.development.js"),
        ui.tags.script(src="https://unpkg.com/babel-standalone@6/babel.min.js"),
        ui.tags.script(src="https://unpkg.com/react-planet@1.0.1/dist/index.umd.js"),
        ui.tags.link(rel="stylesheet", href="css/styles.css"),
        ui.tags.script(
            """
            function loadReactComponent() {
                var script = document.createElement('script');
                script.src = 'js/react_component.js';
                script.type = 'text/babel';
                document.body.appendChild(script);
            }
            window.onload = function() {
                console.log('Window loaded');
                if (typeof ReactPlanet !== 'undefined') {
                    console.log('ReactPlanet loaded');
                    loadReactComponent();
                } else {
                    console.error('ReactPlanet not loaded');
                }
            }
        """
        ),
    ),
    ui.tags.title("Guild Wars 2 - Price Tracker"),
    ui.panel_title(
        ui.h1(
            "Guild Wars 2 - Price Tracker",
            style="text-align: center; margin-bottom: 30px;",
        )
    ),
    ui.div(
        ui.HTML(
            '<div id="react-planet-root" style="height: 300px; border: 1px solid blue;"></div>'
        ),
        style="text-align: center; margin-bottom: 20px;",
    ),
    ui.div(
        ui.output_ui("item_table"),
        style="max-width: 900px; margin: 0 auto; border: 2px solid #ccc; padding: 20px; border-radius: 8px; background-color: #f9f9f9;",
    ),
    ui.div(
        ui.output_text("last_updated", container=ui.h6),
        style="text-align: center; margin-top: 10px;",
    ),
    style="background-color: #FFFFFF; padding: 20px;",
)


def server(input, output, session):
    # Reactive value to store item data and last update time
    data_store = reactive.Value(get_sorted_items_data())
    last_update_time = reactive.Value(
        datetime.now(timezone.utc).strftime("%I:%M %p UTC")
    )

    # Fetch data when the refresh button is clicked
    @reactive.Effect
    @reactive.event(input.refresh)
    def on_refresh():
        data_store.set(get_sorted_items_data())
        last_update_time.set(datetime.now(timezone.utc).strftime("%I:%M %p UTC"))

    # Render the last updated time
    @output
    @render.text
    def last_updated():
        return f"Last Updated: {last_update_time.get()}"

    # Render the item table
    @output
    @render.ui
    def item_table():
        df = data_store.get()
        # Render the table as HTML with the proper layout and styles
        return ui.HTML(
            df.to_html(
                index=False,
                escape=False,
                justify="center",
                classes="table table-striped table-hover",
            )
        )


# Run the App
app = App(app_ui, server, static_assets=static_dir)

if __name__ == "__main__":
    shiny.run_app(app)
