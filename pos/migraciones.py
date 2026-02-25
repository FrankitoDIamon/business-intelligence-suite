import sqlite3 as sq

def ejecutar_migraciones(ruta_bdd):
    with sq.connect(ruta_bdd) as con:
        cur = con.cursor()

        # =========================
        # DEUDORES
        # =========================
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Deudores (
            ID_Deuda INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Monto_Total REAL NOT NULL,
            Abono REAL DEFAULT 0,
            Saldo REAL NOT NULL,
            Fecha INTEGER NOT NULL,
            Estado TEXT NOT NULL
        )
        """)

        # Columnas faltantes Deudores
        columnas_deudores = [c[1] for c in cur.execute("PRAGMA table_info(Deudores)")]
        if "Abono" not in columnas_deudores:
            cur.execute("ALTER TABLE Deudores ADD COLUMN Abono REAL DEFAULT 0")
        if "Saldo" not in columnas_deudores:
            cur.execute("ALTER TABLE Deudores ADD COLUMN Saldo REAL")
        if "Estado" not in columnas_deudores:
            cur.execute("ALTER TABLE Deudores ADD COLUMN Estado TEXT")

        cur.execute("""
        UPDATE Deudores
        SET Saldo = Monto_Total - Abono
        WHERE Saldo IS NULL
        """)

        cur.execute("""
        UPDATE Deudores
        SET Estado = CASE
            WHEN Saldo = 0 THEN 'PAGADO'
            ELSE 'PENDIENTE'
        END
        WHERE Estado IS NULL
        """)

        # =========================
        # DEUDORES DETALLE
        # =========================
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Deudores_Detalle (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_Deuda INTEGER NOT NULL,
            ID_Producto TEXT,
            Nombre_Producto TEXT NOT NULL,
            Cantidad INTEGER NOT NULL,
            Precio_Unitario REAL NOT NULL,
            Subtotal REAL NOT NULL,
            FOREIGN KEY (ID_Deuda) REFERENCES Deudores(ID_Deuda)
        )
        """)

        # =========================
        # VENTAS
        # =========================
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Ventas (
            ID_Venta INTEGER PRIMARY KEY AUTOINCREMENT,
            Fecha_Venta INTEGER NOT NULL,
            Total_Venta REAL NOT NULL,
            Tipo_Venta TEXT NOT NULL,
            Precio_Promocional INTEGER DEFAULT 0
        )
        """)

        columnas_ventas = [c[1] for c in cur.execute("PRAGMA table_info(Ventas)")]
        if "Precio_Promocional" not in columnas_ventas:
            cur.execute(
                "ALTER TABLE Ventas ADD COLUMN Precio_Promocional INTEGER DEFAULT 0"
            )

        cur.execute("""
        UPDATE Ventas
        SET Precio_Promocional = 0
        WHERE Precio_Promocional IS NULL
        """)

        # =========================
        # VENTAS DETALLE
        # =========================
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Ventas_Detalle (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_Venta INTEGER NOT NULL,
            ID_Producto TEXT,
            Valor_Unitario REAL NOT NULL,
            Cantidad_Vendida INTEGER NOT NULL,
            Nombre_Producto TEXT NOT NULL,
            FOREIGN KEY (ID_Venta) REFERENCES Ventas(ID_Venta)
        )
        """)

        # =========================
        # TOP VENTAS
        # =========================
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Top_Ventas (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_Producto TEXT UNIQUE,
            Nombre_Producto TEXT NOT NULL,
            Cantidad_Vendida INTEGER NOT NULL,
            Fecha_Venta INTEGER NOT NULL
        )
        """)
        con.commit()
