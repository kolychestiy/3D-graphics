# Генерация точек случайно
from random import randint

points = []
for _ in range(20):
    points.append([randint(-10, 10) for i in range(3)])
# Или ввести координаты в ручном режиме
# points = [
#     [5, 5, 5],
#     [5, 5, -5],
#     [5, -5, 5],
#     [5, -5, -5],
#     [-5, 5, 5],
#     [-5, 5, -5],
#     [-5, -5, 5],
#     [-5, -5, -5],
#     [7, 0, 0],
#     [-2, 8, 9],
# ]

# настройки ширины и высоты окна
width, height = 1090, 700

# Для управления использовать клавиши:    if key[pygame.K_r]:
# x, y, z - вращение точек в плоскости паралельной выбранной.
# стрелка вверх / вниз - приближение или отдаление объекта
# w, a, s, d - вверх, вниз, влево, вправо (переместить)
# r - инвертированный режим для вращения (x, y, z)

# SZ - начальное приближение объекта (чем больше тем он крупнее)
SZ = 20
sz = SZ
# sd - отвечает за скорость перемещения по wasd
sd = 5 / sz

import pygame
from math import *
from functools import cmp_to_key
from numpy import unique
from copy import deepcopy

INF = 10000000


pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Выпуклые многогранники")

black = (0, 0, 0)
white = (255, 255, 255)
green = (100, 100, 100)


def vect(p, q):
    return [
        p[1] * q[2] - p[2] * q[1],
        p[2] * q[0] - p[0] * q[2],
        p[0] * q[1] - p[1] * q[0],
    ]


def scal(p, q):
    return sum([p[i] * q[i] for i in range(len(p))])


def neg(p, q):
    return [p[i] - q[i] for i in range(len(p))]


def mulsc(sc, p):
    return [sc * e for e in p]


def len2(p):
    return sum([e * e for e in p])


def find_ch(a, torc):
    a.sort()
    up = []
    dw = []
    for p in a:
        while len(up) > 1 and scal(vect(neg(p, up[-1]), neg(up[-1], up[-2])), torc) < 0:
            up.pop()
        up.append(p)
        while len(dw) > 1 and scal(vect(neg(p, dw[-1]), neg(dw[-1], dw[-2])), torc) > 0:
            dw.pop()
        dw.append(p)
    return up[1:] + dw[::-1][1:]


class Side:
    def __init__(self, side):
        side = [points[i] for i in side]
        self.side = side
        self.recalc()
        self.color = [randint(0, 255) for i in range(3)]
        last = self.side[-1]
        for cur in self.side:
            edges.append(sorted([cur, last]))
            last = cur

    def get_z(self, x, y):
        return -(x * self.a + y * self.b + self.d) / self.c

    def recalc(self):
        self.torc = vect(
            neg(self.side[2], self.side[0]), neg(self.side[1], self.side[0])
        )
        self.side = find_ch(self.side, self.torc)
        v = vect(neg(self.side[1], self.side[0]), neg(self.side[2], self.side[0]))
        base = self.side[0]
        self.a = v[0]
        self.b = v[1]
        self.c = v[2]
        self.d = -sum([base[i] * v[i] for i in range(3)])

    def is_in(self, x, y):
        p = [x, y, self.get_z(x, y)]
        last = self.side[-1]
        for cur in self.side:
            if scal(vect(neg(cur, p), neg(p, last)), self.torc) > 1e-6:
                return False
            last = cur
        return True


edges = []
sides = []
for i in range(len(points)):
    for j in range(i + 1, len(points)):
        for k in range(j + 1, len(points)):
            v1 = vect(neg(points[j], points[i]), neg(points[k], points[i]))
            side = []
            for l in range(len(points)):
                v2 = vect(neg(points[l], points[i]), neg(points[k], points[i]))
                v = vect(v1, v2)
                if len2(v) != 0:
                    continue
                side.append(l)
            if side[:3] != [i, j, k]:
                continue
            mn = INF
            mx = -INF
            for l in range(len(points)):
                sc = scal(v1, neg(points[l], points[i]))
                mn = min(mn, sc)
                mx = max(mx, sc)
            if mn < 0 and mx > 0:
                continue
            sides.append(Side(side))

edges.sort()
i = 1
j = 0
while i < len(edges):
    if edges[i] == edges[j]:
        i += 1
        continue
    edges[j + 1] = edges[i]
    i += 1
    j += 1
edges = edges[: j + 1]

points = []
for edge in edges:
    points.append(edge[0])
    points.append(edge[1])
points.sort()
i = 1
j = 0
while i < len(points):
    if points[i] == points[j]:
        i += 1
        continue
    points[j + 1] = points[i]
    i += 1
    j += 1
points = points[: j + 1]


class Line:
    def __init__(self, p, q):
        self.a = q[1] - p[1]
        self.b = p[0] - q[0]
        self.c = -(self.a * p[0] + self.b * p[1])


