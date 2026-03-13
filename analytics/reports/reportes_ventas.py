from analytics.utils.get_bdd import obtener_boletas
from analytics.utils.get_bdd import obtener_detalle_ventas
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

def producto_mas_vendido():
    df=obtener_detalle_ventas()

    df["Fecha_Venta"] = df["Fecha_Venta"].astype(str).str.zfill(8)
    df["Fecha_Venta"] = pd.to_datetime(df["Fecha_Venta"], format= "%d%m%Y")

    #Quitar productos comunes (codigo 0)
    df = df[df["ID_Producto"].astype(str) != "0"]

    ventas = df.groupby([df["Fecha_Venta"].dt.date, "ID_Producto", "Nombre_Producto"])["Cantidad_Vendida"].sum().reset_index()

    ventas.columns = ["Fecha_Venta", "ID_Producto", "Cantidad_Total", "Nombre_Producto"]

    idx = ventas.groupby("Fecha_Venta")["Cantidad_Total"].idxmax()

    resumen = ventas.loc[idx].reset_index(drop = True)

    print(resumen)
if __name__ == "__main__":
    #reporte_ventas_diarias()
    producto_mas_vendido()