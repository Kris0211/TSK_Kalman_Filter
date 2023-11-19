import tkinter as tk


def on_click():
    if draw_measured.get():
        print("owo")
    if draw_kalman.get():
        print("uwu")
    if draw_physical.get():
        print("nya")


if __name__ == '__main__':
    root = tk.Tk(screenName="kalman")
    title = tk.Label(root, text="Kalman's Filter for Ships")
    title.pack()

    draw_measured = tk.BooleanVar()
    draw_kalman = tk.BooleanVar()
    draw_physical = tk.BooleanVar()

    ck1 = tk.Checkbutton(root, text='Draw Measured', variable=draw_measured, onvalue=True, offvalue=False,
                         command=on_click)
    ck1.pack()

    ck2 = tk.Checkbutton(root, text='Draw Kalman Prediction', variable=draw_kalman, onvalue=True, offvalue=False,
                         command=on_click)
    ck2.pack()

    ck3 = tk.Checkbutton(root, text='Draw Physics-Based', variable=draw_physical, onvalue=True, offvalue=False,
                         command=on_click)
    ck3.pack()

    id_textbox = tk.Text(root, height=8)
    id_textbox.pack()

    root.mainloop()
