import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os
from openpyxl import Workbook
from tkinter import filedialog
from datetime import date
from PIL import Image, ImageTk

def resource_path(relative_path):
   
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  
    else:
        base_path = os.path.abspath(".")  

    return os.path.join(base_path, relative_path)
class ReporteMensual:
    def __init__(self):

        self.ruta_bdd = resource_path('database/BDD_MINIMARKET.db')  
        self.ventana = tk.Toplevel()
        self.ventana.title("Reporte Mensual")
        self.ventana.geometry("520x480")
        self.ventana.resizable(False, False)
        self.ventana.focus_force()
        self.ventana.bind("<Escape>", lambda e: self.ventana.destroy())

        #Cargar imagenes
        ruta_barras = resource_path(os.path.join("png", "Barras.jpg"))
        ruta_billete = resource_path(os.path.join("png", "Billete.jpg"))
        ruta_bolsa = resource_path(os.path.join("png", "Bolsa.png"))
        ruta_caja = resource_path(os.path.join("png", "Caja.png"))
        ruta_caja = resource_path(os.path.join("png", "Caja.png"))
        ruta_calendario = resource_path(os.path.join("png", "Calendario.png"))
        ruta_disquete = resource_path(os.path.join("png", "Disquete.png"))
        ruta_grafico = resource_path(os.path.join("png", "Grafico.png"))

        self.icono_barras=ImageTk.PhotoImage(Image.open(ruta_barras).resize((25,25),resample=Image.Resampling.LANCZOS))
        self.icono_billete=ImageTk.PhotoImage(Image.open(ruta_billete).resize((25,25),resample=Image.Resampling.LANCZOS))
        self.icono_bolsa=ImageTk.PhotoImage(Image.open(ruta_bolsa).resize((25,25),resample=Image.Resampling.LANCZOS))
        self.icono_caja=ImageTk.PhotoImage(Image.open(ruta_caja).resize((25,25),resample=Image.Resampling.LANCZOS))
        self.icono_calendario=ImageTk.PhotoImage(Image.open(ruta_calendario).resize((30,30),resample=Image.Resampling.LANCZOS))
        self.icono_disquete=ImageTk.PhotoImage(Image.open(ruta_disquete).resize((25,25),resample=Image.Resampling.LANCZOS))
        self.icono_grafico=ImageTk.PhotoImage(Image.open(ruta_grafico).resize((25,25),resample=Image.Resampling.LANCZOS))

        #Boton Generar Reporte
        
        self.boton_generar_reporte=tk.Button(self.ventana, text=" Generar Reporte del Mes",image=self.icono_barras, compound="left", width=300, height=70, font=("Segoe UI", 16), bg="#0F6431", fg="white", activebackground="#45a049", command=self.generar_reporte)
        self.boton_generar_reporte.pack(pady=10)

        # Frame para mostrar el reporte con iconos
        self.frame_reporte = tk.Frame(self.ventana, bg="white", bd=2, relief="groove")
        self.frame_reporte.pack(padx=10, pady=10, fill="both", expand=True)
        
        #Boton Exportar a excel
        self.boton_exportar_excel=tk.Button(self.ventana, text=" Exportar a Excel",image=self.icono_disquete, compound="left", width=300, height=70, font=("Segoe UI", 14), bg="#F4D03F", fg="#1C2833", activebackground="#FFD54F", command=self.exportar_excel)
        self.boton_exportar_excel.pack(pady=5)

    def generar_reporte(self):

        hoy = date.today()
        mes = hoy.month      
        anio = hoy.year

        conn = sqlite3.connect(self.ruta_bdd)
        cursor = conn.cursor()

        # === 1. Obtener ventas totales ===
        cursor.execute("""
            SELECT IFNULL(SUM(Total_Venta), 0)
            FROM Ventas
            WHERE ((Fecha_Venta / 10000) % 100 )= ? AND (Fecha_Venta % 10000) = ?
        """, (mes, anio))
        total_ventas = cursor.fetchone()[0]

        # === 2. Calcular el costo total del mes ===
        cursor.execute("""
            SELECT vd.ID_Producto, vd.Cantidad_Vendida, p.Precio_Compra
            FROM Ventas_Detalle vd
            JOIN Ventas v ON vd.ID_Venta = v.ID_Venta
            JOIN Productos p ON vd.ID_Producto = p.ID_Producto
            WHERE ((v.Fecha_Venta / 10000) % 100) = ? AND (v.Fecha_Venta % 10000) = ?
        """, (mes, anio))

        filas = cursor.fetchall()
        total_costos = sum(cant * precio for _, cant, precio in filas)

        # === 3. Inversión en inventario actual ===
        cursor.execute("""
            SELECT SUM(Precio_Compra * Cantidad_Disponible)
            FROM Productos
        """)
        costo_inventario = cursor.fetchone()[0] or 0

        # === 4. Cantidad total de productos en stock ===
        cursor.execute("""
            SELECT SUM(Cantidad_Disponible)
            FROM Productos
        """)
        cantidad_total = cursor.fetchone()[0] or 0

        conn.close()

        ganancia = total_ventas - total_costos

        # === Mostrar resultados ===

        self.mes_anio = f"{mes:02d}-{anio}"
        self.total_ventas = total_ventas
        self.total_costos = total_costos
        self.ganancia = ganancia
        self.costo_inventario = costo_inventario
        self.cantidad_total = cantidad_total

        self.mostrar_reporte_con_icono()

        
    
    def mostrar_reporte_con_icono(self):
        for widget in self.frame_reporte.winfo_children():
            widget.destroy()
        
        #Titulo con icono calendario
        frame_titulo = tk.Frame(self.frame_reporte, bg="white")
        frame_titulo.pack(anchor="w", pady=(5,10))
        tk.Label(frame_titulo, image=self.icono_calendario, bg="white").pack(side="left")
        tk.Label(frame_titulo, text=f"Reporte del Mes: {self.mes_anio}", font=("Arial", 16, "bold"), bg="white").pack(side="left", padx=10)

        #Total Ventas con icono billete
        frame_ventas = tk.Frame(self.frame_reporte, bg="white")
        frame_ventas.pack(anchor="w", pady=3)
        tk.Label(frame_ventas, image=self.icono_billete, bg="white").pack(side="left")
        tk.Label(frame_ventas, text=f"Total Ventas:        ${int(self.total_ventas):,}".replace(",", "."), font=("Arial", 14), bg="white").pack(side="left", padx=10)

        # Costos con icono bolsa
        frame_costos = tk.Frame(self.frame_reporte, bg="white")
        frame_costos.pack(anchor="w", pady=3)
        tk.Label(frame_costos, image=self.icono_bolsa, bg="white").pack(side="left")
        tk.Label(frame_costos, text=f"Costos del Mes:      ${int(self.total_costos):,}".replace(",", "."), font=("Arial", 14), bg="white").pack(side="left", padx=10)

        # Ganancia con icono grafico
        frame_ganancia = tk.Frame(self.frame_reporte, bg="white")
        frame_ganancia.pack(anchor="w", pady=3)
        tk.Label(frame_ganancia, image=self.icono_grafico, bg="white").pack(side="left")
        tk.Label(frame_ganancia, text=f"Ganancia Neta:       ${int(self.ganancia):,}".replace(",", "."), font=("Arial", 14), bg="white").pack(side="left", padx=10)
    
        # Espacio separador
        tk.Frame(self.frame_reporte, height=10, bg="white").pack()

        # Inventario - icono caja
        frame_inventario = tk.Frame(self.frame_reporte, bg="white")
        frame_inventario.pack(anchor="w", pady=3)
        tk.Label(frame_inventario, image=self.icono_caja, bg="white").pack(side="left")
        tk.Label(frame_inventario, text="Estado Actual del Inventario:", font=("Arial", 14, "underline"), bg="white").pack(side="left", padx=10)

        # Inversion inventario con barras
        frame_inv = tk.Frame(self.frame_reporte, bg="white")
        frame_inv.pack(anchor="w", pady=1, padx=60)
        tk.Label(frame_inv, image=self.icono_barras, bg="white").pack(side="left")
        tk.Label(frame_inv, text=f"Inversión Total:      ${int(self.costo_inventario):,}".replace(",", "."), font=("Arial", 13), bg="white").pack(side="left", padx=10)

        # Cantidad total stock con caja
        frame_stock = tk.Frame(self.frame_reporte, bg="white")
        frame_stock.pack(anchor="w", pady=1, padx=60)
        tk.Label(frame_stock, image=self.icono_caja, bg="white").pack(side="left")
        tk.Label(frame_stock, text=f"Productos en stock:   {int(self.cantidad_total):,} unidades".replace(",", "."), font=("Arial", 13), bg="white").pack(side="left", padx=10)

    def exportar_excel(self):
        if not hasattr(self, 'total_ventas'):
            messagebox.showwarning("Atención", "Primero genera un reporte.", parent=self.ventana)
            return

        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar reporte como"
            )

        if not ruta_archivo:
            return  # Usuario canceló

        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte Mensual"

        ws.append(["Reporte del Mes", self.mes_anio])
        ws.append([])
        ws.append(["Total Ventas", self.total_ventas])
        ws.append(["Costos del Mes", self.total_costos])
        ws.append(["Ganancia Neta", self.ganancia])
        ws.append([])
        ws.append(["Inversión en Inventario", self.costo_inventario])
        ws.append(["Productos en Stock", self.cantidad_total])

        try:
            wb.save(ruta_archivo)
            messagebox.showinfo("Éxito", f"Reporte exportado a:\n{ruta_archivo}",parent= self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}", parent= self.ventana)