def intersect(p, q, P, Q):
    l = Line(p, q)
    m = Line(P, Q)
    zn = l.b * m.a - l.a * m.b
    if abs(zn) < 1e-6:
        if (
            abs(l.a * m.b - l.b * m.a) > 1e-6
            or abs(l.a * m.c - l.c * m.a) > 1e-6
            or abs(l.b * m.c - l.c * m.b) > 1e-6
        ):
            return -1
        if max(p, q) < min(P, Q) or max(P, Q) < min(p, q):
            return -1
        fi = max(min(p, q), min(P, Q))
        se = min(max(p, q), max(P, Q))
        return mulsc(0.5, neg(fi, mulsc(-1, se)))
    x = (m.c * l.b - m.b * l.c) / -zn
    y = (m.c * l.a - m.a * l.c) / zn
    z = [x, y]
    if scal(neg(p, q), neg(z, q)) < 0 or scal(neg(q, p), neg(z, p)) < 0:
        return -1
    if scal(neg(P, Q), neg(z, Q)) < 0 or scal(neg(Q, P), neg(z, P)) < 0:
        return -1
    return z


def rotate(fix, da):
    for e in points:
        p = []
        for j in range(3):
            if fix != j:
                p.append(e[j])
        angle = atan2(p[1], p[0])
        len = (p[0] ** 2 + p[1] ** 2) ** 0.5
        angle += da
        p = [cos(angle) * len, sin(angle) * len]
        i = 0
        for j in range(3):
            if fix != j:
                e[j] = p[i]
                i += 1
    for e in sides:
        e.recalc()


# rotate(0, pi / 2)
rotate(1, pi / 30)

CR = pi / 100
running = True
center = [width // 2, height // 2]
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    key = pygame.key.get_pressed()
    rev_mn = 1
    if key[pygame.K_r]:
        rev_mn = -1
    if key[pygame.K_x]:
        rotate(0, rev_mn * CR)
    if key[pygame.K_y]:
        rotate(1, rev_mn * CR)
    if key[pygame.K_z]:
        rotate(2, rev_mn * CR)
    if key[pygame.K_UP]:
        sz *= 0.98
    if key[pygame.K_DOWN]:
        sz /= 0.98
    if key[pygame.K_w]:
        center[1] -= sd * sz
    if key[pygame.K_s]:
        center[1] += sd * sz
    if key[pygame.K_a]:
        center[0] -= sd * sz
    if key[pygame.K_d]:
        center[0] += sd * sz

    screen.fill(black)

    buf = []
    bbuf = []
    for ii in range(len(sides)):
        if abs(sides[ii].c) >= 1e-6:
            buf.append(sides[ii])
        else:
            bbuf.append(sides[ii])
    sides = bbuf + buf

    for i, side in enumerate(sides):
        if abs(side.c) < 1e-6:
            continue

        prt = True
        for j, oth in enumerate(sides):
            if abs(oth.c) < 1e-6:
                continue
            s = side.side
            o = oth.side

            for p in s:
                if oth.is_in(p[0], p[1]) and oth.get_z(p[0], p[1]) > p[2] + 1e-6:
                    prt = False
                    break
            if not prt:
                break
            for p in o:
                if side.is_in(p[0], p[1]) and side.get_z(p[0], p[1]) < p[2] - 1e-6:
                    prt = False
                    break

            ls = s[-1]
            for cs in s:
                if not prt:
                    break
                lo = o[-1]
                for co in o:
                    p = intersect(ls[:2], cs[:2], lo[:2], co[:2])
                    if type(p) != list:
                        lo = co
                        continue
                    if oth.get_z(p[0], p[1]) > side.get_z(p[0], p[1]) + 1e-6:
                        if len(s) == 4 and cs[2] > 0:
                            print(ls)
                            print(cs)
                            print(lo)
                            print(co)
                        prt = False
                        break
                    lo = co
                ls = cs

            if not prt:
                break

        if prt:
            # print([[int(e) * 10 for e in p] for p in side.side])
            p = [(g[0] * sz + center[0], g[1] * sz + center[1]) for g in side.side]
            if len(p) > 2:
                pygame.draw.polygon(screen, side.color, p)

    # exit()

    for edge in edges:
        fl = -1
        d = neg(edge[0], edge[1])
        for e in edge:
            x, y, z = neg(e, mulsc(0.0001, d))
            for i, side in enumerate(sides):
                if side.c and side.is_in(x, y) and side.get_z(x, y) > z + 1e-6:
                    fl = i
            d = neg(edge[1], edge[0])
        if fl != -1:
            continue
        p = [(g[0] * sz + center[0], g[1] * sz + center[1]) for g in edge]
        pygame.draw.line(screen, white, p[0], p[1])

    # zs = [e[2] for e in points]
    # mx = max(zs)
    # mn = min(zs)
    # for p in points:
    #     d = (p[2] - mn) / (mx - mn)
    #     pygame.draw.circle(
    #         screen,
    #         (255 * d, 0, 255 - 255 * d),
    #         (int(p[0] * sz + center[0]), int(p[1] * sz + center[1])),
    #         5,
    #     )

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
