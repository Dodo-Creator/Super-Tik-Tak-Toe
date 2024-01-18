import tkinter as tk
import ttkbootstrap as ttk
import random
import time

widget_positions = ["top_left", "top_center", "top_right", "middle_left", "middle_center", "middle_right", "bottom_left", "bottom_center", "bottom_right"]

scores = {"X": 0, "O": 0}

symbols = ["X", "O"]

current_symbol = "X"

frames = {}
buttons = {}

frames_taken_by_symbol = {}

log_history = {"button_location_pressed": [],
               "symbol_state": [],
               "frames_taken_by_symbol_state": []
               }

playing_with_bot = False

def start_game(choice_to_play_with_bot: int):
    global playing_with_bot
    
    # defines with which number the game was started to give the update function a bot logic
    playing_with_bot = choice_to_play_with_bot
    
    # removes the introduction
    intro_canvas.pack_forget()
    
    symbol_canvas.pack()
    score_drawing_canvas.pack()
    playground.pack()
    undo_button_canvas.pack()

def get_bot_placement(open_frame: str):
    global current_symbol
    
    buttons_to_pick = []
    
    for button in frames[open_frame].winfo_children():
        if button.cget("text"):
            continue
        
        buttons_to_pick.append(button)
        
    button_choice = random.choice(buttons_to_pick)
    
    for frame in frames:
        for button in frames[frame].winfo_children():
            if button == button_choice:
                for button_position in buttons:
                    if buttons[button_position] == button_choice:
                        button_choice_position = button_position
    
    return button_choice_position

def undo_step():
    global current_symbol
    global frames_taken_by_symbol
    
    if not log_history["button_location_pressed"] and not log_history["frames_taken_by_symbol_state"] and not log_history["symbol_state"]:
        return
    
    # sets the current symbol to the previous symbol
    current_symbol = log_history["symbol_state"][-1]
    log_history["symbol_state"].pop()
    
    current_symbol_var.set(current_symbol)
    
    # opens the previous frame and resets the button value
    last_button_pressed = log_history["button_location_pressed"][-1]
    
    # resets the buttons text
    buttons[last_button_pressed].config(text="")
    
    last_button_pressed_splitted = last_button_pressed.split("_")
    
    previous_frame = last_button_pressed_splitted[0] + "_" + last_button_pressed_splitted[1]
    button_pressed = last_button_pressed_splitted[2] + "_" + last_button_pressed_splitted[3]
    
    # firstly disables every frame
    for frame in frames:
        for button in frames[frame].winfo_children():
            button.config(state="disabled")
    
    # opens the previous frame that was closed
    if len(log_history["button_location_pressed"]) != 1:
        for frame in frames:
            for button in frames[previous_frame].winfo_children():
                if button.cget("text"):
                    continue
                button.config(state="normal")

    # opens every frame if it was the first turn which was undid
    else:
        for frame in frames:
            for button in frames[frame].winfo_children():
                button.config(state="normal")

    log_history["button_location_pressed"].pop()
    
    # sets the frames taken by symbol values to their previous states
    try:
        frames_taken_by_symbol = log_history["frames_taken_by_symbol_state"][-2].copy()
        for button in frames[previous_frame].winfo_children():
            if button.cget("style") == "won.TButton":
                button.config(style="")
    except IndexError:
        pass

    log_history["frames_taken_by_symbol_state"].pop()

def restart_game(finished_game_widgets):
    global current_symbol
    global frames_taken_by_symbol
    
    # enables the undo button, so it's not disabled forever
    undo_button.config(state="normal")
    
    # removes the widgets appearing when the game has finished
    for widget in finished_game_widgets.winfo_children():
        widget.pack_forget()
        
    # resets every button
    for frame in frames:
        for button in frames[frame].winfo_children():
            button.config(text="", state="normal")

    # resets the frames taken by a symbol
    frames_taken_by_symbol = {}
    
    # resets the starting symbol
    current_symbol = "X"

