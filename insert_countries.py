import os
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(mongo_uri)

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
asyncio.run(update_svg_flags())