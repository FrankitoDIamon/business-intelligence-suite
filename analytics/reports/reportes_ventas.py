from analytics.utils.get_bdd import obtener_boletas
import pandas as pd

def reporte_ventas_diarias():
    df= obtener_boletas()

    df["Fecha_Venta"] = df["Fecha_Venta"].astype(str).str.zfill(8)
    df["Fecha_Venta"] = pd.to_datetime(df["Fecha_Venta"], format="%d%m%Y")

    resumen= df.groupby(df["Fecha_Venta"].dt.date).agg(
        total_ventas = ("Total_Venta", "sum"),
        cantidad_boletas = ("ID_Venta", "count")
    ).reset_index()

    resumen["ticket_promedio"] = (resumen["total_ventas"] / resumen["cantidad_boletas"])
    resumen = resumen.sort_values("Fecha_Venta")
    print(resumen)
    resumen.to_excel("analytics/data/ventas_diarias.xlsx", index= False)
    

if __name__ == "__main__":
    reporte_ventas_diarias()