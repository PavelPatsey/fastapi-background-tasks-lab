from typing import Annotated

from fastapi import Depends

from garage import GarageClient


def get_garage_client():
    return GarageClient()


GarageClientDepends = Annotated[GarageClient, Depends(get_garage_client)]
