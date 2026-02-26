import pandas as pd
import sqlite3

def obtener_boletas(db_path="pos/database/BDD_MINIMARKET.db"):
    conn = sqlite3.connect(db_path)

    query = """
    SELECT ID_Venta, Fecha_Venta, Total_Venta
    FROM Ventas
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def obtener_detalle_ventas(db_path="pos/database/BDD_MINIMARKET.db"):
    conn = sqlite3.connect(db_path)

    query = """
    SELECT v.ID_Venta, v.Fecha_Venta,
           d.ID_producto, d.Nombre_Producto,
           d.Cantidad_Vendida, d.Valor_Unitario
    FROM Ventas v
    JOIN Ventas_Detalle d ON v.ID_Venta = d.ID_Venta
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def obtener_inventario(db_path="pos/database/BDD_MINIMARKET.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM Productos", conn)
    conn.close()
    return df