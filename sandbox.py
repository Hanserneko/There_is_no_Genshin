import pygame as pg
import time
import random as rd
import math
import os

pg.init()

debug = 0
'''重构时注意release版本的路径索引器，release版需要删掉quit()函数'''
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
size = (WINDOW_WIDTH, WINDOW_HEIGHT)

FPS = 60

screen = pg.display.set_mode(size)
pg.display.set_caption('Demo')

bg_image = pg.image.load(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 r'img\background.png')).convert()
# bg_image = pg.image.load('img\\background.png').convert()

clock = pg.time.Clock()

g_rider = pg.sprite.Group()
g_archar = pg.sprite.Group()
g_bullet = pg.sprite.Group()

# jetbrainsmono
# consolas
font = pg.font.SysFont('jetbrainsmono', 10)


class animation:

    def __init__(self, img_name, img_dir, len_frame, interval: int):
        self.FRAME: list[pg.surface.Surface] = []

        for i in range(len_frame):
            img = 'img\\' + img_name + '_' + img_dir + '_' + f'{i}' + '.png'
            self.FRAME.append(
                pg.image.load(
                    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 img)).convert_alpha())
            # self.FRAME.append(pg.image.load(img))

        self.__interval_ms = interval
        self.__timer = 0
        self.__idx_frame = 0
        self.__len_frame = len_frame

    def play(self, pos_x, pos_y, delta):
        self.__timer += delta
        if self.__timer >= self.__interval_ms:
            self.__idx_frame = (self.__idx_frame + 1) % self.__len_frame
            self.__timer = 0

        screen.blit(self.FRAME[self.__idx_frame], (pos_x, pos_y))


