from analytics.utils.get_bdd import obtener_ventas
import pandas as pd

def reporte_ventas_diarias():
    df= obtener_ventas()
    df ["fecha"] = pd.to_datetime(df["fecha"])
    resumen = df.groupby(df["fecha"].dt.date).agg(
        total_ventas = pd.NamedAgg(column="total", aggfunc="sum"),
        cantidad_productos = pd.NamedAgg(column="producto_id", aggfunc="count")
    ).reset_index()
    resumen["ticket_promedio"] = resumen["total_ventas"] / resumen["cantidad_productos"]
    print(resumen)
    resumen.to_excel("analytics/data/ventas_diarias.xlsx", index= False)

if __name__ == "__main__":
    reporte_ventas_diarias()