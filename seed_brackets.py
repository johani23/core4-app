# seed_brackets.py

from db import SessionLocal
from models.discount_bracket import DiscountBracket

db = SessionLocal()

campaign_id = 8  # 👈 change if needed

brackets = [
    (5, 4800),
    (10, 4600),
    (20, 4300),
    (50, 4000),
]

for required, price in brackets:
    b = DiscountBracket(
        campaign_id=campaign_id,
        required_commitments=required,
        price=price,
    )
    db.add(b)

db.commit()
db.close()

print("✅ Brackets inserted successfully")