class player(pg.sprite.Sprite):
    __normalized_x = 1
    __normalized_y = 0

    __interval = 200
    __timer = 0
    __txt_timer = font.render(f'{__timer}', True, (255, 255, 255))

    aim_point_color = (0, 191, 255)
    aim_point_radius = 3

    hurt_timer = 0
    hurt_interval = 60
    health = 3
    txt_health = font.render(f'{health}', True, (255, 255, 255))
    txt_hurt_timer = font.render(f'{hurt_timer}', True, (255, 255, 255))

    def __init__(self):
        super(player, self).__init__()

        self.FRAME_WIDTH = 52
        self.FRAME_HEIGHT = 74
        self.__SHADOW_WIDTH = 32

        self.pos_x = 640
        self.pos_y = 360
        self.pos_point_x = self.FRAME_WIDTH / 2 + self.pos_x
        self.pos_point_y = self.FRAME_HEIGHT / 2 + self.pos_y + 15

        self.__up = False
        self.__down = False
        self.__left = False
        self.__right = False
        self._speed = 4

        self.anim_L = animation('paimon', 'left', 6, 6)
        self.anim_R = animation('paimon', 'right', 6, 6)
        self.anim_SHADOW = pg.image.load(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'img/shadow_player.png')).convert_alpha()
        # self.anim_SHADOW = pg.image.load(
        #     'img\\shadow_player.png').convert_alpha()

        self.__facing_left = False

        self.rect = pg.Rect(self.pos_point_x - 4, self.pos_point_y - 4, 8, 8)
        self.outter_rect = pg.Rect(self.pos_x, self.pos_y, self.FRAME_WIDTH,
                                   self.FRAME_HEIGHT)
        self.__alive = True

        self.__txt_speed = font.render(f'{self._speed:.2f}', True,
                                       (255, 255, 255))

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w or event.key == pg.K_UP:
                self.__up = True
            if event.key == pg.K_s or event.key == pg.K_DOWN:
                self.__down = True
            if event.key == pg.K_a or event.key == pg.K_LEFT:
                self.__left = True
            if event.key == pg.K_d or event.key == pg.K_RIGHT:
                self.__right = True
            if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
                self._speed = 2
            if event.key == pg.K_SPACE:
                self.try_generate_bullet()

        if event.type == pg.KEYUP:
            if event.key == pg.K_w or event.key == pg.K_UP:
                p.__up = False
            if event.key == pg.K_s or event.key == pg.K_DOWN:
                p.__down = False
            if event.key == pg.K_a or event.key == pg.K_LEFT:
                p.__left = False
            if event.key == pg.K_d or event.key == pg.K_RIGHT:
                p.__right = False
            if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
                self._speed = 4

    def move(self):
        self.__dir_x = self.__right - self.__left
        self.__dir_y = self.__down - self.__up
        self.__len_dir = math.sqrt(self.__dir_x * self.__dir_x +
                                   self.__dir_y * self.__dir_y)

        if self.__len_dir != 0:
            self.__normalized_x = self.__dir_x / self.__len_dir
            self.__normalized_y = self.__dir_y / self.__len_dir
            self.pos_x += (self._speed * self.__normalized_x)
            self.pos_y += (self._speed * self.__normalized_y)

            if self.pos_x < 0:
                self.pos_x = 0
            if self.pos_x + self.FRAME_WIDTH > WINDOW_WIDTH:
                self.pos_x = WINDOW_WIDTH - self.FRAME_WIDTH
            if self.pos_y < 0:
                self.pos_y = 0
            if self.pos_y + self.FRAME_HEIGHT > WINDOW_HEIGHT:
                self.pos_y = WINDOW_HEIGHT - self.FRAME_HEIGHT

            self.pos_point_x = self.FRAME_WIDTH / 2 + self.pos_x
            self.pos_point_y = self.FRAME_HEIGHT / 2 + self.pos_y + 15

            self.outter_rect = pg.Rect(self.pos_x, self.pos_y,
                                       self.FRAME_WIDTH, self.FRAME_HEIGHT)
            self.rect = pg.Rect(self.pos_point_x - 4, self.pos_point_y - 4, 8,
                                8)

            self.__txt_speed = font.render(f'{self._speed:.2f}', True,
                                           (255, 255, 255))

    def draw(self, delta: int = 1):
        self.pos_shadow_x = self.pos_x + (self.FRAME_WIDTH / 2 -
                                          self.__SHADOW_WIDTH / 2)
        self.pos_shadow_y = self.pos_y + self.FRAME_HEIGHT - 8
        screen.blit(self.anim_SHADOW, (self.pos_shadow_x, self.pos_shadow_y))

        self.__facing_dir = self.__right - self.__left
        if self.__facing_dir < 0:
            self.__facing_left = True
        elif self.__facing_dir > 0:
            self.__facing_left = False

        if self.__facing_left:
            self.anim_L.play(self.pos_x, self.pos_y, delta)
        else:
            self.anim_R.play(self.pos_x, self.pos_y, delta)
        # (255, 215, 0)
        pg.draw.circle(screen, (255, 215, 0),
                       (self.pos_point_x, self.pos_point_y), 4, 4)
        if self.hurt_timer == 0:
            pg.draw.circle(screen, (255, 0, 0),
                           (self.pos_point_x, self.pos_point_y), 4, 2)
        else:
            pg.draw.circle(screen, (0, 0, 139),
                           (self.pos_point_x, self.pos_point_y), 4, 2)
        if not self.__timer == 0:
            self.draw_timer()
        pg.draw.circle(screen, self.aim_point_color, (
            self.pos_point_x + self.__normalized_x * 60,
            self.pos_point_y + self.__normalized_y * 60,
        ), self.aim_point_radius, 4)

        if debug:
            pg.draw.rect(screen, (0, 0, 0), self.outter_rect, 1)
            pg.draw.rect(screen, (0, 255, 0), self.rect, 1)
            screen.blit(self.__txt_speed, (self.pos_x, self.pos_y - 10))
            screen.blit(self.__txt_timer, (self.pos_x + 40, self.pos_y - 10))
            pg.draw.line(screen, (0, 255, 255),
                         (self.pos_point_x, self.pos_point_y),
                         (self.pos_point_x + self.__normalized_x * 50,
                          self.pos_point_y + self.__normalized_y * 50))
            screen.blit(self.txt_health, (self.pos_x - 8, self.pos_y + 5))
            screen.blit(self.txt_hurt_timer, (self.pos_x - 8, self.pos_y + 15))

    def generate_bullet(self):
        return Bullet(self.pos_point_x, self.pos_point_y, self.__normalized_x,
                      self.__normalized_y, 5, 1)

    def draw_timer(self):
        self.interval_rect = pg.Rect(self.pos_x, self.pos_y - 10,
                                     self.FRAME_WIDTH, 8)
        self.timer_rect = pg.Rect(
            self.pos_x, self.pos_y - 10,
            self.FRAME_WIDTH *
            ((self.__interval - self.__timer) / self.__interval), 8)
        pg.draw.rect(screen, (100, 149, 237), self.interval_rect, 1)
        pg.draw.rect(screen, (100, 149, 237), self.timer_rect, 100)

    def try_generate_bullet(self):
        if self.__timer == 0:
            g_bullet.add(self.generate_bullet())
            self.__timer = self.__interval

    def update_timer(self):
        if self.__timer > 0:
            self.aim_point_color = (255, 255, 255)
            self.aim_point_radius = 2
            self.__timer -= 1
        if self.__timer == 0:
            self.aim_point_color = (0, 191, 255)
            self.aim_point_radius = 3
        self.__txt_timer = font.render(f'{self.__timer}', True,
                                       (255, 255, 255))

        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            self.txt_hurt_timer = font.render(f'{self.hurt_timer}', True,
                                              (255, 255, 255))

    def update(self):
        self.update_timer()
        self.move()
        self.draw()

    def CheckAlive(self):
        if not debug:
            return not self.__alive

    def hurt(self):
        if self.health > 0 and self.hurt_timer == 0:
            if debug:
                print('hurt')
            self.health -= 1
            self.hurt_timer = self.hurt_interval

        self.txt_health = font.render(f'{self.health}', True, (255, 255, 255))
        if self.health == 0:
            if debug:
                print('dead')
            self.__alive = False


