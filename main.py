import pygame, sys
import math, random

pygame.init()
from levels import levels, build_platforms, room_vars, build_platforms_from_csv, room_vars_from_csv, get_spawn
# Screen setup
WIDTH, HEIGHT = 1300, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
bg = pygame.Surface((5000,5000))
prompt_font = pygame.font.Font("Orbitron-Regular.ttf", 18)
title_font = pygame.font.Font("Orbitron-Regular.ttf", 80)
title_timer = 0
title_alpha = 255
flash_active = False
flash_timer = 0
flash_peak = 0
flash_color = (255,255,255)
tile_size = 32
zone = None
particles = []
lasers = []
deaths = 0
TILE_PRIORITIES = {
    "cracked": 8,
    "normal": 7,
    "darkish": 7,
    "darkisher":7,
    "dark": 7,
    "darkest": 7,
    "ice": 4
}

# colours
bg_color = [30, 30, 30]
bg_imgs = {
    "loft": {"bottom": pygame.image.load("images/loft.png").convert_alpha(), "top": pygame.image.load("images/lofttop.png").convert_alpha()},
    "room": {"bottom": pygame.image.load("images/room.png").convert_alpha(), "top": pygame.image.load("images/roomtop.png").convert_alpha()},
    "factory": {"bottom": pygame.image.load("images/factory.png").convert_alpha(), "top": pygame.image.load("images/factorytop.png").convert_alpha()},
    "glacier": {"bottom": pygame.image.load("images/glacier.png").convert_alpha(), "top": pygame.image.load("images/glaciertop.png").convert_alpha()},
    "nrevac": {"bottom": pygame.image.load("images/room.png").convert_alpha(), "top": pygame.image.load("images/roomtop.png").convert_alpha()},
    "pipeworks": {"bottom": pygame.image.load("images/room.png").convert_alpha(), "top": pygame.image.load("images/roomtop.png").convert_alpha()},
    "cavern": {"bottom": pygame.image.load("images/room.png").convert_alpha(), "top": pygame.image.load("images/roomtop.png").convert_alpha()}

}


shadow_offset = 4
shadow_color = (80,80,80)

cracked_tiles = []
dead_cracked = []
current_level = "room_1"

#for double jump
w_pressed_previous_frame = False
up_pressed_previous_frame = False

pretty_zones = {
    "glacier": "The Glacier",
    "cavern":"The Caverns",
    "factory": "The Foundry",
    "pipeworks": "The Pipeworks",
    "loft": "The Loft",
    "nrevac": "NR3VAC",
}
PARTICLE_COLORS = {
    "glacier": (240,240,240),
    "factory": (233, 116, 81),
    "loft": (120, 119, 119),
}
pickup_lore = {
    "Resilience":   "The last of your ability to get back up. You entombed it in that pyramid yourself.",
    "Echo":         "A clean note. The only honest sound you ever made. Now it's just reverberation.",
    "Regret":       "Numbing, yet pointless. It wouldn't bring her back. Nothing would.",
    "Clarity":      "Cold, perfect logic. NR3VAC thought this would save you. It only showed the ashes.",
    "Hope":         "A single ember that refused to die. You hated it for surviving when everything else didn't.",
    "Voice":        "Your real voice, before the fire warped it. You'll never get it back whole.",
    "Promise":      "The vow you made. Now just twisted metal. Like everything you touched."
}
psycho_log = {
    "glacier_1": ["That wind... carries screams you left behind."],
    "glacier_101": ["Ice preserves everything. Even the promises you broke."],

    "cavern_1_4": ["These caves swallow light. Like they swallowed your hope."],
    "cavern_-1_2": ["Darkness clings. You deserve it, after what you did."],
    "cavern_101_4": ["Buried relics. Buried life. Digging won't bring her back."],
    "cavern_102_5": ["Family home. Now a ruin. You left her to die alone."],

    "factory_2": ["Heat forges nothing now. Just scars you can't escape."],
    "factory_1002": ["Assembly line of failures. You're the defective part."],
    "factory_1001": ["The playroom. Now charred, scorched. So many memories burnt to the ground."],
    "factory_10003": ["The fire you started, consuming everything.", 'It consumed you, too.'],

    "loft_2": ["Beams hold secrets. The ones you splintered."],


    "nrevac_1": ["They promised to fix you. NR3VAC. Just more wires in the wound."],
    "nrevac_2": ["An attempt to revive your life in a new place. Failed."],
    "nrevac_-3": ["Evacuate? No one came for you."],
    "nrevac_5": ["No escape. Just deeper delusion."],
    "nrevac_7": ["It was only natural for betrayers like you."],
    "nrevac_103": ["Echo. Your pleas, distorted forever."],

    "room_102": ["You build this pyramid. Brick by brick.", "A tomb for your resilience, buried alive, just like her trust."],
    "room_5": ["Stairs to nowhere. You used to dance together here."],

}

