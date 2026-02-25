import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import sqlite3
import sys
import os
import re

from Top_Ventas import TopVentas
from reporte_diario import ReporteDiario

def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  
    else:
        base_path = os.path.abspath(".")  

    return os.path.join(base_path, relative_path)

class HistorialVentas:
    def __init__(self, root):
    # Ruta a la base de datos
        self.ruta_bdd = resource_path('database\BDD_MINIMARKET.db')

    # Ajustes de ventana
        self.root_historial_ventas = tk.Toplevel()
        self.root_historial_ventas.title('Historial de ventas')
        self.root_historial_ventas.state('zoomed')
        self.root_historial_ventas.grid_rowconfigure(0, weight=1)
        self.root_historial_ventas.grid_columnconfigure(0, weight=1)

    # Creacion del Frame principal
        self.frame_principal = tk.Frame(self.root_historial_ventas, bg='lightcyan')
        self.frame_principal.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        self.frame_principal.grid_rowconfigure(0, weight=2)
        self.frame_principal.grid_rowconfigure(1, weight=3)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(1, weight=1)

    # Frame left (Historial de ventas)
        self.frame_left = tk.Frame(self.frame_principal, bg='#91C491')
        self.frame_left.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=10, pady=10)
        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(0, weight=1)

    # Frame top right (Busqueda y filtros)
        self.frame_top_right = tk.Frame(self.frame_principal, bg='#91C491')
        self.frame_top_right.grid(row=0, column=1, sticky='nsew', padx=10, pady=0)
        self.frame_top_right.grid_rowconfigure(0, weight=2)
        self.frame_top_right.grid_rowconfigure(1, weight=3)
        self.frame_top_right.grid_columnconfigure(0, weight=1)
        self.frame_top_right.grid_columnconfigure(1, weight=1)

    # Frame bot right (Desglose venta)
        self.frame_bot_right = tk.Frame(self.frame_principal, bg='#91C491')
        self.frame_bot_right.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)
        self.frame_bot_right.grid_rowconfigure(2, weight=1)
        self.frame_bot_right.grid_columnconfigure(0, weight=1)
        self.frame_bot_right.grid_columnconfigure(1, weight=1)
        self.frame_bot_right.grid_columnconfigure(2, weight=1)

    # Frame interno seccionde busqueda
        self.frame_interno_tr = tk.Frame(self.frame_top_right, bg='#91C491')
        self.frame_interno_tr.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.frame_interno_tr.grid_rowconfigure(0, weight=0)
        self.frame_interno_tr.grid_rowconfigure(1, weight=0)
        self.frame_interno_tr.grid_columnconfigure(0, weight=1)
        self.frame_interno_tr.grid_columnconfigure(1, weight=2)

        self.frame_top_tr = tk.Frame(self.frame_interno_tr, bg='#91C491')
        self.frame_top_tr.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.frame_top_tr.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="botones")
        

        self.frame_left_tr = tk.Frame(self.frame_interno_tr, bg='#91C491')
        self.frame_left_tr.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.frame_left_tr.grid_rowconfigure(0, weight=1)
        self.frame_left_tr.grid_columnconfigure(0, weight=1)

        self.frame_right_tr = tk.Frame(self.frame_interno_tr, bg='#91C491')
        self.frame_right_tr.grid(row=1, column=0, columnspan= 2, sticky='nsew', padx=5, pady=5)
        self.frame_right_tr.grid_rowconfigure(0, weight=0)
        self.frame_right_tr.grid_rowconfigure(1, weight=0)
        self.frame_right_tr.grid_rowconfigure(2, weight=1)
        self.frame_right_tr.grid_columnconfigure((0, 1), weight=1)
        

    # Parte superior del frame de busqueda
        self.top_ventas= tk.Button(self.frame_top_tr, text='Top Ventas', font=('Segoe UI', 14, "bold"),
                                          bg='#5064AC', fg='white', activebackground='lightblue', activeforeground='blue',  command= self.abrirTopVentas)
        self.top_ventas.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        self.reporte_diario= tk.Button(self.frame_top_tr, text="Reporte Semanal", font=('Segoe UI', 14, "bold"), width= 18, bg='#5064AC', fg='white', activebackground='lightblue', activeforeground='blue', command= self.abrirReporteDiario)
        self.reporte_diario.grid(row=0, column= 1, padx=10, pady= 5, sticky= "ew")

        self.boton_actualizar = tk.Button(self.frame_top_tr, text='Actualizar', font=("Segoe UI", 14, "bold"), command=self.funcionBotonActualizar,
                                          bg='#5064AC', fg='white', activebackground='lightblue', activeforeground='blue')
        self.boton_actualizar.grid(row=0, column=2, padx=10, pady= 5, sticky='ew')

        self.boton_cerrar_ventana = tk.Button(self.frame_top_tr, text='Cerrar ventana', font=("Segoe UI", 10, "bold"), command=self.cerrarVentana,
                                              bg='#EC7063', fg='white', activebackground='pink', activeforeground='black')
        self.boton_cerrar_ventana.grid(row=0, column=3, padx=10, pady= 5, sticky='ew')
        
        self.label_fecha_actual = tk.Label(self.frame_top_tr, font=('Segoe UI Semibold', 12, 'bold'), bg='#91C491')
        self.label_fecha_actual.grid(row=1, column=0, columnspan=4, sticky='ew', pady=(0, 5))
        self.ponerFechaActual()

    # Parte izquierda del frame de busqueda
        self.cb_filtrar_ultimos_var = tk.IntVar()
        self.cb_filtrar_ultimos = tk.Checkbutton(self.frame_right_tr, text='Filtrar por días:', font=('Segoe UI Semibold', 12), bg='#91C491', activebackground='#91C491',
                                                 variable=self.cb_filtrar_ultimos_var, command=lambda:self.unicaSeleccionEnFiltro(self.cb_filtrar_ultimos_var))
        self.cb_filtrar_ultimos.grid(row=0, column=0, pady=5, sticky="w")

        self.filtro_u_seleccionado = tk.StringVar()
        self.filtro_u_seleccionado.set('Hoy')
        self.menu_filtrar_ultimos = tk.OptionMenu(self.frame_right_tr, self.filtro_u_seleccionado,
                                                  'Hoy',
                                                  'Ayer',
                                                  '7 dias',
                                                  '15 dias',
                                                  '30 dias',
                                                  '45 dias')
        self.menu_filtrar_ultimos.grid(row=1, column=0, pady=5, sticky="n")
        self.menu_filtrar_ultimos.grid_remove()

    # Parte derecha del frame de busqueda
        self.cb_filtrar_fecha_var = tk.IntVar()
        self.cb_filtrar_fecha = tk.Checkbutton(self.frame_right_tr, text='Filtrar por fecha:', bg='#91C491', font=('Segoe UI Semibold', 12), activebackground='#91C491',
                                               variable=self.cb_filtrar_fecha_var, command=lambda: self.unicaSeleccionEnFiltro(self.cb_filtrar_fecha_var))
        self.cb_filtrar_fecha.grid(row=0, column=1, sticky="w", pady=5)

        # Filtros de fecha (Año, Mes, Día)
        self.frame_fechas = tk.Frame(self.frame_right_tr, bg='#91C491')
        self.frame_fechas.grid(row=1, column=1,  sticky="ew", padx=  3, pady= (0,15))
        self.frame_fechas.grid_columnconfigure(0, weight=1)
        self.frame_fechas.grid_columnconfigure(1, weight=1)
        self.frame_fechas.grid_columnconfigure(2, weight=1)
        self.frame_fechas.grid_remove()

        self.cb_dia_intvar = tk.IntVar()
        self.cb_mes_intvar = tk.IntVar()
        self.cb_anio_intvar = tk.IntVar()

        self.cb_anio = tk.Checkbutton(self.frame_fechas, text='Año', font=('Segoe UI Semibold', 12), bg='#91C491', variable=self.cb_anio_intvar, command= lambda:self.unicaSeleccionEnFiltroFecha(self.cb_anio_intvar))  
        self.cb_mes = tk.Checkbutton(self.frame_fechas, text='Mes', font=('Segoe UI Semibold', 12), bg='#91C491', variable=self.cb_mes_intvar, command=lambda: self.unicaSeleccionEnFiltroFecha(self.cb_mes_intvar))
        self.cb_dia = tk.Checkbutton(self.frame_fechas, text='Dia', font=('Segoe UI Semibold', 12), bg='#91C491', variable=self.cb_dia_intvar, command=lambda: self.unicaSeleccionEnFiltroFecha(self.cb_dia_intvar))

        self.cb_anio.grid(row=0, column=0, pady=5, sticky="w")
        self.cb_mes.grid(row=0, column=1, pady=5, sticky="w")
        self.cb_dia.grid(row=0, column=2, pady=5, sticky="w")

        self.lista_anios=['2024','2025','2026','2027','2028','2029'
                          ,'2030','2031','2032','2033','2034','2035','2036','2037','2038','2038',
                            '2040'
                        ]
        self.anio_select = tk.StringVar()
        self.anio_select.set('2024')


        self.menu_anio = tk.OptionMenu(self.frame_fechas, self.anio_select,
                                    *self.lista_anios) # Años de ejemplo, aqui va una lista
        self.mes_select = tk.StringVar()
        self.mes_select.set('1')
        self.menu_mes = tk.OptionMenu(self.frame_fechas, self.mes_select,
                                      '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')
        
        self.validacion = self.root_historial_ventas.register(self.soloNumero)

        self.entry_dia = tk.Entry(self.frame_fechas, width=6, justify='center', font=('Segoe UI Semibold', 12), validate='key', validatecommand=(self.validacion, '%S'))
        self.entry_dia.insert(0, '1')
        
        self.menu_anio.grid(row=1, column=0, sticky='n', padx= 5, pady= 10)
        self.menu_mes.grid(row=1, column=1, sticky='n', padx= 5, pady= 10)
        self.entry_dia.grid(row=1, column=2, sticky='n', padx= 5, pady= 10)


    # Frame Bot Right
        self.label_codigo_venta = tk.Label(self.frame_bot_right, text='Código (ID):',font=('Segoe UI Semibold', 10), bg='#91C491', anchor='e')
        self.label_codigo_venta.grid(row=0, column=0, pady=10, sticky='e')

        self.entrada_codigo_venta = tk.Entry(self.frame_bot_right, justify='center', state='readonly')
        self.entrada_codigo_venta.grid(row=0, column=1, columnspan=2, sticky='w', padx=5)

        self.label_fecha = tk.Label(self.frame_bot_right, text='Fecha:',font=('Segoe UI Semibold', 10), bg='#91C491', anchor='e')
        self.label_fecha.grid(row=1, column=0, pady=10, sticky='e')

        self.campo_muestra_fecha = tk.Entry(self.frame_bot_right, width=50, state='readonly', justify='center')
        self.campo_muestra_fecha.grid(row=1, column=1, sticky='w')

        self.campo_muestra_total = tk.Entry(self.frame_bot_right, width=50, state='readonly', justify='center')
        self.campo_muestra_total.grid(row=3, column=1, sticky='w')

        self.btn_cancelar = tk.Button(self.frame_bot_right, text="Eliminar Venta", font=('Segoe UI Semibold', 10), bg= "#EC7063", fg='white', activebackground='pink', activeforeground='black', command= self.eliminarventa)
        self.btn_cancelar.grid(row= 3, column= 2, padx= 10, sticky= "w")

        self.btn_editar = tk.Button(
            self.frame_bot_right,
            text="Editar Venta",
            font=('Segoe UI Semibold', 10),
            bg="#5064AC",
            fg='white',
            activebackground='lightblue',
            activeforeground='black',
            command=self.abrirEditarVenta
            )
        self.btn_editar.grid(row=3, column=3, padx=10, sticky="w")

        # INICIO TABLA DETALLE DE VENTA

        self.tabla_detalle = ttk.Treeview(self.frame_bot_right, columns=('NOMBRE', 'CANTIDAD', 'PRECIO UNITARIO', 'PRECIO TOTAL'), show='headings', height=13)
        self.tabla_detalle.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=30)

        self.tabla_detalle.heading('NOMBRE', text='NOMBRE')
        self.tabla_detalle.heading('CANTIDAD', text='CANTIDAD')
        self.tabla_detalle.heading('PRECIO UNITARIO', text='PRECIO UNITARIO')
        self.tabla_detalle.heading('PRECIO TOTAL', text='PRECIO TOTAL')

        self.tabla_detalle.column('CANTIDAD', width=70)
        self.tabla_detalle.column('PRECIO UNITARIO', width=110)
        self.tabla_detalle.column('PRECIO TOTAL', width=110)

        
        self.label_total = tk.Label(self.frame_bot_right, text='Total:',font=('Segoe UI Semibold', 10), bg='#91C491', anchor='e')
        self.label_total.grid(row=3, column=0, pady=10, sticky='e')
        

    # Tabla de historial de ventas en Frame Left
        self.tabla_historial = ttk.Treeview(self.frame_left, columns=('ID VENTA', 'FECHA', 'TOTAL', "METODO PAGO"), show='headings', height=32)
        self.tabla_historial.grid(row=0, column=0, sticky='nsew')

        scrollbar= ttk.Scrollbar(self.frame_left, orient="vertical", command=self.tabla_historial.yview)
        scrollbar.grid(row=0, column=1,sticky="ns")
        self.tabla_historial.configure(yscrollcommand=scrollbar.set)

        self.tabla_historial.heading('ID VENTA', text='ID VENTA')
        self.tabla_historial.heading('FECHA', text='FECHA')
        self.tabla_historial.heading('TOTAL', text='TOTAL')
        self.tabla_historial.heading('METODO PAGO', text='METODO PAGO')

        # Frame contenedor arriba del historial
        self.frame_resumen = tk.Frame(self.frame_left)
        self.frame_resumen.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Label para mostrar el total
        self.label_resumen_total = tk.Label(self.frame_resumen, text="Total Ventas: $0", font=("Segoe UI", 14, "bold"))
        self.label_resumen_total.grid(column=0, row= 0, padx=5)


        # FIN TABLA DETALLE DE VENTA

        

    # Variables y extras
        self.lista_historial_de_ventas = []
        self.lista_detalle_de_venta = []
        self.lista_datos_venta = []
        self.tabla_historial.bind('<Double-1>', self.guardaDetalleDesdeTabla)
        self.cb_filtrar_ultimos_var.set(1)   # marca el checkbutton
        self.menu_filtrar_ultimos.grid()
        self.ventasEnPlazo(1)
        self.imprimirVentasEnPantalla()
        self.sumar_totales()

    # FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES

    def cerrarVentana(self):
        self.root_historial_ventas.destroy()

    def ponerFechaActual(self):
        dia = datetime.date.today().day
        mes = datetime.date.today().month
        anio = datetime.date.today().year

        self.label_fecha_actual.config(text=f'Fecha actual: {dia} - {mes} - {anio}')

    # INICIO Herramientas para trabajar con las fechas (Retornan listas en este orden [dia, mes, año])
    def descomponerFecha(self, fecha_int):
        anio = fecha_int % 10000
        fecha_int //= 10000
        mes = fecha_int % 100
        fecha_int //= 100
        dia = fecha_int

        return [dia, mes, anio]
    
    def componerFecha(self, fecha_list):
        fecha_int = (fecha_list[0] * 1000000) + (fecha_list[1] * 10000) + (fecha_list[2])

        return fecha_int
    
    def restarDias(self, dias):
        fecha_actual = datetime.date.today()
        delta = datetime.timedelta(days=dias)
        fecha_resultado = fecha_actual - delta
        dia = fecha_resultado.day
        mes = fecha_resultado.month
        anio = fecha_resultado.year

        return [dia, mes, anio]

    def getFechaActual(self):
        dia = datetime.date.today().day
        mes = datetime.date.today().month
        anio = datetime.date.today().year

        return [dia, mes, anio]
    # FIN Herramientas para trabajar con las fechas (Retornan listas en este orden [dia, mes, año])

    # Funciones para el historial de ventas

    # Agrega a la lista de ventas las ventas en un plazo de x dias
    def ventasEnPlazo(self, dias):
        self.lista_historial_de_ventas = []
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        for i in range(dias):               # i = 0 => hoy, i = 1 => ayer, ...
            fecha_evaluada_list = self.restarDias(i)
            fecha_evaluada_int = self.componerFecha(fecha_evaluada_list)
            cursor.execute('SELECT * FROM Ventas WHERE Fecha_Venta = ?', (fecha_evaluada_int,))
            ventas_resultado = cursor.fetchall()
            for venta in ventas_resultado:
                self.lista_historial_de_ventas.append(venta)

        conexion.close()
    
    def ventasEnDia(self, dias_ago):
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        fecha_evaluada_list = self.restarDias(dias_ago)
        fecha_evaluada_int = self.componerFecha(fecha_evaluada_list)

        cursor.execute('SELECT * FROM Ventas WHERE Fecha_Venta = ?', (fecha_evaluada_int,))
        resultado = cursor.fetchall()
        conexion.close()
        return resultado


    # Toma las ventas que esten en lista_historial_de_ventas y las pone en la tabla grande
    def imprimirVentasEnPantalla(self):
        for fila in self.tabla_historial.get_children():
            self.tabla_historial.delete(fila)

        for venta in self.lista_historial_de_ventas:
            venta = list(venta)

            # Formatear fecha
            fecha_list = self.descomponerFecha(venta[1])
            fecha_str = f'{fecha_list[0]} - {fecha_list[1]} - {fecha_list[2]}'
            venta[1] = fecha_str

            # Formatear total
            try:
                venta[2] = f"${int(venta[2]):,}".replace(",", ".")
            except Exception:
                pass

            # ---- AGREGADO: MARCAR PRECIO PROMOCIONAL ----
            try:
                # venta[4] = Precio_Promocional (0 / 1)
                if venta[4] == 1:
                    venta[3] = f"{venta[3]} (PROMO)"
            except Exception:
                pass

            # Insertar en tabla (solo columnas visibles)
            self.tabla_historial.insert('', 'end', values=venta)

    
    def unicaSeleccionEnFiltro(self, cb_seleccionado):
        if cb_seleccionado == self.cb_filtrar_fecha_var:
            if self.cb_filtrar_fecha_var.get() == 1:
                self.cb_filtrar_ultimos_var.set(0)
                self.menu_filtrar_ultimos.grid_remove()
                self.frame_fechas.grid()
            else:
                self.frame_fechas.grid_remove()

        elif cb_seleccionado == self.cb_filtrar_ultimos_var:
            if self.cb_filtrar_ultimos_var.get() == 1:
                self.cb_filtrar_fecha_var.set(0)
                self.frame_fechas.grid_remove()
                self.menu_filtrar_ultimos.grid()
            else:
                self.menu_filtrar_ultimos.grid_remove()
        
        self.sumar_totales()

    # 1 para dia, 2 para mes, 3 para año
    def filtrarSegunFecha(self, dma_tipo, dma):
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        if dma_tipo == 1:
            cursor.execute('SELECT * FROM Ventas WHERE (Fecha_Venta / 1000000) = ?', (dma,))

        elif dma_tipo == 2:
            cursor.execute('SELECT * FROM Ventas WHERE ((Fecha_Venta / 10000) % 100) = ?', (dma,))

        elif dma_tipo == 3:
            cursor.execute('SELECT * FROM Ventas WHERE (Fecha_Venta % 10000) = ?', (dma,))

        resultado = cursor.fetchall()
        conexion.close()
        return resultado

    def mostrarAllVentas(self):
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        cursor.execute('SELECT * FROM Ventas')
        self.lista_historial_de_ventas = []
        self.lista_historial_de_ventas = cursor.fetchall()     

        conexion.close()
        self.imprimirVentasEnPantalla()

    def mostrarVentasFiltroDias(self):
        self.lista_historial_de_ventas = []

        opcion = self.filtro_u_seleccionado.get()

        if opcion == 'Hoy':
            self.ventasEnPlazo(1)               
        elif opcion == 'Ayer':
            self.lista_historial_de_ventas = self.ventasEnDia(1)
        elif opcion == '7 dias':
            self.ventasEnPlazo(7)               
        elif opcion == '15 dias':
            self.ventasEnPlazo(15)
        elif opcion == '30 dias':
            self.ventasEnPlazo(30)
        elif opcion == '45 dias':
            self.ventasEnPlazo(45)

        self.imprimirVentasEnPantalla()

    def mostrarVentasFiltroFecha(self):
        
        self.lista_historial_de_ventas = []

        try:
            dia = int(self.entry_dia.get())
            if dia < 1 or dia > 31:
                raise ValueError
        except:
            dia = 1
            self.entry_dia.delete(0, tk.END)
            self.entry_dia.insert(0, '1')

        mes = int(self.mes_select.get())
        anio = int(self.anio_select.get())

        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        query = 'SELECT * FROM Ventas WHERE 1=1'
        parametros = []

        if self.cb_dia_intvar.get() == 1:
            query += ' AND (Fecha_Venta / 1000000) = ?'
            parametros.append(dia)

        if self.cb_mes_intvar.get() == 1:
            query += ' AND ((Fecha_Venta / 10000) % 100) = ?'
            parametros.append(mes)

        if self.cb_anio_intvar.get() == 1:
            query += ' AND (Fecha_Venta % 10000) = ?'
            parametros.append(anio)

        # Si ningún checkbox está seleccionado, usar los tres valores por defecto
        if not (self.cb_dia_intvar.get() or self.cb_mes_intvar.get() or self.cb_anio_intvar.get()):
            fecha_int = self.componerFecha([dia, mes, anio])
            query = 'SELECT * FROM Ventas WHERE Fecha_Venta = ?'
            parametros = [fecha_int]

        cursor.execute(query, tuple(parametros))
        self.lista_historial_de_ventas = cursor.fetchall()

        conexion.close()
        self.imprimirVentasEnPantalla()

    def funcionBotonActualizar(self):
        if self.cb_filtrar_ultimos_var.get() == 1:
            self.mostrarVentasFiltroDias()

        elif self.cb_filtrar_fecha_var.get() == 1:
            self.mostrarVentasFiltroFecha()

        else:
            self.mostrarAllVentas()
        
        self.sumar_totales()


    def unicaSeleccionEnFiltroFecha(self, cb_seleccionado):
        self.sumar_totales()
        self.funcionBotonActualizar()

    # Funciones para el detalle de las ventas

    def imprimirDetalleEnPantalla(self, codigo = None):
        if codigo == None:
            codigo = self.lista_datos_venta[0]

        for producto in self.lista_detalle_de_venta:
            self.tabla_detalle.insert('', 'end', values=producto)

        self.entrada_codigo_venta.config(state='normal')
        self.entrada_codigo_venta.delete(0, tk.END)
        self.entrada_codigo_venta.insert(0, codigo)
        self.entrada_codigo_venta.config(state='readonly')

        self.campo_muestra_fecha.config(state='normal')
        self.campo_muestra_fecha.delete(0, tk.END)
        self.campo_muestra_fecha.insert(0, self.lista_datos_venta[1])
        self.campo_muestra_fecha.config(state='readonly')

        self.campo_muestra_total.config(state='normal')
        self.campo_muestra_total.delete(0, tk.END)
        self.campo_muestra_total.insert(0, f'{self.lista_datos_venta[2]}')
        self.campo_muestra_total.config(state='readonly')

        self.sumar_totales()

    def guardaDetalleDesdeTabla(self, event):
        self.lista_datos_venta = []

        for fila in self.tabla_detalle.get_children():
            self.tabla_detalle.delete(fila)

        item_selec = self.tabla_historial.selection()
        if item_selec:
            self.lista_datos_venta = list(self.tabla_historial.item(item_selec[0], 'values'))

            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            cursor.execute('SELECT * FROM Ventas_Detalle WHERE ID_Venta = ?', (int(self.lista_datos_venta[0]),))
            self.lista_detalle_de_venta = cursor.fetchall()

            conexion.close()

            lista_detalle_nueva = []

            for producto in self.lista_detalle_de_venta:
                producto_nuevo  = []
                precio_formateado = f"${int(producto[2]):,}".replace(",", ".")
                subtotal_formateado = f"${int(producto[3] * producto[2]):,}".replace(",", ".")
                producto_nuevo.append(producto[4])
                producto_nuevo.append(producto[3])
                producto_nuevo.append(precio_formateado)
                producto_nuevo.append(subtotal_formateado)
                lista_detalle_nueva.append(producto_nuevo)

            self.lista_detalle_de_venta = lista_detalle_nueva

            self.imprimirDetalleEnPantalla()
            self.sumar_totales()

    def sumar_totales(self):
        total = 0
        self.label_resumen_total.config(text=f"Total Ventas: ${total}")
        for venta in self.lista_historial_de_ventas:
            try:
                total += int(venta[2])

            except:
                continue
        total_str = f"${total:,}".replace(",", ".")
        cantidad = len(self.lista_historial_de_ventas)
        self.label_resumen_total.config(text=f"Total Ventas: {total_str} | N° Ventas: {cantidad}")
    
    def eliminarventa(self):
        id_venta = self.entrada_codigo_venta.get().strip()

        if not id_venta:
            messagebox.showinfo("Información", "Debe seleccionar una venta para eliminarla", parent=self.root_historial_ventas)
            return
        respuesta = messagebox.askyesno(
        "Eliminar Venta",
        "¿Deseas Eliminar esta venta?",
        parent=self.root_historial_ventas
        )
        
        if not respuesta:
            return

        conexion = sqlite3.connect(self.ruta_bdd)
        cursor= conexion.cursor()

        try:
            cursor.execute("""SELECT ID_Producto, Cantidad_Vendida FROM Ventas_Detalle WHERE ID_Venta = ? """, (id_venta, ))
            productos= cursor.fetchall()

            for id_producto, cantidad in productos:
                cursor.execute("""
                    UPDATE Productos
                    SET Cantidad_Disponible = Cantidad_Disponible + ?
                    WHERE ID_Producto = ?
                """, (cantidad, id_producto))


            cursor.execute("DELETE FROM Ventas_Detalle WHERE ID_Venta = ?", (id_venta,))
            cursor.execute("DELETE FROM Ventas WHERE ID_Venta = ?", (id_venta,))
            
            conexion.commit()
            messagebox.showinfo("Éxito", f"Venta ID {id_venta} eliminada y stock restaurado.", parent=self.root_historial_ventas)
        except Exception as e:
            conexion.rollback()
            messagebox.showerror("Error", f"Ocurrió un problema al eliminar la venta:\n{e}", parent=self.root_historial_ventas)

        finally:
            conexion.close()

            for fila in self.tabla_detalle.get_children():
                self.tabla_detalle.delete(fila)

            self.entrada_codigo_venta.config(state='normal')
            self.entrada_codigo_venta.delete(0, tk.END)
            self.entrada_codigo_venta.config(state='readonly')

            self.campo_muestra_fecha.config(state='normal')
            self.campo_muestra_fecha.delete(0, tk.END)
            self.campo_muestra_fecha.config(state='readonly')

            self.campo_muestra_total.config(state='normal')
            self.campo_muestra_total.delete(0, tk.END)
            self.campo_muestra_total.config(state='readonly')

            self.funcionBotonActualizar()

    def soloNumero(self, char):
        return char.isdigit()
    

    def abrirReporteDiario(self):
        ReporteDiario()
    def abrirTopVentas(self):
        TopVentas()
    
    def abrirEditarVenta(self):
        id_venta = self.entrada_codigo_venta.get().strip()
        if not id_venta:
            messagebox.showinfo("Información", "Selecciona una venta para editarla", parent=self.root_historial_ventas)
            return

        EditarVenta(self.ruta_bdd, id_venta, self)

