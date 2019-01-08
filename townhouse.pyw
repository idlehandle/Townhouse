import tkinter as tk
import datetime as dt
from random import randint, choice
from tkinter.messagebox import askyesno

class Clock(tk.Tk):

    def set_default(self, width, height):
        self.app_width = width                                                  # Default 240
        self.app_height = height                                                # Default 320
        self.app_mid_x = self.app_width // 2                                    # Default 120
        self.app_margin_x = self.app_width // 6                                 # Default 40
        self.app_margin_y = self.app_height // 16                               # Default 20
        self.win_width = (self.app_width - (self.app_margin_x * 2)) // 8        # Default 20
        self.win_height = (self.app_height - (self.app_margin_y * 4)) // 8      # Default 30
        self.win_gap_x = self.win_width // 2                                    # Default 10 
        self.door_width = self.win_width * 1.5                                  # Default 30
        self.door_height = self.app_margin_y * 2                                # Default 40
        self.transparency = 0.8

    def __init__(self, width=120, height=160):
        super().__init__()
        self.title("Townhouse Clock")
        self.set_default(width, height)

        ### Make the window titlebar-less...                                    ###
        self.restore("<Map event>")                                             # invoke the overrideredirect
        self.geometry('{width}x{height}+{offset}+0'.format(
            width=self.app_width, 
            height=self.app_height, 
            offset=self.winfo_screenwidth() - self.app_width)                   # Default Offset to top right corner
            )
        self.canvas = tk.Canvas(self, width=self.app_width, height=self.app_height)
        self.draw_background(self.canvas)
        self.draw_house(self.canvas)

        ### Presets of 4x4 windows with starting x location                     ###       
        self.windows = [
            [
                self.app_margin_x + self.win_gap_x, 
                self.app_margin_x + self.win_width + self.win_gap_x * 2, 
                self.app_width - self.app_margin_x - self.win_width * 2 - self.win_gap_x * 2, 
                self.app_width - self.app_margin_x - self.win_width - self.win_gap_x
            ] 
            for i in range(4)
        ]   # using *4 makes identical objects
        ### Create each window based on x and an offsetted y                    ###
        for y, rows in enumerate(self.windows): 
            for x, r in enumerate(rows):     
                # y is spaced by * space + offset default *55+60
                self.windows[y][x] = self.draw_window(
                                        self.canvas, r, 
                                        y * (self.win_height * 2) + (self.win_height * 2) + (0 if y < 2 else self.win_height // 6), 
                                        self.win_width, self.win_height
                                        )
        
        ### Courtesy of Bryan Oakley's answer from SO                           ###
        ### This allows mouse dragging by holding on the canvas                 ###
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<MouseWheel>", self.change_transparency)
        self.bind('<Map>', self.restore) # added bindings to pass windows status to function
        self.bind('<Unmap>', self.restore)
        self.canvas.pack()

        ### Sync up the time by milliseconds as best as possible                ###
        sec = int(dt.datetime.strftime(dt.datetime.now(), "%f"))//1000
        self.after(ms=sec, func=self.get_time())
        self.after(ms=1000, func=self.blue_moon)

    def get_time(self):
        now = [f'{int(i):04b}' for i in dt.datetime.strftime(dt.datetime.now(), "%H%M")]
        for x, col in enumerate(now):
            for y, lights_on in enumerate(col):
                self.canvas.itemconfig(self.windows[y][x], state=tk.NORMAL if int(lights_on) else tk.DISABLED)
        self.after(ms=1000, func=self.get_time)

    def change_transparency(self, event):
        transparency = self.transparency + event.delta/2400
        if transparency >= 0.3 and transparency <= 1.0:
            self.transparency = round(transparency, 2)
            self.wm_attributes("-alpha", self.transparency)

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
            self.wm_attributes("-topmost", True)
            self.wm_attributes("-alpha", self.transparency)

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
        blue_moon_colour = 'aquamarine'
        canv.config(background=night_colour, borderwidth=0.0, highlightthickness=0.0)

        ### Grass ###
        canv.create_rectangle(0, self.app_height - self.app_margin_y + 1, self.app_width, self.app_height, fill=ground_colour, outline=ground_colour)
        
        ### Draw a moon surface for clickable minimizing on overrideredirect    ###
        moon_size = self.app_width // 10
        moon_margin = (self.app_margin_x * 3) // 4
        moon_boundary = [
                            self.app_width - moon_margin,
                            moon_margin // 3,
                            self.app_width - moon_margin + moon_size,
                            moon_margin // 3 + moon_size
                        ]
        self.moon = []
        self.moon.append(canv.create_arc(*moon_boundary, start=240, extent=90, style=tk.CHORD, 
                fill=moon_colour, disabledfill=blue_moon_colour, outline=moon_colour, disabledoutline=blue_moon_colour))
        self.moon.append(canv.create_arc(*moon_boundary, start=270, extent=120, style=tk.CHORD, 
                fill=moon_colour, disabledfill=blue_moon_colour, outline=moon_colour, disabledoutline=blue_moon_colour))
        self.moon.append(canv.create_arc(*moon_boundary, start=300, extent=120, style=tk.CHORD, 
                fill=moon_colour, disabledfill=blue_moon_colour, outline=moon_colour, disabledoutline=blue_moon_colour))
        self.moon.append(canv.create_arc(*moon_boundary, start=330, extent=90, style=tk.CHORD, 
                fill=moon_colour, disabledfill=blue_moon_colour, outline=moon_colour, disabledoutline=blue_moon_colour))
        self.moon.append(canv.create_arc(*moon_boundary, start=0, extent=90, style=tk.CHORD, 
                fill=moon_colour, disabledfill=blue_moon_colour, outline=moon_colour, disabledoutline=blue_moon_colour))

    def draw_house(self, canv):
        ### Draw the house                                                      ###
        self.house_colours = ['firebrick4', 'maroon', 'tomato4', 'OrangeRed4', 'sienna4', 'saddle brown']
        self.house_colour = choice(self.house_colours)      # 'firebrick4' # 'saddle brown' # 'DarkOrange4'
        self.door_colour = 'DarkOrange4'                    # 'saddle brown' # '#5F3F22' # 'brown4'
        self.knob_colour = '#4E2D10'                        # 'burlywood4'

        self.draw_house_arc_with_bricks(
            self.canvas,
            self.app_margin_x, 
            self.app_margin_y, 
            self.app_width - self.app_margin_x, 
            self.app_margin_y * 5)

        self.fill_with_bricks(
            canv,
            self.app_margin_x, 
            self.app_margin_y * 3, 
            self.app_width - self.app_margin_x, 
            self.app_height - self.app_margin_y
        )
        canv.create_rectangle(
            self.app_margin_x, 
            self.app_margin_y * 3, 
            self.app_width - self.app_margin_x, 
            self.app_height - self.app_margin_y 
            )
        canv.create_line(
            self.app_margin_x + 1, 
            self.app_margin_y * 3, 
            self.app_width - self.app_margin_x - 1, 
            self.app_margin_y * 3, 
            fill=self.door_colour
            )
        ### Designate the areas in which the door is for exit purpose           ###        
        self.door = []        
        door_x1 = self.app_mid_x - self.door_width // 2
        door_x2 = self.app_mid_x + self.door_width // 2
        door_y1 = self.app_height - self.app_margin_y * 3
        door_y2 = door_y1 + self.door_height
        door_arc_height = self.door_height * 0.375
        knob_x = self.door_width // 6
        knob_y = door_y1 + door_arc_height
        knob_size = (self.door_width * 2) // 15
        self.door.append(canv.create_arc(
            door_x1, 
            door_y1 - door_arc_height, 
            door_x2, 
            door_y1 + self.app_margin_y, 
            start=0, extent=180, fill=self.door_colour)
            )
        self.door.append(canv.create_rectangle(
            door_x1,
            door_y1, 
            door_x2, 
            door_y2, 
            fill=self.door_colour)
            )
        self.door.append(canv.create_line(
            door_x1 + 1, 
            door_y1, 
            door_x2 - 1, 
            door_y1, 
            fill=self.door_colour)
            )
        self.door.append(canv.create_line(
            self.app_mid_x, 
            door_y1 - door_arc_height, 
            self.app_mid_x, 
            door_y2)
            )
        self.door.append(canv.create_oval(
            self.app_mid_x + knob_x - knob_size // 2,
            knob_y - knob_size // 2, 
            self.app_mid_x + knob_x + knob_size // 2, 
            knob_y + knob_size // 2, 
            fill=self.knob_colour, outline=self.knob_colour)
            )
        self.door.append(canv.create_oval(
            self.app_mid_x - knob_x - knob_size // 2, 
            knob_y - knob_size // 2, 
            self.app_mid_x - knob_x + knob_size // 2, 
            knob_y + knob_size // 2, 
            fill=self.knob_colour, outline=self.knob_colour)
            )

    def draw_house_arc_with_bricks(self, canv, x1, y1, x2, y2):        
        divider = 4
        delta_x = (x2 - x1) // (2 * divider)
        delta_y = (y2 - y1) // (2 * divider)
        steps = [15, 20, 30, 60]
        for dy, dx in enumerate(range(0, delta_x * divider, delta_x)):
            for i in range(0, 180, steps[dy]):
                canv.create_arc(
                    x1 + dx, y1 + (dy * delta_y), x2 - dx, y2 - (dy * delta_y),
                    start=i, extent=steps[dy], 
                    outline=self.door_colour, fill=choice(self.house_colours),
                    style=tk.PIESLICE
                    )        
        canv.create_arc(
            x1, y1, x2, y2,
            start=0, extent=180, style=tk.ARC
            )

    def fill_with_bricks(self, canv, x1, y1, x2, y2):
        bricks = {'x': 10, 'y': 20}
        width = (x2 - x1) // bricks.get('x')
        height = (y2 - y1) // bricks.get('y')
        delta_y = y1
        while delta_y < y2:
            delta_x = x1
            while delta_x < x2:
                if delta_x == x1:
                    x_end = delta_x + randint(0, width)
                else:
                    x_end = delta_x + width
                x_end = x_end if x_end <= x2 else x2
                y_end = delta_y + height
                y_end = y_end if y_end <= y2 else y2
                canv.create_rectangle(delta_x, delta_y, x_end, y_end, outline=self.door_colour, fill=choice(self.house_colours))                
                delta_x = x_end
            delta_y += height 

    def blue_moon(self, is_blue=False):
        next_blue = randint(300, 7200) * 1000
        if is_blue:
            for moon_piece in self.moon:
                self.canvas.itemconfig(moon_piece, state=tk.DISABLED)
            self.after(ms=300000, func=lambda: self.blue_moon(False))
        else:
            for moon_piece in self.moon:
                self.canvas.itemconfig(moon_piece, state=tk.NORMAL)
        self.after(ms=next_blue, func=lambda: self.blue_moon(True))

        
def main():    
    townhouse = Clock()
    townhouse.mainloop()

if __name__ == '__main__':
    main()