psycho_logged = set()
#game setup
game_items = {
    "Resilience": {"colour": (255, 220,0), "size": 20, "collected": False},
    "Echo": {"colour": (180,180,240), "size": 20, "collected": False},
    "Regret": {"colour": (240,240,255), "size": 16, "collected": False},
    "Clarity": {"colour": (140,140,140), "size": 10, "collected": False},
    "Hope": {"colour": (50,30,50), "size": 20,"collected": False},
    "Voice": {"colour": (180,180,240), "size": 20, "collected": False},
    "Promise": {"colour": (160,70,50), "size": 20,"collected": False}
}
item_disappear_timer = 0

room_item = None
room_item_pos = None
bounce_unlock = False
dash_unlock = False

#  tile images
tile_images = {
    "normal": pygame.image.load("images/normal.png").convert_alpha(),
    "bounce": pygame.image.load("images/bounce.png").convert_alpha(),
    "ice": pygame.image.load("images/ice.png").convert_alpha(),
    "autobounce": pygame.image.load("images/autobounce.png").convert_alpha(),
    "interact": pygame.image.load("images/interact.png").convert_alpha(),
    "dark": pygame.image.load("images/dark.png").convert_alpha(),
    "darkest": pygame.image.load("images/darkest.png").convert_alpha(),
    "darkish": pygame.image.load("images/darkish.png").convert_alpha(),
    "darkisher": pygame.image.load("images/darkisher.png").convert_alpha(),
    "left": pygame.image.load("images/left.png").convert_alpha(),
    "right": pygame.image.load("images/right.png").convert_alpha(),
    "cracked": pygame.image.load("images/cracked.png").convert_alpha(),
    "laser": pygame.image.load("images/laser.png").convert_alpha(),
    "laserleft": pygame.image.load("images/laserleft.png").convert_alpha(),
    "laserright": pygame.image.load("images/laserright.png").convert_alpha()
}


for image in tile_images:
    tile_images[image] = pygame.transform.scale(tile_images[image], (tile_size, tile_size))




# log (mostly to insult)
message_log = []

