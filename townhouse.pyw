import tkinter as tk
import datetime as dt
from tkinter.messagebox import askyesno

class Clock(tk.Tk):
    app_width = 240                                                             # Default 240
    app_height = 320                                                            # Default 320
    app_mid_x = app_width // 2                                                  # Default 120
    app_margin_x = app_width // 6                                               # Default 40
    app_margin_y = app_height // 16                                             # Default 20
    win_width = (app_width - (app_margin_x * 2)) // 8                           # Default 20
    win_height = (app_height - (app_margin_y * 4)) // 8                         # Default 30
    win_gap_x = win_width // 2                                                  # Default 10 
    door_width = win_width * 1.5                                                # Default 30
    door_height = app_margin_y * 2                                              # Default 40
    def __init__(self):
        super().__init__()
        self.title("Townhouse Clock")

        ### Make the window titlebar-less...                                    ###
        self.overrideredirect(True)
        self.geometry('{width}x{height}+{offset}+0'.format(
            width=Clock.app_width, 
            height=Clock.app_height, 
            offset=self.winfo_screenwidth() - Clock.app_width)                  # Default Offset to top right corner
            )
        self.canvas = tk.Canvas(self, width=Clock.app_width, height=Clock.app_height)
        self.draw_background(self.canvas)
        self.draw_house(self.canvas)

        ### Presets of 4x4 windows with starting x location                     ###       
        self.windows = [
            [Clock.app_margin_x + Clock.win_gap_x, 
                Clock.app_margin_x + Clock.win_width + Clock.win_gap_x * 2, 
                Clock.app_width - Clock.app_margin_x - Clock.win_width * 2 - Clock.win_gap_x * 2, 
                Clock.app_width - Clock.app_margin_x - Clock.win_width - Clock.win_gap_x] 
            for i in range(4)
        ]   # using *4 makes identical objects
        ### Create each window based on x and an offsetted y                    ###
        for y, rows in enumerate(self.windows): 
            for x, r in enumerate(rows):     
                # y is spaced by * space + offset default *55+60
                self.windows[y][x] = self.draw_window(
                                        self.canvas, r, 
                                        y * (Clock.win_height * 2) + (Clock.win_height * 2) + (0 if y < 2 else Clock.win_height // 6), 
                                        Clock.win_width, Clock.win_height
                                    )
        
        ### Courtesy of Bryan Oakley's answer from SO                           ###
        ### This allows mouse dragging by holding on the canvas                 ###
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.bind('<Map>', self.restore) # added bindings to pass windows status to function
        self.bind('<Unmap>', self.restore)
        self.canvas.pack()

        ### Sync up the time by milliseconds as best as possible                ###
        sec = int(dt.datetime.strftime(dt.datetime.now(), "%f"))//1000
        self.after(ms=sec, func=self.get_time())

    def get_time(self):
        now = [f'{int(i):04b}' for i in dt.datetime.strftime(dt.datetime.now(), "%H%M")]
        for x, col in enumerate(now):
            for y, lights_on in enumerate(col):
                self.canvas.itemconfig(self.windows[y][x], state=tk.NORMAL if int(lights_on) else tk.DISABLED)
        self.after(ms=1000, func=self.get_time)

    def start_move(self, event):
        ### Check for special events...
        if self.special_event() == self.door:
            if askyesno("Exit Confirmation", "Exit Townhouse Clock?"):
                self.destroy()
        elif self.special_event() == self.moon:
            self.minimize()
        
        ### If nothing special, allow the movment                               ###
        else:
            self.x = event.x
            self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_motion(self, event):
        ### Check for special events - if nothing special, allow dragging       ###
        if self.special_event() is None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry("+{x}+{y}".format(x=x, y=y))
    
    def special_event(self):
        ### Determine if a special area was clicked for extra handling          ###
        try:
            clicked_tag = self.canvas.find_withtag(tk.CURRENT)[0]
            if clicked_tag in self.door:
                return self.door
            elif clicked_tag in self.moon:
                return self.moon
            else:
                return None

        ### TODO: Getting IndexError near the moon for some reason, see if can be narrowed down... ignored for now. ###
        except IndexError:
            return None

    def minimize(self):
        ### Hide, disable override and iconify the window on callback           ###
        self.withdraw()
        self.overrideredirect(False)
        self.iconify()

    def restore(self, event): 
        ### Apply override on deiconify.                                        ###
        if str(event) == "<Map event>":
            self.overrideredirect(True)                            

    def draw_window(self, canv, x, y, w, h):
        ### Drawing of each window ###
        x2, y2 = x + w, y + h
        window = canv.create_rectangle(x, y, x2, y2, fill='orange', disabledfill='gray20')
        mid_x = w // 2 + x
        mid_y = h // 2 + y
        canv.create_line(mid_x, y, mid_x, y2)
        canv.create_line(x, mid_y, x2, mid_y)
        canv.itemconfig(window, state=tk.DISABLED)

        ### Return the drawn window back layer to control the lights later      ###
        return window

    def draw_background(self, canv):
        ### Create The backdrop for the townhouse                               ###
        night_colour = 'midnight blue'
        ground_colour = 'dark slate gray'
        moon_colour = 'lemon chiffon'
        canv.config(background=night_colour, borderwidth=0.0, highlightthickness=0.0)

        ### Grass ###
        canv.create_rectangle(0, Clock.app_height - Clock.app_margin_y + 1, Clock.app_width, Clock.app_height, fill=ground_colour, outline=ground_colour)
        
        ### Draw a moon surface for clickable minimizing on overrideredirect    ###
        moon_size = Clock.app_width // 10
        moon_margin = (Clock.app_margin_x * 3) // 4
        moon_boundary = [
                            Clock.app_width - moon_margin,
                            moon_margin // 3,
                            Clock.app_width - moon_margin + moon_size,
                            moon_margin // 3 + moon_size
                        ]
        self.moon = []
        self.moon.append(canv.create_arc(*moon_boundary, start=240, extent=90, style=tk.CHORD, fill=moon_colour, outline=moon_colour))
        #self.moon.append(canv.create_arc(*moon_boundary, start=270, extent=90, style=tk.CHORD, fill=moon_colour, outline=moon_colour))
        self.moon.append(canv.create_arc(*moon_boundary, start=270, extent=120, style=tk.CHORD, fill=moon_colour, outline=moon_colour))
        self.moon.append(canv.create_arc(*moon_boundary, start=300, extent=120, style=tk.CHORD, fill=moon_colour, outline=moon_colour))
        self.moon.append(canv.create_arc(*moon_boundary, start=330, extent=90, style=tk.CHORD, fill=moon_colour, outline=moon_colour))
        self.moon.append(canv.create_arc(*moon_boundary, start=0, extent=90, style=tk.CHORD, fill=moon_colour, outline=moon_colour))

    def draw_house(self, canv):
        ### Draw the house                                                      ###
        house_colour = 'DarkOrange4'
        door_colour = 'brown4'
        knob_colour = '#4E2D10' #'burlywood4'

        ### Trying to introduce scalability...
        canv.create_arc(Clock.app_margin_x, Clock.app_margin_y, Clock.app_width - Clock.app_margin_x, Clock.app_margin_y * 5, start=0, extent=180, fill=house_colour)
        canv.create_rectangle(Clock.app_margin_x, Clock.app_margin_y * 3, Clock.app_width - Clock.app_margin_x, Clock.app_height - Clock.app_margin_y, fill=house_colour)
        canv.create_line(Clock.app_margin_x+1, Clock.app_margin_y * 3, Clock.app_width - Clock.app_margin_x - 1, Clock.app_margin_y * 3, fill=house_colour)

        ### Designate the areas in which the door is for exit purpose           ###        
        self.door = []        
        door_x1 = Clock.app_mid_x - Clock.door_width // 2
        door_x2 = Clock.app_mid_x + Clock.door_width // 2
        door_y1 = Clock.app_height - Clock.app_margin_y * 3
        door_y2 = door_y1 + Clock.door_height
        door_arc_height = Clock.door_height * 0.375
        knob_x = Clock.door_width // 6
        knob_y = door_y1 + door_arc_height
        knob_size = (Clock.door_width * 2) // 15
        self.door.append(canv.create_arc(door_x1, door_y1 - door_arc_height, door_x2, door_y1 + Clock.app_margin_y, start=0, extent=180, fill=door_colour))
        self.door.append(canv.create_rectangle(door_x1, door_y1, door_x2, door_y2, fill=door_colour))
        self.door.append(canv.create_line(door_x1 + 1, door_y1, door_x2 - 1, door_y1, fill=door_colour))
        self.door.append(canv.create_line(Clock.app_mid_x, door_y1 - door_arc_height, Clock.app_mid_x, door_y2))
        self.door.append(canv.create_oval(Clock.app_mid_x + knob_x - knob_size // 2,
                                         knob_y - knob_size // 2, 
                                         Clock.app_mid_x + knob_x + knob_size // 2, 
                                         knob_y + knob_size // 2, 
                                         fill=knob_colour, outline=knob_colour))
        self.door.append(canv.create_oval(Clock.app_mid_x - knob_x - knob_size // 2, 
                                         knob_y - knob_size // 2, 
                                         Clock.app_mid_x - knob_x + knob_size // 2, 
                                         knob_y + knob_size // 2, 
                                         fill=knob_colour, outline=knob_colour))
        
def main():    
    townhouse = Clock()
    townhouse.mainloop()

if __name__ == '__main__':
    main()

