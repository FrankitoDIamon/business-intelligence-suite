import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import sqlite3 as sq
import sys
import os
import math
import unicodedata

def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  
    else:
        base_path = os.path.abspath(".")  

    return os.path.join(base_path, relative_path)

class TipoVenta():
    def __init__(self, app, total_venta, productos):
        self.app = app  
        self.total_venta = total_venta
        self.productos = productos
        
        #COLORES
        color_fondo = "#F8F9FA"
        color_boton = "#27AE60"
        color_texto = "#2C3E50"
        color_vuelto = "#2980B9"

        self.ruta_bdd = resource_path('database\BDD_MINIMARKET.db')
        self.numero_venta = self.app.ventas[self.app.venta_actual].get("numero", self.app.venta_actual + 1)

        self.tipoventa=tk.Toplevel(self.app.root)
        self.tipoventa.title(f"Confirmar Pago - Venta #{self.numero_venta}")
        self.tipoventa.geometry("400x460")
        self.tipoventa.resizable(False,False)
        self.tipoventa.focus_force()
        self.tipoventa.configure(bg=color_fondo)

        self.tipoventa.grid_columnconfigure(0, weight=1)
        self.tipoventa.grid_columnconfigure(1, weight=1)

        self.tipoventa.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        self.tipoventa.bind('<Escape>', lambda event: self.cerrar_ventana())
        

        self.total_venta = total_venta

        
        #Metodo de pago
        self.metodo_pago= tk.StringVar(value="")

        # Título
        label_total = tk.Label(self.tipoventa, text=f"Total a pagar: ${total_venta:,.0f}".replace(",", "."), font=("Segoe UI", 18, "bold"), bg=color_fondo, fg=color_texto)
        label_total.grid(column=0, row= 0, columnspan=2, pady= (20, 0))

        # Subtítulo métodos
        label_subtitulo = tk.Label(self.tipoventa, text="Seleccione método de pago",
                           font=("Segoe UI", 11, "bold"), fg=color_texto, bg=color_fondo)
        label_subtitulo.grid(column=0, row=1, columnspan=2, pady=(0, 5))

        # Campo para efectivo
        self.label_efectivo_vuelto= tk.Label(self.tipoventa, text="", font=("Segoe UI", 12, "bold"),
                                              fg=color_vuelto, bg=color_fondo)
        
        self.var_monto_recibido= tk.StringVar()
        self.var_monto_recibido.trace_add("write", self.calcular_vuelto)
        self.var_monto_recibido.set(str(int(self.total_venta)))

        self.label_efectivo = tk.Label(self.tipoventa, text="Monto recibido:", font=("Segoe UI", 11),
                                       fg=color_texto, bg=color_fondo)

        self.entry_efectivo = tk.Entry(self.tipoventa,textvariable=self.var_monto_recibido, font=("Segoe UI", 11))
        self.entry_efectivo.focus_set()
        self.entry_efectivo.bind("<FocusIn>", lambda e: self.entry_efectivo.select_range(0, tk.END))
        self.label_efectivo_txt= tk.Label(self.tipoventa, text= "Vuelto:", font=("Segoe UI", 11),
                                           fg=color_texto, bg=color_fondo)

        

        #Cargar Imagenes
        ruta_efectivo = resource_path(os.path.join("png", "Efectivo.jpg"))
        ruta_tarjeta = resource_path(os.path.join("png", "Tarjeta.jpg"))
        ruta_transferencia = resource_path(os.path.join("png", "Transferencia.png"))
        ruta_fiado = resource_path(os.path.join("png", "Fiado.png"))

        self.img_efectivo= ImageTk.PhotoImage(Image.open(ruta_efectivo).resize((50,50),resample=Image.Resampling.LANCZOS))
        self.img_tarjeta=ImageTk.PhotoImage(Image.open(ruta_tarjeta).resize((50,50),resample=Image.Resampling.LANCZOS))
        self.img_transferencia=ImageTk.PhotoImage(Image.open(ruta_transferencia).resize((50,50),resample=Image.Resampling.LANCZOS))
        self.img_fiado = ImageTk.PhotoImage(Image.open(ruta_fiado).resize((50, 50), resample=Image.Resampling.LANCZOS))

        # Frame método de pago
        self.frame_metodos= tk.Frame(self.tipoventa, bg=color_fondo)
        self.frame_metodos.grid(column=0, row= 2, columnspan=2, pady= 5)

        #Botones con imagenes y etiquetas   
        #Efectivo
        frame_efe = tk.Frame(self.frame_metodos, bg=color_fondo)
        frame_efe.grid(column=0, row=0, padx=10)
        self.btn_efectivo = tk.Radiobutton(frame_efe, image=self.img_efectivo, variable=self.metodo_pago,
                                   value="Efectivo", indicatoron=False, command=self.actualizar_pago,
                                   relief="ridge", bd=2, bg="white", activebackground="#D1F2EB")
        self.btn_efectivo.pack()
        tk.Label(frame_efe, text="Efectivo", font=("Segoe UI", 9, "bold"), bg=color_fondo).pack()
        self.btn_efectivo.select()
        

        
        #Tarjeta
        frame_tar = tk.Frame(self.frame_metodos, bg=color_fondo)
        frame_tar.grid(column=1, row=0, padx=10)
        self.btn_tarjeta = tk.Radiobutton(frame_tar, image=self.img_tarjeta, variable=self.metodo_pago,
                                  value="Tarjeta", indicatoron=False, command=self.actualizar_pago,
                                  relief="ridge", bd=2, bg="white", activebackground="#D6EAF8")
        self.btn_tarjeta.pack()
        tk.Label(frame_tar, text="Tarjeta", font=("Segoe UI", 9, "bold"), bg=color_fondo).pack()

        #Transferencia
        frame_tra = tk.Frame(self.frame_metodos, bg=color_fondo)
        frame_tra.grid(column=2, row=0, padx=10)
        self.btn_transferencia = tk.Radiobutton(frame_tra, image=self.img_transferencia, variable=self.metodo_pago,
                                        value="Transferencia", indicatoron=False, command=self.actualizar_pago,
                                        relief="ridge", bd=2, bg="white", activebackground="#FADBD8")
        self.btn_transferencia.pack()
        tk.Label(frame_tra, text="Transferencia", font=("Segoe UI", 9, "bold"), bg=color_fondo).pack() 

        #Fiado
        frame_fiado = tk.Frame(self.frame_metodos, bg=color_fondo)
        frame_fiado.grid(column=3, row=0, padx=10)

        self.btn_fiado = tk.Radiobutton(frame_fiado,image=self.img_fiado,variable=self.metodo_pago,value="Fiado",indicatoron=False,command=self.actualizar_pago,relief="ridge",bd=2,bg="white",activebackground="#FDEDEC")
        self.btn_fiado.pack()

        tk.Label(frame_fiado,text="Fiado",font=("Segoe UI", 9, "bold"),bg=color_fondo).pack()
        
        self.var_nombre_deudor = tk.StringVar(value="")
        self.label_deudor = tk.Label(self.tipoventa, text="Nombre deudor:", font=("Segoe UI", 11), bg=color_fondo, fg=color_texto)
        self.entry_deudor = tk.Entry(self.tipoventa, textvariable=self.var_nombre_deudor, font=("Segoe UI", 11))
        self.var_abono = tk.StringVar()
        self.label_abono = tk.Label(
            self.tipoventa,
            text="Abono:",
            font=("Segoe UI", 11),
            bg=color_fondo,
            fg=color_texto
        )

        self.entry_abono = tk.Entry(
            self.tipoventa,
            textvariable=self.var_abono,
            font=("Segoe UI", 11)
        )

        # Botón confirmar
        btn_confirmar = tk.Button(self.tipoventa, text="(F2) Confirmar", bg=color_boton, fg="white", font=("Segoe UI", 12, "bold"),padx=20, pady=5, borderwidth=1, cursor="hand2", command=self.confirmar_pago)
        btn_confirmar.grid(column=0, row=7, columnspan=2, pady=20)

        # Resultado
        self.resultado = tk.Label(self.tipoventa, text="", fg="green", font=("Segoe UI", 12), bg=color_fondo)
        self.resultado.grid(column= 0, row= 8, columnspan=2, pady=5)

        #BINDS BINDS
        self.tipoventa.bind('<F2>', lambda event: self.confirmar_pago())
        self.calcular_vuelto()
        self.actualizar_pago()
        #FUNCIONES
    def actualizar_pago(self, *args):
        metodo= self.metodo_pago.get()
        if metodo == "Efectivo":
            self.label_deudor.grid_remove()
            self.entry_deudor.grid_remove()
            self.label_abono.grid_remove()
            self.entry_abono.grid_remove()
            
            self.label_efectivo.grid(column=0, row=5, sticky="e", padx=10, pady=(10, 5))
            self.entry_efectivo.grid(column=1, row=5, sticky="w", padx=10, pady=(10, 5))

            self.label_efectivo_txt.grid(column=0, row=6, sticky="e", padx=10, pady=(5, 10))
            self.label_efectivo_vuelto.grid(column=1, row=6, sticky="w", padx=10, pady=(5, 10))
        elif metodo == "Fiado":
            self.entry_efectivo.grid_remove()
            self.label_efectivo.grid_remove()
            self.label_efectivo_txt.grid_forget()
            self.label_efectivo_vuelto.grid_forget()
            
            # mostrar nombre del deudor
            self.label_deudor.grid(column=0, row=5, sticky="e", padx=(20,10), pady=(10,2))
            self.entry_deudor.grid(column=1, row=5, sticky="w", padx=(10,20), pady=(10,2))

            self.label_abono.grid(column=0, row=6, sticky="e", padx=(20,10), pady=(5,2))
            self.entry_abono.grid(column=1, row=6, sticky="w", padx=(10,20), pady=(5,2))

            self.entry_deudor.focus_set()

        else:
            self.entry_efectivo.grid_remove()
            self.label_efectivo.grid_remove()
            self.label_efectivo_txt.grid_forget()
            self.label_efectivo_vuelto.grid_forget()
            self.label_abono.grid_remove()
            self.entry_abono.grid_remove()
            self.resultado.configure(text="")
    

    def confirmar_pago(self, event=None):

        metodo= self.metodo_pago.get()
        if metodo == "":
            self.resultado.configure(text="Debes seleccionr un metodo de pago", fg="red")
            return
        

        if metodo == "Efectivo":
            if not self.productos:
                    self.resultado.configure(text="No hay productos en la venta", fg="red")
                    return
            try:
                entrada = self.var_monto_recibido.get().replace("$", "").replace(" ", "").replace(".", "")
                monto= int(entrada)
            except ValueError:
                self.resultado.configure(text="Monto inválido", fg="red")
                return
            
            total_redondeado = math.ceil(self.total_venta)
            
            if monto < total_redondeado:
                    self.resultado.configure(text="Monto Insuficiente", fg="red")
                    return
            
        elif metodo == "Fiado":
            if not self.productos:
                self.resultado.configure(text="No hay productos en la venta", fg="red")
                return
                
            nombre_deudor = TipoVenta.normalizar_nombre_deudor(
                self.var_nombre_deudor.get()
            )
            if not nombre_deudor:
                self.resultado.configure(text="Debe ingresar el nombre del deudor", fg="red")
                return
            abono = 0
            try:
                if self.var_abono.get().strip():
                    abono = float(
                        self.var_abono.get()
                        .replace("$", "")
                        .replace(".", "")
                        .strip()
                    )
            except ValueError:
                self.resultado.configure(text="Abono inválido", fg="red")
                return
            
            dia = datetime.date.today().day
            mes = datetime.date.today().month
            anio = datetime.date.today().year
            fecha = (dia * 1000000) + (mes * 10000) + (anio)
            try:
                total_real = self.total_venta
                
                if abono < 0 or abono > total_real:
                    self.resultado.configure(text="Abono fuera de rango", fg="red")
                    return

                saldo = total_real - abono
                estado = "PAGADO" if saldo == 0 else "PENDIENTE"

                with sq.connect(self.app.ruta_bdd, timeout=5) as con:
                    cur = con.cursor()

                    nombre_lower = nombre_deudor.lower()
                    unificar = nombre_lower in ["mama", "mamá", "mami", "madre"]

                    cur.execute("""
                        SELECT ID_Deuda, Monto_Total, Abono, Saldo
                        FROM Deudores
                        WHERE Nombre = ? AND Estado = 'PENDIENTE'
                        ORDER BY ID_Deuda ASC
                    """, (nombre_deudor,))

                    rows = cur.fetchall()

                    if rows and unificar:
                        id_base, monto_base, abono_base, saldo_base = rows[0]

                        monto_total = monto_base + total_real
                        abono_total = abono_base + abono
                        saldo_total = saldo_base + saldo

                        ids_a_eliminar = []

                        for r in rows[1:]:
                            id_d, m, a, s = r
                            monto_total += m
                            abono_total += a
                            saldo_total += s
                            ids_a_eliminar.append(id_d)

                        estado_final = "PAGADO" if saldo_total == 0 else "PENDIENTE"
            
                        cur.execute("""
                            UPDATE Deudores
                            SET Monto_Total = ?, Abono = ?, Saldo = ?, Estado = ?
                            WHERE ID_Deuda = ?
                        """, (monto_total, abono_total, saldo_total, estado_final, id_base))

                        for id_d in ids_a_eliminar:
                            cur.execute("DELETE FROM Deudores WHERE ID_Deuda = ?", (id_d,))

                        id_deuda = id_base

                    else:
                        # 🆕 NO EXISTE → CREAR
                        cur.execute("""
                            INSERT INTO Deudores (Nombre, Monto_Total, Abono, Saldo, Fecha, Estado)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (nombre_deudor, total_real, abono, saldo, fecha, estado))

                        cur.execute("SELECT last_insert_rowid()")
                        id_deuda = cur.fetchone()[0]


                    # Detalle + bajar stock (pero NO sumar a ventas)
                    for producto in self.productos:
                        if isinstance(producto, dict):
                            id_prod = producto["ID"]
                            nombre = producto["Nombre"]
                            cantidad = int(producto["Cantidad"])
                            precio_original = float(producto["Precio"])
                            subtotal = precio_original * cantidad
                        else:
                            id_prod = producto[0]
                            nombre = producto[1]
                            cantidad = int(producto[2])
                            precio_original = float(producto[3])
                            subtotal = precio_original * cantidad
                        if str(id_prod) == "0":
                            # 🚫 Producto sin código → SIEMPRE insertar separado
                            cur.execute("""
                                INSERT INTO Deudores_Detalle
                                (ID_Deuda, ID_Producto, Nombre_Producto, Cantidad, Precio_Unitario, Subtotal)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (id_deuda, id_prod, nombre, cantidad, precio_original, subtotal))

                        else:
                            # ✅ Producto con código → unificar
                            cur.execute("""
                                SELECT Cantidad, Subtotal
                                FROM Deudores_Detalle
                                WHERE ID_Deuda=? AND ID_Producto=?
                            """, (id_deuda, id_prod))

                            detalle_existente = cur.fetchone()

                            if detalle_existente:
                                cant_ant, sub_ant = detalle_existente
                                cur.execute("""
                                    UPDATE Deudores_Detalle
                                    SET Cantidad = ?, Subtotal = ?
                                    WHERE ID_Deuda=? AND Nombre_Producto=?
                                """, (
                                    cant_ant + cantidad,
                                    sub_ant + subtotal,
                                    id_deuda,
                                    nombre
                                ))
                            else:
                                cur.execute("""
                                    INSERT INTO Deudores_Detalle
                                    (ID_Deuda, ID_Producto, Nombre_Producto, Cantidad, Precio_Unitario, Subtotal)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (id_deuda, id_prod, nombre, cantidad, precio_original, subtotal))

                        if str(id_prod) != "0":
                            cur.execute("UPDATE Productos SET Cantidad_Disponible = Cantidad_Disponible - ? WHERE ID_Producto=?",
                                        (cantidad, id_prod))

                    con.commit()

                    self.app.eliminarAllProductos()
                    self.app.mostrarListaProductos()


                    if 0 <= self.app.venta_actual < len(self.app.ventas):
                        self.app.venta_confirmada[self.app.venta_actual] = True


                    self.app.nueva_venta()

                    self.resultado.configure(text=f"Deuda registrada a nombre de {nombre_deudor}", fg="green")
                    self.tipoventa.after(300, self.cerrar_ventana)

                    return
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}", parent=self.tipoventa)
                return

        try:
            # Obtener fecha en formato entero DDMMYYYY
            dia = datetime.date.today().day
            mes = datetime.date.today().month
            anio = datetime.date.today().year
            fecha = (dia * 1000000) + (mes * 10000) + (anio)

            with sq.connect(self.app.ruta_bdd, timeout=5) as conexion:
            
 
                total_real = self.total_venta

                cursor = conexion.cursor()


                cursor.execute('INSERT INTO Ventas (Fecha_Venta, Total_Venta, Tipo_Venta, Precio_Promocional) VALUES (?, ?, ?, ?)',
                       (fecha, total_real, metodo, 1 if self.app.var_venta_promo.get() else 0))
                conexion.commit()

                cursor.execute('SELECT MAX(ID_Venta) FROM Ventas')
                id_venta = cursor.fetchone()[0]

                # Insertar detalles
                for producto in self.productos:
                    if isinstance(producto, dict):  # Producto común
                        id_prod = producto["ID"]
                        nombre = producto["Nombre"]
                        cantidad = int(producto["Cantidad"])
                        precio_original = float(producto["Precio"])
                    else:  # Producto registrado (tupla)
                        id_prod = producto[0]
                        nombre = producto[1]
                        cantidad = int(producto[2])
                        precio_original = float(producto[3])
                    
                    cursor.execute('''
                        INSERT INTO Ventas_Detalle (ID_Venta, ID_Producto, Valor_Unitario, Cantidad_Vendida, Nombre_Producto)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (id_venta, id_prod, precio_original, cantidad, nombre))

                    # Si es producto registrado, actualizar stock y top ventas
                    if id_prod != '0':
                        # Actualizar stock
                        cursor.execute('SELECT Cantidad_Disponible FROM Productos WHERE ID_Producto = ?', (id_prod,))
                        resultado = cursor.fetchone()
                        if resultado:
                            cantidad_antigua = resultado[0]
                            cantidad_nueva = cantidad_antigua - cantidad
                            cursor.execute('''
                                UPDATE Productos
                                SET Cantidad_Disponible = ?
                                WHERE ID_Producto = ?
                            ''', (cantidad_nueva, id_prod))

                    
                        #Actualizar Top Ventas
                        cursor.execute('SELECT Cantidad_Vendida FROM Top_Ventas WHERE ID_Producto = ?', (id_prod,))
                        resultado = cursor.fetchone()
                        if resultado:
                            nueva_cantidad = cantidad + resultado[0]
                            cursor.execute('''
                                UPDATE Top_Ventas
                                SET Cantidad_Vendida = ?, Fecha_Venta = ?
                                WHERE ID_Producto = ?
                            ''', (nueva_cantidad, fecha, id_prod))
                        else:
                            cursor.execute('''
                                INSERT INTO Top_Ventas (ID_Producto, Nombre_Producto, Cantidad_Vendida, Fecha_Venta)
                                VALUES (?, ?, ?, ?)
                            ''', (id_prod, nombre, cantidad, fecha))

                conexion.commit()
            
            # Limpiar interfaz principal
            #self.app.Alertas_stock()
            self.app.eliminarAllProductos()
            self.app.mostrarListaProductos()
            
            # Marcar la venta actual como confirmada
            if 0 <= self.app.venta_actual < len(self.app.ventas):
                self.app.venta_confirmada[self.app.venta_actual] = True
        
            # Crear una nueva venta
            self.app.nueva_venta()

            self.resultado.configure(text=f"Pago confirmado con {metodo}", fg="green")
            self.tipoventa.after(300, self.cerrar_ventana)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Ocurrió un error: {e}", parent=self.tipoventa)

            

    def calcular_vuelto(self, *args):
        try:
            entrada = self.var_monto_recibido.get().replace("$", "").replace(" ", "").replace(".", "")
            monto = int(entrada)

            total_redondeado = math.ceil(self.total_venta)

            if monto < total_redondeado:
                self.label_efectivo_vuelto.configure(text="Monto insuficiente", fg="red")
            else:
                vuelto = monto - total_redondeado
                self.label_efectivo_vuelto.configure(
                    text=f"${vuelto:,.0f}".replace(",", "."),
                    fg="green"
                )

        except ValueError:
            self.label_efectivo_vuelto.configure(text="")
    
    def cerrar_ventana(self):
        # liberar registro para esta venta
        try:
            if hasattr(self.app, "ventanas_pago_abiertas"):
                w = self.app.ventanas_pago_abiertas.get(self.numero_venta)
                # solo borrar si apunta a esta misma ventana o si ya no existe
                if w is None or (not w.winfo_exists()) or (w == self.tipoventa):
                    self.app.ventanas_pago_abiertas.pop(self.numero_venta, None)
        except Exception:
            pass

        if self.tipoventa.winfo_exists():
            self.tipoventa.destroy()

    
    def normalizar_nombre_deudor(nombre):
        nombre = nombre.strip().lower()


        nombre = ''.join(
            c for c in unicodedata.normalize('NFD', nombre)
            if unicodedata.category(c) != 'Mn'
        )

        grupo_mama = {
            "mami", "mama", "mamita",
            "abuela", "abueli",
            "abuelo", "abuelito", "abuelita"
        }

        if nombre in grupo_mama:
            return "Mama"

        return nombre.capitalize()
            