class Servant(pg.sprite.Sprite):

    __facing_left = False
    __alive = True
    speed_x = 0
    speed_y = 0

    def __init__(self, randint: int, speed: float, FRA_W: int, FRA_H: int,
                 SHA_W: int, delta_point_y: int, delta_rect: int,
                 delta_sha: int, anim_L: animation, anim_R: animation,
                 health: int):
        super(Servant, self).__init__()

        self.FRAME_WIDTH = FRA_W
        self.FRAME_HEIGHT = FRA_H
        self.__SHADOW_WIDTH = SHA_W
        self.__enum_l = [[randint % WINDOW_WIDTH, -FRA_H],
                         [randint % WINDOW_WIDTH, WINDOW_HEIGHT],
                         [-FRA_W, randint % WINDOW_HEIGHT],
                         [WINDOW_WIDTH, randint % WINDOW_HEIGHT]]
        self.__rand_l = self.__enum_l[randint % 4]
        self.pos_x = self.__rand_l[0]
        self.pos_y = self.__rand_l[1]
        self.pos_point_x = self.FRAME_WIDTH / 2 + self.pos_x
        self.pos_point_y = self.FRAME_HEIGHT / 2 + self.pos_y + delta_point_y
        self.__delta_point_y = delta_point_y
        self.__delta_rect = delta_rect
        self.__delta_sha = delta_sha

        self.__temp_speed = speed
        self._speed = speed

        # self.anim_L = animation(name, 'left', len_frame, interval)
        # self.anim_R = animation(name, 'right', len_frame, interval)
        self.anim_L = anim_L
        self.anim_R = anim_R
        self.anim_SHADOW = pg.image.load(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'img/shadow_enemy.png')).convert_alpha()
        # self.anim_SHADOW = pg.image.load(
        #     'img\\shadow_enemy.png').convert_alpha()

        self.rect = pg.Rect(self.pos_x + self.__delta_rect, self.pos_y,
                            self.FRAME_WIDTH - self.__delta_rect * 2,
                            self.FRAME_HEIGHT)

        self.__txt_speed = font.render(f'{self._speed:.2f}', True,
                                       (255, 255, 255))

        self.health = health

    def move(self, player: player):

        self.p_pos_x = player.pos_point_x
        self.p_pos_y = player.pos_point_y

        self.__dir_x = self.p_pos_x - self.pos_point_x
        self.__dir_y = self.p_pos_y - self.pos_point_y
        self.__len_dir = math.sqrt(self.__dir_x * self.__dir_x +
                                   self.__dir_y * self.__dir_y)

        if self.__len_dir != 0:
            self.__normalized_x = self.__dir_x / self.__len_dir
            self.__normalized_y = self.__dir_y / self.__len_dir

            self.speed_x = (self._speed * self.__normalized_x)
            self.speed_y = (self._speed * self.__normalized_y)

            self.pos_x += self.speed_x
            self.pos_y += self.speed_y

            self.pos_point_x = self.FRAME_WIDTH / 2 + self.pos_x
            self.pos_point_y = self.FRAME_HEIGHT / 2 + self.pos_y + self.__delta_point_y

            self.rect = pg.Rect(self.pos_x + self.__delta_rect, self.pos_y,
                                self.FRAME_WIDTH - self.__delta_rect * 2,
                                self.FRAME_HEIGHT)

    def draw(self, delta: int = 1):
        self.pos_shadow_x = self.pos_x + (self.FRAME_WIDTH / 2 -
                                          self.__SHADOW_WIDTH / 2)
        self.pos_shadow_y = self.pos_y + self.FRAME_HEIGHT - self.__delta_sha
        screen.blit(self.anim_SHADOW, (self.pos_shadow_x, self.pos_shadow_y))

        if self.__dir_x < 0:
            self.__facing_left = True
        elif self.__dir_x > 0:
            self.__facing_left = False

        if self.__facing_left:
            self.anim_L.play(self.pos_x, self.pos_y, delta)
        else:
            self.anim_R.play(self.pos_x, self.pos_y, delta)

        if debug:
            pg.draw.circle(screen, (255, 0, 0),
                           (self.pos_point_x, self.pos_point_y), 4, 2)
            pg.draw.circle(screen, (255, 215, 0),
                           (self.pos_point_x, self.pos_point_y), 2, 2)
            pg.draw.rect(screen, (0, 0, 0), self.rect, 1)
            screen.blit(self.__txt_speed, (self.pos_x + 10, self.pos_y - 10))

    def CheckPlayerCollision(self, player: player):
        return self.rect.collidepoint(player.pos_point_x, player.pos_point_y)

    def hurt(self):
        self.health -= 1
        if self.health == 0:
            self.__alive = False

    def CheckAlive(self):
        return self.__alive

    def update(self, player: player):

        self.move(player)
        self.draw()
        if self.CheckPlayerCollision(player):
            player.hurt()
            self.kill()
        if not self.CheckAlive():
            self.kill()


