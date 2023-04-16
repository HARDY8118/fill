#!/usr/bin/env python3

from tkinter import Tk, Label, Frame, Button, PhotoImage, StringVar, Radiobutton, Canvas, Scrollbar, VERTICAL, Entry
from random import randint
from copy import deepcopy
from queue import Queue
from collections import Counter
from functools import reduce
from operator import concat
import time
import threading
import sys

colors = ["#000", "#00f", "#0f0", "#0ff", "#f00", "#f0f", "#ff0", "#fff"]
cell_size = 40
sub_cell_size = 8
grid_size = int(sys.argv[1]) if len(sys.argv)==2 else 8
cell_data = None
grid = None
move_count = 0
moves_cols = 4
delay = 0.04
chart_size = 100

window = Tk(className="Fill")

grid_frame = Frame(master=window)
btns_frame = Frame(window)
options_frame = Frame(window)
moves_frame = Frame(window)
scrollbar = Scrollbar(moves_frame, orient=VERTICAL)
moves_canvas = Canvas(moves_frame, confine=False, bg="grey", height=(cell_size*(grid_size+4)),
                      width=((sub_cell_size*grid_size*moves_cols)+(sub_cell_size*(moves_cols-1))), yscrollcommand=scrollbar.set, background="grey")
moves_canvas.configure(scrollregion=moves_canvas.bbox(
    "all"), yscrollcommand=scrollbar.set)
scrollbar.config(command=moves_canvas.yview)

delay_entry = Entry(options_frame, width=5)
delay_entry.insert(0, str(delay))

msg_frame = Frame(window)
status_label = Label(msg_frame)
status_label.pack()

grid_canvas = Canvas(grid_frame, bg="grey", height=(
    cell_size*grid_size), width=(cell_size*grid_size))
grid_canvas.grid(row=1)

chart_canvas = Canvas(options_frame, height=chart_size,
                      width=chart_size, bg="grey")

mode = StringVar()
mode.set("manual")


def random_grid():
    global cell_data
    cell_data = [[randint(0, len(colors)-1) for _ in range(grid_size)]
                 for __ in range(grid_size)]


def displayGrid(grid_data):
    global grid_canvas

    for r in range(len(grid_data)):
        for c in range(len(grid_data[r])):
            grid_canvas.create_rectangle(
                (c*cell_size), (r*cell_size), (c*cell_size)+cell_size, (r*cell_size)+cell_size, fill=colors[grid_data[r][c]], width=0)


def nextStep(currentData, newColor):
    global grid_size

    currentData = deepcopy(currentData)

    if currentData[0][0] == newColor:
        return currentData

    _c = currentData[0][0]
    q = Queue()
    s = set()
    q.put((0, 0))

    while not q.empty():
        r, c = q.get()

        if (r, c) in s or currentData[r][c] != _c:
            continue

        if currentData[r][c] == _c:
            currentData[r][c] = newColor

        if 0 < r < grid_size:
            q.put((r-1, c))
        if 0 <= r < grid_size-1:
            q.put((r+1, c))
        if 0 < c < grid_size:
            q.put((r, c-1))
        if 0 <= c < grid_size-1:
            q.put((r, c+1))

        s.add((r, c))

    return currentData


def handleClick(v):
    global cell_data
    global grid
    global grid_frame
    global move_count
    global moves

    if cell_data[0][0] == v:
        return
    else:
        move_count += 1
        cell_data = nextStep(cell_data, v)

    displayGrid(cell_data)
    moves.configure(text=move_count)

    _state = state(cell_data)
    if _state >= 1.0:
        status_label.configure(text=f"Won in {move_count} moves")
    else:
        status_label.configure(text="{} % completed".format(
            str(_state*100)[:5].rjust(5, ' ')))
    drawChart(cell_data)

    addMove(cell_data)


def state(data):
    return ((Counter(reduce(concat, data)).most_common()[0][1])/(grid_size*grid_size))


def initGrid():
    global moves
    global grid_frame

    moves = Label(grid_frame, text=move_count)
    moves.grid(row=0)

    random_grid()
    displayGrid(cell_data)
    Label(grid_frame, text=" ").grid(row=2)


def autorun(scheme="series"):
    global cell_data

    if scheme == "series":
        _i = 0

        while state(cell_data) < 1.0:
            window.after(int(delay*1000), handleClick, _i % len(colors))
            time.sleep(delay)
            _i += 1
    elif scheme == "random":
        while state(cell_data) < 1.0:
            _r = randint(0, len(colors)-1)

            while state(cell_data) < 1.0:
                _nr = randint(0, len(colors)-1)
                if _nr == _r:
                    continue

                window.after(int(delay*1000), handleClick, _nr)
                time.sleep(delay)
                _r = _nr
    elif scheme == "greedy":
        while state(cell_data) < 1.0:
            _n = neighbours(cell_data)
            window.after(int(delay*1000), handleClick, _n.index(max(_n)))
            time.sleep(delay)
    elif scheme == "minimum":
        start_button.configure(state="disabled", text="Calculating")

        steps = []
        q = Queue()

        for c in range(len(colors)):
            q.put((cell_data, []))

        while not q.empty():
            _d, _m = q.get()
            sys.stdout.write("\r"+" ".join(map(str, _m)))
            status_label.configure(text="{} % completed".format(
                str((len(_m)/(grid_size*grid_size*len(colors)))*100)[:5].rjust(5, ' ')))
            for c in range(len(colors)):
                _n = nextStep(_d, c)
                if state(_n) >= 1.0:
                    steps = _m+[c]
                    while not q.empty():
                        q.get()
                    break
                else:
                    q.put((_n, _m+[c]))

        sys.stdout.write("\r"+" ".join(map(str, steps))+"\n")
        for s in steps:
            window.after(int(delay)*1000, handleClick, s)

    start_button.configure(state="active", text="RESTART")


