import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import datetime
from datetime import datetime
import sys
import os
import shutil
import re

from bodega import Bodega
from historial_ventas import HistorialVentas
from cierre_caja import Cierre_Caja
from tipo_venta import TipoVenta
from deudores import Deudores
from migraciones import ejecutar_migraciones

def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  
    else:
        base_path = os.path.abspath(".")  

    return os.path.join(base_path, relative_path)

class PuntoDeVenta():
    def __init__(self, root=None):
        if root is None:
            root = tk.Tk()
            es_ventana_principal = True
        else:
            es_ventana_principal = False

        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.confirmar_cierre)
        self.es_ventana_principal = es_ventana_principal
        self.ruta_bdd = resource_path('database\BDD_MINIMARKET.db')
        ejecutar_migraciones(self.ruta_bdd)

        if isinstance(self.root, (tk.Tk, tk.Toplevel)):
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            width = int(screen_width * 0.98)
            height = int(screen_height * 0.95)
            self.root.geometry(f"{width}x{height}")
            self.root.minsize(1024, 768)
            self.root.title("Punto de venta")
            self.root.state('zoomed')
            # Hacer root completamente expandible
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            # Icono de la app
            ruta_icono = resource_path("icono.png")
            icono = tk.PhotoImage(file=ruta_icono)  
            root.iconphoto(True, icono)


        

    # Creacion del Frame
        self.frame_principal = tk.Frame(self.root, bg="lightgrey")
        self.frame_principal.grid(row=0, column=0, sticky="nsew")
        self.frame_principal.grid_columnconfigure(0, weight=4)
        self.frame_principal.grid_columnconfigure(1, weight=3)
        self.frame_principal.grid_rowconfigure(0, weight=0)  # para frame_top
        self.frame_principal.grid_rowconfigure(1, weight=1)  # para left y right frames

    # Estilo tabla
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 9, "bold"),
                        background="#D5D8DC")

        
    # Top Frame
        self.frame_top = tk.Frame(self.frame_principal, bg='lightgrey', pady=5)
        self.frame_top.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5)
        for i in range(6):
            self.frame_top.grid_columnconfigure(i, weight=1)
        self.frame_top.grid_rowconfigure(2, weight=2)

        # Barra de accesos rápidos (POS)
        self.frame_accesos = tk.Frame(self.frame_top, bg="lightgrey")
        self.frame_accesos.grid(row=0, column=3, columnspan=2, sticky="e", padx=10)

        btn_style = dict(font=("Segoe UI", 11, "bold"), fg="white", bd=0, padx=14, pady=8, cursor="hand2")

        self.btn_bodega = tk.Button(
        self.frame_accesos, text="(F6) Bodega", bg="#2C3E50", activebackground="#1F2A36", borderwidth= 1,
        command=self.abrirVentanaBodega, **btn_style
    )
        self.btn_bodega.pack(side="left", padx=6)

        self.btn_historial = tk.Button(
        self.frame_accesos, text="(F7) Historial", bg="#2C3E50", activebackground="#1F2A36", borderwidth= 1,
        command=self.abrirVentanaHistorialVentas, **btn_style
    )
        self.btn_historial.pack(side="left", padx=6)

        self.btn_deudores = tk.Button(
            self.frame_accesos, text="(F8) Deudores", bg="#2C3E50", activebackground="#1F2A36", borderwidth= 1,
            command=self.abrirVentanaDeudores, **btn_style
        )
        self.btn_deudores.pack(side="left", padx=6)

        self.btn_cierre = tk.Button(
            self.frame_accesos, text="(F9) Cierre Caja", bg="#F35644", activebackground="#E74C3C", borderwidth= 1,
            command=self.abrirCierreCaja, **btn_style
        )
        self.btn_cierre.pack(side="left", padx=6)

        self.root.bind("<F6>", lambda e: self.abrirVentanaBodega())
        self.root.bind("<F7>", lambda e: self.abrirVentanaHistorialVentas())
        self.root.bind("<F8>", lambda e: self.abrirVentanaDeudores())
        self.root.bind("<F9>", lambda e: self.abrirCierreCaja())
    # Left Frame
        self.frame_left = tk.Frame(self.frame_principal, bg="#BCEBBC", padx=10, pady=10)
        self.frame_left.grid(row=1, column=0, sticky='nsew')
        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(0, weight=1)


    # Right Frame
        self.frame_right = tk.Frame(self.frame_principal, bg='lightcyan', padx=10, pady=10)
        self.frame_right.grid(row=1, column=1, sticky='nsew')
        for r in range(7):
            self.frame_right.grid_rowconfigure(r, weight=1)

        self.frame_right.grid_columnconfigure(0, weight=0)  
        self.frame_right.grid_columnconfigure(1, weight=1)  
         

        

    # Menu
        if isinstance(self.root, (tk.Tk, tk.Toplevel)):
            self.barra_menu = tk.Menu(root)

        # Buscador
        self.label_buscador_texto = tk.Label(self.frame_top, text="Buscar:", bg='lightgrey', font=("Segoe UI", 12, "bold"))
        self.label_buscador_texto.grid(row=0, column=1, padx=(5, 2), sticky="e")

        self.label_buscador_entrada = tk.Entry(self.frame_top, font=("Segoe UI", 12), width=60, justify='left')
        self.label_buscador_entrada.grid(row=0, column=2, padx= 2, pady= 10, sticky= "ew")
        self.label_buscador_entrada.bind("<KeyRelease>", self.mostrar_sugerencia)

        self.popup_sugerencias = None
        
    # Entrada codigo de producto
        self.label_codigo_producto = tk.Label(self.frame_right, text='Código:', bg='lightcyan', font=("Segoe UI", 14, "bold"))
        self.label_codigo_producto.grid(row=0, column=0, sticky='ns', padx=(5, 0), pady=3)
        

        vcmd=(self.root.register(self.validar_input), '%P')

        self.entrada_codigo_producto = tk.Entry(self.frame_right, font=('Arial', 10), validate='key', validatecommand=vcmd)
        self.entrada_codigo_producto.grid(row=0, column=1,columnspan= 2, sticky='ew', padx=(0,10), pady=3)
        self.entrada_codigo_producto.bind('<Return>', self.agregarProducto)
        self.entrada_codigo_producto.bind("<Up>", self.mover_seleccion_treeview)
        self.entrada_codigo_producto.bind("<Down>", self.mover_seleccion_treeview)
        self.entrada_codigo_producto.focus_set()
        
    
    # Campo de muestra de producto seleccionado
        self.texto_entrada = tk.StringVar(value="")
        self.datos_producto_seleccionado = tk.Entry(self.frame_right, state='readonly', font=('Arial', 10),
                                                    textvariable=self.texto_entrada)
        self.datos_producto_seleccionado.grid(row=2, column=0, columnspan=2, sticky='ew', padx=3, pady=3)

        # Cantidad
        self.cantidad_producto_seleccionado = tk.Entry(self.frame_right, font=('Arial', 10), width=10, justify='center')
        self.cantidad_producto_seleccionado.grid(row=2, column=2, sticky='ew', padx=3, pady=3)
        self.cantidad_producto_seleccionado.bind('<Return>', self.actualizar_cantidad_manual)
        self.cantidad_producto_seleccionado.bind('<FocusOut>', self.actualizar_cantidad_manual)

    # Labels informativos en el ingreso
        self.label1_nombre_precio = tk.Label(self.frame_right, text='Nombre / Precio', bg='lightcyan', font=("Segoe UI", 13, "bold"))
        self.label1_nombre_precio.grid(row=1, column=0, columnspan=2, sticky='ns', padx=3)
        self.label2_cantidad = tk.Label(self.frame_right, text='Cantidad', bg='lightcyan', font=("Segoe UI", 13, "bold"))
        self.label2_cantidad.grid(row=1, column=2, sticky='ns', padx=3)

    # Botones de Editar, Borrar y Agregar en right frame
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=1)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.boton_precio_promo = tk.Button(
            self.frame_right,
            text="💲 Aplicar Precio Promo",
            command=self.aplicar_precio_promo,
            bg="#F4D03F",
            font=("Segoe UI", 12, "bold")
        )
        

    # Total a pagar
        self.label_total_a_pagar = tk.Label(self.frame_right, justify='center', pady=70, font=('Impact', 44), bg='lightcyan',
                                            text='Total: $0') # Esto despues sera referenciado con textVariable
        
        self.label_total_a_pagar.grid(row=4, column=0, columnspan=3, sticky='nsew', padx=3, pady=3)

    # Botones de Concretar venta y Eliminar todo
        self.boton_eliminar_todo = tk.Button(self.frame_right, text='Cancelar', height=3, font=('Impact', 20), command=self.cancelarVenta,
                                             bg="#ED6859", fg='white', activebackground='#E74C3C', activeforeground='black')
        self.boton_eliminar_todo.grid(row=5, column=0, padx=3, pady=3, sticky='nsew')

        self.boton_concretar_venta = tk.Button(self.frame_right, text='(F12) Confirmar venta', height=3, font=('Impact', 20), command=self.confirmarVenta,
                                                bg='green', fg='white', activebackground='lightgreen', activeforeground='black')
        self.boton_concretar_venta.grid(row=5, column=1, columnspan=2, padx=3, pady=3, sticky='nsew')

    

        #Boton nueva venta
        self.ventas = []
        self.venta_actual = 0
        self.contador_ventas = 0

        self.label_venta = tk.Label(self.frame_top, text=f"Venta #{self.venta_actual + 1}", font=("Segoe UI", 18, "bold"), bg="#F7DC6F", fg="#154360", relief="ridge", bd=3, padx=20, pady=5)
        self.label_venta.grid(row=0, column=0, sticky="ew", padx=5)

        self.frame_botones_venta = tk.Frame(self.frame_right, bg='lightcyan')
        self.frame_botones_venta.grid(row=6, column=0, columnspan=3, pady=(20, 5), sticky="ew")
        self.frame_botones_venta.grid_columnconfigure(0, weight=1)
        self.frame_botones_venta.grid_columnconfigure(1, weight=2)
        self.frame_botones_venta.grid_columnconfigure(2, weight=1)


        btn_anterior = tk.Button(
        self.frame_botones_venta, text="⏮ Anterior", font=("Segoe UI", 12, "bold"),
        bg="#D6DBDF", fg="#154360", activebackground="#BFC9CA", activeforeground="#154360",
        command=self.venta_anterior, width=12
        )
        btn_anterior.grid(row=0, column=0, padx=10, sticky="w")

        frame_centro = tk.Frame(self.frame_botones_venta, bg='lightcyan')
        frame_centro.grid(row=0, column=1)

        btn_nueva_venta = tk.Button(
        frame_centro, text="🆕 Nueva Venta", font=("Segoe UI", 12, "bold"),
        bg="#58D68D", fg="white", activebackground="#45B39D", activeforeground="white",
        command=self.nueva_venta, width=14
        )
        btn_nueva_venta.pack(side="left", padx=10)

        btn_cerrar_venta = tk.Button(
        frame_centro, text="❌ Cerrar Venta", font=("Segoe UI", 12, "bold"),
        bg="#E74C3C", fg="white", activebackground="#922B21", activeforeground="white",
        command=self.cancelarVenta, width=14
        )
        btn_cerrar_venta.pack(side="left", padx=10)

        
        btn_siguiente = tk.Button(
        self.frame_botones_venta, text="Siguiente ⏭", font=("Segoe UI", 12, "bold"),
        bg="#D6DBDF", fg="#154360", activebackground="#BFC9CA", activeforeground="#154360",
        command=self.venta_siguiente, width=12
        )
        btn_siguiente.grid(row=0, column=2, padx=10, sticky="e")

        
        
        

    # Tabla de productos agregados en Frame Left
        self.tabla_productos = ttk.Treeview(self.frame_left, columns=('CODIGO', 'NOMBRE', 'CANTIDAD', 'PRECIO UNITARIO', 'PRECIO TOTAL'), show='headings', height=30)
        self.tabla_productos.grid(row=0, column=0,sticky="nsew",pady=(0,10))
        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(0, weight=1)

        self.tabla_productos.heading('CODIGO', text='CODIGO')
        self.tabla_productos.heading('NOMBRE', text='NOMBRE')
        self.tabla_productos.heading('CANTIDAD', text='CANTIDAD')
        self.tabla_productos.heading('PRECIO UNITARIO', text='PRECIO UNITARIO')
        self.tabla_productos.heading('PRECIO TOTAL', text='PRECIO TOTAL')

        self.tabla_productos.column('CODIGO', width=170)
        self.tabla_productos.column('NOMBRE', width=200)
        self.tabla_productos.column('CANTIDAD', width=100)
        self.tabla_productos.column('PRECIO UNITARIO', width=150)
        self.tabla_productos.column('PRECIO TOTAL', width=150)

        self.tabla_productos.bind('<Double-1>', self.dobleClickSeleccion)
        self.tabla_productos.bind("<Button-1>", self.seleccionar_sin_perder_focus)


        self.frame_label= tk.Frame(self.frame_left, bg="#A8A8A8")
        self.frame_label.grid(row= 0,column= 0, columnspan= 2, sticky= "sew")

        self.label_cantidad_productos=tk.Label(self.frame_label, text="0 Productos", font=("Segoe UI", 14, "bold"), bg= "#A8A8A8", fg="#154360", padx=8, pady= 4)
        self.label_cantidad_productos.grid(row= 0, column= 0, padx= 5)

        #BINDS BINDS BINDS
        self.root.bind("+", self.aumentar_cantidad)
        self.root.bind("-", self.disminuir_cantidad)
        self.root.bind('<F12>', lambda event: self.confirmarVenta())
        self.tabla_productos.bind("<Button-1>", self.ocultar_boton_promo)
        self.root.bind("<Delete>", self.eliminarProdLista)
        self.tabla_productos.bind("<Button-1>", self.click_en_tabla)

    # Variables globales
        self.ventanas_pago_abiertas = {}
        self._asegurar_tablas_deudores()
        self.alerta_deudores_pendientes()
        self.actualizar_badge_deudores() 
        self.venta_confirmada = []
        self.nueva_venta()
        self.contador_enter = 0
        self.verificacion_codigo = None
        self.nombre_getter = None
        self.precio_getter = None
        self.lista_productos = []
        self.es_aditivo = True
        self.suma_total = 0
        #self.Alertas_stock()
        self.producto_seleccionado_id = None
        self.var_venta_promo = tk.BooleanVar(value=False)
    
    # FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES

    def abrirVentanaBodega(self):
        Bodega(self.root)

    def abrirVentanaHistorialVentas(self):
        HistorialVentas(self.root)
    
    def abrirCierreCaja(self):
        Cierre_Caja(self.root)

    def cerrarYsalir(self):
        self.root.destroy()

    def abrirTipoVenta(self, id_venta):
        from tipo_venta import TipoVenta
        if id_venta in self.ventanas_pago_abiertas:
            ventana = self.ventanas_pago_abiertas[id_venta]
            if ventana.winfo_exists():
                ventana.lift()
                ventana.focus_force()
                return
            else:
                del self.ventanas_pago_abiertas[id_venta]
        total= self.suma_total
        ventana = TipoVenta(self, total, id_venta)

        self.ventanas_pago_abiertas[id_venta] = ventana
    
    def abrirVentanaDeudores(self):
        from deudores import Deudores
        d = Deudores(self.root, self.ruta_bdd)

        # al cerrar la ventana de deudores, refrescar badge
        try:
            d.ventana.protocol("WM_DELETE_WINDOW", lambda: (d.ventana.destroy(), self.actualizar_badge_deudores()))
        except:
            pass
    
    def _asegurar_tablas_deudores(self):
        con = sqlite3.connect(self.ruta_bdd)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Deudores (
                ID_Deuda INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Monto REAL NOT NULL,
                Fecha INTEGER NOT NULL,
                Estado TEXT NOT NULL DEFAULT 'PENDIENTE',
                Fecha_Pago INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Deudores_Detalle (
                ID_Detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Deuda INTEGER NOT NULL,
                ID_Producto TEXT,
                Nombre_Producto TEXT NOT NULL,
                Cantidad INTEGER NOT NULL,
                Precio_Unitario REAL NOT NULL,
                Subtotal REAL NOT NULL,
                FOREIGN KEY (ID_Deuda) REFERENCES Deudores(ID_Deuda)
            )
        """)
        con.commit()
        con.close()

    def alerta_deudores_pendientes(self):
        try:
            con = sqlite3.connect(self.ruta_bdd)
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM Deudores WHERE Estado='PENDIENTE'")
            n = cur.fetchone()[0]
            con.close()
            if n > 0:
                messagebox.showwarning("Deudores pendientes", f"⚠️ Tienes {n} deuda(s) pendiente(s).")
        except:
            pass

    def nueva_venta(self):
        nueva = {
        "productos": [],
        "numero": len(self.ventas) + 1,  # número visible de venta
        "total": 0.0
        }
        self.ventas.append(nueva)
        self.venta_confirmada.append(False)
        self.venta_actual = len(self.ventas) - 1

        self.actualizar_interfaz()

    def venta_anterior(self):
        pos = self.venta_actual - 1
        while pos >= 0:
            if not self.venta_confirmada[pos]:
                self.venta_actual = pos
                self.actualizar_interfaz()
                return
            pos -= 1
            

    def venta_siguiente(self):
        pos = self.venta_actual + 1
        while pos < len(self.ventas):
            if not self.venta_confirmada[pos]:
                self.venta_actual = pos
                self.actualizar_interfaz()
                return
            pos += 1

    def actualizar_interfaz(self):
        numero_venta = self.ventas[self.venta_actual].get("numero", self.venta_actual + 1)
        self.label_venta.config(text=f"Venta #{numero_venta}")

        # Cambia la lista de productos a la de la venta actual
        self.lista_productos = self.ventas[self.venta_actual]["productos"]
        self.suma_total = self.ventas[self.venta_actual]["total"]

        # Actualiza la tabla y el total
        self.mostrarListaProductos()
        self.actualizar_total()
        self.sumar_cantidades()
        self.label_total_a_pagar.config(text=f'Total: ${self.suma_total:,.0f}'.replace(",", "."))


        # Limpia los campos de entrada
        self.entrada_codigo_producto.delete(0, tk.END)
        self.cantidad_producto_seleccionado.delete(0, tk.END)
        self.datos_producto_seleccionado.config(state='normal') 
        self.datos_producto_seleccionado.delete(0, tk.END)
        self.datos_producto_seleccionado.config(state='readonly')

    # Funciones para la lista de productos
    def insertarProducto(self, lista):
        self.lista_productos.insert(0, lista)
        if len(self.ventas) == 0 or self.venta_actual >= len(self.ventas):
            self.nueva_venta()
        
        self.ventas[self.venta_actual]["productos"] = self.lista_productos
        self.ventas[self.venta_actual]["total"] = self.suma_total


    def eliminarProducto(self, codigo, event= None):
        for producto in self.lista_productos:
            if isinstance(producto, dict):
                if producto.get('ID') == codigo:
                    self.lista_productos.remove(producto)
                    break
            else:
                if producto[0] == codigo:
                    self.lista_productos.remove(producto)
                    break
        self.ventas[self.venta_actual]["productos"] = self.lista_productos
        self.ventas[self.venta_actual]["total"] = self.suma_total

    def obtenerProducto(self, codigo):
        for producto in self.lista_productos:
            if isinstance(producto, dict):
                if producto.get('ID') == codigo:
                    return producto
            else:
                if codigo == producto[0]:
                    return producto
        return []
    
    def eliminarAllProductos(self):
        self.lista_productos = []
        self.suma_total = 0
        self.ventas[self.venta_actual]["productos"] = self.lista_productos
        self.ventas[self.venta_actual]["total"] = self.suma_total
    # fin funciones para la lista de productos


    def mostrarListaProductos(self):
        
        self.suma_total = 0
        
        # Eliminar todos los productos de la tabla
        for fila in self.tabla_productos.get_children():
            self.tabla_productos.delete(fila)

        # Volver a ingresar los datos
        for i, producto in enumerate(self.lista_productos):
            if isinstance(producto, dict):
                # Producto común (manual) - diccionario
                codigo = producto.get('ID', '')
                nombre = producto.get('Nombre', '')
                cantidad = producto.get('Cantidad', 0)
                precio_unitario = producto.get('Precio', 0)
                
                try:
                    cantidad = int(cantidad)
                    precio_unitario = float(precio_unitario)
                except:
                    cantidad, precio_unitario = 0, 0

                precio_total = cantidad * precio_unitario
                producto['Total'] = precio_total
                

            else:
                codigo = producto[0]
                nombre = producto[1]
                cantidad = producto[2]
                precio_unitario = producto[3]

                try:
                    cantidad = int(cantidad)
                    precio_unitario = float(precio_unitario)
                except IndexError:
                     cantidad, precio_unitario = 0, 0 

                try:
                    precio_total = float(producto[4])
                except (IndexError, ValueError, TypeError):
                    precio_total = cantidad * precio_unitario
                    if len(producto) > 4:
                        producto[4] = precio_total
                    else:
                        producto.append(precio_total)

            if precio_unitario <= 0:
                continue

            precio_unitario_formateado = f"${precio_unitario:,.0f}".replace(",", ".")
            precio_total_formateado = f"${precio_total:,.0f}".replace(",", ".")

            valores = (codigo, nombre, cantidad, precio_unitario_formateado, precio_total_formateado)
            self.tabla_productos.insert('', '0', values=valores)

            self.suma_total += precio_total

        self.total_venta_real = sum(producto['Total'] if isinstance(producto, dict) else producto[4]
                             for producto in self.lista_productos)

        self.total_venta_formateado = f"${self.total_venta_real:,.0f}".replace(",", ".")

        self.label_total_a_pagar.config(text=f'Total: {self.total_venta_formateado}')
        self.ventas[self.venta_actual]["total"] = self.suma_total

    def getFechaList(self): # 'fecha' para los guardados en bdd
        dia = datetime.date.today().day
        mes = datetime.date.today().month
        anio = datetime.date.today().year   
        fecha = (dia * 1000000) + (mes * 10000) + (anio)
        return [fecha, dia, mes, anio]
    
    def descomponerFecha(self, fecha_int):
        anio = fecha_int % 10000
        fecha_int /= 10000
        mes = fecha_int % 100
        fecha_int /= 100
        dia = fecha_int

        return [dia, mes, anio]

    def getProductoByID(self, codigo):
        
        if codigo == '0':
            # Código 0: producto común (ingreso manual)
            return None
        
        try:
            
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()
            
            cursor.execute('SELECT Nombre_Producto, Precio_Venta, Cantidad_Disponible FROM Productos WHERE ID_Producto = ?', (codigo,))
            datos = cursor.fetchall()

            conexion.close()

            if datos:
                return datos[0]
            else:
                return None
        
        except Exception as e:
            messagebox.showerror('Ocurrió un problema con el producto', f'{e}\nCódigo inexistente')
    
    def ventana_producto_comun (self):
        ventana= tk.Toplevel(self.root)
        ventana.title("Producto Común")
        ventana.geometry("400x250")
        ventana.configure(bg="#F4F6F7")
        ventana.grab_set()

        # Título
        titulo = tk.Label(
            ventana,
            text="Ingresar Producto Común",
            font=("Segoe UI", 14, "bold"),
            bg="#2E86C1",
            fg="white",
            pady=10
        )
        titulo.grid(row=0, column=0, columnspan=2, sticky="ew")

        #LABEL NOMBRE
        tk.Label(ventana, text="Nombre:", font=("Segoe UI", 12), bg="#F4F6F7").grid(row=1, column=0, pady=10, padx=10, sticky="e")
        entry_nombre = tk.Entry(ventana, font=("Segoe UI", 12), width=25)
        entry_nombre.grid(row=1, column=1, pady=10, padx=10)
        entry_nombre.focus_set()

        #LABEL CANTIDAD
        tk.Label(ventana, text="Cantidad:", font=("Segoe UI", 12), bg="#F4F6F7").grid(row=2, column=0, pady=10, padx=10, sticky="e")
        entry_cantidad = tk.Entry(ventana, font=("Segoe UI", 12), width=25)
        entry_cantidad.grid(row=2, column=1, pady=10, padx=10)
        entry_cantidad.config(textvariable=tk.StringVar(value="1"))

        
        #LABEL PRECIO UNITARIO
        tk.Label(ventana, text="Precio Unitario:", font=("Segoe UI", 12), bg="#F4F6F7").grid(row=3, column=0, pady=10, padx=10, sticky="e")
        entry_precio_unitario = tk.Entry(ventana, font=("Segoe UI", 12), width=25)
        entry_precio_unitario.grid(row=3, column=1, pady=10, padx=10)

        # FRAME de botones
        frame_botones = tk.Frame(ventana, bg="#F4F6F7")
        frame_botones.grid(row=4, column=0, columnspan=2, pady=15)

        def agregar_manual():
            nombre = entry_nombre.get().strip()
            cantidad = entry_cantidad.get().strip()
            precio_unitario = entry_precio_unitario.get().strip()

            if not nombre or not cantidad or not precio_unitario:
                messagebox.showerror("Error", "Completa todos los campos", parent=ventana)
                return
            
            try:
                cantidad = int(cantidad)
                precio_unitario = float(precio_unitario)
                if cantidad <= 0 or precio_unitario <= 0:
                    raise ValueError("Cantidad y precio deben ser positivos")
                
            except Exception:
                messagebox.showerror("Error", "Cantidad y precio deben ser números válidos y positivos", parent=ventana)
                return
            
            
            
            producto_manual = {
                'ID': '0',
                'Nombre': nombre,
                'Cantidad': cantidad,
                'Precio': precio_unitario,
                }   
            
            try:
                # Normalizar datos del producto manual
                producto_manual['Precio'] = float(producto_manual.get('Precio', 0))
                producto_manual['Cantidad'] = int(producto_manual.get('Cantidad', 1))
                producto_manual['Subtotal'] = producto_manual['Precio'] * producto_manual['Cantidad']
            except Exception as e:
                messagebox.showerror("Error", f"Datos del producto común no válidos: {e}")
                return

            self.lista_productos.append(producto_manual)
            self.mostrarListaProductos()
            self.actualizar_total()
            self.sumar_cantidades()
            self.focus_primer_item()
            ventana.destroy()   
            
        btn_guardar = tk.Button(frame_botones, text="✔ Aceptar", font=("Segoe UI", 11, "bold"),
                            bg="#28B463", fg="white", width=12, command=agregar_manual)
        btn_guardar.grid(row=0, column=0, padx=10)
        btn_cancelar = tk.Button(frame_botones, text="✖ Cancelar", font=("Segoe UI", 11, "bold"),
                             bg="#E74C3C", fg="white", width=12, command=ventana.destroy)
        btn_cancelar.grid(row=0, column=1, padx=10)

        ventana.bind("<Return>", lambda event: agregar_manual())
        ventana.bind("<Escape>", lambda event: ventana.destroy())
        


    
    def mostrarProductosEnPantalla(self):   
        # Borra todos los elementos actuales del Treeview
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)

        # Insertar productos desde la lista
        for producto in self.lista_productos:
            if isinstance(producto, dict):  # Producto común
                codigo = producto["ID"]
                nombre = producto["Nombre"]
                cantidad = producto["Cantidad"]
                precio = producto["Precio"]
            else:
                codigo = producto[0]
                nombre = producto[1]
                cantidad = producto[2]
                precio = producto[3]
            
            subtotal = round(int(precio) * int(cantidad), 1)

            precio_formateado = f"${float(precio):,.0f}".replace(",", ".")
            subtotal_formateado = f"${float(subtotal):,.0f}".replace(",", ".")

            self.tabla_productos.insert("", "end", values=(codigo, nombre, cantidad, precio_formateado, subtotal_formateado))
        self.actualizar_total()

    def seRepiteCodigo(self):
        cod_entry = str(self.entrada_codigo_producto.get())
        # Verificar si el código ya existe en la tabla
        for item in self.tabla_productos.get_children():
            fila = self.tabla_productos.item(item)['values']
            if str(fila[0]) == cod_entry:  # Compara solo con el código de producto
                return True

        return False  # Si no se encuentra el código, retornar False 
    
    def existeCodigo(self, codigo):

        if codigo == "0":
            self.ventana_producto_comun()
            return True
        
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        cursor.execute('SELECT COUNT(*) FROM Productos WHERE ID_Producto = ?', (codigo,))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado[0] == 0:
            return False
        else:
            return True

    def cantidadDisponibleProducto(self, codigo):
        if codigo == '0':
            return float('inf')  
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        cursor.execute('SELECT Cantidad_Disponible FROM Productos WHERE ID_Producto = ?', (codigo,))
        resultado = cursor.fetchone()
        
        conexion.close()

        if resultado is None:
            return 0

        cantidad_disponible = resultado[0]
        return cantidad_disponible
    
    def agregarProducto(self, event = None, cantidad_a_agregar=1, codigo=None):
        if len(self.ventas) == 0:
            self.nueva_venta()  # Crear la primera venta si no existe
        # Si no hay ventas o la venta_actual está fuera de rango, crea una venta nueva
        if self.venta_actual >= len(self.ventas):
            self.venta_actual = len(self.ventas) - 1

        # Sincronizar lista de productos con la venta actual
        self.lista_productos = self.ventas[self.venta_actual].get("productos", [])

        if codigo is None:
            codigo = self.entrada_codigo_producto.get().strip()
            lista_sel = self.tabla_productos.selection()
            if lista_sel and not codigo:
                codigo = self.tabla_productos.item(lista_sel[0])['values'][0]

        if not codigo:
            return

        
        if codigo == "0":
            self.ventana_producto_comun()
            # Limpiar entrada para nuevo código
            self.entrada_codigo_producto.delete(0, tk.END)
            self.cantidad_producto_seleccionado.delete(0, tk.END)
            self.datos_producto_seleccionado.config(state='normal')
            self.datos_producto_seleccionado.delete(0, tk.END)
            self.datos_producto_seleccionado.config(state='readonly')
            self.entrada_codigo_producto.focus_set()
            return
        
        
        if not self.existeCodigo(codigo):
            messagebox.showerror('Error', f'Producto con código {codigo} no existe')
            self.entrada_codigo_producto.delete(0, tk.END)
            return
        
        
        datos_producto = self.getProductoByID(codigo)
        if datos_producto is None:
            messagebox.showerror("Error", "Producto no encontrado en la base de datos")
            self.entrada_codigo_producto.delete(0, tk.END)
            return
        
        self.nombre_getter = datos_producto[0]
        self.precio_getter = datos_producto[1]
        self.cantidad_getter = datos_producto[2]

        
        # Verificar si ya está el producto en la lista
        producto_existente = None
        for producto in self.lista_productos:
            if isinstance(producto, dict):
                if producto.get('ID') == codigo:
                    producto_existente = producto
                    break
            else:
                if producto[0] == codigo:
                    producto_existente = producto
                    break

        
        cantidad_actual = producto_existente['Cantidad'] if isinstance(producto_existente, dict) else producto_existente[2] if producto_existente else 0

        # Verificar stock para la cantidad que quedaría
        if self.verificar_stock(codigo, cantidad_actual + cantidad_a_agregar):
            if not self.stock_apuro(codigo, desde_bind=False):
                return
        
        if producto_existente:
            if isinstance(producto_existente, dict):
                producto_existente['Cantidad'] += cantidad_a_agregar
            else:
                producto_existente[2] += cantidad_a_agregar
                producto_existente[4] = producto_existente[2] * producto_existente[3]
        else:
            # Si no existe, agregar nuevo producto con cantidad 1
            nuevo_prod = [
                codigo,
                self.nombre_getter,
                cantidad_a_agregar,  # cantidad
                self.precio_getter,
                cantidad_a_agregar * self.precio_getter
            ]
            
            self.insertarProducto(nuevo_prod)

        # Ahora sí puedes asignar productos a la venta actual
        self.ventas[self.venta_actual]["productos"] = self.lista_productos


        self.mostrarProductosEnPantalla()
        self.focus_primer_item()
        self.sumar_cantidades()

        # Limpiar entradas para el próximo código
        self.entrada_codigo_producto.delete(0, tk.END)
        self.cantidad_producto_seleccionado.delete(0, tk.END)
        self.datos_producto_seleccionado.config(state='normal')
        self.datos_producto_seleccionado.delete(0, tk.END)
        self.datos_producto_seleccionado.config(state='readonly')
        self.entrada_codigo_producto.focus_set()

        

    def dobleClickSeleccion(self, event):
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            return
        item = self.tabla_productos.item(seleccion[0])  # Solo la primera selección
        datos = item['values']

        codigo = datos[0]
        nombre = datos[1]
        cantidad = datos[2]
        precio = datos[3]

        self.entrada_codigo_producto.delete(0, tk.END)
        self.entrada_codigo_producto.insert(0, codigo)

        self.datos_producto_seleccionado.config(state='normal')
        self.datos_producto_seleccionado.delete(0, tk.END)
        self.datos_producto_seleccionado.insert(0, f'{nombre} - ${precio}')
        self.datos_producto_seleccionado.config(state='readonly')

        self.cantidad_producto_seleccionado.delete(0, tk.END)
        self.cantidad_producto_seleccionado.insert(0, cantidad)

        self.es_aditivo = False
        self.contador_enter = 1

        self.producto_seleccionado_id = seleccion[0]

        self.boton_precio_promo.grid(row=3, column=0, columnspan=3, sticky="ew", pady= 5)
            

    def eliminarProdLista(self):
        codigo_existe = self.entrada_codigo_producto.get()

        if codigo_existe != '':
            self.eliminarProducto(str(self.entrada_codigo_producto.get()))
            self.mostrarListaProductos()
        else:
            messagebox.showerror('Error', 'No hay un producto seleccionado a eliminar')

    def confirmarVenta(self):
        hijos_tabla_principal = self.tabla_productos.get_children()
        
        if hijos_tabla_principal:
            productos = self.lista_productos
            no_disponible = []

            # Confirmacion de la cantidad de productos
            for p in productos:
                if isinstance(p, dict):
                    codigo = p.get('ID', None)
                    cantidad_lista = p.get('Cantidad', 0)
                else:
                    codigo = p[0]
                    cantidad_lista = int(p[2])

                # Si es producto común, lo saltamos
                if str(codigo) == '0':
                    continue

                cantidad_en_bd = self.cantidadDisponibleProducto(codigo)
                
                
                if cantidad_en_bd < cantidad_lista:
                    no_disponible.append(codigo)

            numero_venta = self.ventas[self.venta_actual].get("numero", self.venta_actual + 1)
            # Si esta disponible
            if not no_disponible:
                if numero_venta in self.ventanas_pago_abiertas:
                    w = self.ventanas_pago_abiertas[numero_venta]
                    if w.winfo_exists():
                        w.lift()
                        w.focus_force()
                        return
                    else:
                    # quedó referencia muerta
                        del self.ventanas_pago_abiertas[numero_venta]

                from tipo_venta import TipoVenta
                total = self.suma_total
                tv = TipoVenta(self, total, productos)

                self.ventanas_pago_abiertas[numero_venta] = tv.tipoventa

            else:
                # Si no esta disponible
                for cod_producto_nd in no_disponible:
                    conexion = sqlite3.connect(self.ruta_bdd)
                    cursor = conexion.cursor()
                
                    cursor.execute('SELECT * FROM Productos WHERE ID_Producto = ?', (cod_producto_nd,))
                    datos = cursor.fetchall()

                    conexion.close()
                    if datos:
                        prod = datos[0]
                        messagebox.showwarning('Hubo un problema',
                                        f'La cantidad disponible de {prod[1]} ({prod[4]}) es menor a la que se quiere vender.')
                    else:
                        messagebox.showwarning('Hubo un problema',
                        f'El producto con código {cod_producto_nd} no se encontró en la base de datos.')
                    
        else:
            messagebox.showerror('Hubo un problema', 'No hay productos agregados')
            return
        
    def cancelarVenta(self):
        if not self.ventas:
        # No hay ventas para cancelar
            return
        
        if not self.venta_confirmada[self.venta_actual]:
            self.eliminarAllProductos()
            self.mostrarListaProductos()
        # Contar cuántas ventas NO están confirmadas
        ventas_activas = [i for i, confirmada in enumerate(self.venta_confirmada) if not confirmada]
        # Si solo queda una venta activa y es la actual, no permitir cerrarla
        if len(ventas_activas) == 1 and ventas_activas[0] == self.venta_actual:
            return
        
        # Verifica si la venta actual NO está confirmada para eliminarla
        if not self.venta_confirmada[self.venta_actual]:
            # Eliminar la venta actual y su estado de confirmación
            del self.ventas[self.venta_actual]
            del self.venta_confirmada[self.venta_actual]
            
            # Ajustar índice para mostrar otra venta no confirmada
            pos = self.venta_actual - 1
            while pos >= 0 and self.venta_confirmada[pos]:
                pos -= 1
            if pos >= 0:
                self.venta_actual = pos
                self.actualizar_interfaz()
            else:
                # No hay ventas no confirmadas hacia atrás, buscar hacia adelante
                pos = self.venta_actual
                while pos < len(self.ventas) and self.venta_confirmada[pos]:
                    pos += 1
                if pos < len(self.ventas):
                    self.venta_actual = pos
                    self.actualizar_interfaz()
                else:
                    # No hay ventas no confirmadas, crear nueva
                    self.nueva_venta()
        
        

    def soloNumero(self, char):
        return 


    def Ventas(self):
        Producto= self.label_buscador_entrada.get().strip()

        if Producto:
            self.Mostrar_Ventas(Producto)   
        else:
            messagebox.showwarning(title="Error", message="No se encontró producto")


    

    def Mostrar_Ventas(self, Producto):
        try:
            conexion= sqlite3.connect(self.ruta_bdd)
            cursor= conexion.cursor()

            cursor.execute("SELECT ID_Producto, Nombre_Producto, Precio_Venta FROM Productos WHERE Nombre_Producto LIKE ?", ("%" + Producto.strip() + "%", ))
            registros= cursor.fetchall()
            
            if registros:
                for registro in registros:
                    codigo= registro[0]
                    nombre= registro[1]
                    precio_venta= registro[2]
                    cantidad=1
                    precio_total = precio_venta * cantidad
                    existe= False



                    for item in self.tabla_productos.get_children():
                        valores_existentes = self.tabla_productos.item(item)['values']
                        if valores_existentes[0] == codigo:
                            existe = True
                            break

                    if not existe:
                        self.tabla_productos.insert("", "end", values=(codigo, nombre, cantidad, precio_venta, precio_total))


        except sqlite3.Error as e:
            print(f"Ocurrió un error {e}")

        finally:
            if conexion in locals():
                conexion.close()

    def Agregar_producto_bind(self, event= None):
        try: 
            seleccion= self.tabla_productos.selection()

            item= seleccion[0]
            valores_existentes= self.tabla_productos.item(item)["values"]
            ID_Producto= valores_existentes[0]

            conexion= sqlite3.connect(self.ruta_bdd)
            cursor= conexion.cursor()
            
            cursor.execute("SELECT ID_Producto, Nombre_Producto, Precio_Venta FROM Productos WHERE ID_Producto=?",(ID_Producto, ))
            producto= cursor.fetchone()

            if producto:
                if self.verificar_stock(ID_Producto) == True:
                        return
                ID_Producto, Nombre_Producto, Precio_Venta = producto

                self.tabla_productos.insert("", "end", values=(ID_Producto, Nombre_Producto, Precio_Venta))
                messagebox.showinfo("Éxito", f"Producto '{Nombre_Producto}' agregado a la venta.")
            self.sumar_cantidades()
        except sqlite3.Error as e:
            messagebox.showinfo(title="Informacion", message= f"{e}")


    def Alertas_stock(self):

        conn=sqlite3.connect(self.ruta_bdd)
        cursor=conn.cursor()

        cursor.execute("SELECT ID_Producto, Cantidad_Disponible, Cantidad_Minima, Nombre_Producto FROM Productos")
        resultados=cursor.fetchall()

        if resultados:
            for resultado in resultados:
                if resultado[1] <= resultado[2]:
                    messagebox.showwarning(title="Informacion", message= f"Falta re stock del siguiente producto\n Codigo: {resultado[0]}\n Nombre Producto: {resultado[3]}\n Cantidad Disponible: {resultado[1]}")
        conn.close()
    

    def aumentar_cantidad(self, event=None, desde_stock_apuro=False):
        seleccion=self.tabla_productos.selection()

        if not seleccion:
            return
        item= seleccion[0]
        valores = list(self.tabla_productos.item(item, "values"))
        codigo_tabla_str = str(valores[0]).strip()
        cantidad_tabla = int(valores[2])
        nombre_tabla = str(valores[1]).strip()    

        
        producto_encontrado = None
        for idx, producto in enumerate(self.lista_productos):
            if isinstance(producto, dict):
                id_producto_str = str(producto.get('ID')).strip()
                if id_producto_str == codigo_tabla_str and producto['Cantidad'] == cantidad_tabla and producto['Nombre'].strip() == nombre_tabla:
                    producto_encontrado = producto
                    break
            else:
                id_producto_str = str(producto[0]).strip()
                nombre_producto = str(producto[1]).strip()
                cantidad_producto = producto[2]
                if id_producto_str == codigo_tabla_str and cantidad_producto == cantidad_tabla and nombre_producto == nombre_tabla:
                    producto_encontrado = producto
                    break
        if not producto_encontrado:
            return

        cantidad_actual = producto_encontrado['Cantidad'] if isinstance(producto_encontrado, dict) else producto_encontrado[2]

        if not desde_stock_apuro and self.verificar_stock(codigo_tabla_str, cantidad_actual + 1):
            if not self.stock_apuro(codigo_tabla_str, desde_bind=True):
                return
        
        # Aumentar la cantidad
        if isinstance(producto_encontrado, dict):
            producto_encontrado['Cantidad'] += 1
            subtotal = producto_encontrado['Cantidad'] * producto_encontrado['Precio']
            precio = producto_encontrado['Precio']
        else:
            producto_encontrado[2] += 1
            subtotal = producto_encontrado[2] * producto_encontrado[3]
            precio = producto_encontrado[3]

        # Actualizar la tabla
        nuevos_valores = [
            producto_encontrado['ID'] if isinstance(producto_encontrado, dict) else producto_encontrado[0],
            producto_encontrado['Nombre'] if isinstance(producto_encontrado, dict) else producto_encontrado[1],
            producto_encontrado['Cantidad'] if isinstance(producto_encontrado, dict) else producto_encontrado[2],
            f"${precio:,.0f}".replace(',', '.'),
            f"${subtotal:,.0f}".replace(',', '.')
        ]
        self.tabla_productos.item(item, values=nuevos_valores)


        self.ventas[self.venta_actual]["productos"] = self.lista_productos
        self.ventas[self.venta_actual]["total"] = self.suma_total
        self.actualizar_total()
        self.sumar_cantidades()

    def disminuir_cantidad(self, event=None):
        seleccion= self.tabla_productos.selection()
        if not seleccion:
            return
        item = seleccion[0]
        valores = list(self.tabla_productos.item(item, "values"))
        codigo_tabla_str = str(valores[0]).strip()
        cantidad_tabla = int(valores[2])
        nombre_tabla = str(valores[1]).strip()

        for producto in self.lista_productos:
            if isinstance(producto, dict):
                id_producto_str = str(producto.get('ID')).strip()
                if id_producto_str == codigo_tabla_str and producto['Cantidad'] == cantidad_tabla and producto['Nombre'].strip() == nombre_tabla:
                    producto_encontrado = producto
                    break
            else:
                id_producto_str = str(producto[0]).strip()
                nombre_producto = str(producto[1]).strip()
                cantidad_producto = producto[2]
                if id_producto_str == codigo_tabla_str and cantidad_producto == cantidad_tabla and nombre_producto == nombre_tabla:
                    producto_encontrado = producto
                    break
        if not producto_encontrado:
                    return
        
        if isinstance(producto_encontrado, dict):
            producto_encontrado['Cantidad'] -= 1
            if producto_encontrado['Cantidad'] <= 0:
                self.lista_productos.remove(producto_encontrado)
                self.tabla_productos.delete(item)
            else:
                precio_formateado = f"${producto_encontrado['Precio']:,.0f}".replace(",", ".")
                subtotal_formateado = f"${producto_encontrado['Cantidad'] * producto['Precio']:,.0f}".replace(",", ".")
                nuevos_valores = [
                    producto_encontrado['ID'], producto_encontrado['Nombre'], producto_encontrado['Cantidad'], 
                    precio_formateado, subtotal_formateado
                ]

                self.tabla_productos.item(item, values=nuevos_valores)
        else:
            producto_encontrado[2] -= 1
            if producto_encontrado[2] <= 0:
                self.lista_productos.remove(producto_encontrado)
                self.tabla_productos.delete(item)
            else:
                precio_formateado = f"${producto_encontrado[3]:,.0f}".replace(",", ".")
                subtotal_formateado = f"${producto_encontrado[2] * producto_encontrado[3]:,.0f}".replace(",", ".")
                nuevos_valores = [
                    producto_encontrado[0], producto_encontrado[1], producto_encontrado[2], 
                    precio_formateado, subtotal_formateado
                ]
                self.tabla_productos.item(item, values=nuevos_valores)
                    
        self.ventas[self.venta_actual]["productos"] = self.lista_productos
        self.ventas[self.venta_actual]["total"] = self.suma_total
        self.actualizar_total()
        self.sumar_cantidades()

    def actualizar_total(self):
        self.suma_total = 0

        for idx, producto in enumerate(self.lista_productos):
            if isinstance(producto, dict):
                subtotal = producto['Cantidad'] * producto['Precio']
                self.suma_total += subtotal
                # actualizar subtotal en el dict
                producto['Subtotal'] = subtotal  

                # actualizar fila en tabla
                item_id = self.tabla_productos.get_children()[idx]
                precio_formateado = f"${producto['Precio']:,.0f}".replace(",", ".")
                subtotal_formateado = f"${subtotal:,.0f}".replace(",", ".")
                nuevos_valores = [
                    producto['ID'],
                    producto['Nombre'],
                    producto['Cantidad'],
                    precio_formateado,
                    subtotal_formateado
                ]
                self.tabla_productos.item(item_id, values=nuevos_valores)
            else:
                subtotal = producto[2] * producto[3]
                self.suma_total += subtotal
                # actualizar fila en tabla
                item_id = self.tabla_productos.get_children()[idx]
                precio_formateado = f"${producto[3]:,.0f}".replace(",", ".")
                subtotal_formateado = f"${subtotal:,.0f}".replace(",", ".")
                nuevos_valores = [
                    producto[0],
                    producto[1],
                    producto[2],
                    precio_formateado,
                    subtotal_formateado
                ]
                self.tabla_productos.item(item_id, values=nuevos_valores)


        self.label_total_a_pagar.config(text=f'Total: ${self.suma_total:,.0f}'.replace(',', '.'))
        self.ventas[self.venta_actual]["total"] = self.suma_total
        self.sumar_cantidades()

    def actualizar_cantidad_manual(self, event=None):
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            return

        item = seleccion[0]
        valores = list(self.tabla_productos.item(item, "values"))
        codigo = valores[0]

        cantidad_actual = int(valores[2])
        nueva_cantidad_str = self.cantidad_producto_seleccionado.get().strip()

        if not nueva_cantidad_str:
            return

        try:
            nueva_cantidad = int(nueva_cantidad_str)
            if nueva_cantidad <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida. Debe ser un número entero positivo.")
            self.cantidad_producto_seleccionado.delete(0, tk.END)
            return
        
        stock_agregado = 0  # Contador de stock agregado
        while cantidad_actual < nueva_cantidad:
            if self.verificar_stock(codigo, cantidad_actual + 1):
                # Falta stock, agregar stock de apuro
                if not self.agregar_stock_apuro_codigo(codigo):
                    break
                stock_agregado += 1
            cantidad_actual += 1

        if stock_agregado > 0:
            messagebox.showinfo("Stock agregado", f"Se agregaron {stock_agregado} unidades de stock de apuro.")


        # Actualizar cantidad en lista_productos y tabla
        for producto in self.lista_productos:
            if isinstance(producto, dict):
                if producto.get('ID') == codigo:
                    producto['Cantidad'] = cantidad_actual
                    precio_formateado = f"${producto['Precio']:,.0f}".replace(",", ".")
                    subtotal_formateado = f"${producto['Cantidad'] * producto['Precio']:,.0f}".replace(",", ".")
                    nuevos_valores = [
                        producto['ID'], producto['Nombre'], producto['Cantidad'], 
                        precio_formateado, subtotal_formateado
                    ]
                    self.tabla_productos.item(item, values=nuevos_valores)
                    break
            elif not isinstance(producto, dict):
                if producto[0] == codigo:
                    producto[2] = cantidad_actual
                    precio_formateado = f"${producto[3]:,.0f}".replace(",", ".")
                    subtotal_formateado = f"${producto[2] * producto[3]:,.0f}".replace(",", ".")
                    nuevos_valores = [
                        producto[0], producto[1], producto[2], 
                        precio_formateado, subtotal_formateado
                    ]
                    self.tabla_productos.item(item, values=nuevos_valores)
            else:
                continue
        
            
        
        self.entrada_codigo_producto.delete(0, tk.END)
        self.cantidad_producto_seleccionado.delete(0, tk.END)
        self.texto_entrada.set("")

        self.ventas[self.venta_actual]["productos"] = self.lista_productos
        self.actualizar_total()
        self.ventas[self.venta_actual]["total"] = self.suma_total

        self.tabla_productos.selection_remove(item)
        self.sumar_cantidades()


    def mostrar_sugerencia(self, event=None):

        if event.keysym in ("Up", "Down", "Return"):
            return
        
        texto = self.label_buscador_entrada.get().strip()

        if not texto:
            if self.popup_sugerencias:
                self.cerrar_popup()
            return
        
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        cursor.execute("SELECT ID_Producto, Nombre_Producto, Precio_Venta FROM Productos WHERE LOWER(Nombre_Producto) LIKE ?", ("%" + texto.lower() + "%", ))
        resultados = cursor.fetchall()
        conexion.close()

        if not resultados:
            if self.popup_sugerencias:
                self.cerrar_popup()
            return
        
        if not self.popup_sugerencias:
            self.popup_sugerencias = tk.Toplevel(self.root)
            self.popup_sugerencias.wm_overrideredirect(True)
            self.popup_sugerencias.lift()
            

            self.lista_sugerencias = tk.Listbox(self.popup_sugerencias, font=("Segoe UI", 12), width=60, height=6)
            self.lista_sugerencias.pack(fill="both", expand=True)

            #BINDS
            self.lista_sugerencias.bind("<<ListboxSelect>>", self.agregar_producto_desde_sugerencia)
            self.label_buscador_entrada.bind("<Escape>", lambda e: self.cerrar_popup())
            self.label_buscador_entrada.bind("<Return>", self.agregar_producto_desde_sugerencia)
            self.label_buscador_entrada.bind("<Up>", self.mover_cursor_listbox)
            self.label_buscador_entrada.bind("<Down>", self.mover_cursor_listbox)

        # Ubicar popup justo debajo del entry
        x = self.label_buscador_entrada.winfo_rootx()
        y = self.label_buscador_entrada.winfo_rooty() + self.label_buscador_entrada.winfo_height()
        self.popup_sugerencias.geometry(f"+{x}+{y}")

        self.lista_sugerencias.delete(0, tk.END)

        if resultados:
            
            for r in resultados:
                self.lista_sugerencias.insert(tk.END, f"{r[0]} - {r[1]}")   
            
        
    def agregar_producto_desde_sugerencia(self, event=None):
        if not self.lista_sugerencias.size():
            return
        
        if self.lista_sugerencias.curselection():
            seleccion = self.lista_sugerencias.curselection()
        else:
            seleccion = (0,)
            self.lista_sugerencias.selection_set(0)
        
        item = self.lista_sugerencias.get(seleccion[0])
        codigo = item.split(" - ")[0]

        self.cerrar_popup()

        self.label_buscador_entrada.delete(0, tk.END)
        self.entrada_codigo_producto.insert(0, codigo)
        self.agregarProducto(codigo=codigo)

    def cerrar_popup(self):
        if self.popup_sugerencias:
            self.popup_sugerencias.destroy()
            self.entrada_codigo_producto.focus_set()
            self.label_buscador_entrada.delete(0, tk.END)
            self.popup_sugerencias = None

    def mover_cursor_listbox(self, event=None):
        try:
            if not self.lista_sugerencias.size():
                return
            
            if not self.lista_sugerencias.curselection():
                self.lista_sugerencias.selection_set(0)
                return "break"

            index = self.lista_sugerencias.curselection()[0]

            if event.keysym == "Up":
                nuevo_index = max(0, index - 1)
            elif event.keysym == "Down":
                nuevo_index = min(self.lista_sugerencias.size() - 1, index + 1)
            else:
                return

            # Quitar selección anterior y marcar la nueva
            self.lista_sugerencias.selection_clear(0, tk.END)
            self.lista_sugerencias.selection_set(nuevo_index)
            self.lista_sugerencias.activate(nuevo_index)
            
            self.lista_sugerencias.see(nuevo_index)

            return "break"

        except Exception as e:
            print("Error al mover cursor:", e)


    def stock_apuro(self, codigo=None, desde_bind=False):
        if codigo is None:
            codigo = self.entrada_codigo_producto.get().strip()

        self.ventana_stock= tk.Toplevel(self.root)
        self.ventana_stock.title("Agregar Stock de Apuro")
        self.ventana_stock.geometry("450x250")
        self.ventana_stock.resizable(False,False)
        self.ventana_stock.grab_set()
        self.ventana_stock.focus_force()

        # Fondo de la ventana
        self.ventana_stock.configure(bg="#f0f2f5")

        # Frame central tipo card
        frame_card = tk.Frame(self.ventana_stock, bg="white", bd=2, relief="raised")
        frame_card.place(relx=0.5, rely=0.5, anchor="center", width=400, height=180)
            
        # Etiquetas
        label1 = tk.Label(frame_card, text="¡No hay stock de este producto!", 
                      font=("Segoe UI", 14, "bold"), bg="white", fg="#e53935")
        label1.pack(pady=(20, 10))

        label2 = tk.Label(frame_card, text="¿Desea agregar stock para la venta actual?", 
                      font=("Segoe UI", 12), bg="white")
        label2.pack(pady=(0, 20))

        # Frame para botones
        frame_botones = tk.Frame(frame_card, bg="white")
        frame_botones.pack(pady=(0, 15))

        self.btn_confirmar= tk.Button(frame_botones, text="Confirmar", font=("Segoe UI", 12, "bold"), bg="#4caf50", fg="white", activebackground="#45a049",
                              width=12, command= lambda: self.agregar_stock_apuro(codigo, desde_bind))
        self.btn_confirmar.grid(row= 0, column= 0, padx= 10)
        self.ventana_stock.bind("<Return>", lambda event: self.agregar_stock_apuro(codigo, desde_bind))

        self.btn_cancelar= tk.Button(frame_botones, text="Cancelar", font=("Segoe UI", 12, "bold"), bg="#f44336", fg="white", activebackground="#d32f2f",
                             width=12, command= self.ventana_stock.destroy)
        self.btn_cancelar.grid(row= 0, column= 1, padx= 10)
        self.ventana_stock.bind("<Escape>", lambda event: self.ventana_stock.destroy())

    def agregar_stock_apuro(self, codigo, desde_bind=False):
        conexion= sqlite3.connect(self.ruta_bdd)
        cursor= conexion.cursor()
       
        cursor.execute("UPDATE Productos SET Cantidad_Disponible = Cantidad_Disponible + 1 WHERE ID_Producto = ?", (codigo, ))

        conexion.commit()
        conexion.close()

        if desde_bind:
            self.aumentar_cantidad(desde_stock_apuro=True)
        else:
            self.agregarProducto(cantidad_a_agregar=1)

        messagebox.showinfo("Exito", "Se agregó stock correctamente", parent= self.root)
        self.ventana_stock.destroy()
    
    def agregar_stock_apuro_codigo(self, codigo):
        conexion= sqlite3.connect(self.ruta_bdd)
        cursor= conexion.cursor()
       
        cursor.execute("UPDATE Productos SET Cantidad_Disponible = Cantidad_Disponible + 1 WHERE ID_Producto = ?", (codigo, ))

        conexion.commit()
        conexion.close()

        return True
    
    def verificar_stock(self, codigo, cantidad_deseada):
        
        conexion= sqlite3.connect(self.ruta_bdd)
        cursor= conexion.cursor()

        cursor.execute("SELECT Cantidad_Disponible FROM Productos WHERE ID_Producto = ?", (codigo, ))
        fila = cursor.fetchone()
        conexion.close()

        if fila:
            stock = fila[0]
            if stock <= 0 or cantidad_deseada > stock:
                return True
            
        return False
    
    def focus_primer_item(self):
        hijos = self.tabla_productos.get_children()
        if hijos:
            self.tabla_productos.focus(hijos[0])
            self.tabla_productos.selection_set(hijos[0])
            self.tabla_productos.see(hijos[0])
            return
        
    def validar_input(self, texto):
        # Solo permite letras y números (sin tildes ni símbolos)
        return re.match("^[a-zA-Z0-9]*$", texto) is not None


    def sumar_cantidades(self):
        cantidad= 0
        self.label_cantidad_productos.config(text=f" {cantidad} Productos")

        for item in self.tabla_productos.get_children():
            fila= self.tabla_productos.item(item, "values")
            try:
                cantidad += int(fila[2])
            except:
                continue
        self.label_cantidad_productos.config(text=f"{cantidad} Productos")
    
    def confirmar_cierre(self):
        respuesta = messagebox.askyesno("Cerrar aplicación", "¿Estás seguro que quieres cerrar la ventana sin confirmar el cierre?")
        if respuesta:
            self.crear_respaldo()
            self.root.destroy()

    def crear_respaldo(self):
        try:
            # Carpeta de respaldos
            backup_folder = resource_path("respaldos")
            os.makedirs(backup_folder, exist_ok=True)

            # Nombre del archivo con fecha y hora
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_folder, f"BDD_MINIMARKET_{fecha}.db")

            # Ruta completa del respaldo
            

            # Copiar archivo
            shutil.copy2(self.ruta_bdd, backup_file)
            messagebox.showinfo("Exito", f"✅ Respaldo creado: {backup_file}")

        except Exception as e:
            messagebox.showerror("Error", f"⚠️ Error al crear respaldo: {e}")
    def mover_seleccion_treeview(self, event):
        tree = self.tabla_productos
        seleccion = tree.selection()
        
        # Si no hay selección, seleccionar la primera fila
        if not seleccion:
            first = tree.get_children()[0]
            tree.selection_set(first)
            tree.see(first)
            return "break"

        item = seleccion[0]
        hijos = tree.get_children()
        index = hijos.index(item)

        if event.keysym == "Up" and index > 0:
            tree.selection_set(hijos[index-1])
            tree.see(hijos[index-1])
        elif event.keysym == "Down" and index < len(hijos)-1:
            tree.selection_set(hijos[index+1])
            tree.see(hijos[index+1])

        return "break"  # Evita que el cursor del Entry se mueva
    
    def seleccionar_sin_perder_focus(self, event):
        item = self.tabla_productos.identify_row(event.y)
        if item:
            self.tabla_productos.selection_set(item)
        # Devolver foco al Entry
        self.entrada_codigo_producto.focus_set()
        return "break"

    def contar_deudores_pendientes(self):
        try:
            con = sqlite3.connect(self.ruta_bdd)
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM Deudores WHERE Estado='PENDIENTE'")
            n = cur.fetchone()[0]
            con.close()
            return n
        except:
            return 0
    
    def actualizar_badge_deudores(self):
        n = self.contar_deudores_pendientes()
        if n > 0:
            self.btn_deudores.config(text=f"(F8) Deudores: {n}", bg="#C0392B", activebackground="#922B21")
        else:
            self.btn_deudores.config(text="(F8) Deudores", bg="#2C3E50", activebackground="#2C3E50")

    def aplicar_precio_promo(self):
        if not self.producto_seleccionado_id:
            return

        item = self.producto_seleccionado_id
        valores = self.tabla_productos.item(item, "values")

        codigo = valores[0]
        nombre = valores[1]

        ventana = tk.Toplevel(self.root)
        ventana.title("Precio Promocional")
        ventana.geometry("300x150")

        tk.Label(ventana, text="Precio Promocional (Unitario)", font=("Segoe UI", 11, "bold")).pack(pady=5)

        entrada = tk.Entry(ventana)
        entrada.pack(pady=5)
        entrada.focus()

        def confirmar():
            try:
                texto = entrada.get().replace(",", ".")
                nuevo_precio = float(texto)

                index = self.tabla_productos.index(item)
                producto = self.lista_productos[index]

                # 🔹 Producto normal (lista)
                if isinstance(producto, list):
                    producto[3] = nuevo_precio            
                    producto[4] = producto[2] * nuevo_precio  

                # 🔹 Producto común (dict)
                elif isinstance(producto, dict):
                    if "ID" in producto:
                        producto["Precio"] = nuevo_precio


                self.var_venta_promo.set(True)
                self.mostrarListaProductos()
                self.actualizar_total()

                self.limpiar_panel_derecho()
                ventana.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Error real: {e}", parent=ventana)

        tk.Button(ventana, text="Aplicar",bg= "green",fg="white", font= ("Segoe UI", 11, "bold"), command=confirmar).pack(pady=5)

    def ocultar_boton_promo(self, event):
        item = self.tabla_productos.identify_row(event.y)
        if not item:
            self.boton_precio_promo.grid_remove()
            self.producto_seleccionado_id = None
    
    def limpiar_panel_derecho(self):
        self.datos_producto_seleccionado.config(state="normal")
        self.datos_producto_seleccionado.delete(0,tk.END)
        self.datos_producto_seleccionado.config(state="readonly")
        self.cantidad_producto_seleccionado.delete(0, tk.END)
        self.producto_seleccionado_id = None
        self.entrada_codigo_producto.delete(0, tk.END)
        self.boton_precio_promo.grid_remove()
        self.focus_primer_item()
        self.entrada_codigo_producto.focus_set()

    def click_en_tabla(self, event):
        item = self.tabla_productos.identify_row(event.y)

        if not item:
            self.tabla_productos.selection_remove(self.tabla_productos.selection())
            self.limpiar_panel_derecho()

        # 🔥 devolver focus después del click
        self.root.after(1, self.entrada_codigo_producto.focus_set)

    