class Rider(Servant):

    __name = 'enemy'
    __FRAME_WIDTH = 74
    __FRAME_HEIGHT = 54
    __SHADOW_WIDTH = 48
    __delta_point_y = 5
    __delta_rect = 10
    __delta_sha = 14

    def __init__(self, randint: int, speed: float, health: int):
        super().__init__(randint, speed, self.__FRAME_WIDTH,
                         self.__FRAME_HEIGHT, self.__SHADOW_WIDTH,
                         self.__delta_point_y, self.__delta_rect,
                         self.__delta_sha, animation('enemy', 'left', 6, 6),
                         animation('enemy', 'right', 6, 6), health)


class Archar(Servant):

    __name = 'bee'
    __FRAME_WIDTH = 72
    __FRAME_HEIGHT = 80
    __SHADOW_WIDTH = 48
    __delta_point_y = 10
    __delta_rect = 6
    __delta_sha = 14

    __timer = 0
    __interval = 300

    def __init__(self, randint: int, speed: float, health: int):

        super(Archar, self).__init__(randint, speed, self.__FRAME_WIDTH,
                                     self.__FRAME_HEIGHT, self.__SHADOW_WIDTH,
                                     self.__delta_point_y, self.__delta_rect,
                                     self.__delta_sha,
                                     animation('bee', 'left', 4, 4),
                                     animation('bee', 'right', 4, 4), health)

        self.rect = pg.Rect(self.pos_x + self.__delta_rect, self.pos_y,
                            self.FRAME_WIDTH - self.__delta_rect * 2,
                            self.FRAME_HEIGHT - 10)

        self.__txt_speed = font.render(f'{self._speed:.2f}', True,
                                       (255, 255, 255))
        self.__txt_timer = font.render(f'{self.__timer}', True,
                                       (255, 255, 255))

        self.__temp_speed = speed
        pass

    def move(self, player: player):

        if self.pos_x < 0 or self.pos_x > WINDOW_WIDTH - self.FRAME_WIDTH:
            self._speed = 2
        elif self.pos_y < 0 or self.pos_y > WINDOW_HEIGHT - self.FRAME_HEIGHT:
            self._speed = 2
        else:
            self._speed = self.__temp_speed

        self.__txt_speed = font.render(f'{self._speed:.2f}', True,
                                       (255, 255, 255))

        self.p_pos_x = player.pos_point_x
        self.p_pos_y = player.pos_point_y

        self.__dir_x = self.p_pos_x - self.pos_point_x
        self.__dir_y = self.p_pos_y - self.pos_point_y
        self.__len_dir = math.sqrt(self.__dir_x * self.__dir_x +
                                   self.__dir_y * self.__dir_y)

        if self.__len_dir != 0:
            self.__normalized_x = self.__dir_x / self.__len_dir
            self.__normalized_y = self.__dir_y / self.__len_dir

            self.speed_x = (self._speed * self.__normalized_x)
            self.speed_y = (self._speed * self.__normalized_y)

            self.pos_x += self.speed_x
            self.pos_y += self.speed_y

            self.pos_point_x = self.FRAME_WIDTH / 2 + self.pos_x
            self.pos_point_y = self.FRAME_HEIGHT / 2 + self.pos_y + self.__delta_point_y

            self.rect = pg.Rect(self.pos_x + self.__delta_rect,
                                self.pos_y + 30,
                                self.FRAME_WIDTH - self.__delta_rect * 2,
                                self.FRAME_HEIGHT - 30)

    def draw(self, delta: int = 1):
        self.pos_shadow_x = self.pos_x + (self.FRAME_WIDTH / 2 -
                                          self.__SHADOW_WIDTH / 2)
        self.pos_shadow_y = self.pos_y + self.FRAME_HEIGHT - self.__delta_sha
        screen.blit(self.anim_SHADOW, (self.pos_shadow_x, self.pos_shadow_y))

        if self.__dir_x < 0:
            self.__facing_left = True
        elif self.__dir_x > 0:
            self.__facing_left = False

        if self.__facing_left:
            self.anim_L.play(self.pos_x, self.pos_y, delta)
        else:
            self.anim_R.play(self.pos_x, self.pos_y, delta)

        if debug:
            pg.draw.circle(screen, (255, 0, 0),
                           (self.pos_point_x, self.pos_point_y), 4, 2)
            pg.draw.circle(screen, (255, 215, 0),
                           (self.pos_point_x, self.pos_point_y), 2, 2)
            pg.draw.rect(screen, (0, 0, 0), self.rect, 1)
            screen.blit(self.__txt_speed, (self.pos_x + 8, self.pos_y + 15))
            screen.blit(self.__txt_timer, (self.pos_x + 40, self.pos_y + 15))

    def generate_bullet(self, player: player):

        if self.__facing_left:
            self.__delta_x = 23
        else:
            self.__delta_x = 49
        self.__dir_pos_x = player.pos_point_x - (self.pos_x + self.__delta_x)
        self.__dir_pos_y = player.pos_point_y - (self.pos_y +
                                                 self.FRAME_HEIGHT)
        self.__len_dir = math.sqrt(self.__dir_pos_x * self.__dir_pos_x +
                                   self.__dir_pos_y * self.__dir_pos_y)

        if self.__len_dir != 0:
            self.__b_dir_x = self.__dir_pos_x / self.__len_dir
            self.__b_dir_y = self.__dir_pos_y / self.__len_dir

        return Bullet(self.pos_x + self.__delta_x,
                      self.pos_y + self.FRAME_HEIGHT, self.__b_dir_x,
                      self.__b_dir_y, 1, 0)

    def try_genetare_bullet(self, player: player):
        self.__timer = (self.__timer + 1) % self.__interval
        self.__txt_timer = font.render(f'{self.__timer}', True,
                                       (255, 255, 255))
        if self.__timer == 0:
            g_bullet.add(self.generate_bullet(player))

    def update(self, player: player):

        self.move(player)
        self.draw()
        self.try_genetare_bullet(player)
        if self.CheckPlayerCollision(player):
            player.hurt()
            self.kill()
        if not self.CheckAlive():
            self.kill()