def stop_game(symbol_that_won: str):
    global current_symbol
    global scores
    
    # disables the undo button, so no unlimited points glitch can be exploited
    undo_button.config(state="disabled")
    
    for frame in frames:
        for button in frames[frame].winfo_children():
            button.config(state="disabled")
            
    scores[symbol_that_won] += 1
    
    x_score_tracker.set(f"X:  {scores['X']}")
    o_score_tracker.set(f"O:  {scores['O']}")
    
    finished_game_widget_canvas = ttk.Frame(root)
    finished_game_widget_canvas.pack()
        
    finished_game_information_label = ttk.Label(finished_game_widget_canvas, text=f"Das Spiel ist zuende. \"{symbol_that_won}\" hat das Spiel gewonnen.", foreground="#60100B", font="Monospace 18 bold")
    finished_game_information_label.pack()
    
    restart_game_button = ttk.Button(finished_game_widget_canvas, text="Nächstes Spiel", takefocus=False, command= lambda w=finished_game_widget_canvas: restart_game(w))
    restart_game_button.pack()

def update_button(position: str, iteration: int = 0):
    global current_symbol
        
    # saves the current symbol to the history
    log_history["symbol_state"].append(current_symbol)
    
    # saves the button pressed to the history
    log_history["button_location_pressed"].append(position)
    
    # every button of every frame will firstly set disabled
    for frame in frames:
        for button in frames[frame].winfo_children():
            button.config(state="disabled")
    
    # sets the current symbol to the button
    buttons[position].config(text=current_symbol)
    
    button_clicked_position = position.split("_")
    
    current_frame = button_clicked_position[0] + "_" + button_clicked_position[1]
    next_frame = button_clicked_position[2] + "_" + button_clicked_position[3]
    
    # calculates if a three-in-a-row-hit was made in a frame
    if not frames_taken_by_symbol.get(current_frame):
        for button in frames[current_frame].winfo_children():
            for symbol in symbols:
                # left to right
                if buttons[current_frame+"_"+"top_left"].cget("text") == symbol and buttons[current_frame+"_"+"top_center"].cget("text") == symbol and buttons[current_frame+"_"+"top_right"].cget("text") == symbol:
                    frames_taken_by_symbol[current_frame] = current_symbol
                    buttons[current_frame+"_"+"top_left"].config(style="won.TButton")
                    buttons[current_frame+"_"+"top_center"].config(style="won.TButton")
                    buttons[current_frame+"_"+"top_right"].config(style="won.TButton")
                    
                elif buttons[current_frame+"_"+"middle_left"].cget("text") == symbol and buttons[current_frame+"_"+"middle_center"].cget("text") == symbol and buttons[current_frame+"_"+"middle_right"].cget("text") == symbol:
                    frames_taken_by_symbol[current_frame] = current_symbol

                elif buttons[current_frame+"_"+"bottom_left"].cget("text") == symbol and buttons[current_frame+"_"+"bottom_center"].cget("text") == symbol and buttons[current_frame+"_"+"bottom_right"].cget("text") == symbol:
                    frames_taken_by_symbol[current_frame] = current_symbol
                    buttons[current_frame+"_"+"bottom_left"].config(style="won.TButton")
                    buttons[current_frame+"_"+"bottom_center"].config(style="won.TButton")
                    buttons[current_frame+"_"+"bottom_right"].config(style="won.TButton")
                    
                # top to bottom or vice versa (doesn't matter)
                elif buttons[current_frame+"_"+"top_left"].cget("text") == symbol and buttons[current_frame+"_"+"middle_left"].cget("text") == symbol and buttons[current_frame+"_"+"bottom_left"].cget("text") == symbol:
                    frames_taken_by_symbol[current_frame] = current_symbol
                    buttons[current_frame+"_"+"top_left"].config(style="won.TButton")
                    buttons[current_frame+"_"+"middle_left"].config(style="won.TButton")
                    buttons[current_frame+"_"+"bottom_left"].config(style="won.TButton")

                elif buttons[current_frame+"_"+"top_center"].cget("text") == symbol and buttons[current_frame+"_"+"middle_center"].cget("text") == symbol and buttons[current_frame+"_"+"bottom_center"].cget("text") == symbol:
                    frames_taken_by_symbol[current_frame] = current_symbol
                    buttons[current_frame+"_"+"top_center"].config(style="won.TButton")
                    buttons[current_frame+"_"+"middle_center"].config(style="won.TButton")
                    buttons[current_frame+"_"+"bottom_center"].config(style="won.TButton")

                elif buttons[current_frame+"_"+"top_right"].cget("text") == symbol and buttons[current_frame+"_"+"middle_right"].cget("text") == symbol and buttons[current_frame+"_"+"bottom_right"].cget("text") == symbol:
                    frames_taken_by_symbol[current_frame] = current_symbol
                    buttons[current_frame+"_"+"top_right"].config(style="won.TButton")
                    buttons[current_frame+"_"+"middle_right"].config(style="won.TButton")
                    buttons[current_frame+"_"+"bottom_right"].config(style="won.TButton")

                # top left to bottom right
                elif buttons[current_frame+"_"+"top_left"].cget("text") == symbol and buttons[current_frame+"_"+"middle_center"].cget("text") == symbol and buttons[current_frame+"_"+"bottom_right"].cget("text") == symbol:
                    frames_taken_by_symbol[current_frame] = current_symbol
                    buttons[current_frame+"_"+"top_left"].config(style="won.TButton")
                    buttons[current_frame+"_"+"middle_center"].config(style="won.TButton")
                    buttons[current_frame+"_"+"bottom_right"].config(style="won.TButton")

                # top right to bottom left
                elif buttons[current_frame+"_"+"top_right"].cget("text") == symbol and buttons[current_frame+"_"+"middle_center"].cget("text") == symbol and buttons[current_frame+"_"+"bottom_left"].cget("text") == symbol:
                    frames_taken_by_symbol[current_frame] = current_symbol
                    buttons[current_frame+"_"+"top_right"].config(style="won.TButton")
                    buttons[current_frame+"_"+"middle_center"].config(style="won.TButton")
                    buttons[current_frame+"_"+"bottom_left"].config(style="won.TButton")

    # saves the frame taken by symbol to the history
    log_history["frames_taken_by_symbol_state"].append({x: y for x, y in frames_taken_by_symbol.items()})
    
    # opens the next frame
    for button in frames[next_frame].winfo_children():
        if button.cget("text"):
            continue
        button.config(state="normal")
    
    current_symbol = "O" if current_symbol == "X" else "X"
    current_symbol_var.set(current_symbol)
    
    # calculates if a three-in-a-row-hit was made with frames taken by symbol
    for symbol in symbols:
        # left to right
        if frames_taken_by_symbol.get("top_left") == symbol and frames_taken_by_symbol.get("top_center") == symbol and frames_taken_by_symbol.get("top_right") == symbol:
            stop_game(symbol)

        elif frames_taken_by_symbol.get("middle_left") == symbol and frames_taken_by_symbol.get("middle_center") == symbol and frames_taken_by_symbol.get("middle_right") == symbol:
            stop_game(symbol)

        elif frames_taken_by_symbol.get("bottom_left") == symbol and frames_taken_by_symbol.get("bottom_center") == symbol and frames_taken_by_symbol.get("bottom_right") == symbol:
            stop_game(symbol)

        # top to bottom or vice versa (doesn't matter)
        elif frames_taken_by_symbol.get("top_left") == symbol and frames_taken_by_symbol.get("middle_left") == symbol and frames_taken_by_symbol.get("bottom_left") == symbol:
            stop_game(symbol)
                
        elif frames_taken_by_symbol.get("top_center") == symbol and frames_taken_by_symbol.get("middle_center") == symbol and frames_taken_by_symbol.get("bottom_center") == symbol:
            stop_game(symbol)

        elif frames_taken_by_symbol.get("top_right") == symbol and frames_taken_by_symbol.get("middle_right") == symbol and frames_taken_by_symbol.get("bottom_right") == symbol:
            stop_game(symbol)

        # top left to bottom right
        elif frames_taken_by_symbol.get("top_left") == symbol and frames_taken_by_symbol.get("middle_center") == symbol and frames_taken_by_symbol.get("bottom_right") == symbol:
            stop_game(symbol)

        # top right to bottom left
        elif frames_taken_by_symbol.get("top_right") == symbol and frames_taken_by_symbol.get("middle_center") == symbol and frames_taken_by_symbol.get("bottom_left") == symbol:
            stop_game(symbol)

    if iteration == 0 and playing_with_bot:
        enemy_button_choice = get_bot_placement(next_frame)
        update_button(enemy_button_choice, iteration=1)
        time.sleep(random.choice(range(0.25, 0.75, 0.1)))

