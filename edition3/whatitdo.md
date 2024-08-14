### Imports and Dependencies

```python
import shiny
from shiny import App, ui, reactive, render
import requests
import pandas as pd
from datetime import datetime, timezone
```

- **shiny:** A framework for building interactive web applications in Python.
- **requests:** A library to make HTTP requests, used here for interacting with external APIs.
- **pandas:** A powerful data manipulation library used for creating data structures like DataFrames.
- **datetime and timezone:** Modules for working with date and time, particularly to ensure timezone awareness.

### Configuration

```python
ITEM_IDS = [19721, 19976, 24283, 24289, 19701]
```

- **ITEM_IDS:** A list of item IDs used to fetch data from the Guild Wars 2 (GW2) APIs.

```python
ITEMS_ENDPOINT = "https://api.guildwars2.com/v2/items/"
PRICES_ENDPOINT = "https://api.guildwars2.com/v2/commerce/prices/"
HISTORY_ENDPOINT = "https://api.datawars2.ie/gw2/v1/history?itemID="
```

- **API Endpoints:** URLs for accessing GW2 API resources, including item details, prices, and historical price data.

### Helper Functions

```python
def format_price(price_in_copper):
```

- **format_price:** Converts a price in copper units into a string formatted as Gold/Silver/Copper.

```python
def fetch_30_entry_average(item_id):
```

- **fetch_30_entry_average:** Fetches the last 30 entries of historical price data for a given item and calculates the average price. It handles errors and ensures datetime entries are timezone-aware.

```python
def calculate_price_difference(current_price, average_price_30d):
```

- **calculate_price_difference:** Computes the difference between the current price and the 30-day average price, then formats this difference correctly based on sign (profit/loss).

```python
def fetch_item_data(item_id):
```

- **fetch_item_data:** Fetches item details and pricing information from the GW2 API. It calculates the profit/loss compared to the 30-day average and formats the results for display.

### Data Handling

```python
def get_sorted_items_data():
```

- **get_sorted_items_data:** Collects and sorts data for all item IDs based on the current price (highest to lowest). It structures the data into a DataFrame for easier manipulation and display.

### User Interface (UI)

```python
app_ui = ui.page_fluid(
```

- **app_ui:** Defines the layout and design of the Shiny application, including the title, refresh button, data table, and last updated time. The UI uses HTML and CSS styling to ensure proper formatting and responsiveness.

### Server Logic

```python
def server(input, output, session):
```

- **server:** Contains the reactive logic for the Shiny app, handling data updates and rendering components.

```python
data_store = reactive.Value(get_sorted_items_data())
last_update_time = reactive.Value(datetime.now(timezone.utc).strftime('%I:%M %p UTC'))
```

- **Reactive Values:** `data_store` and `last_update_time` are reactive values that store the item data and the timestamp of the last update.

```python
@reactive.Effect
@reactive.event(input.refresh)
def on_refresh():
```

- **Reactive Effect:** Triggers a data refresh and updates the last updated time when the user clicks the refresh button.

```python
@output
@render.text
def last_updated():
```

- **Render Output:** Renders the last updated time as a text element in the UI.

```python
@output
@render.ui
def item_table():
```

- **Render UI:** Renders the item data table as an HTML element, using `pandas` to generate the table layout.

### Running the App

```python
app = App(app_ui, server)
shiny.run_app(app)
```

- **App Instance:** Initializes the Shiny app with the defined UI and server logic.
- **Run App:** Executes the Shiny app, making it accessible via a web browser.
