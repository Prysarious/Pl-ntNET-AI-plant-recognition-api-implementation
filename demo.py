import io
import os
 
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image, ImageOps

load_dotenv()
API_KEY = os.environ["PLANTNET_API_KEY"]
PROJECT = os.getenv("PLANTNET_PROJECT", "all")

URL = f"https://my-api.plantnet.org/v2/identify/{PROJECT}"

app = FastAPI(title="Plant demo")   

def shrink(raw: bytes) -> bytes:
    """Fix phone rotation, strip EXIF, shrink, re-encode as JPEG."""
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    img.thumbnail((1600, 1600))
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=90)
    return out.getvalue()
 
@app.post("/identify")
async def identify(image: UploadFile = File(...), organ: str = Form("auto")):
    try:
        jpg = shrink(await image.read())
    except Exception:
        raise HTTPException(400, "That file is not a readable image")
 
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                URL,
                params={"api-key": API_KEY, "lang": "fr", "nb-results": 3},
                files=[("images", ("photo.jpg", jpg, "image/jpeg"))],
                data={"organs": [organ]},       # leaf, flower, fruit, bark or auto
            )
    except httpx.HTTPError:
        raise HTTPException(504, "Could not reach Pl@ntNet (check the internet connection)")
 
    if r.status_code == 404:                    # Pl@ntNet rejects photos that are not plants
        return {"status": "not_a_plant", "results": []}
    if r.status_code == 429:
        raise HTTPException(503, "Daily Pl@ntNet quota reached")
    if r.status_code != 200:
        raise HTTPException(502, f"Pl@ntNet error {r.status_code}")
 
    body = r.json()
    results = [
        {
            "scientific_name": x["species"]["scientificNameWithoutAuthor"],
            "common_names": x["species"].get("commonNames", [])[:3],
            "score": round(x["score"], 3),
        }
        for x in body.get("results", [])[:3]
    ]
    return {
        "status": "ok" if results else "no_match",
        "results": results,
        "remaining_quota": body.get("remainingIdentificationRequests"),
    }