root = ttk.Window(themename="darkly")

button_style_change = ttk.Style()
button_style_change.map("won.TButton", background=[("disabled", "#60100B")])

# just the title of the game
title = ttk.Label(root, text="Super Tic Tac Toe", foreground="#9867C5", font="Monospace 24 bold")
title.pack()

# starts the game either to play with a friend or a bot
intro_canvas = ttk.Frame(root)
intro_canvas.pack()

intro_label = ttk.Label(intro_canvas, text="Möchtest du mit einem Freund oder einem einfachen Bot spielen?", font="Monospace 16 bold")
intro_label.pack()

intro_canvas_button_canvas = ttk.Frame(intro_canvas)
intro_canvas_button_canvas.pack()

play_with_friend_button = ttk.Button(intro_canvas_button_canvas, text="Freund", takefocus=False, command=lambda m=False: start_game(m))
play_with_friend_button.pack(side="left", padx=5, pady=5)

play_with_bot_button = ttk.Button(intro_canvas_button_canvas, text="Bot", takefocus=False, command=lambda m=True: start_game(m))
play_with_bot_button.pack(side="right", padx=5, pady=5)

# the scores in case more games want to be played
score_drawing_canvas = ttk.Frame(root)

# the score for X
x_score_tracker = ttk.StringVar()
x_score_tracker.set("X:  0")
x_score_label = ttk.Label(score_drawing_canvas, textvariable=x_score_tracker, foreground="#80400B", font="Monospace 12 bold")
x_score_label.pack(side="left", padx=50)

