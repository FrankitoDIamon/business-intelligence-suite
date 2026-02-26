import pandas as pd
import sqlite3

def obtener_ventas(db_path="pos/database/BDD_MINIMARKET.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM Ventas", conn)
    conn.close()
    return df


def obtener_inventario(db_path="pos/database/BDD_MINIMARKET.db"):
    conn = sqlite3.connect(db_path)
    df = pd