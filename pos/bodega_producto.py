import tkinter as tk
import sqlite3
import sys
import os

def resource_path(relative_path):
# Si es un exe de PyInstaller
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".") 

    return os.path.join(base_path, relative_path)

class BodegaProducto():
    def __init__(self, parent, mostrarProductos, cod_producto = None):
        self.cod_producto = cod_producto
        self.mostrarProductos = mostrarProductos

    # Ruta a la base de datos
        self.ruta_bdd = resource_path('database\BDD_MINIMARKET.db')

    # Ajustes de ventana
        self.root_bodega_producto = tk.Toplevel(parent)
        self.root_bodega_producto.title('Producto seleccionado')
        self.root_bodega_producto.geometry('550x530')
        self.root_bodega_producto.resizable(width=False, height=False)

        vcmd_int = (self.root_bodega_producto.register(self._solo_enteros), "%P")

    # Creacion del frame principal
        self.frame_principal = tk.Frame(self.root_bodega_producto, bg='lightgrey')
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

    # Labels simples
        self.label_codigo = tk.Label(self.frame_principal, text='Código o ID:', anchor='e', bg='lightgrey')
        self.label_nombre = tk.Label(self.frame_principal, text='Nombre del producto:', anchor='e', bg='lightgrey')
        self.label_cantidad_total = tk.Label(self.frame_principal, text='Cantidad existente:', anchor='e', bg='lightgrey')
        self.label_cantidad_add_sus = tk.Label(self.frame_principal, text='Cantidad a agregar/sustraer:', anchor='e', bg='lightgrey')
        
        self.label_codigo.grid(row=0, column=0, sticky='ew')
        self.label_nombre.grid(row=1, column=0, sticky='ew')
        self.label_cantidad_total.grid(row=2, column=0, sticky='ew')
        self.label_cantidad_add_sus.grid(row=3, column=0, sticky='ew')

    # Entrys simples
        self.entry_codigo = tk.Entry(self.frame_principal, width=30, justify='center')
        self.entry_nombre = tk.Entry(self.frame_principal, width=30, justify='center')
        self.entry_codigo.focus_set()
        self.entry_cantidad_total = tk.Entry(self.frame_principal, width=30, justify='center', readonlybackground='lightgrey',
                                     validate="key", validatecommand=vcmd_int)
        self.entry_cantidad_add_sus = tk.Entry(self.frame_principal, width=30, justify='center',
                                     validate="key", validatecommand=vcmd_int)
        self.entry_cantidad_add_sus.bind(
            "<FocusIn>",
            lambda e: self.entry_cantidad_add_sus.select_range(0, tk.END)
            )
        self.entry_cantidad_add_sus.insert(0, '0')

        self.entry_codigo.grid(row=0, column=1, padx=5, pady=10)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=10)
        self.entry_cantidad_total.grid(row=2, column=1, padx=5, pady=10)
        self.entry_cantidad_add_sus.grid(row=3, column=1, padx=5, pady=10)

    # Cantidad total para nuevo producto
        self.opcion_add_sus = tk.StringVar()
        self.opcion_add_sus.set('Agregar (+)')
        self.menu_add_sus = tk.OptionMenu(self.frame_principal, self.opcion_add_sus, 'Agregar (+)', 'Sustraer (-)')
        self.menu_add_sus.grid(row=3, column=2, padx=5, pady=10, sticky='ew')

    # Precio compra
        self.label_pcompra = tk.Label(self.frame_principal, text='Precio de compra:', anchor='e', bg='lightgrey')
        self.label_pcompra.grid(row=4, column=0, sticky='ew', padx=5, pady=10)

        self.entry_pcompra = tk.Entry(self.frame_principal, width=30, justify='center',
                                     validate="key", validatecommand=vcmd_int)
        self.entry_pcompra.grid(row=4, column=1, padx=5, pady=10)

    # Precio de venta
        self.label_pventa = tk.Label(self.frame_principal, text='Precio de venta:', anchor='e', bg='lightgrey')
        self.label_pventa.grid(row=6, column=0, sticky='ew', padx=5, pady=10)

        self.entry_pventa = tk.Entry(self.frame_principal, width=30, justify='center',
                                     validate="key", validatecommand=vcmd_int)
        self.entry_pventa.grid(row=6, column=1, padx=5, pady=10)

        self.entry_pcompra.bind('<KeyRelease>', self.actualizar_porcentaje_ganancia)
        self.entry_pventa.bind('<KeyRelease>', self.actualizar_porcentaje_ganancia)


    # Porcentaje de ganancia automatica
        self.label_pganancia = tk.Label(self.frame_principal, text='Porcentaje de ganancia (%):', anchor='e', bg='lightgrey')
        self.label_pganancia.grid(row=5, column=0, sticky='ew', padx=5, pady=10)

        self.entry_pganancia_var = tk.StringVar(value="0")
        self.entry_pganancia = tk.Entry(self.frame_principal, width=30, justify='center', textvariable=self.entry_pganancia_var)
        self.entry_pganancia.grid(row=5, column=1, padx=5, pady=10)
        self.entry_pganancia.bind('<KeyRelease>', self.actualizarPrecioDesdeGanancia)
        

    # Familia o tipo
        self.label_familia =tk.Label(self.frame_principal, text='Familia / Tipo', anchor='e', bg='lightgrey')
        self.label_familia.grid(row=7, column=0, sticky='ew', padx=5, pady=10)

        self.entry_familia = tk.Entry(self.frame_principal, justify='center')
        self.entry_familia.grid(row=7, column=1, sticky='ew')

        self.lista_familias_existentes = self.obtenerFamilias()
        if not self.lista_familias_existentes:
            self.lista_familias_existentes = ["No Hay familias"]

        self.opcion_familia = tk.StringVar(value=self.lista_familias_existentes[0])

        self.menu_familia = tk.OptionMenu(self.frame_principal, self.opcion_familia, *self.lista_familias_existentes)
        self.menu_familia.grid(row=7, column=2, padx=5, pady=10, sticky='ew')

        self.opcion_familia.trace_add('write', self.actualizarEntryFamilias)

    # MINIMO PRODUCTOS
        self.minimo_producto_label=tk.Label(self.frame_principal, text="Cantidad Minima", anchor= "e", bg="lightgrey")
        self.minimo_producto_label.grid(row=8, column=0,sticky="ew" )

        self.minimo_producto_entry= tk.Entry(self.frame_principal, justify="center",
                                     validate="key", validatecommand=vcmd_int)
        self.minimo_producto_entry.grid(row= 8, column= 1,sticky="ew")

    # Botones guardar cambios y cancelar
        self.boton_guardar = tk.Button(self.frame_principal, font= ("Segoe UI", 10, "bold"), bg='green', fg='white', activebackground='lightgreen', activeforeground='green', width=20)
        self.boton_cancelar = tk.Button(self.frame_principal, text='Cancelar', font=("Segoe UI", 10, "bold"), bg='red', fg='white', activebackground='pink', activeforeground='red', width=20, command=self.cerrarVentana)

        self.boton_guardar.grid(row=9, column=1, pady=30)
        self.boton_cancelar.grid(row=9, column=2, pady=30)

        # Se ve si el boton que se presiono es editar o agregar(Se ve si cogido esta vacio o no). if: agregar, else: editar
        if cod_producto is None:
            self.boton_guardar.config(command=self.funcionesBotonAgregar, text='Guardar producto')
        else:
            self.boton_guardar.config(command=self.funcionesBotonEditar, text='Guardar cambios')

    # Avertencias en ventana
        self.label_adv_verif = tk.Label(self.frame_principal, bg='lightgrey', fg='red')
        self.label_adv_verif.grid(row=10, column=0, columnspan=3)

        self.ingresoDatosAutomatico()

        



    # FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES

    def ingresoDatosAutomatico(self):
        if self.cod_producto != None:

            cod_producto_str = str(self.cod_producto).zfill(4)
            # Obtener todos los datos
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            cursor.execute('SELECT * FROM Productos WHERE ID_Producto = ?', (cod_producto_str, ))
            datos_lista = cursor.fetchall()
            if not datos_lista:
                print(cod_producto_str)
                self.label_adv_verif.config(text=f'No se encontró el producto con ID {cod_producto_str}')
                return
            
            datos = datos_lista[0]

            conexion.close()

            # Setear los datos en los Entry
            self.entry_codigo.delete(0, tk.END)
            self.entry_codigo.insert(0, str(datos[0]).zfill(len(str(datos[0]))))  # Mantiene todos los ceros tal cual
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, str(datos[1]))
            self.entry_cantidad_total.delete(0, tk.END)
            self.entry_cantidad_total.insert(0, str(datos[4]))
            self.entry_pcompra.delete(0, tk.END)
            self.entry_pcompra.insert(0, str(datos[3]))
            self.entry_pventa.delete(0, tk.END)
            self.entry_pventa.insert(0, str(datos[2]))
            self.entry_pganancia.insert(0, str(datos[6]))
            self.entry_familia.delete(0, tk.END)
            self.entry_familia.insert(0, str(datos[5]))
            self.minimo_producto_entry.delete(0, tk.END)
            self.minimo_producto_entry.insert(0,str(datos[7]))

        if self.entry_cantidad_total.get() == '':
            self.entry_cantidad_total.insert(0, '0')

        self.entry_cantidad_total.config(state='readonly')

        if float(datos[6]) == 0:
            self.actualizar_porcentaje_ganancia()

    def cerrarVentana(self):
        self.root_bodega_producto.destroy()

    def existeCodigoProducto(self, codigo, es_para_btn_editar = False):
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()
    
        cursor.execute('SELECT 1 FROM Productos WHERE ID_Producto = ?', (codigo,))
        fila = cursor.fetchone()

        conexion.close()

        if es_para_btn_editar:
        # Permite si el código no cambió
            if str(codigo) == str(self.cod_producto).zfill(4):
                return False
        # Si el código cambió y ya existe, avisa
            if fila is not None:
                self.label_adv_verif.config(text='Existe un codigo igual a este.\nUtilice otro')
                return True
            return False
        else:
        # Si es agregar, avisa si ya existe
            if fila is not None:
                self.label_adv_verif.config(text='Existe un codigo igual a este.\nUtilice otro')
                return True
            return False
                
            
            

    def guardarDatos(self):
        try: # Para no matar la bdd
            
            codigo = str(self.entry_codigo.get().strip()).zfill(4)
            nombre = str(self.entry_nombre.get().strip())
            pcompra = float(self.entry_pcompra.get())
            pventa = float(self.entry_pventa.get())
            pganancia = float(self.entry_pganancia.get())
            familia = str(self.entry_familia.get().strip())
            cantidad = self.calculoCantidadTotal()
            cantidad_minima=int(self.minimo_producto_entry.get())
            
            
            
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            if self.cod_producto is None:
                # INSERT NUEVO PRODUCTO
                cursor.execute('''INSERT INTO Productos (
                                ID_Producto, Nombre_Producto, Precio_Compra, Precio_Venta,
                                Cantidad_Disponible, Familia_Tipo, Porcentaje_Ganancia, Cantidad_Minima)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (codigo, nombre, pcompra, pventa, cantidad, familia, pganancia, cantidad_minima))
            else:
                cursor.execute('''UPDATE Productos SET 
                            Nombre_Producto = ?, 
                            Precio_Venta = ?, 
                            Precio_Compra = ?, 
                            Cantidad_Disponible = ?, 
                            Familia_Tipo = ?, 
                            Porcentaje_Ganancia = ?, 
                            Cantidad_Minima = ?
                          WHERE ID_Producto = ?''',
                       (nombre, pventa, pcompra, cantidad, familia, pganancia, cantidad_minima, self.cod_producto))

            conexion.commit()
            conexion.close()

            self.mostrarProductos()
            self.root_bodega_producto.destroy()

        except Exception as e:
            self.label_adv_verif.config(text=f'Hubo un problema:\n{e}\nVerifique los datos ingresados e intentelo de nuevo.')

    def actualizarDatos(self):
        print('Actualizar datos')

    def verificarCampos(self): 
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get()
        cantidad_as = self.entry_cantidad_add_sus.get()
        pcompra = self.entry_pcompra.get()
        pventa = self.entry_pventa.get()
        pganancia = self.entry_pganancia.get()
        familia = self.entry_familia.get()
    
        # Verificar si alguno de los campos está vacío
        if not all([codigo, nombre, cantidad_as, pcompra, pventa, pganancia, familia]):
            self.label_adv_verif.config(text='Faltan campos por rellenar')  # Mostrar label de advertencia
            return False
        elif int(cantidad_as) < 0:
            self.label_adv_verif.config(text='La cantidad que agregas o sustraes debe ser positiva')
            return False
        else:
            return True
        
    def obtenerFamilias(self):
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        cursor.execute('SELECT DISTINCT Familia_Tipo FROM Productos')
        familias = [fila[0] for fila in cursor.fetchall()]

        conexion.close()
    
        return familias
    
    def actualizarEntryFamilias(self, *args):
        self.entry_familia.delete(0, tk.END)
        self.entry_familia.insert(0, self.opcion_familia.get())

    
    def actualizar_porcentaje_ganancia(self, event=None):
        try:
            pcompra_text = self.entry_pcompra.get().strip()
            pventa_text = self.entry_pventa.get().strip()

            if pcompra_text == '' or pventa_text == '':
                self.entry_pganancia.delete(0, tk.END)
                self.entry_pganancia.insert(0, '0')
                return

            pcompra = float(pcompra_text)
            pventa = float(pventa_text)

            if pcompra == 0:
                self.entry_pganancia.delete(0, tk.END)
                self.entry_pganancia.insert(0, '0')
                return

            porcentaje = ((pventa - pcompra) / pcompra) * 100
            self.entry_pganancia.delete(0, tk.END)
            self.entry_pganancia.insert(0, f'{porcentaje:.2f}')
        except ValueError:
            pass

    def actualizarPrecioDesdeGanancia(self, *args):
        try:
            pcompra = float(self.entry_pcompra.get())
            pganancia = float(self.entry_pganancia_var.get())

            pventa = round(pcompra * (1 + pganancia / 100))
            self.entry_pventa.delete(0, tk.END)
            self.entry_pventa.insert(0, str(pventa))
        except ValueError:
            pass

        
    def calculoCantidadTotal(self):
        cantidad_total = int(self.entry_cantidad_total.get())
        if self.opcion_add_sus.get() == 'Agregar (+)':
            cantidad_total += int(self.entry_cantidad_add_sus.get())
        else:
            cantidad_total -= int(self.entry_cantidad_add_sus.get())
        return cantidad_total
    
    def borrarDatos(self):
        try:
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            cursor.execute(f'DELETE FROM Productos WHERE ID_Producto = ?', (str(self.cod_producto).zfill(4), ))

            conexion.commit()
            conexion.close()

        except Exception as e:
            self.label_adv_verif.config(text=f'Hubo un problema con la eliminación del dato anterior:\n{e}\nInténtelo de nuevo.')

    def funcionesBotonAgregar(self):
        if self.verificarCampos():    
            if not self.existeCodigoProducto(str(self.entry_codigo.get())):
                self.guardarDatos()

    def funcionesBotonEditar(self):
        if self.verificarCampos():    
                if not self.existeCodigoProducto(str(self.entry_codigo.get()), es_para_btn_editar=True):
                    self.guardarDatos()
        # ---------- VALIDACIONES ----------
    def _solo_enteros(self, texto):
        # permite vacío para poder borrar
        return texto.isdigit() or texto == ""

