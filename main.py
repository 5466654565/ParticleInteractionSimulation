# ===================================================
# Incubator
# ===================================================

import tkinter as tk
import random
import math
import psutil
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import sys
import os
import numpy as np
from PIL import Image, ImageTk
import pygame
pygame.init()
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# ===================================================
# INITIAL CONFIGURATION
# ===================================================

canvas_width_ratio = 1.0
canvas_height_ratio = 1.0

current_process = psutil.Process(os.getpid())

fig = Figure(figsize=(6, 4), dpi=100, facecolor='black')

freeze_movement = False

window_closed = False

checkpoint = False

# ===================================================
# GLOBAL FONCTION
# ===================================================

def keyboard(event):
    if event.keysym == 'Return':
        create_clouds()

# ===================================================
# SETTING
# ===================================================

#clash
min_speed = 0.1
max_speed = 2

#angle
min_angle = 0
max_angle = 180

#electronegativity
bond_chance = 0.25 
min_electronegativity = 0.7
max_electronegativity = 4.0

#polarity
polar_covalent_threshold = 0.4
ionic_threshold = 1.7

#type_cloud
num_cloud_types = 100
min_type = 1
max_type = num_cloud_types
clouds = []
group_clouds = []
cloud_quantity_entry = None
create_cloud_button = None
size = 20

#mass
standard_mass = 1

class Initial_Assign_Properties:

    def __init__(self, x, y):
        self.color = Initial_Assign_Properties.color_initial_assign()
        self.dx, self.dy = self.clash_initial_assign()
        self.electronegativities = self.electronegativity_initial_assign()
        self.x = x
        self.y = y
        self.radius = size/2
        self.canvas_id = None
        self.angular_velocity = 1

    @staticmethod
    def color_initial_assign():
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        color = f'#{red:02X}{green:02X}{blue:02X}'
        
        return color

    def clash_initial_assign(self):   
        angle = random.uniform(min_angle, max_angle)
        speed = random.uniform(min_speed, max_speed)
        dx = speed * math.cos(math.radians(angle))
        dy = speed * math.sin(math.radians(angle))

        return dx, dy

    def electronegativity_initial_assign(self):
        type_probability = random.randint(min_type, max_type)
        cloud_type = random.randint(min_type,type_probability)
        x = cloud_type % 10
        y = cloud_type // 10
        electronegativities = min_electronegativity + ((max_electronegativity - min_electronegativity) / 10) * (x + y)
        
        return electronegativities

class GroupCloud:
    def __init__(self, clouds):
        self.clouds = clouds
        self.x, self.y = self.calculate_center_of_mass()
        self.dx, self.dy = self.calculate_group_velocity()
        #self.angular_velocity = self.calculate_angular_velocity()
        #self.moment_of_inertia = self.calculate_moment_of_inertia()
        self.canvas_group_id = None

    def calculate_center_of_mass(self):
        total_mass = standard_mass * len(self.clouds)
        CMx = sum(cloud.x * standard_mass for cloud in self.clouds) / total_mass
        CMy = sum(cloud.y * standard_mass for cloud in self.clouds) / total_mass
        return (CMx, CMy)

    #def calculate_angular_velocity(self):
        #total_mass = standard_mass * len(self.clouds)
        #weighted_sum = sum(cloud.angular_velocity * standard_mass for cloud in self.clouds)
        #angular_velocity = weighted_sum / total_mass
        #return angular_velocity

    #def calculate_moment_of_inertia(self):
        #CMx, CMy = self.calculate_center_of_mass()
        #moment_of_inertia = sum(standard_mass * ((cloud.x - CMx)**2 + (cloud.y - CMy)**2) for cloud in self.clouds)
        #return moment_of_inertia
    
    def calculate_group_velocity(self):
        total_momentum_dx = sum(cloud.dx * standard_mass for cloud in self.clouds)
        total_momentum_dy = sum(cloud.dy * standard_mass for cloud in self.clouds)
        total_mass = standard_mass * len(self.clouds)
        group_dx = total_momentum_dx / total_mass
        group_dy = total_momentum_dy / total_mass
        return group_dx, group_dy

    def update_position(self):
        self.x += self.dx
        self.y += self.dy

# ===================================================
# EVENT
# ===================================================
    