class Bullet(pg.sprite.Sprite):

    __RADIUS = 6
    __owner_list = ['Archar', 'Player']

    def __init__(self, x: int, y: int, dir_x: float, dir_y: float,
                 speed: float, owner: int):
        super(Bullet, self).__init__()
        self.pos_x = x
        self.pos_y = y
        self.dir_x = dir_x
        self.dir_y = dir_y

        self.__speed = speed

        self.rect = pg.Rect(self.pos_x - self.__RADIUS,
                            self.pos_y - self.__RADIUS, self.__RADIUS * 2,
                            self.__RADIUS * 2)

        self.__owner = self.__owner_list[owner]

    def draw(self):
        if self.__owner == 'Archar':
            pg.draw.circle(screen, (0, 0, 0), (self.pos_x, self.pos_y),
                           self.__RADIUS, 10)
            pg.draw.circle(screen, (255, 0, 0), (self.pos_x, self.pos_y),
                           self.__RADIUS, 3)
        elif self.__owner == 'Player':
            pg.draw.circle(screen, (25, 25, 112), (self.pos_x, self.pos_y),
                           self.__RADIUS, 10)
            pg.draw.circle(screen, (211, 211, 211), (self.pos_x, self.pos_y),
                           self.__RADIUS, 3)

        if debug:
            pg.draw.rect(screen, (255, 255, 255), self.rect, 1)
            pg.draw.line(
                screen, (0, 255, 255), (self.pos_x, self.pos_y),
                (self.pos_x + self.dir_x * 20, self.pos_y + self.dir_y * 20))

    def move(self):

        self.pos_x += self.dir_x * self.__speed
        self.pos_y += self.dir_y * self.__speed

        self.rect = pg.Rect(self.pos_x - self.__RADIUS,
                            self.pos_y - self.__RADIUS, self.__RADIUS * 2,
                            self.__RADIUS * 2)

        if self.pos_x > WINDOW_WIDTH + self.__RADIUS or self.pos_x < 0 - self.__RADIUS:
            self.kill()
        if self.pos_y > WINDOW_HEIGHT + self.__RADIUS or self.pos_y < 0 - self.__RADIUS:
            self.kill()

    def self_destroy(self):
        self.kill()

    def CheckPlayerCollision(self, player: player):
        if pg.sprite.collide_circle_ratio(0.70)(self, player):
            player.hurt()
            if debug:
                print('hit')
            self.kill()

    def check_enemy_collision(self):
        self.collision_list = pg.sprite.spritecollide(
            self, g_archar, 0) + pg.sprite.spritecollide(self, g_rider, 0)
        for enemy in self.collision_list:
            enemy.hurt()
        if len(self.collision_list) > 0:
            self.self_destroy()

    def update(self, player: player):
        self.move()
        if self.__owner == 'Archar':
            self.CheckPlayerCollision(player)
        elif self.__owner == 'Player':
            self.check_enemy_collision()

        self.draw()