class EditarVenta:
    def __init__(self, ruta_bdd, id_venta, parent):
        self.ruta_bdd = ruta_bdd
        self.id_venta = id_venta
        self.parent = parent

        self.root_editar = tk.Toplevel()
        self.root_editar.title(f"Editar Venta {id_venta}")
        self.root_editar.geometry("1000x600")
        self.root_editar.config(bg="#D5F5E3")
        self.root_editar.bind("<plus>", self.aumentarCantidadSeleccionada)
        self.root_editar.bind("<minus>", self.disminuirCantidadSeleccionada)

        # Tabla de productos actuales
        self.tabla = ttk.Treeview(self.root_editar, columns=('Codigo', 'Producto', 'Cantidad', 'Precio', 'Precio Total', 'Precio_Num'), show='headings')
        self.tabla.heading('Codigo', text='Codigo')
        self.tabla.heading('Producto', text='Nombre Producto')
        self.tabla.heading('Cantidad', text='Cantidad')
        self.tabla.heading('Precio', text='Precio Unitario')
        self.tabla.heading('Precio Total', text='Precio Total')
        self.tabla.heading('Precio_Num', text='')
        self.tabla.column('Precio_Num', width=0, stretch=False)
        self.tabla.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame de edición
        self.frame_edit = tk.Frame(self.root_editar, bg="#D5F5E3")
        self.frame_edit.pack(fill='x', padx=10, pady=5)

        
        self.frame_edit.grid_columnconfigure(5, weight=1)

        tk.Label(self.frame_edit, text="Código:", font= ("Segoe UI", 12, "bold"), bg="#D5F5E3").grid(row=0, column=0, padx= 5)
        self.entry_codigo = tk.Entry(self.frame_edit)
        self.entry_codigo.grid(row=0, column=1, padx= 5)
        self.entry_codigo.bind("<Return>", self.agregarProducto)

        tk.Button(self.frame_edit, text="Eliminar Producto", bg="#EC7063", command=self.eliminarProducto).grid(row=0, column=2, padx=10)

        total= 0
        self.label_total= tk.Label(self.frame_edit, text= f"Total: ${total}", bg="#D5F5E3", font=("Segoe UI", 16, "bold"))
        self.label_total.grid(row= 0, column= 3,padx= 10)

        tk.Label(self.frame_edit, text="", bg="#D5F5E3").grid(row=0, column=5, sticky="ew")
        self.cargarProductos()
        tk.Button(self.frame_edit, text="Guardar Cambios", bg="#5064AC", fg="white", command=self.guardarCambios).grid(row=0, column=6, padx=10)

        

        

    def cargarProductos(self):
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM Ventas_Detalle WHERE ID_Venta = ?", (self.id_venta,))
        self.productos = cursor.fetchall()
        conexion.close()

        for p in self.productos:
            codigo = p[1]
            nombre = p[4]
            cantidad = p[3]
            precio_num = int(p[2])
            precio_total_num = precio_num * cantidad

            precio_formateado = f"${precio_num:,.0f}".replace(",", ".")
            precio_total_formateado = f"${precio_total_num:,.0f}".replace(",", ".")

            self.tabla.insert('', 'end', values=(codigo, nombre, cantidad, precio_formateado, precio_total_formateado, precio_num))

        self.actualizarTotal()
        
    def agregarProducto(self, event= None):
        try:
            codigo = self.entry_codigo.get().strip()
            if not codigo:
                messagebox.showwarning("Error", "Ingrese código válido", parent= self.root_editar)
                self.entry_codigo.delete(0, tk.END)
                self.entry_codigo.focus_set()
                return
            
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            cursor.execute("SELECT Precio_Venta, Nombre_Producto, Cantidad_Disponible FROM Productos WHERE ID_Producto = ?", (codigo, ))
            producto= cursor.fetchone()
            conexion.close()

            if not producto:
                messagebox.showwarning("Error", "No se encontró producto con ese código", parent= self.root_editar)
                self.entry_codigo.delete(0, tk.END)
                self.entry_codigo.focus_set()
                return
            
            precio_num = int(producto[0])
            nombre = producto[1]
            stock_disponible = producto[2]


            cantidad = 0
            for item in self.tabla.get_children():
                valores = self.tabla.item(item, "values")
                if valores[0] == codigo:
                    cantidad = int(valores[2])
                    break
            if cantidad + 1 > stock_disponible:
                messagebox.showwarning("Error", f"No hay suficiente stock para {nombre}. Disponible: {stock_disponible}", parent= self.root_editar)
                self.entry_codigo.delete(0, tk.END)
                self.entry_codigo.focus_set()
                return

            existe= False
            for item in self.tabla.get_children():
                valores = self.tabla.item(item, "values")
                if valores[0] == codigo:
                    nueva_cantidad = int(valores[2]) + 1
                    precio_total_num = precio_num * nueva_cantidad
                    precio_total_formateado = f"${precio_total_num:,.0f}".replace(",", ".")
                    precio_formateado = f"${precio_num:,.0f}".replace(",", ".")
                    self.tabla.item(item, values=(valores[0], valores[1], nueva_cantidad, precio_formateado, precio_total_formateado, precio_num))
                    existe = True
                    break
            if not existe:
                precio_total_num = precio_num * cantidad
                precio_formateado = f"${precio_num:,.0f}".replace(",", ".")
                precio_total_formateado = f"${precio_total_num:,.0f}".replace(",", ".")
                self.tabla.insert('', 'end', values=(codigo, nombre, cantidad + 1, precio_formateado, precio_total_formateado, precio_num))

            if cantidad + 1 > stock_disponible:
                messagebox.showwarning("Error", f"No hay suficiente stock para {nombre}. Disponible: {stock_disponible}")
                return
            
            self.entry_codigo.delete(0, tk.END)
            self.entry_codigo.focus_set()

            self.actualizarTotal()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al agregar el producto:\n{e}")

    
    def eliminarProducto(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showinfo("Selecciona", "Selecciona un producto para eliminar.")
            return

        item = seleccionado[0]
        self.tabla.delete(item)

        self.actualizarTotal()
        

    def actualizarTotal(self):
        total = 0
        for item in self.tabla.get_children():
            valores = self.tabla.item(item, "values")
            cantidad = int(valores[2])
            precio_num = int(valores[5])
            total += cantidad * precio_num

            subtotal_formateado = f"${cantidad * precio_num:,.0f}".replace(",", ".")
            precio_formateado = f"${precio_num:,.0f}".replace(",", ".")
            self.tabla.item(item, values=(valores[0], valores[1], cantidad, precio_formateado, subtotal_formateado, precio_num))

            
        
        total_str = f"${total:,.0f}".replace(",", ".")
        self.label_total.config(text=f"Total: {total_str}")
        

    def guardarCambios(self):
        def parse_price(value):
            if isinstance(value, (int, float)):
                return int(value)
            s = str(value)
            # quitar todo lo que no sea dígito
            nums = re.sub(r'[^\d]', '', s)
            return int(nums) if nums else 0

        try:
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            
            cursor.execute("""
                SELECT ID_Producto, Cantidad_Vendida
                FROM Ventas_Detalle
                WHERE ID_Venta = ?
            """, (self.id_venta,))
            productos_originales = {str(row[0]): row[1] for row in cursor.fetchall()}

            
            productos_actualizados = {}
            for item in self.tabla.get_children():
                valores = self.tabla.item(item, "values")
                codigo = str(valores[0])
                cantidad = int(valores[2])
                productos_actualizados[codigo] = cantidad

           
            for codigo, cantidad_original in productos_originales.items():
                cantidad_nueva = productos_actualizados.get(codigo)

                if cantidad_nueva is None:
                    cursor.execute("""
                        UPDATE Productos
                        SET Cantidad_Disponible = Cantidad_Disponible + ?
                        WHERE ID_Producto = ?
                    """, (cantidad_original, codigo))
                elif cantidad_nueva > cantidad_original:
                    diferencia = cantidad_nueva - cantidad_original
                    cursor.execute("""
                        UPDATE Productos
                        SET Cantidad_Disponible = Cantidad_Disponible - ?
                        WHERE ID_Producto = ?
                    """, (diferencia, codigo))
                elif cantidad_nueva < cantidad_original:
                    diferencia = cantidad_original - cantidad_nueva
                    cursor.execute("""
                        UPDATE Productos
                        SET Cantidad_Disponible = Cantidad_Disponible + ?
                        WHERE ID_Producto = ?
                    """, (diferencia, codigo))

            for codigo, cantidad in productos_actualizados.items():
                if codigo not in productos_originales:
                    cursor.execute("""
                        UPDATE Productos
                        SET Cantidad_Disponible = Cantidad_Disponible - ?
                        WHERE ID_Producto = ?
                    """, (cantidad, codigo))

            cursor.execute("DELETE FROM Ventas_Detalle WHERE ID_Venta = ?", (self.id_venta,))

            total_calc = 0
            for item in self.tabla.get_children():
                valores = self.tabla.item(item, "values")
                codigo = valores[0]
                nombre = valores[1]
                cantidad = int(valores[2])
                precio_unitario = parse_price(valores[3])

                cursor.execute("""
                    INSERT INTO Ventas_Detalle (ID_Venta, ID_Producto, Cantidad_Vendida, Valor_Unitario, Nombre_Producto)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.id_venta, codigo, cantidad, precio_unitario, nombre))

                total_calc += precio_unitario * cantidad

            cursor.execute("UPDATE Ventas SET Total_Venta = ? WHERE ID_Venta = ?", (total_calc, self.id_venta))

            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Cambios guardados correctamente y stock actualizado.", parent=self.root_editar)
            self.root_editar.destroy()
            try:
                self.parent.funcionBotonActualizar()
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al guardar los cambios:\n{e}", parent=self.root_editar)

    def aumentarCantidadSeleccionada(self, event=None):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            return
        item = seleccionado[0]
        valores = self.tabla.item(item, "values")
        codigo = valores[0]
        cantidad_actual = int(valores[2])
        precio_unitario = int(valores[5])

        # Revisar stock disponible
        if codigo != "0" and codigo != 0:
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()
            cursor.execute("SELECT Cantidad_Disponible FROM Productos WHERE ID_Producto = ?", (codigo,))
            resultado = cursor.fetchone()
            conexion.close()

            if resultado is None:
                messagebox.showerror("Error", f"No se encontró el producto {valores[1]} en la base de datos.", parent=self.root_editar)
                return
            
            stock_disponible = resultado[0]

            if cantidad_actual + 1 > stock_disponible:
                messagebox.showwarning("Stock insuficiente", f"No hay suficiente stock para {valores[1]}. Disponible: {stock_disponible}", parent=self.root_editar)
                return

        nueva_cantidad = cantidad_actual + 1
        precio_total_num = nueva_cantidad * precio_unitario
        precio_total_formateado = f"${precio_total_num:,.0f}".replace(",", ".")
        precio_formateado = f"${precio_unitario:,.0f}".replace(",", ".")
        self.tabla.item(item, values=(valores[0], valores[1], nueva_cantidad, precio_formateado, precio_total_formateado, precio_unitario))
        self.actualizarTotal()

    def disminuirCantidadSeleccionada(self, event=None):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            return
        item = seleccionado[0]
        valores = self.tabla.item(item, "values")
        codigo = valores[0]
        cantidad_actual = int(valores[2])
        precio_unitario = int(valores[5])

        if cantidad_actual == 1:
            if messagebox.askyesno("Eliminar producto", f"¿Desea eliminar {valores[1]} de la venta?", parent=self.root_editar):
                self.tabla.delete(item)
                self.actualizarTotal()
            return

        nueva_cantidad = cantidad_actual - 1
        precio_total_num = nueva_cantidad * precio_unitario
        precio_total_formateado = f"${precio_total_num:,.0f}".replace(",", ".")
        precio_formateado = f"${precio_unitario:,.0f}".replace(",", ".")
        self.tabla.item(item, values=(valores[0], valores[1], nueva_cantidad, precio_formateado, precio_total_formateado, precio_unitario))
        self.actualizarTotal()
