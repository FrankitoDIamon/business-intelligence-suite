import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import sqlite3 as sq
import sys
import os

def resource_path(relative_path):
   
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  
    else:
        base_path = os.path.abspath(".") 

    return os.path.join(base_path, relative_path)

class TopVentas():
    def __init__(self):
        self.ruta_bdd = resource_path('database\BDD_MINIMARKET.db')

        
        self.cigarros = [
        'CIGARRILLOS CARNIVAL AZUL',
        'CIGARRILLOS EIHT AZUL',
        'CIGARRILLOS TIME SANDIA',
        'CIGARRILLOS TIME UVA',
        'CIGARRILOS TIME MANGO',
        'CIGARROS HILLS',
        'CIGARROS TIME',
        'Cigarrillos Doble Click',
        'Cigarros Carnival Azul',
        'Cigarros Fox',
        'GIFT AZUL',
        'GIFT VERDE'
        ]

        self.buscar_por_producto = tk.BooleanVar(value=False)

        self.root_topventas=tk.Toplevel()
        self.root_topventas.title("Top Ventas")
        self.root_topventas.state("zoomed")
        self.root_topventas.grid_rowconfigure(0, weight=1)
        self.root_topventas.grid_columnconfigure(0, weight=1)

        #Frame Principal
        self.frame_principal = tk.Frame(self.root_topventas, bg="#91C491")
        self.frame_principal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.frame_principal.grid_rowconfigure(1, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)

        #FRAME SUPERIOR
        self.frame_superior = tk.Frame(self.frame_principal, bg="#91C491")
        self.frame_superior.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        for i in range(7):
            self.frame_superior.grid_columnconfigure(i, weight=1)



        #Top Ventas
        tk.Label(self.frame_superior, text="Top Ventas:", font=("Segoe UI", 12, "bold"), bg="#91C491").grid(row=0, column=0, sticky="e", padx=(10,2), pady=(10,0))
        self.filtroseleccionado=tk.StringVar(value= "20 Más Vendidos")
        self.rango_top = tk.OptionMenu(self.frame_superior, self.filtroseleccionado, "20 Más Vendidos", "20 Menos Vendidos", command=self.actualizar_busqueda)
        self.rango_top.config(font=("Segoe UI", 10), bg="white", width=18)
        self.rango_top.grid(row=0, column=1, sticky="w", padx=(2,10), pady=(10,0))

        self.usar_rango = tk.BooleanVar(value=False)
        self.check_rango = tk.Checkbutton(
            self.frame_superior, text="Aplicar rango de semanas", variable=self.usar_rango,
            font=("Segoe UI", 10, "bold"), bg="#91C491",
            command=self.actualizar_busqueda
        )
        self.check_rango.grid(row=0, column=2, sticky="w", padx=(10, 0), pady=(10, 0))
        
        #Espaciador
        tk.Label(self.frame_superior, text="", bg="#91C491", width=20).grid(row=1, column=0)

        # Buscar por producto
        self.label_codigo = tk.Label(self.frame_superior, text= "Buscar producto por código: ", font= ("Segoe UI", 12, "bold"), bg= "#91C491")
        self.label_codigo.grid(row=2, column=0, sticky="e", padx=(0,2), pady=(5,0) )
        self.entry_codigo = tk.Entry(self.frame_superior, font=("Arial", 10), justify="left", width= 25)
        self.entry_codigo.grid(row=2, column= 1, sticky="w", padx=(0,5), pady=(5,0))
        self.entry_codigo.bind("<Return>", self.buscar_ventas_por_producto)
        self.entry_codigo.focus_force()
        self.entry_codigo.bind("<FocusIn>", lambda e: self.entry_codigo.select_range(0, tk.END))
        #Rango Semanas
        self.label_semanas= tk.Label(self.frame_superior, text= "Últimas Semanas:", font= ("Segoe UI", 12, "bold"), bg= "#91C491")
        self.label_semanas.grid(row= 2, column= 2, sticky="w", padx=(0,60), pady=(5,0))

        self.semana_seleccionada=tk.StringVar(value= "1")
        self.rango_semanas=tk.OptionMenu(self.frame_superior,self.semana_seleccionada,
                                         "1", "2", "3", "4", "5", "6", "7",
                                         command=lambda _: self.actualizar_busqueda()
                                         )
        self.rango_semanas.config(font=("Segoe UI", 10), bg="white", width=10)
        self.rango_semanas.grid(row= 2, column= 2, sticky="e", padx=(0,5), pady=(5,0))

        #BOTON CERRAR VENTANA
        self.boton_cerrar = tk.Button(self.frame_superior, text="Cerrar Ventana", font=("Segoe UI", 10, "bold"), 
                                      bg="#EC7063", fg="white", command=self.root_topventas.destroy
                                      )
        self.boton_cerrar.grid(row= 0, column= 6, sticky="e", padx=20)


        
        #FRAME TABLA
        self.frame_tabla = tk.Frame(self.frame_principal)
        self.frame_tabla.grid(row= 1, column= 0, sticky= "nsew")
        self.frame_tabla.grid_rowconfigure(0, weight=1)
        self.frame_tabla.grid_columnconfigure(0, weight=1)


        #TABLA
        self.tabla= ttk.Treeview(self.frame_tabla, show="headings", 
                                 columns= ("Código", "Nombre Producto", "Cantidad Vendida"), height=28
                                 )
        self.tabla.grid(row= 0, column= 0, sticky= "nsew")
        scrollbar= ttk.Scrollbar(self.frame_tabla, orient="vertical", command= self.tabla.yview)
        scrollbar.grid(row= 0, column=1, sticky= "ns")
        self.tabla.configure(yscrollcommand=scrollbar.set)

        #Encabezados
        self.tabla.heading("Código", text= "Código", anchor="center")
        self.tabla.heading("Nombre Producto", text= "Nombre Producto", anchor="w")
        self.tabla.heading("Cantidad Vendida", text= "Cantidad Vendida", anchor="center")

        self.actualizar_busqueda()

        #FUNCIONES
    def actualizar_busqueda(self, event=None):
        codigo= self.entry_codigo.get()
        if codigo:
            self.buscar_ventas_por_producto()
        else:
            self.mostrar_top_ventas()

    def mostrar_top_ventas(self, *_):
        self.tabla.delete(*self.tabla.get_children())
        conn = sq.connect(self.ruta_bdd)
        cursor = conn.cursor()

        try:
            filtro = self.filtroseleccionado.get()
            order = "DESC" if filtro == "20 Más Vendidos" else "ASC"
            usar_rango = self.usar_rango.get()

            if usar_rango:
                semanas_atras = int(self.semana_seleccionada.get())
                hoy = datetime.date.today()
                fecha_inicio = hoy - datetime.timedelta(weeks=semanas_atras)

                # Traemos todas las ventas, luego filtramos por fechas en Python
                query = f"""
                    SELECT VD.ID_Producto, VD.Nombre_Producto, VD.Cantidad_Vendida, V.Fecha_Venta
                    FROM Ventas_Detalle VD
                    JOIN Ventas V ON VD.ID_Venta = V.ID_Venta
                    WHERE VD.Nombre_Producto NOT IN ({','.join('?' for _ in self.cigarros)})
                    AND VD.ID_Producto <> 0
                """
                cursor.execute(query, self.cigarros)
                filas = cursor.fetchall()

                # Contabilizamos ventas dentro del rango
                ventas_totales = {}
                for id_prod, nombre, cantidad, fecha_int in filas:
                    try:
                        fecha_str = str(fecha_int).zfill(8)
                        dia = int(fecha_str[:2])
                        mes = int(fecha_str[2:4])
                        anio = int(fecha_str[4:])
                        fecha_real = datetime.date(anio, mes, dia)
                        if fecha_inicio <= fecha_real <= hoy:
                            if (id_prod, nombre) not in ventas_totales:
                                ventas_totales[(id_prod, nombre)] = 0
                            ventas_totales[(id_prod, nombre)] += cantidad
                    except Exception:
                        continue

                # Ordenamos y mostramos top 20
                resultados = sorted(ventas_totales.items(), key=lambda x: x[1], reverse=(order=="DESC"))[:20]
                for (id_prod, nombre), total in resultados:
                    self.tabla.insert("", "end", values=(id_prod, nombre, total))

            else:
                # Sin rango de semanas, podemos usar SQL directo con SUM
                query = f"""
                    SELECT VD.ID_Producto, VD.Nombre_Producto, SUM(VD.Cantidad_Vendida) as TotalVendida
                    FROM Ventas_Detalle VD
                    JOIN Ventas V ON VD.ID_Venta = V.ID_Venta
                    WHERE VD.Nombre_Producto NOT IN ({','.join('?' for _ in self.cigarros)})
                    AND VD.ID_Producto <> 0
                    GROUP BY VD.ID_Producto, VD.Nombre_Producto
                    ORDER BY TotalVendida {order}
                    LIMIT 20
                """
                cursor.execute(query, self.cigarros)
                resultados = cursor.fetchall()
                for id_prod, nombre, total in resultados:
                    self.tabla.insert("", "end", values=(id_prod, nombre, total))

        except sq.Error as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}", parent=self.root_topventas)
        finally:
            conn.close()

            
    def buscar_ventas_por_producto(self, event=None):
        try:
            codigo = self.entry_codigo.get().strip()
            if not codigo:
                return

            semanas_atras = int(self.semana_seleccionada.get())
            hoy = datetime.date.today()
            fecha_inicio = hoy - datetime.timedelta(weeks=semanas_atras)

            conn = sq.connect(self.ruta_bdd)
            cursor = conn.cursor()

            # Traemos todas las ventas del producto
            cursor.execute("""
                SELECT 
                    VD.Cantidad_Vendida,
                    VD.Nombre_Producto,
                    V.Fecha_Venta
                FROM Ventas_Detalle VD
                JOIN Ventas V ON VD.ID_Venta = V.ID_Venta
                WHERE VD.ID_Producto = ?
            """, (codigo,))
            filas = cursor.fetchall()

            cantidad_vendida = 0
            nombre_producto = "Producto no encontrado"

            for cantidad, nombre, fecha_int in filas:
                # Convertir DDMMYYYY → datetime.date
                try:
                    fecha_str = str(fecha_int).zfill(8)
                    dia = int(fecha_str[:2])
                    mes = int(fecha_str[2:4])
                    anio = int(fecha_str[4:])
                    fecha_real = datetime.date(anio, mes, dia)

                    if fecha_inicio <= fecha_real <= hoy:
                        cantidad_vendida += cantidad
                        nombre_producto = nombre
                except Exception:
                    continue

            if nombre_producto.upper() in [c.upper() for c in self.cigarros]:
                self.tabla.delete(*self.tabla.get_children())
                messagebox.showinfo("Ignorado", "El producto pertenece a la lista de cigarros (se ignora).", parent=self.root_topventas)
            else:
                self.tabla.delete(*self.tabla.get_children())
                self.tabla.insert("", "end", values=(codigo, nombre_producto, cantidad_vendida))

            conn.close()

        except sq.Error as e:
            messagebox.showerror("Error", f"Ocurrió un error en la consulta:\n{e}", parent=self.root_topventas)




