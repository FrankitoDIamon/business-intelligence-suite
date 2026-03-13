import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3 as sq
import datetime
import sys
import os
import shutil

def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Cierre_Caja:
    def __init__(self, ventana_principal):
        
        self.root_cierre_caja = tk.Toplevel()
        self.root= ventana_principal
        self.root_cierre_caja.title("Cierre de Caja")
        self.root_cierre_caja.geometry("400x510")
        self.root_cierre_caja.resizable(False, False)
        self.root_cierre_caja.focus_force()
        self.root.protocol("WM_DELETE_WINDOW", self.ConfirmarCierre)

        self.ruta_bdd = resource_path('database\\BDD_MINIMARKET.db')

        # Fecha de hoy
        self.fecha_actual = datetime.date.today().strftime("%Y-%m-%d")

        # Frame principal
        self.frame = tk.Frame(self.root_cierre_caja)
        self.frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Título
        self.label_titulo = tk.Label(self.frame, text="Resumen de Pagos", font=("Segoe UI", 16, "bold"), fg="#2C3E50")
        self.label_titulo.pack(pady=(0, 1))

        # Fecha
        self.label_fecha = tk.Label(self.frame, text=f"Fecha: {self.fecha_actual}", font=("Segoe UI", 12, "bold"), fg="#2C3E50")
        self.label_fecha.pack(pady=(0,10))

        #Mostrar detalle con metodo de pago
        efectivo, tarjeta, transferencia = self.metodos()

        tk.Label(self.frame, text="Métodos de Pago", font=("Segoe UI", 13, "bold"), fg="#2C3E50").pack(pady=(10, 5))

        # Método: Efectivo
        frame_efectivo = tk.Frame(self.frame)
        frame_efectivo.pack(fill='x', padx=10)
        tk.Label(frame_efectivo, text="Total Efectivo:", font=("Segoe UI Semibold", 14), fg="#34495E").pack(side='left')
        tk.Label(frame_efectivo, text=f"${efectivo:,.0f}".replace(",", "."), font=("Segoe UI", 14, "bold"), fg="#1F618D").pack(side='right')

        # Método: Tarjeta
        frame_tarjeta = tk.Frame(self.frame)
        frame_tarjeta.pack(fill='x', padx=10)
        tk.Label(frame_tarjeta, text="Total Tarjeta:", font=("Segoe UI Semibold", 14), fg="#34495E").pack(side='left')
        tk.Label(frame_tarjeta, text=f"${tarjeta:,.0f}".replace(",", "."), font=("Segoe UI", 14, "bold"), fg="#1F618D").pack(side='right')

        # Método: Transferencia
        frame_transferencia = tk.Frame(self.frame)
        frame_transferencia.pack(fill='x', padx=10)
        tk.Label(frame_transferencia, text="Total Transferencia:", font=("Segoe UI Semibold", 14), fg="#34495E").pack(side='left')
        tk.Label(frame_transferencia, text=f"${transferencia:,.0f}".replace(",", "."), font=("Segoe UI", 14, "bold"), fg="#1F618D").pack(side='right')

        # Línea divisoria
        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", pady=10)

        # Obtener totales
        total_vendido, ganancia = self.obtenerTotalVentasDelDia()

        # Agrupación: Totales
        tk.Label(self.frame, text="Totales", font=("Segoe UI", 13, "bold"), fg="#2C3E50").pack(pady=(10, 5))

        # Mostrar total vendido
        frame_total_vendido = tk.Frame(self.frame)
        frame_total_vendido.pack(fill='x', padx=10)
        tk.Label(frame_total_vendido, text="Total Vendido:", font=("Segoe UI Semibold", 14), fg="#34495E").pack(side='left')
        tk.Label(frame_total_vendido, text=f"${total_vendido:,.0f}".replace(",", "."), font=("Segoe UI", 14, "bold"), fg="#1F618D").pack(side='right')


        # Mostrar ganancia (total - costos)
        frame_ganancia = tk.Frame(self.frame)
        frame_ganancia.pack(fill='x', padx=10)
        tk.Label(frame_ganancia, text="Ganancia neta:", font=("Segoe UI", 14, "bold"), fg="#057A36").pack(side='left')
        tk.Label(frame_ganancia, text=f"${ganancia:,.0f}".replace(",", "."), font=("Segoe UI", 14, "bold"), fg="#1F618D").pack(side='right')

        # Botones
        self.boton_confirmar = tk.Button(self.frame, text="Confirmar Cierre", bg="#58D68D",activebackground="#45B97C", fg="#1C2833", font=("Segoe UI", 12, "bold"),
                                         command=self.ConfirmarCierre)
        self.boton_confirmar.pack(pady=(20,0), fill='x')

        self.boton_cancelar = tk.Button(self.frame, text="Cancelar", bg="#F57162",activebackground="#E74C3C", fg="#1C2833", font=("Segoe UI", 12, "bold"),
                                        command=self.root_cierre_caja.destroy)
        self.boton_cancelar.pack(pady=5, fill='x')


        #FUNCIONES

    def getFechaList(self):
        dia = datetime.date.today().day
        mes = datetime.date.today().month
        anio = datetime.date.today().year   
        fecha = (dia * 1000000) + (mes * 10000) + (anio)
        return [fecha, dia, mes, anio]
    

    def obtenerTotalVentasDelDia(self):

        conn= sq.connect(self.ruta_bdd)
        cursor=conn.cursor()

        fecha= self.getFechaList()[0]

        # Total vendido sumando todas las ventas del día (incluye comunes y normales)
        cursor.execute("SELECT SUM (Total_Venta) FROM Ventas WHERE Fecha_Venta = ?", (fecha, ))
        resultado= cursor.fetchone()
        total_vendido = resultado[0] if resultado[0] is not None else 0


        # Obtener el costo solo para productos con ID distinto a '0' (productos normales)
        cursor.execute("SELECT p.Precio_Compra, vd.Cantidad_Vendida FROM Productos p JOIN Ventas_Detalle vd ON p.ID_Producto = vd.ID_Producto JOIN Ventas v ON vd.ID_Venta = v.ID_Venta WHERE Fecha_Venta = ?", (fecha, ))
        datos=cursor.fetchall()

        costo_total = 0
        for precio_compra, cantidad_vendida in datos:
            costo_total += precio_compra * cantidad_vendida

        
        ganancia = total_vendido - costo_total

        conn.close()

        return total_vendido, ganancia
        
    
    def ConfirmarCierre(self):
        respuesta= messagebox.askyesno("Confirmar Cierre", "¿Estás seguro que quieres cerrar la aplicacion?", parent=self.root_cierre_caja)

        if respuesta:
            self.crear_respaldo()
            messagebox.showinfo("Cierre Confirmado", "Se a confirmado el cierre", parent=self.root)
            self.root_cierre_caja.destroy()

            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.destroy()

    def metodos(self):

        conn=sq.connect(self.ruta_bdd)
        cursor=conn.cursor()

        fecha = self.getFechaList()[0]

        try:

            cursor.execute("SELECT Tipo_Venta, SUM(Total_Venta) FROM Ventas WHERE Fecha_Venta = ? GROUP BY Tipo_Venta", (fecha, ))
            resultados= cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar métodos de pago: {e}", parent=self.root_cierre_caja)
            resultados = []


        conn.close()

        total_efectivo = 0
        total_tarjeta = 0
        total_transferencia = 0

        

        for tipo,total in resultados:
            if tipo == "Efectivo":
                total_efectivo+= total
            elif tipo == "Tarjeta":
                total_tarjeta+= total
            elif tipo == "Transferencia":
                total_transferencia+= total
                
        return total_efectivo, total_tarjeta, total_transferencia
    
    def crear_respaldo(self):
        try:
            # Carpeta de respaldos
            backup_folder = "respaldos"
            os.makedirs(backup_folder, exist_ok=True)

            # Nombre del archivo con fecha y hora
            fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_folder, f"BDD_MINIMARKET_{fecha}.db")

            # Ruta completa del respaldo
            

            # Copiar archivo
            shutil.copy2(self.ruta_bdd, backup_file)
            messagebox.showinfo("Exito", f"✅ Respaldo creado: {backup_file}")

        except Exception as e:
            messagebox.showerror("Error", f"⚠️ Error al crear respaldo: {e}")

                    
        