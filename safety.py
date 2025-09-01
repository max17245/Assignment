from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running on https://api.myproject.com"}

# GET endpoint: https://api.myproject.com/items/1?q=test
@app.get("/items/{item_id}")
def get_item(item_id: int, q: Optional[str] = None):
    return {
        "item_id": item_id,
        "query": q,
        "full_url": f"https://api.myproject.com/items/{item_id}?q={q}" if q else f"https://api.myproject.com/items/{item_id}"
    }
###
