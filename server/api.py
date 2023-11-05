from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import main

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class UserInput(BaseModel):
    query: str

def prompt(query: str):
    response = main.preprocessing().run(query)
    return response

@app.post("/input")
async def root(user_input: UserInput):
    query = user_input.query
    res = prompt(query)
    # response = main.remove_formatting(res)
    return {"response": res}

# uvicorn api:app --host 192.168.42.89 --port 80