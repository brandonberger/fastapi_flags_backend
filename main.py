import os
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mongo connection
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(mongo_uri)
db = client.flaggame
collection = db.countries
scores_collection = db.scores

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

# Score submission
class ScoreSubmission(BaseModel):
    name: str
    score: int


@app.get("/get-scores")
async def get_scores():
    scores = []
    async for entry in scores_collection.find().sort("score", -1):
        scores.append({
            "name": entry["name"],
            "score": entry["score"]
        })
    return {"scores": scores}
        

@app.post("/submit-score")
async def submit_score(submission: ScoreSubmission):
    try:
        result = await scores_collection.insert_one(submission.dict())
        if result.inserted_id:
            return {"message": "Score submitted successfully", "id": str(result.inserted_id)}
        raise HTTPException(status_code=500, detail="Failed to submit score")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))