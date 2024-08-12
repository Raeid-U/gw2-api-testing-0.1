import shiny
from shiny import App, ui, reactive
import requests
import pandas as pd

# Define the item IDs
ITEM_IDS = [19721, 19976, 24283, 24289, 19701]

# API Endpoints
ITEMS_ENDPOINT = "https://api.guildwars2.com/v2/items/"
PRICES_ENDPOINT = "https://api.guildwars2.com/v2/commerce/prices/"

# Function to fetch item data from the GuildWars2 API
def fetch_item_data(item_id):
    item_url = f"{ITEMS_ENDPOINT}{item_id}"
    price_url = f"{PRICES_ENDPOINT}{item_id}"

    item_response = requests.get(item_url).json()
    price_response = requests.get(price_url).json()

    # Combine item information with the current price
    item_data = {
        "ID": item_id,
        "Name": item_response.get("name", "Unknown"),
        "Description": item_response.get("description", "No description"),
        "Price": price_response.get("buys", {}).get("unit_price", 0) / 100.0  # Convert to gold
    }
    return item_data

# Function to fetch data for all item IDs and sort by price
def get_sorted_items_data():
    data = [fetch_item_data(item_id) for item_id in ITEM_IDS]
    sorted_data = sorted(data, key=lambda x: x["Price"])
    return pd.DataFrame(sorted_data)

# Shiny UI
app_ui = ui.page_fluid(
    ui.panel_title("GuildWars2 Item Price Viewer"),
    ui.output_text("last_updated", container=ui.h4),  # Changed ID to 'last_updated'
    ui.output_table("item_table"),
    ui.input_action_button("refresh", "Refresh Data")
)

# Shiny Server
def server(input, output, session):
    
    @reactive.Calc
    def item_data():
        return get_sorted_items_data()
    
    @output
    @reactive.event(input.refresh)
    def last_updated():
        return f"Last Updated: {pd.Timestamp.now()}"
    
    @output
    @reactive.event(input.refresh)
    def item_table():
        return item_data().to_dict("records")
    
# Run the app
app = App(app_ui, server)

# To run the app, use the following:
shiny.run_app(app)
