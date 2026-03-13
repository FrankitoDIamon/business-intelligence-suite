import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
import sys
import os
from tkinter import filedialog, messagebox
from datetime import datetime

from bodega_producto import BodegaProducto
from bodega_eliminar import BodegaEliminar
from reporte_mensual import ReporteMensual

def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  
    else:
        base_path = os.path.abspath(".")  

    return os.path.join(base_path, relative_path)

class Bodega:
    def __init__(self, parent):

    # Ruta a la base de datos
        self.ruta_bdd = resource_path('database\BDD_MINIMARKET.db')

    # Ajustes de ventana
        self.root_bodega = tk.Toplevel(parent)
        self.root_bodega.title('Gestion de bodega')
        self.root_bodega.state('zoomed')
        self.root_bodega.grid_rowconfigure(0, weight=1)
        self.root_bodega.grid_columnconfigure(0, weight=1)

    # Creacion del frame principal
        self.frame_principal = tk.Frame(self.root_bodega, bg='lightgrey')
        self.frame_principal.grid(row=0, column=0, sticky="nsew")
        
        self.frame_principal.grid_rowconfigure(0, weight=1)
        self.frame_principal.grid_rowconfigure(1, weight=13)
        self.frame_principal.grid_rowconfigure(2, weight=3)
        self.frame_principal.grid_columnconfigure(0, weight=1)

    # Frame top (busqueda)
        self.frame_top = tk.Frame(self.frame_principal, bg="#91C491")
        self.frame_top.grid(row=0, column=0, sticky='nsew')
        self.frame_top.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)

    # Frame mid (planilla)
        self.frame_mid = tk.Frame(self.frame_principal, bg='lightcyan')
        self.frame_mid.grid(row=1, column=0, sticky='nsew')
        self.frame_mid.grid_columnconfigure(0, weight=1)
        self.frame_mid.grid_columnconfigure(1, weight=0)
        self.frame_mid.grid_rowconfigure(0, weight=1)

    # Frame bottom (botones CRUD)
        self.frame_bottom = tk.Frame(self.frame_principal, bg='#91C491')
        self.frame_bottom.grid(row=2, column=0, sticky='nsew')
        for i in range(5):
            self.frame_bottom.grid_columnconfigure(i, weight=1)
        self.frame_bottom.grid_rowconfigure(0, weight=1)

    # Selector para que familia/tipo mostrar
        self.lista_familias = ['Todas las familias/tipo'] + self.obtenerFamilias()
        if not self.lista_familias:
            self.lista_familias = ["Sin Familias"]
        self.familia_seleccionada = tk.StringVar()
        self.familia_seleccionada.set('Todas las familias/tipo')
        self.menu_selector_familia_tipo = tk.OptionMenu(self.frame_top, self.familia_seleccionada,
                                                        *self.lista_familias
                                                        )
        self.menu_selector_familia_tipo.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # Boton de actualizar
        self.boton_actualizar = tk.Button(self.frame_top, text='Actualizar', command=self.Filtro_Familias)
        self.boton_actualizar.grid(row=0, column=1, padx=5, sticky='ew')

    # Filtro de busqueda
        self.filtro_seleccionado = tk.StringVar()
        self.filtro_seleccionado.set('Código')
        self.menu_filtro_de_busqueda = tk.OptionMenu(self.frame_top, self.filtro_seleccionado,
                                                     'Código',
                                                     'Nombre',
                                                     'Precio')
        self.menu_filtro_de_busqueda.grid(row=0, column=2, padx=5, sticky='ew')

    # Barra de busqueda
        self.barra_de_busqueda = tk.Entry(self.frame_top, font=('Segoe UI', 10), justify='right')
        self.barra_de_busqueda.grid(row=0, column=3, padx=5, sticky='ew')
        self.barra_de_busqueda.focus_set()
        self.barra_de_busqueda.bind('<Return>', self.buscar_codigo)

    # Boton Buscar
        self.boton_buscar = tk.Button(self.frame_top, text='Buscar', command= self.buscar_codigo)
        self.boton_buscar.grid(row=0, column=4, padx=5, sticky='ew')

    # Deseleccionar casillas
        self.boton_deseleccionar = tk.Button(self.frame_top, text='Deseleccionar',font=("Segoe UI", 10, "bold"), bg="#5064AC", fg='white', activebackground='lightcyan', activeforeground='blue', command=self.deseleccionarFila)
        self.boton_deseleccionar.grid(row=0, column=5, padx=5, sticky='ew')

    #Importar Inventario
        self.boton_importar=tk.Button(self.frame_top, text="Importar/Exportar Inventario",font=("Segoe UI", 10, "bold"), bg="#F4D03F", fg="#1C2833", command= self.abrir_menu)
        self.boton_importar.grid(row= 0, column= 6, padx=5, sticky='ew')

    #Reporte Mensual
        self.boton_reporte=tk.Button(self.frame_top, text="Reporte Mensual",font=("Segoe UI", 10, "bold") ,bg="#0F6431", fg="white", command=self.reporte_mensual)
        self.boton_reporte.grid(row=0, column=7, padx=5, sticky='ew')

    # Boton cerrar ventana de bodega
        self.boton_cerrar_bodega = tk.Button(self.frame_top, text='Cerrar ventana', font=("Segoe UI", 10, "bold"), bg='#EC7063', fg='white', activebackground='pink', activeforeground='white', command=self.cerrarVentana)
        self.boton_cerrar_bodega.grid(row=0, column=8, padx=5, sticky='ew')

    # INICIO TABLA PRINCIPAL
        
        self.tabla_principal = ttk.Treeview(self.frame_mid, show='headings', columns=('ID Codigo', 'Nombre', 'Precio de venta', 'Precio de compra', 'Cantidad disponible', 'Familia / Tipo', 'Porcentaje de ganancia', 'Cantidad Minima'))
        self.tabla_principal.grid(row=0, column=0, pady=20, sticky='nsew')

        scrollbar=ttk.Scrollbar(self.frame_mid, orient="vertical", command=self.tabla_principal.yview)
        scrollbar.grid(row=0, column=1,sticky="ns")
        self.tabla_principal.configure(yscrollcommand=scrollbar.set)

        self.tabla_principal.heading('ID Codigo', text='ID Codigo')
        self.tabla_principal.heading('Nombre', text='Nombre')
        self.tabla_principal.heading('Precio de venta', text='Precio de venta')
        self.tabla_principal.heading('Precio de compra', text='Precio de compra')
        self.tabla_principal.heading('Cantidad disponible', text='Cantidad disponible')
        self.tabla_principal.heading('Familia / Tipo', text='Familia / Tipo')
        self.tabla_principal.heading('Porcentaje de ganancia', text='Porcentaje de ganancia')
        self.tabla_principal.heading('Cantidad Minima', text='Cantidad Minima')

        self.tabla_principal.column('Cantidad Minima', width=110)
        self.tabla_principal.column("Precio de venta", anchor='e')
        self.tabla_principal.column("Precio de compra", anchor='e')
        self.tabla_principal.column("Cantidad disponible", anchor='e')
        self.tabla_principal.column('Familia / Tipo', anchor='center')

        self.mostrarProductos()

    # FIN TABLA PRINCIPAL     

    # Botones CRUD
        
        # Boton agregar
        self.boton_agregar = tk.Button(
                            self.frame_bottom, text='Agregar', font=('Segoe UI', 14, 'bold'), command=self.funcionesBotonAgregar,
                            bg="#0F6431", fg='white', activebackground='#45B97C', activeforeground='white', state='normal',
                            borderwidth=1
                            )
        self.boton_agregar.grid(row=0, column=1, padx=5, pady=10, sticky='nsew')

        # Boton editar
        self.boton_editar = tk.Button(
                            self.frame_bottom, text='Editar', font=('Segoe UI', 14, 'bold'), command=self.abrirBodegaProducto,
                            bg='#F4D03F', fg='#1C2833', activebackground='#D4AC0D', activeforeground='#1C2833', state='disabled',
                            borderwidth=1
                            )
        self.boton_editar.grid(row=0, column=2, padx=5, pady=10, sticky='nsew')
        
        # Boton eliminar
        self.boton_eliminar = tk.Button(
                                self.frame_bottom, text='Eliminar', font=('Segoe UI', 14, 'bold'), command=self.abrirBodegaEliminar,
                                bg='#EC7063', fg='white', activebackground='#C0392B', activeforeground='white', state='disabled',
                                borderwidth=1
                                )
        self.boton_eliminar.grid(row=0, column=3, padx=5, pady=10, sticky='nsew')

        #BINDS
        self.tabla_principal.bind("<<TreeviewSelect>>", self.enableDisableBotones)



    # FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES

    def cerrarVentana(self):
        self.root_bodega.destroy()

    def abrirBodegaProducto(self):
        datos = self.getFilaProducto()
        if datos == ():
            BodegaProducto(self.root_bodega, self.mostrarProductos)
            self.barra_de_busqueda.delete(0, tk.END)
            self.barra_de_busqueda.focus_set() # Foco en el campo de código
        else:
            codigo = str(datos[0])
            BodegaProducto(self.root_bodega, self.mostrarProductos, codigo)
            self.barra_de_busqueda.delete(0, tk.END)
            self.barra_de_busqueda.focus_set()

    def abrirBodegaEliminar(self):
        datos = self.getFilaProducto()
        cod = str(datos[0]).strip()
        BodegaEliminar(self.root_bodega, cod, self.mostrarProductos)
        self.barra_de_busqueda.delete(0, tk.END)

    def mostrarProductos(self):
        # Eliminar datos
        for item in self.tabla_principal.get_children():
            self.tabla_principal.delete(item)

        # Vuelve a llenar
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()
            
        cursor.execute('SELECT * FROM Productos')
        all_productos = cursor.fetchall()

        conexion.close()

        for r in all_productos:
            self.tabla_principal.insert('', tk.END, values=self.formatear_producto(r))

     

    def getFilaProducto(self):
        fila = self.tabla_principal.selection()
        if fila:
            datos = self.tabla_principal.item(fila, 'values')
            # Aseguramos que el ID_Producto sea string, manteniendo ceros a la izquierda
            datos = (str(datos[0]),) + tuple(datos[1:])
            return datos
        return ()

    
    def deseleccionarFila(self):
        self.tabla_principal.selection_remove(self.tabla_principal.selection())

    def funcionesBotonAgregar(self):
        self.deseleccionarFila()
        self.abrirBodegaProducto()

    def enableDisableBotones(self, event):
        seleccion = self.tabla_principal.selection()
        if seleccion:
            self.boton_editar.config(state='normal')
            self.boton_eliminar.config(state='normal')
        else:
            self.boton_editar.config(state='disabled')
            self.boton_eliminar.config(state='disabled')

    def Filtro_Busqueda(self, Producto):
        try:
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            Filtro = self.filtro_seleccionado.get()

            for item in self.tabla_principal.get_children():
                self.tabla_principal.delete(item)

            if Filtro == 'Nombre':
                cursor.execute("SELECT * FROM Productos WHERE Nombre_Producto LIKE ?", ('%'+ Producto.strip() + '%',))
                registros = cursor.fetchall()

                if registros:
                    for registro in registros:
                        self.tabla_principal.insert('', 'end', values=self.formatear_producto(registro))
                else:
                    messagebox.showinfo("Error","No se encontró ningun producto", parent=self.root_bodega)
                    self.barra_de_busqueda.delete(0, tk.END)
                    self.mostrarProductos()

            elif Filtro == 'Código':
                cursor.execute("SELECT * FROM Productos WHERE ID_Producto=?", (Producto.strip(),))
                registros = cursor.fetchall()
                if registros:
                    for registro in registros:
                        self.tabla_principal.insert('', 'end', values=self.formatear_producto(registro))
                        BodegaProducto(self.root_bodega, self.mostrarProductos, cod_producto=registro[0])
                        self.barra_de_busqueda.delete(0, tk.END)
                else:
                    messagebox.showinfo("Error","No se encontró ningun producto", parent=self.root_bodega)
                    self.barra_de_busqueda.delete(0, tk.END)
                    self.mostrarProductos()
            else:
                messagebox.showinfo("Error","No se encontró ningun producto", parent=self.root_bodega)

        except sqlite3.Error as e:
            messagebox.showinfo(message=f"Ocurrió un error {e}")

        finally:
            if 'conexion' in locals():
                conexion.close()  


    def Mostrar_Familias(self, Familia):
        try:
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            if Familia == 'Todas las familias/tipo':
                cursor.execute("SELECT * FROM Productos")
            else:
                cursor.execute("SELECT * FROM Productos WHERE Familia_Tipo=?", (Familia,))

            registros = cursor.fetchall()

            for item in self.tabla_principal.get_children():
                self.tabla_principal.delete(item)

            if registros:
                for r in registros:
                    self.tabla_principal.insert('', 'end', values=self.formatear_producto(r))

        except sqlite3.Error as e:
            messagebox.showinfo(title="Error", message=f"Ocurrió un error {e}", parent=self.root_bodega)

        finally:
            if 'conexion' in locals():
                conexion.close()

    def buscar_codigo(self, event=None):
        Producto = self.barra_de_busqueda.get()
        if Producto:
            self.Filtro_Busqueda(Producto)
        else:
            messagebox.showinfo("Informacion", "Ingrese codigo de barras valido", parent=self.root_bodega)

    def Filtro_Familias(self):
        Familia = self.familia_seleccionada.get()
        if Familia:
            self.Mostrar_Familias(Familia)
        else:
            messagebox.showinfo("No se encontró ningun producto de esta familia", parent=self.root_bodega)
    def obtenerFamilias(self):
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        cursor.execute('SELECT DISTINCT Familia_Tipo FROM Productos')
        familias = [fila[0] for fila in cursor.fetchall()]

        conexion.close()
    
        return familias
    
    def exportarAExcel(self):
        archivo_excel = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")],
            title="Guardar archivo Excel",
            parent=self.root_bodega
        )

        if not archivo_excel:
            return
        
        try:
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()
            cursor.execute("SELECT ID_Producto, Nombre_Producto, Precio_Venta, Precio_Compra, Cantidad_Disponible, Familia_Tipo, Porcentaje_Ganancia, Cantidad_Minima FROM Productos")
            datos = cursor.fetchall()
            conexion.close()

            df = pd.DataFrame(datos, columns=['Código', 'Producto', 'P. Venta', 'P. Costo', 'Existencia', 'Departamento', "Ganancia %", 'Inv. Mínimo', ])
            df.to_excel(archivo_excel, index=False)
            df['Ganancia %'] = df['Ganancia %'] / 100 
           
            with pd.ExcelWriter(archivo_excel, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Productos")

        
                workbook = writer.book
                worksheet = writer.sheets["Productos"]

       
                formato_moneda = workbook.add_format({"num_format": '"$"#,##0', "align": "right"})
                formato_entero = workbook.add_format({"num_format": "0", "align": "center"})
                formato_porcentaje = workbook.add_format({"num_format": "0%", "align": "center"})
                formato_texto = workbook.add_format({"align": "left"})

        
                worksheet.set_column("A:A", 10, formato_entero)     # Código
                worksheet.set_column("B:B", 30, formato_texto)      # Producto
                worksheet.set_column("C:D", 15, formato_moneda)     # P. Venta, P. Costo
                worksheet.set_column("E:E", 12, formato_entero)     # Existencia
                worksheet.set_column("F:F", 20, formato_texto)      # Departamento
                worksheet.set_column("G:G", 12, formato_porcentaje) # Ganancia %
                worksheet.set_column("H:H", 12, formato_entero) # Inv. Mínimo

        
                worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
            messagebox.showinfo("Éxito", "El inventario se exportó correctamente.", parent=self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al exportar:\n{e}", parent=self.ventana)
    
    def importarInventario(self):
    
        from unidecode import unidecode
        archivo_excel = filedialog.askopenfilename(
        title="Selecciona el archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        ,parent=self.root_bodega
        )

        if not archivo_excel:
            return
        
        try:

            df=pd.read_excel(archivo_excel)
            
            df_sql = df.rename(columns={
            'Código': 'ID_Producto',
            'Producto': 'Nombre_Producto',
            'P. Costo': 'Precio_Compra',
            'P. Venta': 'Precio_Venta',
            'Existencia': 'Cantidad_Disponible',
            'Inv. Mínimo': 'Cantidad_Minima',
            'Departamento': 'Familia_Tipo'
            })
            # Función para limpiar números con formato latino: puntos para miles y coma para decimales
            def limpiar_num_latino(valor):
                if pd.isna(valor):
                    return 0.0
                valor_str = str(valor).strip()
                # Eliminar cualquier símbolo de moneda o espacios
                valor_str = valor_str.replace("$", "").replace(" ", "")
                # Quitar separadores de miles y decimales
                valor_str = valor_str.replace(".", "").split(",")[0]

                
                try:
                    return float(valor_str)
                except:
                    return 0.0

            # Aplicar la limpieza a las columnas numéricas
            for col in ["Precio_Compra", "Precio_Venta"]:
                df_sql[col] = df_sql[col].apply(limpiar_num_latino).astype(int)
            
            for col in ["Cantidad_Disponible", "Cantidad_Minima"]:
                df_sql[col] = df_sql[col].apply(limpiar_num_latino).astype(int)

            
                

            
            # Otros campos
    
            df_sql["ID_Producto"] = df_sql["ID_Producto"].apply(lambda x: str(x).replace(".0", "") if pd.notna(x) else "")
            df_sql["Nombre_Producto"] = df_sql["Nombre_Producto"].astype(str).str.strip()
            df_sql["Familia_Tipo"] = df_sql["Familia_Tipo"].astype(str).str.strip()

            df_sql["Porcentaje_Ganancia"] = df_sql.apply(lambda row: 
                round(((row["Precio_Venta"] - row["Precio_Compra"]) / row["Precio_Compra"] * 100) 
                if row["Precio_Compra"] > 0 else 0, 2), axis=1)

            conn= sqlite3.connect(self.ruta_bdd)
            cursor= conn.cursor()

            errores = []

            for index, row in df_sql.iterrows():
                try:
                    if not row["Nombre_Producto"] or row["Nombre_Producto"].strip() == "":
                        raise ValueError("Nombre de producto vacío o inválido")
                    
                    
                    cursor.execute("""
                            INSERT OR REPLACE INTO Productos 
                            (ID_Producto, Nombre_Producto, Precio_Venta, Precio_Compra, Cantidad_Disponible, Familia_Tipo, Porcentaje_Ganancia, Cantidad_Minima)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                row["ID_Producto"], 
                                row["Nombre_Producto"], 
                                row["Precio_Venta"], 
                                row["Precio_Compra"], 
                                row["Cantidad_Disponible"], 
                                row["Familia_Tipo"], 
                                row["Porcentaje_Ganancia"],
                                row["Cantidad_Minima"]
                            )
                        )

                    
                except Exception as e:
                    errores.append(f"Fila {index + 2} (ID: {row.get('ID_Producto')}): {str(e)}")

        
            conn.commit()
            conn.close()
            if errores:
                error_texto = "\n".join(errores)
                messagebox.showwarning("Importación parcial", f"Algunas filas no se importaron:\n\n{error_texto}", parent=self.ventana)
            else:
                messagebox.showinfo("Éxito", "El inventario se importó correctamente.", parent=self.ventana)
        except Exception as e:
            messagebox.showerror("Error general", f"❌ Error inesperado:\n{e}", parent=self.ventana)

    def abrir_menu(self):

        self.ventana=tk.Toplevel(self.root_bodega)
        self.ventana.title("Importar/Exportar inventario desde Excel")
        self.ventana.geometry("420x320")
        self.ventana.resizable(False, False)
        self.ventana.focus_force()

        self.ventana.grid_rowconfigure((0,1,2), weight=1)
        self.ventana.grid_columnconfigure((0,1), weight=1)

        label_seleccion = tk.Label(self.ventana, text="Seleccione una opción", font=("Segoe UI", 12, "bold"))
        label_seleccion.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10,20))

        boton_importar = tk.Button(self.ventana, text="📥 Importar inventario", font=("Segoe UI", 10, "bold"), bg="#0F6431", fg="white", activebackground="#1E8449", activeforeground="white", width= 18, height=2, command=self.importarInventario)
        boton_importar.grid(row=1, column= 0, padx=15, pady=10)

        boton_exportar = tk.Button(self.ventana, text="📤 Exportar inventario", font=("Segoe UI", 10, "bold"), bg="#5064AC", fg="white", activebackground="#1A5276", 
        activeforeground="white",
        width=18, height=2, command=self.exportarAExcel)
        boton_exportar.grid(row= 1, column=1, padx= 15, pady=10)

        boton_cancelar = tk.Button(self.ventana, text="✖ Cancelar", font=("Segoe UI", 10, "bold"), bg="#E74C3C", fg="white", activebackground="#922B21", 
        activeforeground="white",
        width=25, height=2, command=self.ventana.destroy)
        boton_cancelar.grid(row= 2, column=0, columnspan=2, pady=(15, 20))
        self.ventana.bind("<Escape>", lambda e: self.ventana.destroy())

    def reporte_mensual(self):
        ReporteMensual()
    
    def formatear_producto(self, r):
        id_producto = r[0] if r[0] is not None else ""
        nombre = str(r[1]).strip()
        precio_venta = f"${int(r[2]):,}".replace(",", ".") if r[2] is not None else "$0"
        precio_compra = f"${int(r[3]):,}".replace(",", ".") if r[3] is not None else "$0"
        cantidad_disp = int(r[4]) if r[4] is not None else 0
        familia_tipo = str(r[5]).strip() if r[5] is not None else ""
        porcentaje_ganancia = f"{r[6]}%" if r[6] is not None else "0%"
        cantidad_minima = int(r[7]) if r[7] is not None else 0
        
        return (id_producto, nombre, precio_venta, precio_compra,
                cantidad_disp, familia_tipo, porcentaje_ganancia,
                cantidad_minima)
