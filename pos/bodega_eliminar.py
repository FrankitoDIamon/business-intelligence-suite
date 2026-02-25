import tkinter as tk
import sqlite3
import sys
import os

def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable) 
    else:
        base_path = os.path.abspath(".") 

    return os.path.join(base_path, relative_path)

class BodegaEliminar():
    def __init__(self, parent, codigo, mostrarProductos):
        self.codigo = codigo
        self.mostrarProductos = mostrarProductos

    # Ruta a la base de datos
        self.ruta_bdd = resource_path('database\BDD_MINIMARKET.db')

    # Configuracion ventana
        self.root_bodega_eliminar = tk.Toplevel(parent)
        self.root_bodega_eliminar.geometry('400x300')
        self.root_bodega_eliminar.resizable(False, False)
        self.root_bodega_eliminar.title('Eliminar producto')
        self.root_bodega_eliminar.focus_force()

    # Configuracion frame principal
        self.frame_principal = tk.Frame(self.root_bodega_eliminar, bg='#D1D1D1')
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(1, weight=1)

    # Label default
        self.label_texto_default = tk.Label(self.frame_principal, text='¿Está seguro que quiere eliminar este producto?', font=('Arial', 12), bg='#D1D1D1')
        self.label_texto_default.grid(row=0, column=0, columnspan=2, pady=20)

    # Label error
        self.label_error = tk.Label(self.frame_principal, bg='lightgrey', fg='red')
        self.label_error.grid(row=5, column=0, columnspan=2)

    # Labels datos
        self.label_codigo = tk.Label(self.frame_principal, bg='#D1D1D1', font=('Arial', 12))
        self.label_nombre = tk.Label(self.frame_principal, bg='#D1D1D1', font=('Arial', 12))

        self.label_codigo.grid(row=2, column=0, columnspan=2)
        self.label_nombre.grid(row=3, column=0, columnspan=2)

        self.printDatos()

    # Botones de confirmacion
        self.boton_si = tk.Button(self.frame_principal, text='Si', font=("Segoe UI", 10, "bold"), width=10, command=self.eliminarDato, bg='#3353C4', fg='white', activebackground='lightcyan', activeforeground='blue')
        self.boton_no = tk.Button(self.frame_principal, text='No', font=("Segoe UI", 10, "bold"), width=10, command=self.cerrarVentana)

        self.boton_si.grid(row=4, column=0, pady=35)
        self.boton_no.grid(row=4, column=1, pady=35)



    # FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES FUNCIONES

    def getFila(self):
        conexion = sqlite3.connect(self.ruta_bdd)
        cursor = conexion.cursor()

        cursor.execute('SELECT * FROM Productos WHERE ID_Producto = ? ', (self.codigo, ))
        datos_lista = cursor.fetchall()
        datos = datos_lista[0]

        conexion.close()

        return datos

    def printDatos(self):
        datos = self.getFila()
        self.label_codigo.config(text=f'(Código) {str(datos[0])}')
        self.label_nombre.config(text=f'(Nombre) {datos[1]}')

    def eliminarDato(self):
        try:
            conexion = sqlite3.connect(self.ruta_bdd)
            cursor = conexion.cursor()

            datos = self.getFila()

            cursor.execute('DELETE FROM Productos WHERE ID_Producto = ?', (datos[0], ))
            conexion.commit()

            conexion.close()
            self.mostrarProductos()
            self.cerrarVentana()

        except Exception as e:
            self.label_error.config(text=f'Hubo un error al eliminar el producto:\n{e}\nIntentelo de nuevo.')

    def cerrarVentana(self):
        self.root_bodega_eliminar.destroy()