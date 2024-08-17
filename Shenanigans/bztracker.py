import shiny
from shiny import App, ui, reactive, render
import requests
import pandas as pd
from datetime import datetime, timezone

# Function to fetch data from Hypixel API
def get_bazaar_data():
    url = "https://api.hypixel.net/v2/skyblock/bazaar"
    response = requests.get(url)
    data = response.json()
    return data

# Function to extract and process quick status from the data
def extract_quick_status(data):
    products = data["products"]
    status_list = []
    
    for product_id, details in products.items():
        # Skip items starting with "ENCHANTMENT"
        if product_id.startswith("ENCHANTMENT"):
            continue
        
        quick_status = details["quick_status"]
        buy_price = quick_status['buyPrice']
        sell_price = quick_status['sellPrice']
        flip_profit = buy_price - sell_price
        
        status_list.append({
            "Item ID": quick_status["productId"],
            "Buy Price": f"{buy_price:.2f}",
            "Sell Price": f"{sell_price:.2f}",
            "Buy Volume": quick_status["buyVolume"],
            "Sell Volume": quick_status["sellVolume"],
            "Flip Profit": f"{flip_profit:.2f}"
        })
    
    # Convert to DataFrame and sort by Flip Profit from most to least
    df = pd.DataFrame(status_list)
    df["Flip Profit"] = df["Flip Profit"].astype(float)
    df = df.sort_values(by="Flip Profit", ascending=False)
    
    return df

# Shiny UI
app_ui = ui.page_fluid(
    ui.panel_title(ui.h1("Hypixel Skyblock Bazaar Tracker", style="text-align: center; margin-bottom: 30px;")),
    ui.div(
        ui.input_action_button("refresh", "Refresh Data", class_="btn btn-primary"),
        style="text-align: center; margin-bottom: 20px;"
    ),
    ui.div(
        ui.output_ui("bazaar_table"),
        style="max-width: 900px; margin: 0 auto; border: 2px solid #ccc; padding: 20px; border-radius: 8px; background-color: #f9f9f9;"
    ),
    ui.div(
        ui.output_text("last_updated", container=ui.h6),
        style="text-align: center; margin-top: 10px;"
    ),
    style="background-color: #FFFFFF; padding: 20px;"
)

# Shiny server
def server(input, output, session):

    # Reactive value to store item data and last update time
    data_store = reactive.Value(extract_quick_status(get_bazaar_data()))
    last_update_time = reactive.Value(datetime.now(timezone.utc).strftime('%I:%M %p UTC'))

    # Fetch data when the refresh button is clicked
    @reactive.Effect
    @reactive.event(input.refresh)
    def on_refresh():
        data_store.set(extract_quick_status(get_bazaar_data()))
        last_update_time.set(datetime.now(timezone.utc).strftime('%I:%M %p UTC'))

    # Render the last updated time
    @output
    @render.text
    def last_updated():
        return f"Last Updated: {last_update_time.get()}"

    # Render the bazaar table
    @output
    @render.ui
    def bazaar_table():
        df = data_store.get()
        # Render the table as HTML with the proper layout and styles
        return ui.HTML(df.to_html(index=False, escape=False, justify='center', classes='table table-striped table-hover'))

# Run the app
app = App(app_ui, server)
shiny.run_app(app)
