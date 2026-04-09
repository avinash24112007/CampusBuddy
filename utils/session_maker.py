from database import SessionLocal

def make_db_session():
    try:
        db = SessionLocal()

        yield db 
    finally: 
        
        db.close()