def addMove(data):
    global move_count
    global moves_canvas

    r = (((move_count-1)//moves_cols)*((grid_size*sub_cell_size)+(sub_cell_size)))
    c = ((move_count-1) % moves_cols)*((grid_size*sub_cell_size)+sub_cell_size)
    # c = 0
    for i in range(len(data)):
        for j in range(len(data[i])):
            moves_canvas.create_rectangle(
                j*sub_cell_size+c, (i*sub_cell_size)+r, (j*sub_cell_size)+sub_cell_size+c, (i*sub_cell_size)+sub_cell_size+r,  fill=colors[data[i][j]], width=0)


def neighbours(data):
    n = [set() for _ in range(len(colors))]

    _c = data[0][0]
    q = Queue()
    s = set()
    q.put((0, 0))

    while not q.empty():
        r, c = q.get()

        if (r, c) in s:
            continue

        if 0 < r < grid_size:
            if data[r-1][c] == _c:
                q.put((r-1, c))
            else:
                n[data[r-1][c]].add((r-1, c))
        if 0 <= r < grid_size-1:
            if data[r+1][c] == _c:
                q.put((r+1, c))
            else:
                n[data[r+1][c]].add((r+1, c))
        if 0 < c < grid_size:
            if data[r][c-1] == _c:
                q.put((r, c-1))
            else:
                n[data[r][c-1]].add((r, c-1))
        if 0 <= c < grid_size-1:
            if data[r][c+1] == _c:
                q.put((r, c+1))
            else:
                n[data[r][c+1]].add((r, c+1))

        s.add((r, c))

    return list(map(len, n))


def drawChart(data):
    global chart_canvas
    global chart_size
    global grid_size

    data = Counter(reduce(concat, data))
    _s = 0.0

    chart_canvas.create_rectangle(
        0, 0, chart_size, chart_size, fill="white")
    for c in range(len(colors)):
        _d = (data[c]/(grid_size*grid_size))*360
        chart_canvas.create_arc(
            0, 0, chart_size, chart_size, start=_s, extent=_d, fill=colors[c])
        _s += _d


Label(btns_frame, text="").grid(row=0, column=0)
pixel = PhotoImage(width=1, height=1)
for c in range(len(colors)):
    Button(btns_frame, text="", image=pixel, height=cell_size,
           width=cell_size, compound="c", bg=colors[c], activebackground=colors[c], command=lambda x=c: handleClick(x)).grid(row=1, column=c)
Label(btns_frame, text="").grid(row=2, column=0)


def init():
    global cell_data
    global start_button
    global delay
    global delay_entry
    global moves_canvas
    global move_count

    moves_canvas.create_rectangle(
        0, 0, moves_canvas.winfo_width(), moves_canvas.winfo_height(), fill="grey", width=0)
    move_count = 0
    start_button.configure(state="disabled")

    initGrid()
    drawChart(cell_data)

    if mode.get() == "manual":
        return

    try:
        delay = float(delay_entry.get())
    except:
        pass

    if mode.get() == "series":
        threading.Thread(target=autorun, args=(mode.get(),)).start()
    elif mode.get() == "random":
        threading.Thread(target=autorun, args=(mode.get(),)).start()
    elif mode.get() == "greedy":
        threading.Thread(target=autorun, args=(mode.get(),)).start()
    elif mode.get() == "minimum":
        threading.Thread(target=autorun, args=(mode.get(),)).start()


delay_entry.pack()
Radiobutton(options_frame, text="Manual", variable=mode, value='manual').pack()
Radiobutton(options_frame, text="Series", variable=mode, value='series').pack()
Radiobutton(options_frame, text="Random", variable=mode, value='random').pack()
Radiobutton(options_frame, text="Greedy", variable=mode, value='greedy').pack()
Radiobutton(options_frame, text="Minimum",
            variable=mode, value='minimum').pack()

start_button = Button(options_frame, text="START",
                      command=init, width=5)
start_button.pack()

chart_canvas.pack()

# Moves
moves_canvas.grid(row=0, column=0)
scrollbar.grid(row=0, column=1)

# Root
grid_frame.grid(row=0, column=1)
msg_frame.grid(row=1, column=0)
btns_frame.grid(row=2, column=1)
options_frame.grid(row=0, column=0, rowspan=3)
moves_frame.grid(row=0, column=2, rowspan=3)

window.mainloop()
