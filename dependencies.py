from garage import GarageClient
from fastapi import Depends
from typing import Annotated


def get_garage_client():
    return GarageClient()


GarageClientDepends = Annotated[GarageClient, Depends(get_garage_client)]
