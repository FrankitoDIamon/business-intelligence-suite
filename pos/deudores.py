import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import time
from PIL import Image, ImageTk
import sys
import os

def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  
    else:
        base_path = os.path.abspath(".")  

    return os.path.join(base_path, relative_path)

class Deudores:
    def __init__(self,pareent, ruta_bdd):
        self.ruta_bdd = ruta_bdd
        self.ventana = tk.Toplevel(pareent)
        self.ventana.title("Deudores")
        self.ventana.state("zoomed")
        
        cont = tk.Frame(self.ventana)
        cont.pack(fill="both", expand=True, padx=10, pady=10)
        cont.columnconfigure(0, weight=1)
        cont.columnconfigure(1, weight=1)
        cont.rowconfigure(0, weight=1)
        
        frame_left = tk.LabelFrame(cont, text="Deudas")
        frame_left.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        cols = ("ID", "Nombre", "Monto", "Fecha", "Estado")
        self.tree_deudas = ttk.Treeview(frame_left, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree_deudas.heading(c, text=c)
        self.tree_deudas.column("ID", width=60, anchor="center")
        self.tree_deudas.column("Monto", width=120, anchor="e")
        self.tree_deudas.column("Fecha", width=110, anchor="center")
        self.tree_deudas.column("Estado", width=110, anchor="center")
        self.tree_deudas.pack(fill="both", expand=True, padx=8, pady=8)

        self.tree_deudas.bind("<<TreeviewSelect>>", self.cargar_detalle)

        # Botones de deuda
        btns = tk.Frame(frame_left)
        btns.pack(fill="x", padx=8, pady=(0,8))
        tk.Button(btns, text="Actualizar", bg="#5064AC", fg='white', activebackground="lightblue", activeforeground="blue", command=self.cargar_deudas).pack(side="left", padx=5)
        tk.Button(btns,text="Cobrar deuda", bg= "green", activebackground= "lightgreen", fg='white',activeforeground="black", command=self.seleccionar_metodo_cobro).pack(side="left", padx=5)
        tk.Button(btns, text="Eliminar deuda", bg= "#ED6859", fg="white", activebackground="#E74C3C", activeforeground="black", command=self.eliminar_deuda).pack(side="left", padx=5)

        # ---- Tabla Detalle ----
        frame_right = tk.LabelFrame(cont, text="Desglose (productos)")
        frame_right.grid(row=0, column=1, sticky="nsew")

        cols2 = ("Producto", "Cant", "P.Unit", "Subtotal")
        self.tree_detalle = ttk.Treeview(frame_right, columns=cols2, show="headings", height=18)
        for c in cols2:
            self.tree_detalle.heading(c, text=c)
        self.tree_detalle.column("Cant", width=60, anchor="center")
        self.tree_detalle.column("P.Unit", width=110, anchor="e")
        self.tree_detalle.column("Subtotal", width=120, anchor="e")
        self.tree_detalle.pack(fill="both", expand=True, padx=8, pady=8)

        self.lbl_total = tk.Label(frame_right, text="Total deuda: $0", font=("Segoe UI", 12, "bold"))
        self.lbl_total.pack(anchor="e", padx=10, pady=(0,10))

        self.btn_abonar = tk.Button(
            frame_right,
            text="Abonar deuda",
            command=self.abonar_deuda,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 10, "bold")
        )
        self.btn_abonar.pack(anchor="e", padx=10, pady=5)

        self.cargar_deudas()
    
    def _asegurar_tablas(self):
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
    
    def _fecha_entera_hoy(self):
        d = datetime.date.today()
        return (d.day * 1000000) + (d.month * 10000) + d.year
    
    def _id_deuda_seleccionada(self):
        sel = self.tree_deudas.selection()
        if not sel:
            return None
        values = self.tree_deudas.item(sel[0], "values")
        return int(values[0])
    
    def _fmt_pesos(self, n):
        try:
            return f"${float(n):,.0f}".replace(",", ".")
        except:
            return "$0"
    def _fmt_fecha(self, fecha_int):
        try:
            f = int(fecha_int)
            anio = f % 10000
            f //= 10000
            mes = f % 100
            dia = f // 100
            return f"{dia:02d}/{mes:02d}/{anio}"
        except:
            return ""
    
    def cargar_deudas(self):
        for i in self.tree_deudas.get_children():
            self.tree_deudas.delete(i)
        for i in self.tree_detalle.get_children():
            self.tree_detalle.delete(i)
        self.lbl_total.config(text="Total deuda: $0")

        con = sqlite3.connect(self.ruta_bdd)
        cur = con.cursor()
        cur.execute("""
            SELECT ID_Deuda, Nombre, Saldo, Fecha, Estado
            FROM Deudores
            ORDER BY CASE WHEN Estado='PENDIENTE' THEN 0 ELSE 1 END, ID_Deuda DESC
        """)
        rows = cur.fetchall()
        con.close()

        for r in rows:
            idd, nombre, monto, fecha, estado = r
            self.tree_deudas.insert("", "end", values=(idd, nombre, self._fmt_pesos(monto), self._fmt_fecha(fecha), estado))



    def cargar_detalle(self, event=None):
        idd = self._id_deuda_seleccionada()
        self.deuda_actual = idd
        for i in self.tree_detalle.get_children():
            self.tree_detalle.delete(i)
        self.lbl_total.config(text="Total deuda: $0")
        if not idd:
            return

        con = sqlite3.connect(self.ruta_bdd)
        cur = con.cursor()
        cur.execute("""
            SELECT Nombre_Producto, Cantidad, Precio_Unitario, Subtotal
            FROM Deudores_Detalle
            WHERE ID_Deuda=?
        """, (idd,))
        detalle = cur.fetchall()

        cur.execute("""
            SELECT Monto_Total, Abono, Saldo
            FROM Deudores
            WHERE ID_Deuda=?
        """, (idd,))
        datos = cur.fetchone()
        con.close()

        for nom, cant, punit, sub in detalle:
            self.tree_detalle.insert("", "end", values=(
                nom,
                int(cant),
                self._fmt_pesos(punit),
                self._fmt_pesos(sub)
            ))

        if datos:
            monto_total, abono, saldo = datos

            texto = f"Total: {self._fmt_pesos(monto_total)}"

            if abono and float(abono) > 0:
                texto += f"  |  Abono: {self._fmt_pesos(abono)}"

            texto += f"  |  Saldo: {self._fmt_pesos(saldo)}"

            self.lbl_total.config(text=texto)

    
    def pagar_deuda(self, metodo):
        idd = self._id_deuda_seleccionada()
        if not idd:
            messagebox.showinfo("Info", "Selecciona una deuda", parent=self.ventana)
            return

        con = sqlite3.connect(self.ruta_bdd)
        cur = con.cursor()

        cur.execute("""
            SELECT Nombre, Saldo, Estado
            FROM Deudores
            WHERE ID_Deuda=?
        """, (idd,))

        row = cur.fetchone()
        if not row:
            con.close()
            return

        nombre, monto, estado = row
        if estado != "PENDIENTE":
            con.close()
            messagebox.showinfo("Info", "Esa deuda ya está pagada", parent=self.ventana)
            return

        if not messagebox.askyesno(
            "Confirmar",
            f"¿Cobrar deuda de {nombre} por {self._fmt_pesos(monto)} con {metodo}?",
            parent=self.ventana
        ):
            con.close()
            return

        cur.execute("""
            SELECT ID_Producto, Nombre_Producto, Cantidad, Precio_Unitario
            FROM Deudores_Detalle WHERE ID_Deuda=?
        """, (idd,))
        detalles = cur.fetchall()
        if not detalles:
            con.close()
            messagebox.showerror("Error", "No hay detalle de productos para esta deuda", parent=self.ventana)
            return

        fecha = self._fecha_entera_hoy()

        try:
            # Insertar en Ventas con el método elegido
            cur.execute(
                "INSERT INTO Ventas (Fecha_Venta, Total_Venta, Tipo_Venta) VALUES (?, ?, ?)",
                (fecha, float(monto), metodo)
            )
            con.commit()

            cur.execute("SELECT MAX(ID_Venta) FROM Ventas")
            id_venta = cur.fetchone()[0]

            # Ventas_Detalle + Top_Ventas (NO tocar stock)
            for id_prod, nom_prod, cant, precio in detalles:
                cur.execute("""
                    INSERT INTO Ventas_Detalle (ID_Venta, ID_Producto, Valor_Unitario, Cantidad_Vendida, Nombre_Producto)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_venta, id_prod, float(precio), int(cant), nom_prod))

                if str(id_prod) != "0":
                    cur.execute("SELECT Cantidad_Vendida FROM Top_Ventas WHERE ID_Producto=?", (id_prod,))
                    r = cur.fetchone()
                    if r:
                        cur.execute("""
                            UPDATE Top_Ventas
                            SET Cantidad_Vendida=?, Fecha_Venta=?
                            WHERE ID_Producto=?
                        """, (int(r[0]) + int(cant), fecha, id_prod))
                    else:
                        cur.execute("""
                            INSERT INTO Top_Ventas (ID_Producto, Nombre_Producto, Cantidad_Vendida, Fecha_Venta)
                            VALUES (?, ?, ?, ?)
                        """, (id_prod, nom_prod, int(cant), fecha))

            # Marcar deuda pagada (fecha pago entero)
            cur.execute("""
                UPDATE Deudores
                SET
                    Abono = Monto_Total,
                    Saldo = 0,
                    Estado = 'PAGADO',
                    Fecha_Pago = ?
                WHERE ID_Deuda = ?
            """, (fecha, idd))
            con.commit()
            con.close()

            messagebox.showinfo("OK", f"Deuda cobrada con {metodo} y agregada a Ventas", parent=self.ventana)
            self.cargar_deudas()

        except Exception as e:
            con.rollback()
            con.close()
            messagebox.showerror("Error", f"Ocurrió un error al cobrar deuda: {e}", parent=self.ventana)



    def eliminar_deuda(self):
        idd = self._id_deuda_seleccionada()
        if not idd:
            messagebox.showinfo("Info", "Selecciona una deuda", parent=self.ventana)
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar esta deuda y su detalle? (No revierte stock)", parent=self.ventana):
            return

        con = sqlite3.connect(self.ruta_bdd)
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM Deudores_Detalle WHERE ID_Deuda=?", (idd,))
            cur.execute("DELETE FROM Deudores WHERE ID_Deuda=?", (idd,))
            con.commit()
            con.close()
            self.cargar_deudas()
        except Exception as e:
            con.rollback()
            con.close()
            messagebox.showerror("Error", f"No se pudo eliminar: {e}", parent=self.win)
    
    def seleccionar_metodo_cobro(self):
        self.metodo_pago = None
        self.cards_metodo = {}
        idd = self._id_deuda_seleccionada()
        if not idd:
            messagebox.showinfo(
                "Info",
                "Selecciona una deuda",
                parent=self.ventana
            )
            return

        win = tk.Toplevel(self.ventana)
        win.title("Seleccionar método de cobro")
        win.configure(bg="#F4F6F7")
        win.geometry("550x320")
        win.resizable(False, False)
        win.grab_set()
        win.focus_force()


        tk.Label(
            win,
            text="¿Cómo se pagó la deuda?",
            font=("Segoe UI", 13, "bold")
        ).pack(pady=15)

        frame = tk.Frame(win)
        frame.pack(expand=True)

        def elegir(metodo):
            win.destroy()
            self.pagar_deuda(metodo)

        def seleccionar(metodo):
            self.metodo_pago = metodo
            for m, card in self.cards_metodo.items():
                if m == metodo:
                    card.config(bg="#D6EAF8", bd=3)
                else:
                    card.config(bg="white", bd=2)
            btn_confirmar.config(state="normal")
        
        def tarjeta_metodo(parent, imagen, texto, metodo):
            card = tk.Frame(
                parent,
                bg="white",
                bd=2,
                relief="ridge",
                width=150,
                height=160
            )
            card.pack_propagate(False)
            card.pack(side="left", padx=14, pady=10)

            lbl_img = tk.Label(card, image=imagen, bg="white")
            lbl_img.pack(pady=(18, 6))

            lbl_txt = tk.Label(
                card,
                text=texto,
                font=("Segoe UI", 11, "bold"),
                bg="white",
                fg="#2C3E50"
            )
            lbl_txt.pack()

            def click(_=None):
                seleccionar(metodo)

            for w in (card, lbl_img, lbl_txt):
                w.bind("<Button-1>", click)

            self.cards_metodo[metodo] = card


        self.metodo_pago= tk.StringVar(value="")
        IMG_SIZE = (80, 80)

        ruta_efectivo = resource_path(os.path.join("png", "Efectivo.jpg"))
        ruta_tarjeta = resource_path(os.path.join("png", "Tarjeta.jpg"))
        ruta_transferencia = resource_path(os.path.join("png", "Transferencia.png"))
        ruta_fiado = resource_path(os.path.join("png", "Fiado.png"))
        
        self.img_efectivo= ImageTk.PhotoImage(Image.open(ruta_efectivo).resize((IMG_SIZE),resample=Image.Resampling.LANCZOS))
        self.img_tarjeta=ImageTk.PhotoImage(Image.open(ruta_tarjeta).resize((IMG_SIZE),resample=Image.Resampling.LANCZOS))
        self.img_transferencia=ImageTk.PhotoImage(Image.open(ruta_transferencia).resize((IMG_SIZE),resample=Image.Resampling.LANCZOS))
        self.img_fiado = ImageTk.PhotoImage(Image.open(ruta_fiado).resize((IMG_SIZE), resample=Image.Resampling.LANCZOS))

        frame = tk.Frame(win, bg="#F4F6F7")
        frame.pack(expand=True)

        tarjeta_metodo(frame, self.img_efectivo, "Efectivo", "Efectivo")
        tarjeta_metodo(frame, self.img_tarjeta, "Tarjeta", "Tarjeta")
        tarjeta_metodo(frame, self.img_transferencia, "Transferencia", "Transferencia")

        btn_confirmar = tk.Button(
            win,
            text="Confirmar pago",
            font=("Segoe UI", 12, "bold"),
            bg="#27AE60",
            fg="white",
            activebackground="#1E8449",
            state="disabled",
            width=18,
            command=lambda: (
                win.destroy(),
                self.pagar_deuda(self.metodo_pago)
            )
        )
        btn_confirmar.pack(pady=15)

    


    def abonar_deuda(self):
        if not hasattr(self, "deuda_actual") or not self.deuda_actual:
            messagebox.showwarning("Atención", "Selecciona una deuda primero", parent= self.ventana)
            return

        idd = self.deuda_actual

        win = tk.Toplevel()
        win.title("Abonar deuda")
        win.resizable(False, False)

        tk.Label(win, text="Monto a abonar:", font=("Segoe UI", 10)).pack(padx=10, pady=5)
        entry_abono = tk.Entry(win)
        entry_abono.pack(padx=10, pady=5)
        entry_abono.focus()

        def confirmar():
            try:
                monto = float(entry_abono.get())
                if monto <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Ingresa un monto válido",parent= self.ventana)
                return

            conn = sqlite3.connect(self.ruta_bdd)
            cur = conn.cursor()

            cur.execute("""
                SELECT Monto_Total, Abono, Saldo
                FROM Deudores
                WHERE ID_Deuda=?
            """, (idd,))
            monto_total, abono_actual, saldo_actual = cur.fetchone()

            if monto > saldo_actual:
                messagebox.showerror("Error", "El abono no puede ser mayor al saldo",parent= self.ventana)
                conn.close()
                return

            nuevo_abono = abono_actual + monto
            nuevo_saldo = saldo_actual - monto
            nuevo_estado = "PAGADO" if nuevo_saldo == 0 else "PENDIENTE"

            cur.execute("""
                UPDATE Deudores
                SET Abono=?, Saldo=?, Estado=?, Fecha_Pago=?
                WHERE ID_Deuda=?
            """, (
                nuevo_abono,
                nuevo_saldo,
                nuevo_estado,
                int(time.time()) if nuevo_estado == "PAGADO" else None,
                idd
            ))

            conn.commit()
            conn.close()

            win.destroy()
            self.cargar_deudas()
            self.cargar_detalle(None)

        tk.Button(
            win,
            text="Confirmar abono",
            command=confirmar,
            bg="#2196F3",
            fg="white"
        ).pack(pady=10)

    
