from tkinter import messagebox

from filminfo.controllers.database_controller import DatabaseController


def save_database(controller: DatabaseController) -> None:
    if reply := controller.save_database():
        messagebox.showerror("Error", str(reply))