enemy_generate_timer = 0
enemy_generete_interval = 300


def TryGenerateEnemy():

    global enemy_generate_timer, enemy_generete_interval
    enemy_generate_timer = (enemy_generate_timer + 1) % enemy_generete_interval
    if enemy_generate_timer == 0:
        rand = rd.randint(0, 1)
        if rand:
            g_archar.add(Archar(rd.randint(0, 2000), 0.1, 1))
        else:
            g_rider.add(Rider(rd.randint(0, 2000), rd.uniform(1, 2), 2))
        enemy_generete_interval = rd.randint(200, 500)


''''''

g_archar.add(Archar(rd.randint(0, 2000), 0.05, 2))
p = player()
''''''
done = False

while not done:

    done = p.CheckAlive()

    screen.blit(bg_image, (0, 0))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        p.get_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                done = True
            if event.key == pg.K_e and debug:
                enemy_generate_timer = enemy_generete_interval - 1
                pass

    TryGenerateEnemy()
    g_rider.update(p)
    g_archar.update(p)

    p.update()

    g_bullet.update(p)
    if debug:
        l_rider = g_rider.sprites()
        l_archar = g_archar.sprites()
        l_bullet = g_bullet.sprites()
        txt_rider = font.render(f'rider:{len(l_rider)}', True, (255, 255, 255))
        txt_archar = font.render(f'archar:{len(l_archar)}', True,
                                 (255, 255, 255))
        txt_bullet = font.render(f'bullet:{len(l_bullet)}', True,
                                 (255, 255, 255))
        txt_timer = font.render(f'timer:{enemy_generate_timer}', True,
                                (255, 255, 255))
        txt_interval = font.render(f'interval:{enemy_generete_interval}', True,
                                   (255, 255, 255))
        screen.blit(txt_rider, (0, 700))
        screen.blit(txt_archar, (60, 700))
        screen.blit(txt_bullet, (120, 700))
        screen.blit(txt_interval, (0, 0))
        screen.blit(txt_timer, (100, 0))
    pg.display.update()
    clock.tick(FPS)

pg.quit()
quit()
