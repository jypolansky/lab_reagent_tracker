import sqlite3
import os

# Common functions to manage databases (saved at reagents.db)

def create_table(conn: sqlite3.Connection, cur: sqlite3.Cursor):
    result = cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='reagents'""")
    if result.fetchone() is None:
        cur.execute("""CREATE TABLE reagents(name TEXT PRIMARY KEY, stock_amount REAL, amount_left REAL, units TEXT, location TEXT, expiration_date TEXT, notes TEXT)""")
    conn.commit()

def define_new_reagent(conn: sqlite3.Connection, cur: sqlite3.Cursor, name: str, stock_amount: float, amount_left: float, units: str, location: str=None, expiration_date: str=None, notes: str=None):
    """Insert a new reagent into the inventory."""
    cur.execute("INSERT INTO reagents (name, stock_amount, amount_left, units, location, expiration_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, stock_amount, amount_left, units, location, expiration_date, notes))
    conn.commit()

def delete_reagent(conn: sqlite3.Connection, cur: sqlite3.Cursor, reagent_name: str):
    """Delete a reagent from the inventory."""
    cur.execute("DELETE FROM reagents WHERE name = ?", (reagent_name,))
    conn.commit()

def use_reagent(conn: sqlite3.Connection, cur: sqlite3.Cursor, reagent_name: str, used_amount: float):
    """Subtract used_amount from the inventory. Prevents negative amounts. Returns True if successful, False if not enough stock."""
    operation = cur.execute("""
        UPDATE reagents
        SET amount_left = amount_left - ?
        WHERE name = ? AND amount_left >= ?;
    """, (used_amount, reagent_name, used_amount))
    conn.commit()

    # operation.rowcount tells how many rows were updated
    return operation.rowcount > 0

def restock_reagent(conn: sqlite3.Connection, cur: sqlite3.Cursor, reagent_name: str, added_amount: float):
    """Atomically add 'added_amount' to inventory."""
    cur.execute("""
        UPDATE reagents
        SET amount_left = amount_left + ?
        WHERE name = ?;
    """, (added_amount, reagent_name))
    conn.commit()

def get_item(conn: sqlite3.Connection, cur: sqlite3.Cursor, reagent_name: str):
    """Fetches requested reagent."""
    result = cur.execute("SELECT * FROM reagents WHERE name = ?", (reagent_name,))
    conn.commit()
    return result.fetchone()

if __name__ == "__main__":
    # Example usage
    # Make reagent, use some, restock
    with sqlite3.connect(f"database_management/reagents.db") as conn:
        curr = conn.cursor()
        create_table(conn, curr)
        delete_reagent(conn, curr, "Ethanol")
        define_new_reagent(conn, curr, "Ethanol", 1000, 1000, "mL", "Shelf A", "2025-12-31", "For lab use")
        print(get_item(conn, curr, "Ethanol"))
        use_reagent(conn, curr, "Ethanol", 200)
        print(get_item(conn, curr, "Ethanol"))
        restock_reagent(conn, curr, "Ethanol", 500)
        print(get_item(conn, curr, "Ethanol"))