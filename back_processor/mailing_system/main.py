from fastapi import FastAPI
from database import engine, SessionLocal
from sqlalchemy import text

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Python Server is running"}

@app.get("/db-test")
def test_db():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {"status": "success", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/send-remark")
def send_remark():


@app.get("/check-status")
def check_status():

@app.get("/groupby_vendor")
def groupby_vendor():

@app.get("/groupby_location")
def groupby_location():
    
    
@app.get("/get_contact_vendor_details")
def vendor_details():