import pandas as pd
from extensions import *  # adjust this if needed
from models import *  # adjust this if your models are in a separate file
from setup import *  # adjust this if your setup is in a separate file
from run import *  # adjust this if your run is in a separate file

# Load the Excel sheet
file_path = "Copy of NUST Bites.xlsx"  # or the full path if needed
sheet_name = "KFC Menu"  # or the exact sheet name
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Use the app context for database interaction
with app.app_context():
    # Loop through each row and add to DB
    for _, row in df.iterrows():
        menu_item = Menu(
            restaurant_id=1,  # KFC
            name=row['ItemName'],
            price=float(row['Price']),
            description=row.get('Description', ''),
            is_available=bool(row['Available']),
            image_url=row.get('ImageURL', ''),
            category=row.get('Category', 'Uncategorized')
        )
        db.session.add(menu_item)

    # Commit the session
    db.session.commit()
    print("✅ KFC menu items added successfully.")