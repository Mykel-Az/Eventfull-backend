from fastapi import Depends
import models
from database import engine, sessionlocal
from typing import Annotated
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]