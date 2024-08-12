import shiny
from shiny import App, ui, reactive, render
import requests
import pandas as pd

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
        item_url = f"{ITEMS_ENDPOINT}{item_id}"
        price_url = f"{PRICES_ENDPOINT}{item_id}"

        item_response = requests.get(item_url, timeout=5).json()
        price_response = requests.get(price_url, timeout=5).json()

        # Combine item information with the current price
        item_data = {
            "ID": item_id,
            "Name": item_response.get("name", "Unknown"),
            "Description": item_response.get("description", "No description"),
            "Price": format_price(price_response.get("buys", {}).get("unit_price", 0))
        }
        return item_data
    except Exception as e:
        print(f"Error fetching data for item ID {item_id}: {e}")
        return None

# Function to fetch data for all item IDs and sort by price
def get_sorted_items_data(sort_order):
    data = [fetch_item_data(item_id) for item_id in ITEM_IDS]
    # Filter out any None values (in case of errors)
    data = [d for d in data if d is not None]
    sorted_data = sorted(data, key=lambda x: x["Price"], reverse=sort_order == 'desc')
    return pd.DataFrame(sorted_data)

# Shiny UI
app_ui = ui.page_fluid(
    ui.panel_title(ui.h1("Guild Wars 2 - Price Tracker", style="text-align: center; margin-bottom: 30px;")),
    ui.div(
        ui.div(
            ui.input_action_button("refresh", "Refresh Data", class_="btn btn-primary"),
            ui.input_radio_buttons("sort_order", "Sort Order", choices={"asc": "Low to High", "desc": "High to Low"}, inline=True, selected='desc'),
            style="text-align: center; margin-bottom: 20px;"
        ),
        ui.div(
            ui.output_table("item_table"),
            style="width: 100%; margin: 0 auto; border: 1px solid #ccc; padding: 20px; border-radius: 8px; background-color: #f9f9f9;"
        ),
        ui.div(
            ui.output_text("last_updated", container=ui.h6),
            style="text-align: center; margin-top: 10px;"
        ),
        style="max-width: 900px; margin: 0 auto;"
    ),
    style="background-color: #f1f1f1; padding: 20px;"
)

# Shiny Server
def server(input, output, session):

    @reactive.Calc
    def item_data():
        sort_order = input.sort_order() or 'desc'
        return get_sorted_items_data(sort_order)

    @output
    @render.text
    @reactive.event(input.refresh)
    def last_updated():
        return f"Last Updated: {pd.Timestamp.now().strftime('%I:%M %p')}"

    @output
    @render.table
    @reactive.event(input.refresh, input.sort_order)
    def item_table():
        df = item_data()
        df.style.set_properties(subset=['Price'], **{'white-space': 'nowrap'})
        return df

# Run the app
app = App(app_ui, server)
shiny.run_app(app)
