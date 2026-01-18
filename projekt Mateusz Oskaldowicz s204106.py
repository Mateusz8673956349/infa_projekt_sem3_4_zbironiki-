import pygame
import sys

WIDTH = 1400
HEIGHT = 750

WHITE = (235, 235, 235)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)
DARK_GRAY = (120, 120, 120)
WATER = (30, 144, 255)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4-zbiorniki")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

TOP_H = 50
MID_H = 140
BOT_H = 50
W_TOP = 220
W_MID = 150
W_BOT = 40
TOTAL_H = TOP_H + MID_H + BOT_H

liquid_surface1 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
liquid_surface2 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
liquid_surface3 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
liquid_surface4 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

def tank_points(cx, top_y):
    return [
        (cx - W_TOP // 2, top_y),
        (cx + W_TOP // 2, top_y),
        (cx + W_MID // 2, top_y + TOP_H),
        (cx + W_MID // 2, top_y + TOP_H + MID_H),
        (cx + W_BOT // 2, top_y + TOTAL_H),
        (cx - W_BOT // 2, top_y + TOTAL_H),
        (cx - W_MID // 2, top_y + TOP_H + MID_H),
        (cx - W_MID // 2, top_y + TOP_H),
    ]

def prepare_liquid_surface(surface, cx, top_y):
    p1 = (cx - W_TOP // 2, top_y)
    p2 = (cx + W_TOP // 2, top_y)
    p3 = (cx + W_MID // 2, top_y + TOP_H)
    p4 = (cx - W_MID // 2, top_y + TOP_H)
    p5 = (cx + W_MID // 2, top_y + TOP_H + MID_H)
    p6 = (cx - W_MID // 2, top_y + TOP_H + MID_H)
    p7 = (cx + W_BOT // 2, top_y + TOTAL_H)
    p8 = (cx - W_BOT // 2, top_y + TOTAL_H)

    points = [p1, p2, p3, p5, p7, p8, p6, p4]
    pygame.draw.polygon(surface, (30, 144, 255, 180), points)


# pozycje zbiorników
x1, y1 = 200, 80
x2, y2 = 650, 80
x3, y3 = 1000, 80
x4, y4 = 300, 400

tank1 = tank_points(x1, y1)
tank2 = tank_points(x2, y2)
tank3 = tank_points(x3, y3)
tank4 = tank_points(x4, y4)

prepare_liquid_surface(liquid_surface1, x1, y1)
prepare_liquid_surface(liquid_surface2, x2, y2)
prepare_liquid_surface(liquid_surface3, x3, y3)
prepare_liquid_surface(liquid_surface4, x4, y4)

# poziomy
floor1_y = y1 + TOTAL_H
floor2_y = y2 + TOTAL_H
floor3_y = y3 + TOTAL_H
floor4_y = y4 + TOTAL_H
roof4_y = y4
roof2_y = y2
roof3_y = y3

v2_x = x2
v3_x = x3
mag2 = floor4_y + 50

level1 = 0   
level2 = 0
level3 = 0
level4 = 0
valve_42_open = False
valve_23_open = False   
flow_42_active = False
flow_23_active = False
fill_on = False
drain_on = False
reset_system = False
overflow_alarm = False
drain_from_3 = False
drain_from_2 = False
drain_from_4 = False
pump42_temp = 19.0
pump23_temp = 19.0
pump42_overheat = False
pump23_overheat = False

fill_speed = 0.002        
transfer_speed = 0.002  
drain_speed = 0.002
temp_rate = 1.0 / 60.0   

def draw_valve(x, y, size=20):
    bg_rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
    pygame.draw.rect(screen, GRAY, bg_rect)

    r = 6                 
    t = size - 4           

    left_triangle = [
        (x - t, y - t // 2),    
        (x - t, y + t // 2),    
        (x - r, y)              
    ]

    right_triangle = [
        (x + t, y - t // 2),    
        (x + t, y + t // 2),    
        (x + r, y)              
    ]

    pygame.draw.polygon(screen, BLACK, left_triangle, 2)
    pygame.draw.polygon(screen, BLACK, right_triangle, 2)
    pygame.draw.circle(screen, BLACK, (x, y), r, 2)



def draw_pump(x, y, w=50, h=30):

    rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
    pygame.draw.rect(screen, ORANGE, rect)

    arrow = [
        (x - 10, y - 8),
        (x - 10, y + 8),
        (x + 10, y),
    ]

    pygame.draw.polygon(screen, BLACK, arrow)
    pygame.draw.rect(screen, BLACK, rect, 2)

def draw_pipe_scada(p1, p2, active, width=14):
    pygame.draw.line(screen, BLACK, p1, p2, width)
    inner_color = WATER if active else WHITE
    pygame.draw.line(screen, inner_color, p1, p2, width - 4)

def draw_liquid(cx, top_y, level,):
    liquid_h = int(TOTAL_H * level)
    y = top_y + TOTAL_H - liquid_h

    rect = pygame.Rect(cx - W_MID // 2 + 6, y, W_MID - 12, liquid_h)
    pygame.draw.rect(screen, WATER, rect)

def draw_liquid_shaped(surface, cx, top_y, level):
    if level <= 0:
        return

    current = surface.copy()
    liquid_h = int(TOTAL_H * level)
    empty_h = TOTAL_H - liquid_h
    liquid_top_y = top_y + empty_h
    clear_rect = pygame.Rect(0, 0, WIDTH, liquid_top_y)
    current.fill((0, 0, 0, 0), clear_rect, special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(current, (0, 0))
def draw_status_panel():
    lines = [
        f"Tank 1: {int(level1 * 100)}%",
        f"Tank 2: {int(level2 * 100)}%",
        f"Tank 3: {int(level3 * 100)}%",
        f"Tank 4: {int(level4 * 100)}%",
        "",
        f"Fill:  {'ON' if fill_on else 'OFF'}",
        f"Drain: {'ON' if drain_on else 'OFF'}",
    ]
    x = 10
    y = 10
    for line in lines:
        color = BLACK
        if "ON" in line:
            color = (0, 150, 0)  
        if "OFF" in line:
            color = (180, 0, 0)

        text = font.render(line, True, color)
        screen.blit(text, (x, y))
        y += 25

def draw_valve_panel():
    lines = [
        "VALVES",
        f"V 4→2: {'OPEN' if valve_42_open else 'CLOSED'}",
        f"V 2→3: {'OPEN' if valve_23_open else 'CLOSED'}",
        "",
        "PUMPS:",
        f"P 4→2: {'FAULT' if pump42_overheat else ('ON' if valve_42_open else 'OFF')}  {int(pump42_temp)}°C",
        f"P 2→3: {'FAULT' if pump23_overheat else ('ON' if valve_23_open else 'OFF')}  {int(pump23_temp)}°C",

        "",
        "DRAIN ACTIVE:",
        f"T3: {'ON' if drain_from_3 else 'OFF'}",
        f"T2: {'ON' if drain_from_2 else 'OFF'}",
        f"T4: {'ON' if drain_from_4 else 'OFF'}",
    ]
    x = WIDTH - 180   
    y = 10
    for line in lines:
        color = BLACK

        if "OPEN" in line:
            color = (0, 150, 0) 
        if "CLOSED" in line:
            color = (180, 0, 0)
        text = font.render(line, True, color)
        screen.blit(text, (x, y))
        y += 25
def draw_reset_hint():
    text = font.render("R = RESET", True, (0, 0, 150))
    screen.blit(text, (10, HEIGHT - 30))
def draw_overflow_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((150, 0, 0)) 
    screen.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont("Arial", 60, bold=True)
    text1 = big_font.render("PRZEPEŁNIENIE ZBIORNIKÓW", True, (255, 255, 255))
    text2 = font.render("SYSTEM ZATRZYMANY", True, (255, 255, 255))
    text3 = font.render("Naciśnij R aby zresetować", True, (255, 255, 255))

    screen.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 80))
    screen.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2))
    screen.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 + 50))

while True:
    # klawisze
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                fill_on = not fill_on
            if event.key == pygame.K_DOWN:
                drain_on = not drain_on
            if event.key == pygame.K_r:
                reset_system = True
    # full check
    all_full = (
        level1 >= 0.999 and
        level2 >= 0.999 and
        level3 >= 0.999 and
        level4 >= 0.999
    )
    if reset_system:
        overflow_alarm = False

    elif all_full:
        overflow_alarm = True

    if overflow_alarm:
        fill_on = False
        drain_on = False
        valve_42_open = False
        valve_23_open = False

    if overflow_alarm:
        fill_on = False
        drain_on = False
        valve_42_open = False
        valve_23_open = False
    # reset system
    if reset_system:
        level1 = 0
        level2 = 0
        level3 = 0
        level4 = 0

        fill_on = False
        drain_on = False

        valve_42_open = False
        valve_23_open = False

        drain_from_3 = False
        drain_from_2 = False
        drain_from_4 = False

        pump42_temp = 19.0
        pump23_temp = 19.0

        reset_system = False
    # filling
    if fill_on and not overflow_alarm:
        level1 += fill_speed

    if level1 > 0.05 and level4 < 1.0:
        flow = transfer_speed * level1

        free_space = 1.0 - level4
        flow = min(flow, free_space)

        level1 -= flow
        level4 += flow

    level1 = max(0, min(1, level1))
    level2 = max(0, min(1, level2))
    level3 = max(0, min(1, level3))
    level4 = max(0, min(1, level4))
    # valve control
    if level1 >= 0.7 and level4 >= 0.99:
        valve_42_open = True
    elif level4 <= 0.3:
        valve_42_open = False

    flow_42_active = False

    if valve_42_open and not pump42_overheat and level4 > 0.05 and level2 < 1.0:
        flow_42_active = True

        flow_42 = transfer_speed * level4

        free_space_2 = 1.0 - level2
        flow_42 = min(flow_42, free_space_2)

        level4 -= flow_42
        level2 += flow_42

    if level2 >= 0.5:
        valve_23_open = True
    elif level2 <= 0.3:
        valve_23_open = False

    flow_23_active = False

    if valve_23_open and not pump23_overheat and level2 > 0.05 and level3 < 1.0:
        flow_23_active = True

        flow23 = 0.001 * level2

        free_space3 = 1.0 - level3
        flow23 = min(flow23, free_space3)

        level2 -= flow23
        level3 += flow23

    drain_from_3 = False
    drain_from_2 = False
    drain_from_4 = False
    # draining
    if drain_on and not overflow_alarm:

        if level3 > 0:
            out3 = min(drain_speed, level3)
            level3 -= out3
            drain_from_3 = True

        if level2 > 0:
            out2 = min(drain_speed, level2)
            level2 -= out2
            drain_from_2 = True

        if level3 <= 0.3 and level2 <= 0.3 and level4 > 0:
            out4 = min(drain_speed, level4)
            level4 -= out4
            drain_from_4 = True
    # pump temperature
    if valve_42_open and not pump42_overheat:
        pump42_temp += temp_rate
    else:
        pump42_temp -= temp_rate

    if pump42_temp >= 100:
        pump42_overheat = True

    if pump42_temp <= 70:
        pump42_overheat = False
        pump42_temp = max(19.0, pump42_temp)

    if valve_23_open and not pump23_overheat:
        pump23_temp += temp_rate
    else:
        pump23_temp -= temp_rate

    if pump23_temp >= 100:
        pump23_overheat = True

    if pump23_temp <= 70:
        pump23_overheat = False
    pump23_temp = max(19.0, pump23_temp)

    if level3 < 0: level3 = 0
    if level2 < 0: level2 = 0
    if level4 < 0: level4 = 0

    flow_14_active = False

    if level1 > 0.05:
        flow_14_active = True

    screen.fill(WHITE)
    draw_liquid_shaped(liquid_surface1, x1, y1, level1)
    draw_liquid_shaped(liquid_surface2, x2, y2, level2)
    draw_liquid_shaped(liquid_surface3, x3, y3, level3)
    draw_liquid_shaped(liquid_surface4, x4, y4, level4)

    pygame.draw.polygon(screen, BLACK, tank1, 3)
    pygame.draw.polygon(screen, BLACK, tank2, 3)
    pygame.draw.polygon(screen, BLACK, tank3, 3)
    pygame.draw.polygon(screen, BLACK, tank4, 3)

    draw_pipe_scada((x1, floor1_y),(x1, floor1_y+36),flow_14_active)
    draw_pipe_scada((x1-5, floor1_y+30),(x4, floor1_y+30),flow_14_active)
    draw_pipe_scada((x4-6 , floor1_y+25),(x4-6 , roof4_y),flow_14_active)

    h_low = floor4_y      
    h_high = roof2_y - 40     
    offset_x42 = x2 - 180
    draw_pipe_scada((x4 , h_low-6),(offset_x42, h_low-6), flow_42_active)
    draw_pipe_scada((offset_x42, h_low),(offset_x42, h_high), flow_42_active)
    draw_pipe_scada((offset_x42 - 5, h_high+6),(x2 + 6, h_high+6), flow_42_active)
    draw_pipe_scada((x2 , h_high+1),(x2 , roof2_y), flow_42_active)

    h_low_23 = floor2_y     
    h_high_23 = roof3_y - 40     
    offset23_x = x3 - 180

    draw_pipe_scada((x2, h_low_23-6),(offset23_x + 5, h_low_23-6), flow_23_active)
    draw_pipe_scada((offset23_x , h_low_23),(offset23_x, h_high_23), flow_23_active)
    draw_pipe_scada((offset23_x - 5, h_high_23+6),(x3+6, h_high_23+6), flow_23_active)
    draw_pipe_scada((x3, h_high_23+1),(x3, roof3_y), flow_23_active)

    draw_pipe_scada((x4-1, floor4_y), (x4-1 , mag2+7), drain_from_4)
    draw_pipe_scada((x3, floor3_y), (x3 , mag2+7), drain_from_3)
    draw_pipe_scada((x2, floor2_y), (x2 , mag2+7), drain_from_2)

    draw_pipe_scada((x4 -6, mag2),(x2-6, mag2), drain_from_4 )
    draw_pipe_scada((x3 +6, mag2),(x2 -6, mag2), drain_from_3 )

    draw_pipe_scada((v2_x, mag2),(v2_x, HEIGHT),drain_from_2 or drain_from_3 or drain_from_4 )

    draw_valve(x4, floor4_y + 20, 18)
    draw_valve(x2, floor2_y + 20, 18)
    draw_valve(x3, floor3_y + 20, 18)
    draw_valve(v2_x, mag2 + 20, 18)
    draw_valve(x4 + 60, h_low - 5, 18)
    draw_valve(x2 + 60, h_low_23 - 5, 18)

    draw_pump(offset_x42, h_low - 10, 60, 30)
    draw_pump(offset23_x, h_low_23 - 10, 60, 30)

    draw_status_panel()
    draw_valve_panel()
    draw_reset_hint()
    if overflow_alarm:
        draw_overflow_screen()

    pygame.display.flip()
    clock.tick(60)