class Particle:
    def __init__(self,colour, x=None,y=None,vx=None,vy=None, life=None, life_decrement=0.1):
        self.colour = colour
        self.x =x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life= life
        self.life_decrement=life_decrement

        if self.life == None:
            self.life = random.randint(180,255)
        if self.x == None:
            self.x = random.randint(0,room_width)
        if self.y == None:
            self.y = random.randint(0, room_height//4)
        if self.vx == None:
            self.vx = random.uniform(0.3,1)
        if self.vy == None:
            self.vy = random.uniform(0.2,0.6)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.life_decrement
        if self.life <1:
            self.life = random.randint(180,255)
            self.x = random.randint(0,room_width)
            self.y = random.randint(0,room_height//4)
            self.vx = random.uniform(0.3,1)
            self.vy = random.uniform(0.2,0.6)
        if self.x > room_width:
            self.x = 0
        if self.x < 0:
            self.x = room_width
    def draw(self):
        surface = pygame.Surface((5,5), pygame.SRCALPHA)
        surface.fill((*self.colour, self.life))
        screen.blit(surface, (self.x - camera.x, self.y - camera.y))



class Player:
    def __init__(self, x, y, width, height, camera):
        self.camera = camera
        self.rect = pygame.Rect(x, y, width, height)
        self.vel_x = 0
        self.vel_y = 0
        self.base_speed = 7 #should be 7
        self.active_speed = self.base_speed
        self.jump_power = -15 #should be -15
        self.extra_jumps = 0
        self.jumps_left = self.extra_jumps
        self.bounces = 0
        self.bounceable = False
        self.bounces_left = self.bounces
        self.bounce_lock = 0
        self.gravity = 0.8
        self.grounded = False
        self.coyote_timer = 0
        self.COYOTE_TIME = 100  # ms
        self.current_tile = None
        self.last_tile = None
        self.last_bounce_side = None
        self.autobounce_multiplier = 1.2
        self.boost_recovering = False
        self.recover_timer=0
        self.dashes = 0
        self.dashes_left = self.dashes
        self.dash_speed = 25
        self.dash_timer = 0
        self.dash_length = 12
        self.dash_dir = None
        self.pr_dashes= 0 #previous dashes for reset
        self.pr_rect = self.rect.copy()
        self.grounded_tiles = []
        # Cyan flash setup
        self.color = [0, 60, 210]
        self.base_blue = 210
        self.base_green = 60
        self.base_red = 0
        self.flash_speed = 0.2
        self.flash_timer = 0



    def handle_input(self, keys, jump_triggered):
        if self.bounce_lock > 0:
            self.vel_x *= 0.95
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0
            self.boost_recovering = True
            self.recover_timer = 40
            return

        elif self.bounce_lock <= 0 and self.boost_recovering == True:
            self.vel_x *= 0.94
            self.recover_timer -= 1
            if self.recover_timer <= 0 or abs(self.vel_x) < 0.5: # <0.5 is in case of wall collision
                self.boost_recovering = False
            target_vel_x = self.vel_x
        else: target_vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_vel_x = -self.active_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_vel_x = self.active_speed


        if jump_triggered and self.extra_jumps > 0 and not self.grounded:
            if self.jumps_left > 0:
                self.vel_y = self.jump_power
                self.jumps_left -= 1
                self.color[2] = 20  # blue
                self.color[1] = 255  # green
                self.color[0] = self.base_red #i cant remmeber number
                self.flash_timer = 15



        if self.current_tile == "ice":
            acceleration = 0.12
            friction = 0.97
            self.active_speed = 11
        else:
            acceleration = 0.2
            friction = 0.85
            self.active_speed = self.base_speed

        if target_vel_x != 0:

            self.vel_x += (target_vel_x - self.vel_x) * acceleration
        else:
            self.vel_x *= friction
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0

        self.vel_x = max(-self.active_speed, min(self.active_speed, self.vel_x))

    def dash(self):
        keys=  pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction = -1
        else: direction = 0
        if keys[pygame.K_SPACE] and direction != 0:
            if self.dashes_left > 0 and self.dash_timer <= 0:
                self.dashes_left -=1
                self.dash_timer = self.dash_length
                self.dash_dir = direction
                self.bounce_lock = self.dash_length
                self.vel_x = self.dash_speed * direction
                self.vel_y = 0
                self.color = [255,50,150]
    def update_dash(self):
        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.vel_x = self.dash_speed * self.dash_dir
            self.vel_y = 0 #just to ensure gravity doesnt kick in
            self.bounce_lock = self.dash_timer
            if self.dash_timer <= 0:
                self.vel_x *= 0.6
                self.dash_dir = 0


    def move_x(self, platforms):

        self.rect.x += self.vel_x
        for tile in platforms:
            if tile.type in ["laser", "laserleft", "laserright"]: continue
            if self.rect.colliderect(tile):
                if self.vel_x > 0: # moving right
                    self.rect.right = tile.rect.left
                    if tile.type == "autobounce":
                        self.vel_x = -18
                        self.vel_y = -15
                        self.boost_recovering = True
                        self.bounce_lock = 7
                        self.color =[255,180,70]
                        self.flash_timer = 15

                elif self.vel_x < 0: #moving left
                    self.rect.left = tile.rect.right
                    if tile.type == "autobounce":
                        self.vel_x = 18
                        self.vel_y = -15
                        self.bounce_lock = 7
                        self.color =[255,180,70]
                        self.flash_timer = 15

    def apply_gravity(self, platforms):
        if self.dash_timer <= 0:
            self.vel_y += self.gravity
            self.vel_y = min(self.vel_y, 29)
            self.rect.y += self.vel_y

        self.grounded = False
        self.grounded_tiles = []
        self.bounceable = False

        # falllling
        if self.vel_y > 0:
            landing_tile = None
            highest = self.rect.bottom

            for tile in platforms:
                if (self.rect.colliderect(tile.rect) and
                    tile.rect.top < highest and
                    tile.rect.top >= self.rect.top and  # we actually crossed from above
                    (tile.type != "cracked" or tile not in dead_cracked)):
                    highest = tile.rect.top
                    landing_tile = tile

            if landing_tile:
                self.rect.bottom = landing_tile.rect.top
                self.vel_y = 0
                self.grounded = True

                # flings
                if landing_tile.type == "autobounce":
                    self.vel_y = -19
                    self.vel_x = 3 * -self.vel_x
                    self.bounce_lock = 10
                    self.color = [255,180,70]
                    self.flash_timer = 10
                elif landing_tile.type == "left":
                    self.vel_y = -12
                    self.vel_x = -20
                    self.bounce_lock = 20
                    self.color = [220,250,50]
                    self.flash_timer = 10
                elif landing_tile.type == "right":
                    self.vel_y = 12
                    self.vel_x = 20
                    self.bounce_lock = 20
                    self.color = [220,250,50]
                    self.flash_timer = 10



        #bonk
        if self.vel_y < 0:
            for tile in platforms:
                if self.rect.colliderect(tile.rect):
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 1 #useless lil bounce



        for tile in platforms:

            if (abs(self.rect.bottom - tile.rect.top) <= 2 and #little 2px grace
                self.rect.right > tile.rect.left and
                self.rect.left < tile.rect.right):
                self.grounded_tiles.append(tile)

                if tile.type == "bounce":
                    self.bounceable = True
                if tile.type == "cracked" and not tile.triggered:
                    tile.triggered = True
                    tile.flash = 15
                    self.camera.start_shake(20,9)


        #refills
        if self.grounded:
            self.jumps_left = self.extra_jumps

            if any(t.type in ["normal", "darkest", "dark", "darkish", "darkisher"] for t in self.grounded_tiles):
                self.bounces_left = self.bounces
            if any(t.type == "darkest" for t in self.grounded_tiles):
                self.dashes_left = self.dashes

            if self.grounded_tiles: #which physics used(ice or normal)
                dominant = max(self.grounded_tiles, key=lambda t: TILE_PRIORITIES.get(t.type, 0)).type
                self.current_tile = dominant
                self.last_tile = dominant
            else:
                self.current_tile = self.last_tile
        else:
            self.current_tile = self.last_tile

      #coyote time
        if self.grounded:
            self.coyote_timer = self.COYOTE_TIME
        else:
            self.coyote_timer = max(0, self.coyote_timer - dt)

    def jump(self, keys):
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]):
                    if self.bounceable:
                        if self.bounces_left > 0:
                            multiplier = 1 + 0.3 * (self.bounces - self.bounces_left + 1)
                            self.vel_y = self.jump_power * multiplier
                            self.bounces_left -= 1
                            self.color = [255,255,255]
                            self.flash_timer=10
                        else:
                            if self.bounces > 0:
                                self.vel_y = self.jump_power * (1 + 0.3 * (self.bounces))
                                self.color = [255,255,255]
                                self.flash_timer = 10

                    else: self.vel_y = self.jump_power
            else:
                self.vel_y = self.jump_power
            self.grounded = False
            self.coyote_timer = 0
            # flash cyan
            self.color[2] = 255  # blue
            self.color[1] = 255  # green
            self.flash_timer =3


    def fade_color(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1
        else:
            self.color[0] += (self.base_red - self.color[0]) * self.flash_speed
            self.color[2] += (self.base_blue - self.color[2]) * self.flash_speed
            self.color[1] += (self.base_green - self.color[1]) * self.flash_speed

    def draw(self, screen, camera_x, camera_y):
        if self.dashes_left > 0:
        # brighter with available dash - brighter/more saturated
            fill_color = [min(255, self.color[0] + 50),
                        min(255, self.color[1] + 50),
                        min(255, self.color[2] + 50)]
        else:
            #dimmer else
            fill_color = [max(0, self.color[0]),
                        max(0, self.color[1] ),
                        max(0, self.color[2])]
        pygame.draw.rect(screen, fill_color,
                        (self.rect.x - camera_x, self.rect.y - camera_y, self.rect.width, self.rect.height),
                        border_radius=3)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.smoothing = 0.09
        self.threshold = 100
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.init_shake_duration = 0

    def update(self, player_rect, room_width, room_height, WIDTH, HEIGHT):
        target_x = player_rect.centerx - WIDTH // 2
        target_x = max(0, min(target_x, room_width - WIDTH))
        target_y = player_rect.centery - HEIGHT // 2 + self.threshold
        target_y = max(0, min(target_y, room_height - HEIGHT))
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing
        if self.shake_duration > 0:
            self.shake_duration -= 1
            decay = self.shake_duration / self.init_shake_duration
            self.shake_intensity = self.shake_intensity * decay
            self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
            self.shake_intensity = 0
            self.init_shake_duration = 0



    def start_shake(self, duration, intensity):
        self.shake_duration = self.init_shake_duration = duration
        self.shake_intensity = intensity

    def get_offset(self):
        return (self.shake_offset_x,self.shake_offset_y)

def add_log(text):
    global message_log
    current_time = pygame.time.get_ticks()
    message_log.append({"text": text, "time": current_time})
    if len(message_log) > 5:
        message_log.pop(0)
def draw_log():
    now = pygame.time.get_ticks()
    log_y = HEIGHT - 40
    for message in reversed(message_log):
        elapsed = now - message["time"]

        fade_start = 10000
        fade_duration = 4000
        alpha = 255
        if elapsed > fade_start:
            alpha = max(0, 255 - int((elapsed - fade_start) / fade_duration * 255))
        if alpha <= 0:
            continue

        text_surface = prompt_font.render(message["text"], True, (255,255,255))
        text_surface.set_alpha(alpha)
        screen.blit(text_surface, (WIDTH - text_surface.get_width() - 30, log_y))

        log_y -= 25



def interact_tile(current_level, player):
    global bounce_unlock
    global dash_unlock
    if "interact_zone" in levels[current_level]:
        interact_zone = levels[current_level]["interact_zone"]
        if player.rect.colliderect(interact_zone):
            text_surface = prompt_font.render("Press E to interact", True, (255, 255, 255))
            screen.blit(text_surface,
                (interact_zone.x - camera.x, interact_zone.y - 30 - camera.y))

            if pygame.key.get_pressed()[pygame.K_e]:
                if current_level == "cavern_102_5":
                    unlocked = (game_items["Echo"]["collected"] and game_items["Resilience"]["collected"] and game_items["Regret"]["collected"])
                    if unlocked:
                        if bounce_unlock == False:
                            player.bounces += 1
                            add_log("You force Resilience, Echo and Regret together at the charred family table.")

                            camera.start_shake(100,0)
                            player.color = [255,255,255]
                            player.flash_timer = 80
                            camera.start_shake(30,5)
                            start_flash()
                            add_log("Something inside you remembers how to rise again.")
                            add_log("Press S or down to bounce higher on purple tiles.")
                            add_log("Sometimes, you must fall harder to rise higher.")
                            bounce_unlock = True
                        else:
                            pass
                    else:
                        message = "You sink to the ground, drained. You're missing Factors. Come back later."
                        if message not in message_log:
                            add_log(message)
                elif current_level == "factory_105":
                    unlocked = all(
                        item["collected"]
                        for item in (
                            game_items["Voice"],
                            game_items["Hope"],
                            game_items["Promise"]
                        )
                    )
                    if unlocked:
                        if dash_unlock == False:
                            add_log("The Factors meld together beautifully.")

                            player.dashes += 1
                            start_flash()
                            camera.start_shake(5000,50)
                            add_log("Press space while moving to dash.")
                            add_log("The darkest tiles will refill.")
                            player.color = [30,30,30]
                            player.flash_timer = 25
                            dash_unlock = True
                        else:
                            pass
                    else:
                        message = "Come back later... if you can."
                        if message not in message_log:
                            add_log(message)
def get_zone(current_level):
    return current_level.split("_")[0]


def draw_items():
    global item_disappear_timer
    global game_items

    if room_item != None and room_item_pos != None:
        float_y = 8 * math.sin(pygame.time.get_ticks() * 0.004)

        if levels[current_level]["collected"] == False:
            colour = game_items[room_item]["colour"]
            size = game_items[room_item]["size"]
            pygame.draw.rect(screen, colour,
                            (room_item_pos.x - size // 2 - camera.x,
                            room_item_pos.y - size // 2 + float_y - camera.y,
                            size, size), border_radius=3)
            colli_size = size * 5
            item_rect = pygame.Rect((room_item_pos.x - colli_size// 2,
                            room_item_pos.y - colli_size//2,
                            colli_size, colli_size))

            if player.rect.colliderect(item_rect):
                text_surface = prompt_font.render("Press E to pick up", True, (255, 255, 255))

                text_x = room_item_pos.x - camera.x - text_surface.get_width() // 2
                text_y = room_item_pos.y - camera.y - 60 + float_y  # 40 pixels above the item
                screen.blit(text_surface, (text_x, text_y))
                if pygame.key.get_pressed()[pygame.K_e]:
                    item_disappear_timer = pygame.time.get_ticks()
                    levels[current_level]["collected"] = True


                    game_items[room_item]["collected"] = True
                    add_log(f"{room_item}.")
                    add_log(pickup_lore[room_item])





def show_start_screen(camera_x, camera_y):
    # Draw start screen
    start_surface = pygame.Surface((WIDTH, HEIGHT))
    start_surface.fill((0, 0, 0))

    title_surface = title_font.render("One More Jump", True, (255, 255, 255))
    subtitle_surface = prompt_font.render("<press any key to begin>", True, (200, 200, 200))

    title_x = WIDTH // 2 - title_surface.get_width() // 2
    title_y = HEIGHT // 2 - title_surface.get_height() // 2 - 50

    subtitle_x = WIDTH // 2 - subtitle_surface.get_width() // 2
    subtitle_y = HEIGHT // 2 + 50

    start_surface.blit(title_surface, (title_x, title_y))
    start_surface.blit(subtitle_surface, (subtitle_x, subtitle_y))

    screen.blit(start_surface, (0, 0))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

    game_frame = pygame.Surface((WIDTH, HEIGHT))
    game_frame.blit(static, (-camera_x, -camera_y))

    for alpha in range(0, 255, 5):
        screen.blit(game_frame, (0, 0))

        overlay = start_surface.copy()
        overlay.set_alpha(255 - alpha)
        screen.blit(overlay, (0, 0))

        pygame.display.flip()
        pygame.time.delay(10)

def start_flash(color=(255, 255, 255)):
    global flash_active, flash_color, flash_timer
    flash_active = True
    flash_color = color
    flash_timer = 0
    camera.start_shake(60, 16)

def draw_tiles(platforms, static, room_width, room_height):


    for tile in platforms: #shadow
        if tile.type != "cracked" and tile.type not in ["laser", "laserleft", "laserright"]:
            pygame.draw.rect(static, shadow_color,
                    (tile.rect.x+ shadow_offset, tile.rect.y+ shadow_offset, tile_size, tile_size))
    for tile in platforms: #actual tile
        if tile.type != "cracked":
            image = tile_images.get(tile.type, tile_images["normal"])
            static.blit(image, (tile.rect.x, tile.rect.y))
    return static

def spawn_particles(quantity, room_width, room_height, colour):
    global particles
    particles = []
    for _ in range(quantity):
        particle = Particle(colour)
        particles.append(particle)


def load_level(current_level, tile_size, player, bg):
    global platforms, room_item, room_item_pos, room_width, room_height, cracked_tiles
    global psycho_logged, bg_imgs, particles, lasers
    particles = []
    zone = get_zone(current_level)
    if "csv" in levels[current_level]:
        platforms,room_item, room_item_pos, cracked_tiles, lasers = build_platforms_from_csv(current_level, tile_size)
        room_width, room_height = room_vars_from_csv(current_level, tile_size)
        static = pygame.Surface((room_width, room_height), pygame.SRCALPHA)
        static.fill((0,0,0,0))
        static = draw_tiles(platforms, static, room_width, room_height)
        bg = draw_bg(room_width, room_height, current_level)

        if zone in PARTICLE_COLORS:
            spawn_particles(30, room_width, room_height, PARTICLE_COLORS[zone])



    else:
        platforms, room_item, room_item_pos = build_platforms(current_level, tile_size)
        room_width, room_height = room_vars(current_level, tile_size)
        static = pygame.Surface((room_width, room_height))
        static = draw_tiles(platforms, static, room_width, room_height)
    if current_level in psycho_log and current_level not in psycho_logged:
        for log in psycho_log[current_level]:
            add_log(log)
            psycho_logged.add(current_level)
    player.pr_dashes = player.dashes_left




    return static, bg

def draw_bg(room_width, room_height, current_level):
    zone = get_zone(current_level)
    top_image = bg_imgs[zone]["top"]
    bottom_image = bg_imgs[zone]["bottom"]
    w = top_image.get_width()
    h = top_image.get_height()
    bg = pygame.Surface(((room_width+w), (room_height + h)))

    for y in range(0, room_height + h - 1, h): #top
        for x in range(0, room_width + w - 1, w):
            bg.blit(top_image, (x, y))
    num = current_level.split("_")
    num = num[1]
    if len(str(num)) < 3:
        #bottom
        w = bottom_image.get_width()
        h = bottom_image.get_height()
        for x in range(0, room_width + w - 1, w):
                bg.blit(bottom_image, (x, room_height - h))
    return bg







camera = Camera()
player = Player(8*tile_size, 51*tile_size, 30, 30,camera)
player.rect.x = 8*tile_size
player.rect.y=51*tile_size


last_level = current_level
current_level = "room_1"
room_item = None
spawn_point = "spawn_left"
static,bg = load_level(current_level, tile_size, player, bg)

static = pygame.Surface((room_width, room_height))

static,bg = load_level(current_level, tile_size, player, bg)

show_start_screen(camera.x, camera.y)

add_log("Welcome to the game!")
add_log("Use the arrow keys or [A][D] to move.")


player.vel_x, player.vel_y = 0,0
title_timer = pygame.time.get_ticks()
title_alpha = 255


###### MAIN LOOP
########################
#######################3
########################
############################################3
####################
######################3

running = True
while running:
    dt = clock.tick(60)  # frame delta




    player.pr_rect = player.rect.copy()

    camera.update(player.rect, room_width, room_height, WIDTH, HEIGHT)
    shake_x, shake_y = camera.get_offset()

    bg_x = int(-camera.x +shake_x) * 0.4

    bg_y = int(-camera.y + shake_y)

    screen.blit(bg, (bg_x, bg_y))

    if particles:
        for particle in particles:
            particle.update()
            particle.draw()



    if cracked_tiles:
        for tile in cracked_tiles[:]:
            if tile not in dead_cracked:
                shadow_x = tile.rect.x - camera.x + shake_x + shadow_offset
                shadow_y = tile.rect.y - camera.y + shake_y + shadow_offset
                tile_x = tile.rect.x - camera.x + shake_x
                tile_y = tile.rect.y - camera.y + shake_y
                pygame.draw.rect(screen, shadow_color, (shadow_x, shadow_y, tile_size, tile_size))
                image = tile_images["cracked"]
                screen.blit(image, (tile_x, tile_y))

            if tile.triggered:
                if tile.flash > 0:
                    flash_x = tile.rect.x - camera.x + shake_x
                    flash_y = tile.rect.y - camera.y + shake_y
                    intensity = tile.flash * 17  # 0-255 range roughly
                    flash_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    flash_surface.fill((255, 255, 255, intensity))

                    screen.blit(flash_surface, (flash_x, flash_y))


                tile.timer -= 1
                tile.flash -= 1   # keep decreasing even after timer hits zero so it fades nicely

                if tile.timer <= 0 and tile not in dead_cracked:
                    dead_cracked.append(tile)
                    platforms.remove(tile)
    screen.blit(static, (-camera.x + shake_x, -camera.y + shake_y))




    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if player.bounce_lock > 0: player.bounce_lock -= 1
    keys = pygame.key.get_pressed()
    w_just_pressed = keys[pygame.K_w] and not w_pressed_previous_frame
    up_just_pressed = keys[pygame.K_UP] and not up_pressed_previous_frame
    jump_triggered= w_just_pressed or up_just_pressed
    player.apply_gravity(platforms)
    player.handle_input(keys, jump_triggered)
    player.dash()
    player.update_dash()
    player.move_x(platforms)





    if player.grounded and player.coyote_timer > 0 and player.current_tile != "autobounce":
        player.jump(keys)
    w_pressed_previous_frame = keys[pygame.K_w]
    up_pressed_previous_frame = keys[pygame.K_UP]


    player.fade_color()

    if "title" in levels[current_level]:
        elapsed = pygame.time.get_ticks() - title_timer
        title_alpha = max(0, 255- elapsed/10)
        title_surface = title_font.render(levels[current_level]["title"], True, (255, 255, 255))
        title_surface.set_alpha(title_alpha)
        title_x = WIDTH // 2 - title_surface.get_width() // 2
        title_y = 200  # adjust vertical position
        screen.blit(title_surface, (title_x, title_y))

    interact_tile(current_level, player)

#room changes

    #down
    if player.rect.y > room_height:

            #down
        if "down" in levels[current_level]["exits"]:
            last_level = current_level
            current_level = levels[current_level]["exits"]["down"]
            zone = get_zone(current_level)
            if zone != get_zone(last_level) and "title" not in levels[current_level] and zone != "room":
                add_log(f"Returned to {pretty_zones.get(zone, zone)}")
            room_item = None
            spawn_point = "spawn_up"
            static,bg = load_level(current_level, tile_size, player,bg)

            player.rect.x, player.rect.y = get_spawn(current_level, spawn_point, tile_size)
            title_timer = pygame.time.get_ticks()
            title_alpha = 255

        else: #die
            player.rect.x, player.rect.y = get_spawn(current_level, spawn_point, tile_size)
            player.dashes_left = player.pr_dashes
            deaths +=1
            #cracked tiles
            dead_cracked.clear()
            if cracked_tiles:
                for tile in cracked_tiles:
                    tile.triggered = False
                    tile.timer = 10
                    if tile not in platforms:
                        platforms.append(tile)



        player.vel_y = 0
        player.vel_x = 0
    #right
    if player.rect.x > room_width and "right" in levels[current_level]["exits"]:

        last_level = current_level
        current_level = levels[current_level]["exits"]["right"]
        zone = get_zone(current_level)
        if zone != get_zone(last_level) and "title" not in levels[current_level] and zone != "room":
            add_log(f"Returned to {pretty_zones.get(zone, zone)}")
        room_item = None
        spawn_point = "spawn_left" # so player cant just fall and respawn where they want to
        static,bg = load_level(current_level, tile_size, player, bg)

        player.rect.x, player.rect.y = get_spawn(current_level, spawn_point, tile_size)
        player.vel_x, player.vel_y = 0,0
        title_timer = pygame.time.get_ticks()
        title_alpha = 255
    #left
    elif player.rect.x < -20 and "left"in levels[current_level]["exits"]:
        last_level = current_level
        current_level = levels[current_level]["exits"]["left"]
        zone = get_zone(current_level)
        if zone != get_zone(last_level) and "title" not in levels[current_level] and zone != "room":
            add_log(f"Returned to {pretty_zones.get(zone, zone)}")
        room_item = None
        spawn_point = "spawn_right"
        static, bg = load_level(current_level, tile_size, player,bg)

        player.rect.x, player.rect.y = get_spawn(current_level, spawn_point, tile_size)
        player.vel_x, player.vel_y = 0,0
        title_timer = pygame.time.get_ticks()
        title_alpha = 255
    #up
    elif player.rect.y < -50 and "up" in levels[current_level]["exits"]:
        last_level = current_level
        current_level = levels[current_level]["exits"]["up"]
        zone = get_zone(current_level)
        if zone != get_zone(last_level) and "title" not in levels[current_level] and zone != "room":
            add_log(f"Returned to {pretty_zones.get(zone, zone)}")
        room_item = None
        spawn_point = "spawn_down"
        static,bg = load_level(current_level, tile_size, player,bg)

        player.rect.x, player.rect.y = get_spawn(current_level, spawn_point, tile_size)
        player.vel_x, player.vel_y = 0,0
        title_timer = pygame.time.get_ticks()
        title_alpha = 255


    if "death_zone" in levels[current_level]:
        for zone in levels[current_level]["death_zone"]:
                if player.rect.colliderect(zone):
                    deaths +=1
                    player.rect.x, player.rect.y = get_spawn(current_level, spawn_point, tile_size)
                    player.vel_x = player.vel_y = 0
                    dead_cracked.clear()
                    if cracked_tiles:
                        for tile in cracked_tiles:
                            tile.triggered = False
                            tile.timer = 10
                            if tile not in platforms:
                                platforms.append(tile)


    if lasers:
        for laser in lasers:
            if (abs(player.rect.bottom - laser.rect.top) <= 2 and #little 2px grace
                player.rect.right > laser.rect.left and
                player.rect.left < laser.rect.right) or (abs(player.rect.top - laser.rect.bottom) <= 2 and
                player.rect.right > laser.rect.left and
                player.rect.left < laser.rect.right):

                    player.rect.x, player.rect.y = get_spawn(current_level, spawn_point, tile_size)
                    player.vel_x = player.vel_y = 0
                    dead_cracked.clear()
                    if cracked_tiles:
                        for tile in cracked_tiles:
                            tile.triggered = False
                            tile.timer = 10
                            if tile not in platforms:
                                platforms.append(tile)
                    deaths += 1



    draw_items()
    draw_log()

    player.draw(screen, camera.x + shake_x, camera.y + shake_y)

    if flash_active:
        flash_timer += 1

        if flash_timer <= 8:  #instant white blast
            alpha = 255
        elif flash_timer <= 28: #hold
            alpha = 255
        elif flash_timer <= 80:  #fade
            alpha = int(255 * (1 - (flash_timer - 28) / 52))
        else:
            flash_active = False  # done

        flash_surf = pygame.Surface((WIDTH, HEIGHT))
        flash_surf.fill(flash_color if flash_timer > 8 else (255,255,255))
        flash_surf.set_alpha(alpha)
        screen.blit(flash_surf, (0, 0))




    fps = int(clock.get_fps())
    fps_count = prompt_font.render(f"FPS: {fps}", True, (255,255,255))
    death_count = prompt_font.render(f"Deaths: {deaths}", True, (255,255,255))

    screen.blit(fps_count, (30,30))
    screen.blit(death_count, (WIDTH-150,30))


    pygame.display.flip()
