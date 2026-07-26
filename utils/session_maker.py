from database import SessionLocal
from contextlib import contextmanager

def make_db_session():
    try:
        db = SessionLocal()

        yield db 
    finally: 
        
        db.close()

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()