def freeze():
    global freeze_movement
    if freeze_movement:
        freeze_movement = False
    else:
        freeze_movement = True

def create_clouds():  
    cloud_quantity= int(cloud_quantity_entry.get())
    for _ in range(cloud_quantity):
        x, y = random.uniform(0, right_frame.winfo_width()), random.uniform(0, right_frame.winfo_height())
        new_cloud = Initial_Assign_Properties(x, y)
        new_cloud.canvas_id = canvas.create_oval(x, y, x + size, y + size, fill=new_cloud.color)
        clouds.append(new_cloud)
    if len(clouds) >= 2:
        monitoring()
    move_clouds()

def move_clouds():
    for cloud in clouds:
        if not freeze_movement:
            cloud_coords = canvas.coords(cloud.canvas_id)
            if cloud_coords:
                x1, y1, x2, y2 = cloud_coords
                new_x1, new_y1 = x1 + cloud.dx, y1 + cloud.dy
                new_x2, new_y2 = x2 + cloud.dx, y2 + cloud.dy
                
                canvas_width = right_frame.winfo_width()
                canvas_height = right_frame.winfo_height()

                if new_x2 > canvas_width:
                    new_x1, new_x2 = 1, 21
                elif new_x1 < 0:
                    new_x1, new_x2 = canvas_width - 20, canvas_width

                if new_y2 > canvas_height:
                    new_y1, new_y2 = 1, 21
                elif new_y1 < 0:
                    new_y1, new_y2 = canvas_height - 20, canvas_height

                canvas.coords(cloud.canvas_id, new_x1, new_y1, new_x2, new_y2)

                cloud.x = new_x1
                cloud.y = new_y1

    window.after(50, move_clouds)

def monitoring():
    for i, cloud1 in enumerate(clouds):
        for j, cloud2 in enumerate(clouds):
            if i == j:
                continue
            detected = detection(cloud1, cloud2)
            if detected:
                cloud_impact(cloud1, cloud2) 
    window.after(100, monitoring)

def detection(cloud1, cloud2):
    x1, y1, _, _ = canvas.coords(cloud1.canvas_id)
    x2, y2, _, _ = canvas.coords(cloud2.canvas_id)
    center_cloud1 = (x1 + size / 2, y1 + size / 2)
    center_cloud2 = (x2 + size / 2, y2 + size / 2)
    
    dx_detec = center_cloud1[0] - center_cloud2[0]
    dy_detec = center_cloud1[1] - center_cloud2[1]
    distance = (dx_detec**2 + dy_detec**2)**0.5
    
    rel_vel_x = cloud1.dx - cloud2.dx
    rel_vel_y = cloud1.dy - cloud2.dy
    distance_change = (rel_vel_x * dx_detec + rel_vel_y * dy_detec) / distance
    
    sum_of_radii = cloud1.radius + cloud2.radius
    if distance <= sum_of_radii and distance_change < 0:
        return True
    else:
        return False

def cloud_impact(cloud1, cloud2):  
    if random.random() <= 0.75:
        clash(cloud1, cloud2)
    else:
        electronegativities_difference = abs(cloud1.electronegativities - cloud2.electronegativities)
        if electronegativities_difference < 0.4 :
            covalent_bond(cloud1, cloud2)
        if 0.4 <= electronegativities_difference <= 1.7:
            covalent_bond(cloud1, cloud2)
        else:
            clash(cloud1, cloud2)

def clash(cloud1, cloud2):
    vA_init = [cloud1.dx, cloud1.dy]
    vB_init = [cloud2.dx, cloud2.dy]

    x1_A, y1_A, _, _ = canvas.coords(cloud1.canvas_id)
    x1_B, y1_B, _, _ = canvas.coords(cloud2.canvas_id)
    xA = (x1_A + size / 2, y1_A + size / 2)
    xB = (x1_B + size / 2, y1_B + size / 2)

    mA = mB = standard_mass

    dx = xA[0] - xB[0]
    dy = xA[1] - xB[1]

    distance = math.sqrt(dx**2 + dy**2)

    nx = dx / distance
    ny = dy / distance

    dvx = vA_init[0] - vB_init[0]
    dvy = vA_init[1] - vB_init[1]

    p = 2.0 * (nx * dvx + ny * dvy) / (mA + mB)

    vA_final = [vA_init[0] - p * mB * nx, vA_init[1] - p * mB * ny]
    vB_final = [vB_init[0] + p * mA * nx, vB_init[1] + p * mA * ny]

    cloud1.dx, cloud1.dy = vA_final
    cloud2.dx, cloud2.dy = vB_final
 
    canvas.move(cloud1.canvas_id, vA_final[0], vA_final[1])
    canvas.move(cloud2.canvas_id, vB_final[0], vB_final[1])

