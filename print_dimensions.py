import tkinter as tk
import mouse

root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

print(screen_width, screen_height)
input("Press enter to exit...")

mouse.move(screen_width // 2, screen_height // 2)
