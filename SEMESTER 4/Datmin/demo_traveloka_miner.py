#!/usr/bin/env python3
"""
Demo script for Traveloka Price Mining

This script demonstrates how to use the Traveloka mining tools
with various configuration options.

Author: Data Mining Script
Date: 2025
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

def test_basic_mining():
    """Test the basic mining functionality"""
    print("🧪 Testing Basic Traveloka Mining...")
    
    try:
        # Import the basic miner
        from traveloka_price_miner import TravelokaPriceMiner
        
        # Create miner instance
        miner = TravelokaPriceMiner()
        
        # Test with a small sample
        test_routes = [('CGK', 'DPS')]  # Jakarta to Bali
        test_dates = [(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')]
        
        print(f"Testing route: {test_routes[0][0]} -> {test_routes[0][1]}")
        print(f"Testing date: {test_dates[0]}")
        
        # Mine flight data
        flights = miner.mine_flight_prices(test_routes, test_dates)
        
        print(f"✅ Basic mining test completed: {len(flights)} flights found")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in basic mining: {e}")
        return False

def test_advanced_mining():
    """Test the advanced mining functionality"""
    print("\n🚀 Testing Advanced Traveloka Mining...")
    
    try:
        # Import the advanced miner
        from traveloka_advanced_miner import AdvancedTravelokaMiner, SELENIUM_AVAILABLE
        
        if not SELENIUM_AVAILABLE:
            print("⚠️  Selenium not available - skipping advanced test")
            return False
        
        # Create advanced miner instance
        miner = AdvancedTravelokaMiner(use_selenium=True)
        
        # Test with a small sample
        test_route = {'from': 'CGK', 'to': 'DPS', 'name': 'Jakarta-Bali', 'distance': 1150}
        test_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        
        print(f"Testing advanced route: {test_route['from']} -> {test_route['to']}")
        print(f"Testing date: {test_date}")
        
        # Extract flight data using Selenium
        flights = miner.extract_flight_data_selenium(
            test_route['from'], 
            test_route['to'], 
            test_date
        )
        
        print(f"✅ Advanced mining test completed: {len(flights)} flights found")
        
        # Clean up
        if hasattr(miner, 'driver'):
            miner.driver.quit()
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in advanced mining: {e}")
        return False

def demo_custom_mining():
    """Demonstrate custom mining configurations"""
    print("\n⚙️  Demonstrating Custom Mining Configurations...")
    
    try:
        from traveloka_price_miner import TravelokaPriceMiner
        
        # Create custom miner
        miner = TravelokaPriceMiner()
        
        # Custom route configuration
        custom_routes = [
            ('CGK', 'JOG'),  # Jakarta to Yogyakarta
            ('SUB', 'CGK'),  # Surabaya to Jakarta
        ]
        
        # Custom date range (next 3 days)
        custom_dates = [
            (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') 
            for i in range(1, 4)
        ]
        
        print("Custom routes:", custom_routes)
        print("Custom dates:", custom_dates)
        
        # Mine with custom configuration
        flights = miner.mine_flight_prices(custom_routes, custom_dates[:1])  # Test with 1 date
        
        print(f"✅ Custom mining completed: {len(flights)} flights found")
        
        # Demonstrate car rental mining
        custom_cities = ['Jakarta', 'Bali']
        rentals = miner.mine_car_rental_prices(custom_cities, custom_dates[:1])
        
        print(f"✅ Car rental mining completed: {len(rentals)} rentals found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in custom mining: {e}")
        return False

def demo_data_analysis():
    """Demonstrate data analysis capabilities"""
    print("\n📊 Demonstrating Data Analysis...")
    
    # Create sample data for demonstration
    sample_data = {
        'origin': ['CGK', 'CGK', 'DPS', 'CGK', 'SUB'],
        'destination': ['DPS', 'JOG', 'CGK', 'SIN', 'CGK'],
        'airline': ['Garuda', 'Lion Air', 'Garuda', 'Singapore Airlines', 'Citilink'],
        'price': [1500000, 800000, 1600000, 3200000, 900000],
        'departure_date': ['2025-01-20', '2025-01-20', '2025-01-21', '2025-01-22', '2025-01-20']
    }
    
    df = pd.DataFrame(sample_data)
    
    print("Sample flight data:")
    print(df)
    
    # Basic analysis
    print(f"\nBasic Analysis:")
    print(f"Average price: IDR {df['price'].mean():,.0f}")
    print(f"Cheapest flight: IDR {df['price'].min():,.0f}")
    print(f"Most expensive flight: IDR {df['price'].max():,.0f}")
    
    # Price by airline
    print(f"\nPrice by airline:")
    airline_avg = df.groupby('airline')['price'].mean().sort_values()
    for airline, price in airline_avg.items():
        print(f"  {airline}: IDR {price:,.0f}")
    
    # Price by route
    print(f"\nPrice by route:")
    df['route'] = df['origin'] + '-' + df['destination']
    route_avg = df.groupby('route')['price'].mean().sort_values()
    for route, price in route_avg.items():
        print(f"  {route}: IDR {price:,.0f}")
    
    print("✅ Data analysis demo completed")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking Dependencies...")
    
    required_packages = [
        'requests', 'pandas', 'beautifulsoup4', 'lxml', 
        'fake_useragent', 'openpyxl'
    ]
    
    optional_packages = ['selenium']
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} (REQUIRED)")
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} (optional)")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️  {package} (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install " + ' '.join(missing_required))
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("Install with: pip install " + ' '.join(missing_optional))
    
    print("\n✅ All required dependencies are available")
    return True

def main():
    """Main demo function"""
    print("Traveloka Price Mining Demo")
    print("=" * 40)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before continuing")
        return
    
    # Run demos
    demos = [
        ("Basic Mining Test", test_basic_mining),
        ("Advanced Mining Test", test_advanced_mining),
        ("Custom Mining Demo", demo_custom_mining),
        ("Data Analysis Demo", demo_data_analysis),
    ]
    
    results = {}
    
    for name, demo_func in demos:
        print(f"\n{'='*50}")
        try:
            results[name] = demo_func()
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("DEMO SUMMARY")
    print(f"{'='*50}")
    
    for name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    successful = sum(results.values())
    total = len(results)
    
    print(f"\nOverall: {successful}/{total} demos passed")
    
    if successful == total:
        print("🎉 All demos completed successfully!")
        print("\nYou can now run:")
        print("  python traveloka_price_miner.py")
        print("  python traveloka_advanced_miner.py")
    else:
        print("⚠️  Some demos failed. Check the error messages above.")

if __name__ == "__main__":
    main() 