from sqlalchemy import create_all
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models.shopperz_models import RetailInventory

def populate_shopperz():
    db = SessionLocal()
    try:
        # Clear existing if needed or just add new
        # db.query(RetailInventory).delete()
        
        products = [
            {
                "name": 'KU Official Hoodie',
                "price": 899,
                "category": 'Apparel',
                "stock_level": 12,
                "image_url": 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&q=80&w=1000',
                "bulk_min": 5,
                "bulk_price": 799,
                "rating": 4.8
            },
            {
                "name": 'A4 Premium Sheets (100pk)',
                "price": 120,
                "category": 'Stationery',
                "stock_level": 3,
                "image_url": 'https://images.unsplash.com/photo-1586075010633-2470bbcf0044?auto=format&fit=crop&q=80&w=1000',
                "bulk_min": 10,
                "bulk_price": 95,
                "rating": 4.5
            },
            {
                "name": 'ED Drafter (Student Edition)',
                "price": 340,
                "category": 'Lab Equipment',
                "stock_level": 10, # Adjusted from 0 for testing
                "image_url": 'https://images.unsplash.com/photo-1544604196-4f51e08922cf?auto=format&fit=crop&q=80&w=1000',
                "rating": 4.2
            },
            {
                "name": 'Graphing Calculator TI-84',
                "price": 2450,
                "category": 'Electronics',
                "stock_level": 8,
                "image_url": 'https://images.unsplash.com/photo-1574605284833-e18e69acb3a1?auto=format&fit=crop&q=80&w=1000',
                "rating": 4.9
            },
            {
                "name": 'Pilot G2 Premium Pens (Set of 10)',
                "price": 450,
                "category": 'Stationery',
                "stock_level": 25,
                "image_url": 'https://images.unsplash.com/photo-1511376916892-91f86807eb36?auto=format&fit=crop&q=80&w=1000',
                "rating": 4.9
            },
            {
                "name": 'Sticky Notes Mega-Pack',
                "price": 150,
                "category": 'Stationery',
                "stock_level": 100,
                "image_url": 'https://images.unsplash.com/photo-1516962215378-7fa2e137ae93?auto=format&fit=crop&q=80&w=1000',
                "bulk_min": 5,
                "bulk_price": 120,
                "rating": 4.8
            }
        ]
        
        for p in products:
            item = RetailInventory(**p)
            db.add(item)
        
        db.commit()
        print("Shopperz retail inventory populated!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_shopperz()
