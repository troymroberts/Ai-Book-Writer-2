"""Provide a facade class for a GUI featuring just message boxes.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from tkinter import messagebox
import tkinter as tk
from pywriter.pywriter_globals import *
from pywriter.ui.ui import Ui


class UiMb(Ui):
    """UI subclass with messagebox.
    
    Public methods:
        ask_yes_no(text) -- query yes or no with a pop-up box.
        set_info_how(message) -- show a pop-up message in case of error.
        show_warning(message) -- Display a warning message box.
    """

    def __init__(self, title):
        """Initialize the GUI and remove the tk window from the screen.
        
        Positional arguments:
            title -- application title to be displayed at the messagebox frame.
            
        Extends the superclass constructor.
        """
        super().__init__(title)
        root = tk.Tk()
        root.withdraw()
        self.title = title

    def ask_yes_no(self, text):
        """Query yes or no with a pop-up box.
        
        Positional arguments:
            text -- question to be asked in the pop-up box. 
            
        Overrides the superclass method.       
        """
        return messagebox.askyesno(self.title, text)

    def set_info_how(self, message):
        """Show a pop-up message in case of error.
        
        Positional arguments:
            message -- message to be displayed. 
            
        Overrides the superclass method.
        """
        if message.startswith('!'):
            message = message.split('!', maxsplit=1)[1].strip()
            messagebox.showerror(self.title, message)
        else:
            messagebox.showinfo(self.title, message)

    def show_warning(self, message):
        """Display a warning message box."""
        messagebox.showwarning(self.title, message)
