import uvicorn
from fastapi import FastAPI

from garage import GarageClient
from schemas import CarList

app = FastAPI()

garage_client = GarageClient()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/cars", response_model=CarList)
def get_cars():
    return garage_client.get_car_list()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
