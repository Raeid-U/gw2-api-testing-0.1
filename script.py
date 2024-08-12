import shiny
from shiny import App, ui, reactive, render
import requests
import pandas as pd

# Define the item IDs
ITEM_IDS = [19721, 19976, 24283, 24289, 19701]

# API Foolishness
ITEMS_ENDPOINT = "https://api.guildwars2.com/v2/items/"
PRICES_ENDPOINT = "https://api.guildwars2.com/v2/commerce/prices/"

# Function to fetch item data from the GuildWars2 API
def fetch_item_data(item_id):
    try:
        item_url = f"{ITEMS_ENDPOINT}{item_id}"
        price_url = f"{PRICES_ENDPOINT}{item_id}"

        print(f"Fetching data for item ID: {item_id}")  # Debugging statement
        
        item_response = requests.get(item_url, timeout=5).json()
        price_response = requests.get(price_url, timeout=5).json()

        # Combine item information with the current price
        item_data = {
            "ID": item_id,
            "Name": item_response.get("name", "Unknown"),
            "Description": item_response.get("description", "No description"),
            "Price": price_response.get("buys", {}).get("unit_price", 0) / 100.0  # Convert to gold
        }
        return item_data
    except Exception as e:
        print(f"Error fetching data for item ID {item_id}: {e}")  # Error handling
        return None

# Function to fetch data for all item IDs and sort by price
def get_sorted_items_data():
    data = [fetch_item_data(item_id) for item_id in ITEM_IDS]
    data = [d for d in data if d is not None]
    sorted_data = sorted(data, key=lambda x: x["Price"])
    return pd.DataFrame(sorted_data)

# Shiny UI
app_ui = ui.page_fluid(
    ui.panel_title("GuildWars2 Item Price Viewer"),
    ui.output_text("last_updated", container=ui.h4),
    ui.output_table("item_table"),
    ui.input_action_button("refresh", "Refresh Data")
)

# Shiny Server
def server(input, output, session):
    
    @reactive.Calc
    def item_data():
        print("Fetching and sorting item data...")  # Debugging statement
        return get_sorted_items_data()
    
    @output
    @render.text 
    @reactive.event(input.refresh)
    def last_updated():
        print("Updating last updated timestamp...")  # Debugging statement
        return f"Last Updated: {pd.Timestamp.now()}"
    
    @output
    @render.table 
    @reactive.event(input.refresh)
    def item_table():
        print("Updating item table...")  # Debugging statement
        return item_data().to_dict("records")

# Run the app
app = App(app_ui, server)
shiny.run_app(app)
