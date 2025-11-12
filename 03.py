from fastapi import FastAPI
from pydantic import BaseModel



app = FastAPI()

class Message(BaseModel):
    message: str
    name: str
    price: float
    
@app.post("/")
async def root(message: Message):
    return {"message": message.message, "name": message.name, "price": message.price}
    
    
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