# the score for O
o_score_tracker = ttk.StringVar()
o_score_tracker.set("O:  0")
o_score_label = ttk.Label(score_drawing_canvas, textvariable=o_score_tracker, foreground="#80400B", font="Monospace 12 bold")
o_score_label.pack(side="left", padx=50)

# shows which symbol's turn it currently is
symbol_canvas = ttk.Frame(root)

current_symbol_var = ttk.StringVar()
current_symbol_var.set("X")
current_symbol_label = ttk.Label(symbol_canvas, textvariable=current_symbol_var, foreground="#028A0F", font="Monospace 16 bold")
current_symbol_label.pack()

# the canvas for the frames
playground = ttk.Frame(root)

# creates the frames the buttons will be created and drawn on
current_row = 0
current_column = 0
for position in widget_positions:
    if current_column % 3 == 0:
        current_row += 1
        current_column = 0
    
    frames[position] = ttk.Frame(playground)
    frames[position].grid(row=current_row, column=current_column, padx=5, pady=5)
    current_column += 1

# creates and draws the 3x3 button grid on the frames
current_row = 0
current_column = 0
for frame in frames:
    for position in widget_positions:
        if current_column % 3 == 0:
            current_row += 1
            current_column = 0
        buttons[frame+"_"+position] = ttk.Button(frames[frame], takefocus=False, command= lambda p=frame+"_"+position: update_button(p))
        buttons[frame+"_"+position].grid(row=current_row, column=current_column, padx=5, pady=5)
        current_column += 1

# createds an button, to undo the latest pressed button
undo_button_canvas = ttk.Frame(root)

undo_button = ttk.Button(undo_button_canvas, text="Schritt zurück", takefocus=False, command=undo_step)
undo_button.pack()

root.mainloop()
