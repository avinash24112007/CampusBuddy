from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.caffenity_models import MenuItem, Canteen
from langchain_core.tools import StructuredTool
from schemas.uassist_schemas import FoodSearchInput

def search_food_items(
    db: Session,
    keyword:        str | None = None,
    category:       str | None = None,
    canteen:        str | None = None,
    max_price:      int | None = None,
    min_price:      int | None = None,
    only_available: bool = True
) -> str:

    query = db.query(MenuItem)

    # --- Join Canteen if filtering by canteen name or returning it ---
    # We join Canteen so we can reference Canteen.name in filtering and results
    query = query.join(Canteen, MenuItem.canteen_id == Canteen.id, isouter=True)

    # --- Filter 1: Availability ---
    if only_available:
        query = query.filter(MenuItem.in_stock == True)

    # --- Filter 2: Canteen name (partial match) ---
    if canteen:
        query = query.filter(
            Canteen.name.ilike(f"%{canteen}%")
        )

    # --- Filter 3: Category (partial match) ---
    if category:
        query = query.filter(
            MenuItem.category.ilike(f"%{category}%")
        )

    # --- Filter 4: Keyword searches across name + description ---
    if keyword:
        query = query.filter(
            or_(
                MenuItem.name.ilike(f"%{keyword}%"),
                MenuItem.description.ilike(f"%{keyword}%")
            )
        )

    # --- Filter 5: Price range ---
    if max_price:
        query = query.filter(MenuItem.price <= max_price)
    if min_price:
        query = query.filter(MenuItem.price >= min_price)

    results = query.limit(8).all()   # cap results so LLM response stays clean

    # --- Format output as readable string for the LLM ---
    if not results:
        return "No food items found matching your request. Try different filters!"

    lines = [f"Found {len(results)} item(s):\n"]
    for item in results:
        canteen_name = item.canteen.name if item.canteen else "Unknown Canteen"
        status_str = '\u2705 Available' if item.in_stock else '\u274c Sold Out'
        lines.append(
            f"🍽️ {item.name} ({canteen_name})\n"
            f"   Category : {item.category}\n"
            f"   Price    : \u20b9{item.price}\n"
            f"   About    : {item.description or 'No description'}\n"
            f"   Status   : {status_str}\n"
        )

    return "\n".join(lines)


def make_caffenity_tool(db: Session):
    def _search(
        keyword:        str | None = None,
        category:       str | None = None,
        canteen:        str | None = None,
        max_price:      int | None = None,
        min_price:      int | None = None,
        only_available: bool = True
    ) -> str:
        return search_food_items(
            db, keyword, category, 
            canteen, max_price, min_price, only_available
        )

    return StructuredTool.from_function(
        func=_search,
        name="search_food_items",
        description='''
            Search canteen food items for the student.
            Use this when the student asks about:
            - Food menu, what's available, what to eat
            - Specific dishes like 'dosa', 'pasta', 'coffee'
            - Budget queries like 'under \u20b9100', 'cheap snacks'
            - Canteen-specific: 'what does Container have?'
            - Category queries: 'show me South Indian', 'any beverages?'
            - Combos, salads, snacks, beverages etc.
        ''',
        args_schema=FoodSearchInput,
    )
