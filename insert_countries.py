import os
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv
import json
import ssl


load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=True)

db = client.flaggame
collection = db.countries

def fetch_country_data():
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print('Something went wrong')
        return []

def transform_country_data(raw_data):
    countries = []
    for country in raw_data:
        print(country.get("name").get("common"))
        countries.append({
            "name": country.get("name").get("common"),
            "flag": country.get("flags").get("png"),
            "code": country.get("cca2", ""),
            "region": country.get("region", "Unknown"),
            "subregion": country.get("subregion", "Unknown")
        })
    return countries

async def update_svg_flags():
    country_data = fetch_country_data()

    for country in country_data:
        name = country.get("name").get("common")
        svg_flag = country.get("flags").get("svg")

        if name and svg_flag:
            result = await collection.update_one(
                {"name": name},
                {"$set": {"flag_svg": svg_flag}}
            )
            if result.matched_count > 0:
                print("updated")
            else:
                print("something went wrong")

async def update_countries():
    country_data = fetch_country_data()
    # print(json.dumps(country_data[0], indent=4))

    for country in country_data:
        name = country.get("name").get("common")
        official_name = country.get("name").get("official")
        independent = country.get("independent")    
        un_member = country.get("unMember")
        capital = country.get("capital")
        landlocked = country.get("landlocked")
        area = country.get("area")
        google_map = country.get("maps").get("googleMaps")
        openstreet_map = country.get("maps").get("openStreetMaps")
        population = country.get("population")
        drive_side = country.get("car").get("side")

        print(official_name, independent, un_member, capital, landlocked, area, google_map, openstreet_map, population, drive_side)

        if (official_name):
            result = await collection.update_one(
                {"name": name},
                {"$set": {
                    "official_name": official_name,
                    "independent": independent,
                    "un_member": un_member,
                    "capital": capital,
                    "landlocked": landlocked,
                    "area": area,
                    "google_map": google_map,
                    "openstreet_map": openstreet_map,
                    "population": population,
                    "drive_side": drive_side
                }}
            )
            if result.matched_count > 0:
                print("updated")
            else:
                print("something went wrong")

    # for country in country_data:
        # print(country)

asyncio.run(update_countries())

async def insert_countries():
    raw_data = fetch_country_data()
    country_data = transform_country_data(raw_data)
    print("inserting")
    if country_data:
        result = await collection.insert_many(country_data)
        print(f"Inserted {len(result.inserted_ids)} countries into MongoDB.")
    else:
        print("No country data to insert")

# asyncio.run(insert_countries())
# asyncio.run(update_svg_flags())