def covalent_bond(cloud1, cloud2):
    new_group = GroupCloud ([cloud1, cloud2])
    group_clouds.append(new_group)

    surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    surface.fill((0, 0, 0))
    center_x, center_y = new_group.calculate_center_of_mass()
    for group in group_clouds:
        for cloud in group.clouds:
            cloud_position = (int(cloud.x - center_x + size), int(cloud.y - center_y + size))
            pygame.draw.circle(surface, cloud.color, cloud_position, cloud.radius)

    pygame_image_str = pygame.image.tostring(surface, 'RGB')
    pil_image = Image.frombytes('RGB', surface.get_size(), pygame_image_str)
    tkinter_image = ImageTk.PhotoImage(pil_image)

    new_group.canvas_group_id = canvas.create_image(center_x, center_y, image=tkinter_image)

    update_simulation(group_clouds, tkinter_image)

def update_simulation(group_clouds, tkinter_image):
    for group_cloud in group_clouds:
        group_cloud.update_position()
                
        if not hasattr(group_cloud, 'canvas_group_id') or group_cloud.canvas_group_id is None:
            group_cloud.canvas_group_id = canvas.create_image(group_cloud.x, group_cloud.y, image=tkinter_image)
        else:
            canvas.coords(group_cloud.canvas_group_id, group_cloud.x, group_cloud.y)

        group_cloud.tkinter_image = tkinter_image

    window.after(50, update_simulation, group_clouds, tkinter_image)

def update_canvas_ratios(event=None):
    global canvas_width_ratio, canvas_height_ratio
    canvas_width_ratio = canvas.winfo_width() / right_frame.winfo_width()
    canvas_height_ratio = canvas.winfo_height() / right_frame.winfo_height()

def close_window():
    global window_closed
    window_closed = True
    pygame.quit()
    window.destroy()

# ===================================================
# MAIN LOOP
# ===================================================

window = tk.Tk()
window.title("Incubateur")
window.geometry("800x600")
window.configure(bg="black")

sys.stdout = open('output.log', 'w')

    # ===================================================
    # MAIN LOOP/control pannel division
    # ===================================================

top_frame = tk.Frame(window, bg="gray", width=800, height=200, borderwidth=2, relief="solid", highlightbackground="white", highlightthickness=2)
top_frame.pack(side="top", fill="both", expand=True)

cloud_label = tk.Label(top_frame, bg="gray", text="Element quantity:")
cloud_label.pack(side="left", padx=10, pady=5)
cloud_quantity_entry = tk.Entry(top_frame)
cloud_quantity_entry.pack(side="left", padx=10, pady=5)
create_cloud_button = tk.Button(top_frame, text="Add element(s)", command=create_clouds)
create_cloud_button.pack(side="left", padx=10, pady=5)
window.bind("<Return>", keyboard)

freeze_button = tk.Button(top_frame, text="▶ / ||", command=freeze)
freeze_button.place(relx=1.0, rely=0.0, anchor='ne')
freeze_button.pack(side="left")

    # ===================================================
    # MAIN LOOP/cloud division
    # ===================================================

bottom_frame = tk.Frame(window,  width=800, height=400)
bottom_frame.pack(side="bottom", fill="both", expand=True)

right_frame = tk.Frame(bottom_frame, bg="black",  width=400, height=400, borderwidth=2, relief="solid", highlightbackground="white", highlightthickness=2)
right_frame.pack(side="right", fill="both", expand=True)

canvas = tk.Canvas(right_frame, bg="black", highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)

window.bind("<Configure>", update_canvas_ratios)
update_canvas_ratios()

fig, ax = plt.subplots()
ax.set_facecolor('black')
ax2 = ax.twinx()
ax2.set_ylabel('Mémoire (MB)', color='tab:red')

window.protocol("WM_DELETE_WINDOW", close_window)

sys.stdout.close()
sys.stdout = sys.__stdout__

window.mainloop()