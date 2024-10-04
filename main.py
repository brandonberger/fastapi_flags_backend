import os
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

app = FastAPI()

# Mongo connection
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(mongo_uri)
db = client.flaggame
collection = db.countries

@app.get("/countries")
async def get_countries():
    countries = []
    async for country in collection.find():
        countries.append({
            "name": country["name"],
            "flag": country["flag_svg"],
            "code": country["code"],
            "region": country["region"],
            "subregion": country["subregion"]
        })
    return {"countries": countries}
