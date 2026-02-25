import tkinter as tk

from tkinter import ttk

from punto_de_venta import PuntoDeVenta


if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')
    app = PuntoDeVenta(root)


    root.mainloop()
