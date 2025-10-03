# Traveloka Transportation Price Data Mining Tool

A comprehensive Python script for mining transportation price data from [Traveloka.com](https://www.traveloka.com/), including flights, car rentals, and airport transfers.

## Features

- **Flight Price Mining**: Extract flight prices for domestic and international routes
- **Car Rental Price Mining**: Gather car rental pricing data for major cities
- **Airport Transfer Mining**: Collect airport transfer service prices
- **Data Export**: Save all mined data to CSV files with timestamps
- **Price Analysis**: Generate detailed price analysis reports
- **Rate Limiting**: Built-in delays to respect website resources
- **Comprehensive Logging**: Track all mining activities and errors

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the script files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the complete data mining process:

```bash
python traveloka_price_miner.py
```

### What the Script Does

1. **Flight Price Mining**:
   - Searches popular domestic routes (Jakarta-Bali, Jakarta-Yogyakarta, etc.)
   - Searches international routes (Jakarta-Singapore, Jakarta-Bangkok, etc.)
   - Collects data for the next 3 days

2. **Car Rental Mining**:
   - Searches major Indonesian cities (Jakarta, Bali, Surabaya, Yogyakarta)
   - Collects pricing for 3-day rental periods
   - Covers various car types and providers

3. **Airport Transfer Mining**:
   - Searches airport to city center transfers
   - Covers major airports (CGK, DPS, SUB, etc.)
   - Different vehicle types and service providers

## Output Files

The script generates several output files with timestamps:

### CSV Data Files
- `traveloka_flights_YYYYMMDD_HHMMSS.csv` - Flight price data
- `traveloka_car_rentals_YYYYMMDD_HHMMSS.csv` - Car rental price data
- `traveloka_transfers_YYYYMMDD_HHMMSS.csv` - Airport transfer price data

### Analysis Reports
- `traveloka_price_analysis_YYYYMMDD_HHMMSS.txt` - Price analysis summary
- `traveloka_mining.log` - Detailed mining logs

## Data Structure

### Flight Data
- Origin/Destination airports
- Departure/Return dates
- Airline information
- Price in IDR
- Flight duration and timing
- Number of stops

### Car Rental Data
- Pickup/Return locations and dates
- Car type and provider
- Daily and total pricing
- Vehicle specifications
- Passenger capacity

### Airport Transfer Data
- Pickup/Dropoff locations
- Transfer date and time
- Vehicle type and provider
- Price and duration
- Passenger capacity

## Configuration

### Customizable Parameters

You can modify the script to customize:

**Routes and Destinations**:
```python
# Edit popular_destinations in TravelokaPriceMiner.__init__()
self.popular_destinations = {
    'domestic': [
        ('CGK', 'DPS'),  # Add your preferred routes
        # ...
    ]
}
```

**Cities for Car Rentals**:
```python
# Edit cities list
self.cities = [
    'Jakarta', 'Bali', 'Surabaya'  # Add your preferred cities
]
```

**Date Range**:
```python
# In run_full_mining(), modify:
dates = self.get_future_dates(7)  # Change number of days
```

## Important Notes

### Legal and Ethical Considerations

1. **Respect Website Terms**: Always check and comply with Traveloka's Terms of Service
2. **Rate Limiting**: The script includes delays between requests to avoid overloading servers
3. **Data Usage**: Use mined data responsibly and in accordance with applicable laws
4. **Website Changes**: Traveloka may update their website structure, requiring script updates

### Technical Considerations

1. **Anti-Bot Measures**: Modern websites use sophisticated bot detection
2. **Dynamic Content**: Some content may be loaded via JavaScript (not captured by this script)
3. **Session Management**: The script maintains session cookies for consistency
4. **Error Handling**: Comprehensive error handling prevents crashes

### Limitations

1. **HTML Structure Dependency**: Script relies on current website structure
2. **Rate Limiting**: Mining speed is limited to prevent blocking
3. **Data Accuracy**: Prices may change rapidly; data represents point-in-time snapshots
4. **Regional Restrictions**: Some content may vary by geographic location

## Advanced Usage

### Custom Mining Functions

You can use individual mining functions:

```python
from traveloka_price_miner import TravelokaPriceMiner

miner = TravelokaPriceMiner()

# Mine specific routes
routes = [('CGK', 'DPS'), ('CGK', 'SIN')]
dates = ['2025-01-15', '2025-01-16']
flights = miner.mine_flight_prices(routes, dates)

# Mine specific cities
cities = ['Jakarta', 'Bali']
rentals = miner.mine_car_rental_prices(cities, dates)
```

### Data Analysis

The generated CSV files can be imported into:
- **Excel** for basic analysis
- **Python/Pandas** for advanced data science
- **R** for statistical analysis
- **Tableau/Power BI** for visualization

## Troubleshooting

### Common Issues

1. **Network Errors**: Check internet connection and website availability
2. **Parsing Errors**: Website structure may have changed
3. **Rate Limiting**: Increase delays if getting blocked
4. **Missing Data**: Some searches may return no results

### Debugging

Check the log file `traveloka_mining.log` for detailed error information:

```bash
tail -f traveloka_mining.log
```

## Contributing

To improve the script:

1. Update parsing logic for website changes
2. Add support for new transportation types
3. Enhance data analysis capabilities
4. Improve error handling and robustness

## Disclaimer

This tool is for educational and research purposes. Users are responsible for:
- Complying with website terms of service
- Respecting rate limits and server resources
- Using data ethically and legally
- Updating the script as needed for website changes

## License

This script is provided as-is for educational purposes. Use responsibly and in accordance with all applicable laws and website terms of service.

---

**Author**: Data Mining Script  
**Date**: 2025  
**Version**: 1.0  

For questions or issues, please review the code and logs for troubleshooting guidance. 