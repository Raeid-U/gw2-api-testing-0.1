import shiny
from shiny import App, ui, reactive, render
import requests
import pandas as pd
from datetime import datetime

# Define the item IDs
ITEM_IDS = [19721, 19976, 24283, 24289, 19701]

# API Endpoints
ITEMS_ENDPOINT = "https://api.guildwars2.com/v2/items/"
PRICES_ENDPOINT = "https://api.guildwars2.com/v2/commerce/prices/"

# Function to format price as G/S/C (Gold/Silver/Copper)
def format_price(price_in_copper):
    gold = price_in_copper // 10000
    silver = (price_in_copper % 10000) // 100
    copper = price_in_copper % 100
    return f"{gold}G {silver}S {copper}C"

# Function to fetch item data from the GuildWars2 API
def fetch_item_data(item_id):
    try:
        item_response = requests.get(f"{ITEMS_ENDPOINT}{item_id}").json()
        price_response = requests.get(f"{PRICES_ENDPOINT}{item_id}").json()
        item_data = {
            "ID": item_id,
            "Name": item_response.get("name", "Unknown"),
            "PriceRaw": price_response.get("buys", {}).get("unit_price", 0)  # Store raw price for sorting
        }
        item_data["Price"] = format_price(item_data["PriceRaw"])  # Format price after sorting
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
app_ui = ui.page_fluid(
    ui.panel_title(ui.h1("Guild Wars 2 - Price Tracker", style="text-align: center; margin-bottom: 30px;")),
    ui.div(
        ui.input_action_button("refresh", "Refresh Data", class_="btn btn-primary"),
        style="text-align: center; margin-bottom: 20px;"
    ),
    ui.div(
        ui.output_ui("item_table"),
        style="max-width: 900px; margin: 0 auto; border: 2px solid #ccc; padding: 20px; border-radius: 8px; background-color: #f9f9f9;"
    ),
    ui.div(
        ui.output_text("last_updated", container=ui.h6),
        style="text-align: center; margin-top: 10px;"
    ),
    style="background-color: #FFFFFF; padding: 20px;"
)

# Shiny Server
def server(input, output, session):

    # Reactive value to store item data and last update time
    data_store = reactive.Value(get_sorted_items_data())
    last_update_time = reactive.Value(datetime.now().strftime('%I:%M %p'))

    # Fetch data when the refresh button is clicked
    @reactive.Effect
    @reactive.event(input.refresh)
    def on_refresh():
        data_store.set(get_sorted_items_data())
        last_update_time.set(datetime.now().strftime('%I:%M %p'))

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
        return ui.HTML(df.to_html(index=False, escape=False, justify='center', classes='table table-striped table-hover'))

# Run the app
app = App(app_ui, server)
shiny.run_app(app)
