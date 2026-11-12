"""SODIUM GROTESK v0.1 — gerador paramétrico da fonte display da marca.

Regras de desenho (DNA):
- Peso Black, proporções largas, sempre reta (sem inclinação).
- Curvas em "squircle": cantos de raio grande e tensão alta (nem círculo, nem quadrado).
- Terminais cortados na horizontal/vertical, nunca na diagonal.
- Ink traps (entalhes) em todas as junções agudas: a "luz que vaza" de dentro da letra.
- Espaçamento apertado, pensado para caixa-alta.
"""
import sys
from pathops import Path, op, PathOp
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

import os
WS = float(os.environ.get('WS', '1'))
CAP = 700
V = 200      # haste vertical
H = 166      # haste horizontal
HS = 150     # horizontais das letras de duas barrigas (S, B, 2, 3, 5, 6, 8, 9)
HM = 140     # barra do meio dessas letras
R = int(os.environ.get('RAD', '250'))      # raio externo das curvas
RI = 26      # raio interno (contraformas)
K = 0.74     # tensão externa (0.552 = círculo)
KI = 0.5
DX = int(232 * (0.85 + 0.15 * WS))     # largura horizontal das diagonais
TRAP = 58    # profundidade do ink trap
TRAPW = 40   # meia-abertura do ink trap
TRAPR = 70   # alcance do ink trap ao longo das bordas

MID_T = 360 + HM // 2
MID_B = 360 - HM // 2


def new():
    return Path()


def poly(*pts):
    p = Path()
    pen = p.getPen()
    pen.moveTo(pts[0])
    for q in pts[1:]:
        pen.lineTo(q)
    pen.closePath()
    return p


def rect(x0, y0, x1, y1):
    return poly((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def rrect(x0, y0, x1, y1, bl=0, br=0, tr=0, tl=0, k=K):
    """Retângulo com raio por canto (sentido anti-horário)."""
    p = Path()
    pen = p.getPen()
    pen.moveTo((x0 + bl, y0))
    pen.lineTo((x1 - br, y0))
    if br:
        pen.curveTo((x1 - br + k * br, y0), (x1, y0 + br - k * br), (x1, y0 + br))
    pen.lineTo((x1, y1 - tr))
    if tr:
        pen.curveTo((x1, y1 - tr + k * tr), (x1 - tr + k * tr, y1), (x1 - tr, y1))
    pen.lineTo((x0 + tl, y1))
    if tl:
        pen.curveTo((x0 + tl - k * tl, y1), (x0, y1 - tl + k * tl), (x0, y1 - tl))
    pen.lineTo((x0, y0 + bl))
    if bl:
        pen.curveTo((x0, y0 + bl - k * bl), (x0 + bl - k * bl, y0), (x0 + bl, y0))
    pen.closePath()
    return p


def U(*paths):
    out = paths[0]
    for p in paths[1:]:
        out = op(out, p, PathOp.UNION)
    return out


def D(a, *bs):
    for b in bs:
        a = op(a, b, PathOp.DIFFERENCE)
    return a


def band(tx0, ty, bx0, by, w=DX):
    """Diagonal de largura horizontal constante: topo em (tx0..tx0+w, ty), base em (bx0..bx0+w, by)."""
    return poly((bx0, by), (bx0 + w, by), (tx0 + w, ty), (tx0, ty))


def trap_down(x, y):
    """Entalhe apontando para baixo a partir de uma junção (x, y)."""
    return poly((x - TRAPW, y + 2), (x + TRAPW, y + 2), (x, y - TRAP))


def trap_up(x, y):
    return poly((x - TRAPW, y - 2), (x, y + TRAP), (x + TRAPW, y - 2))


def trap_dir(x, y, dx, dy, depth=TRAP, half=TRAPW):
    """Entalhe na junção (x, y) apontando na direção (dx, dy)."""
    import math
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    return poly((x - px * half - ux * 2, y - py * half - uy * 2),
                (x + px * half - ux * 2, y + py * half - uy * 2),
                (x + ux * depth, y + uy * depth))


def trap2(P, a, b, depth=None, reach=None):
    """Ink trap clássico na virilha P (onde duas bordas se encontram formando uma abertura).
    a e b: pontos ao longo das duas bordas, na direção da abertura.
    Corta um triângulo (P+u1*reach, ponta, P+u2*reach): abre a virilha e entra no sólido pela bissetriz."""
    import math
    depth = depth or TRAP
    reach = reach or TRAPR
    def nrm(v):
        n = math.hypot(*v)
        return (v[0] / n, v[1] / n)
    u1 = nrm((a[0] - P[0], a[1] - P[1]))
    u2 = nrm((b[0] - P[0], b[1] - P[1]))
    d = nrm((-(u1[0] + u2[0]), -(u1[1] + u2[1])))
    tip = (P[0] + d[0] * depth, P[1] + d[1] * depth)
    return poly((P[0] + u1[0] * reach, P[1] + u1[1] * reach), tip, (P[0] + u2[0] * reach, P[1] + u2[1] * reach))


def lerp_x(p0, p1, y):
    (x0, y0), (x1, y1) = p0, p1
    t = (y - y0) / (y1 - y0)
    return x0 + t * (x1 - x0)


def intersect(a0, a1, b0, b1):
    (x1, y1), (x2, y2) = a0, a1
    (x3, y3), (x4, y4) = b0, b1
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


G = {}   # nome -> (path, largura_tinta, lsb, rsb)
SB = 26
SBR = 16  # curvas
SBD = 2   # diagonais


def glyph(name, w, lsb=SB, rsb=SB):
    def deco(fn):
        ww = w if name in ('I', 'period', 'uni25A0', 'colon', 'comma') else w * WS
        G[name] = (fn(ww), ww, lsb, rsb)
        return fn
    return deco


# ---------- redondas ----------
def bowl(w, h=CAP, y0=0):
    outer = rrect(0, y0, w, y0 + h, R, R, R, R)
    inner = rrect(V, y0 + H, w - V, y0 + h - H, RI, RI, RI, RI, KI)
    return D(outer, inner)


@glyph("O", 800, SBR, SBR)
def _(w):
    return bowl(w)


@glyph("Q", 800, SBR, SBR - 30)
def _(w):
    tail = band(w * 0.50, 250, w - DX + 40, -70, DX - 20)
    return D(U(bowl(w), tail), trap_dir(w * 0.5 + 6, 250, 0, -1))


@glyph("C", 740, SBR, SB)
def _(w):
    return D(bowl(w), rect(w / 2, 270, w + 5, 430))


@glyph("G", 770, SBR, SB)
def _(w):
    g = D(bowl(w), rect(w / 2, 352, w + 5, 548))
    bar = rect(w / 2 - 10, 222, w - V + 8, 352)
    return U(g, bar)


@glyph("D", 770, SB, SBR)
def _(w):
    outer = rrect(0, 0, w, CAP, 0, R, R, 0)
    inner = rrect(V, H, w - V, CAP - H, 0, RI, RI, 0, KI)
    return D(outer, inner)


@glyph("U", 760, SB, SB)
def _(w):
    outer = rrect(0, 0, w, CAP, R, R, 0, 0)
    inner = rrect(V, H, w - V, CAP + 5, RI, RI, 0, 0, KI)
    return D(outer, inner)


@glyph("J", 640, SB - 10, SB)
def _(w):
    outer = rrect(0, 0, w, CAP, R, R, 0, 0)
    inner = rrect(V, H, w - V, CAP + 5, RI, RI, 0, 0, KI)
    return D(outer, inner, rect(-5, 300, V + 1, CAP + 5))


# ---------- duas barrigas ----------
def s_shape(w, round_top=True, round_bottom=True):
    r_top = R if round_top else 0
    r_bot = R if round_bottom else 0
    outer = rrect(0, 0, w, CAP, r_bot, r_bot, r_top, r_top)
    upper = rrect(V, MID_T, w + 5, CAP - HS, 0, 0, 0, RI, KI)
    upper = U(upper, rrect(V, MID_T, w + 5, CAP - HS, RI, 0, 0, RI, KI))
    lower = rrect(-5, HS, w - V, MID_B, 0, RI, RI, 0, KI)
    return D(outer, upper, lower)


@glyph("S", 720, SBR, SBR)
def _(w):
    return s_shape(w)


@glyph("B", 750, SB, SBR)
def _(w):
    low = rrect(0, 0, w, MID_T, 0, R * 0.85, R * 0.6, 0)
    up = rrect(0, MID_B, w - 36, CAP, 0, R * 0.55, R * 0.8, 0)
    c1 = rrect(V, HS, w - V, MID_B, 0, RI, RI, 0, KI)
    c2 = rrect(V, MID_T, w - 36 - V, CAP - HS, 0, RI, RI, 0, KI)
    return D(U(low, up), c1, c2)


@glyph("P", 720, SB, SBR)
def _(w):
    yb = 250
    stem = rect(0, 0, V, CAP)
    b = rrect(0, yb, w, CAP, 0, R * 0.8, R * 0.8, 0)
    c = rrect(V, yb + H, w - V, CAP - H, 0, RI, RI, 0, KI)
    return D(U(stem, b), c)


@glyph("R", 760, SB, SBD + 10)
def _(w):
    yb = 270
    stem = rect(0, 0, V, CAP)
    b = rrect(0, yb, w - 10, CAP, 0, R * 0.7, R * 0.8, 0)
    c = rrect(V, yb + H, w - 10 - V, CAP - H, 0, RI, RI, 0, KI)
    leg = band(V + 70, yb + 10, w - DX, 0)
    shape = D(U(stem, b, leg), c)
    # ink trap onde a perna encontra a barriga (lado de baixo)
    jx = lerp_x((V + 70, yb + 10), (w - DX, 0), yb)
    return D(shape, trap2((jx, yb), (V, yb), (w - DX, 0)))


# ---------- retas ----------
@glyph("I", V)
def _(w):
    return rect(0, 0, V, CAP)


@glyph("E", 640)
def _(w):
    return U(rect(0, 0, V, CAP), rect(0, CAP - H, w, CAP), rect(0, 360 - H // 2, w - 46, 360 + H // 2), rect(0, 0, w, H))


@glyph("F", 600, SB, SB - 10)
def _(w):
    return U(rect(0, 0, V, CAP), rect(0, CAP - H, w, CAP), rect(0, 330 - H // 2, w - 56, 330 + H // 2))


@glyph("L", 580, SB, SB - 14)
def _(w):
    return U(rect(0, 0, V, CAP), rect(0, 0, w, H))


@glyph("T", 700, SB - 20, SB - 20)
def _(w):
    return U(rect(0, CAP - H, w, CAP), rect(w / 2 - V / 2, 0, w / 2 + V / 2, CAP))


@glyph("H", 780)
def _(w):
    return U(rect(0, 0, V, CAP), rect(w - V, 0, w, CAP), rect(0, 360 - H // 2, w, 360 + H // 2))


# ---------- diagonais ----------
@glyph("A", 840, SBD, SBD)
def _(w):
    cx, half = w / 2, DX / 2
    left = band(cx - half, CAP, 0, 0)
    right = band(cx - half, CAP, w - DX, 0)
    bar = rect(DX * 0.6, 150, w - DX * 0.6, 150 + H - 10)
    s = U(left, right, bar)
    # entalhe sob o ápice
    ap = intersect((DX, 0), (cx + half, CAP), (w - DX, 0), (cx - half, CAP))
    return D(s, trap2(ap, (DX, 0), (w - DX, 0)))


@glyph("V", 840, SBD, SBD)
def _(w):
    cx, half = w / 2, DX / 2
    left = band(0, CAP, cx - half, 0)
    right = band(w - DX, CAP, cx - half, 0)
    s = U(left, right)
    cr = intersect((DX, CAP), (cx + half, 0), (w - DX, CAP), (cx - half, 0))
    return D(s, trap2(cr, (DX, CAP), (w - DX, CAP)))


@glyph("W", 1100, SBD, SBD)
def _(w):
    d = 176
    h = d / 2
    c1, c2, cx = w * 0.27, w * 0.73, w / 2
    a = band(0, CAP, c1 - h, 0, d)
    b = band(cx - h, CAP, c1 - h, 0, d)
    c = band(cx - h, CAP, c2 - h, 0, d)
    e = band(w - d, CAP, c2 - h, 0, d)
    s = U(a, b, c, e)
    cr1 = intersect((d, CAP), (c1 + h, 0), (cx - h, CAP), (c1 - h, 0))
    cr2 = intersect((cx + h, CAP), (c2 + h, 0), (w - d, CAP), (c2 - h, 0))
    top = intersect((c1 + h, 0), (cx + h, CAP), (c2 - h, 0), (cx - h, CAP))
    return D(s, trap2(cr1, (d, CAP), (cx - h, CAP)), trap2(cr2, (cx + h, CAP), (w - d, CAP)), trap2(top, (c1 + h, 0), (c2 - h, 0)))


@glyph("M", 990)
def _(w):
    cx, half = w / 2, DX / 2
    vy = 160
    l = rect(0, 0, V, CAP)
    r = rect(w - V, 0, w, CAP)
    ld = poly((0, CAP), (DX, CAP), (cx + half, vy), (cx - half, vy))
    rd = poly((w - DX, CAP), (w, CAP), (cx + half, vy), (cx - half, vy))
    s = U(l, r, ld, rd)
    cr = intersect((DX, CAP), (cx + half, vy), (w - DX, CAP), (cx - half, vy))
    jl = intersect((DX, CAP), (cx + half, vy), (V, 0), (V, CAP))
    jr = intersect((w - DX, CAP), (cx - half, vy), (w - V, 0), (w - V, CAP))
    return D(s, trap2(cr, (DX, CAP), (w - DX, CAP)))


@glyph("N", 800)
def _(w):
    l = rect(0, 0, V, CAP)
    r = rect(w - V, 0, w, CAP)
    dg = band(0, CAP, w - DX, 0)
    s = U(l, r, dg)
    j1 = intersect((DX, CAP), (w, 0), (V, 0), (V, CAP))
    j2 = intersect((0, CAP), (w - DX, 0), (w - V, 0), (w - V, CAP))
    return D(s, trap2(j1, (V, 0), (w, 0), 34, 50), trap2(j2, (w - V, CAP), (0, CAP), 34, 50))


@glyph("Y", 830, SBD, SBD)
def _(w):
    cx, half = w / 2, DX / 2
    ym = 300
    ld = poly((0, CAP), (DX, CAP), (cx + half, ym), (cx - half, ym))
    rd = poly((w - DX, CAP), (w, CAP), (cx + half, ym), (cx - half, ym))
    st = rect(cx - V / 2, 0, cx + V / 2, ym + 4)
    s = U(ld, rd, st)
    cr = intersect((DX, CAP), (cx + half, ym), (w - DX, CAP), (cx - half, ym))
    return D(s, trap2(cr, (DX, CAP), (w - DX, CAP)))


@glyph("X", 830, SBD, SBD)
def _(w):
    a = band(0, CAP, w - DX, 0)
    b = band(w - DX, CAP, 0, 0)
    s = U(a, b)
    top = intersect((DX, CAP), (w, 0), (w - DX, CAP), (0, 0))
    bot = intersect((0, CAP), (w - DX, 0), (w, CAP), (DX, 0))
    return D(s, trap2(top, (DX, CAP), (w - DX, CAP)), trap2(bot, (DX, 0), (w - DX, 0)))


@glyph("K", 800, SB, SBD)
def _(w):
    st = rect(0, 0, V, CAP)
    arm = poly((V - 30, 200), (V - 30 + DX, 200), (w, CAP), (w - DX, CAP))
    lx = w * 0.40
    leg = poly((lx, 470), (lx + DX, 470), (w, 0), (w - DX, 0))
    s = U(st, arm, leg)
    up = intersect((V - 30, 200), (w - DX, CAP), (V, 0), (V, CAP))
    rc = intersect((V - 30 + DX, 200), (w, CAP), (lx + DX, 470), (w, 0))
    return D(s, trap2(rc, (w, CAP), (w, 0)))


@glyph("Z", 700, SB - 10, SB - 10)
def _(w):
    t = rect(0, CAP - H, w, CAP)
    b = rect(0, 0, w, H)
    dg = poly((w - DX - 30, CAP - H), (w, CAP - H), (DX + 30, H), (0, H))
    return U(t, b, dg)


# ---------- números (tabulares) ----------
NW = 680


@glyph("zero", NW, SBR, SBR)
def _(w):
    return bowl(w)


@glyph("one", NW, SB, SB)
def _(w):
    x = w / 2 - V / 2 + 60
    return U(rect(x, 0, x + V, CAP), rect(x - 180, CAP - H, x + 4, CAP))


@glyph("two", NW, SBR, SBR)
def _(w):
    outer = rrect(0, 0, w, CAP, 0, 0, R, R)
    upper = rrect(-5, MID_T, w - V, CAP - HS, 0, 0, RI, 0, KI)
    lower = rrect(V, HS, w + 5, MID_B, RI, 0, 0, RI, KI)
    return D(outer, upper, lower)


@glyph("three", NW, SBR, SBR)
def _(w):
    outer = rrect(0, 0, w, CAP, R, R, R, R)
    upper = rrect(-5, MID_T, w - V, CAP - HS, 0, 0, RI, 0, KI)
    lower = rrect(-5, HS, w - V, MID_B, 0, RI, 0, 0, KI)
    return D(outer, upper, lower, rect(-5, MID_B - 2, w * 0.3, MID_T + 2))


@glyph("four", NW + 20, SB - 14, SB - 14)
def _(w):
    x = w - V - 50
    return U(rect(0, 250, V, CAP), rect(0, 250, w, 250 + H), rect(x, 0, x + V, CAP))


@glyph("five", NW, SBR, SBR)
def _(w):
    outer = rrect(0, 0, w, CAP, R, R, 0, 0)
    upper = rrect(V, MID_T, w + 5, CAP - HS, 0, 0, 0, 0, KI)
    lower = rrect(-5, HS, w - V, MID_B, 0, RI, RI, 0, KI)
    return D(outer, upper, lower)


@glyph("six", NW, SBR, SBR)
def _(w):
    outer = rrect(0, 0, w, CAP, R, R, R, R)
    upper = rrect(V, MID_T, w + 5, CAP - HS, 0, 0, 0, RI, KI)
    lower = rrect(V, HS, w - V, MID_B, RI, RI, RI, RI, KI)
    return D(outer, upper, lower)


@glyph("seven", NW, SB - 10, SB - 10)
def _(w):
    return U(rect(0, CAP - H, w, CAP), poly((w - DX, CAP - H), (w, CAP - H), (190 + DX, 0), (190, 0)))


@glyph("eight", NW, SBR, SBR)
def _(w):
    outer = rrect(0, 0, w, CAP, R, R, R, R)
    upper = rrect(V + 14, MID_T, w - V - 14, CAP - HS, RI, RI, RI, RI, KI)
    lower = rrect(V, HS, w - V, MID_B, RI, RI, RI, RI, KI)
    return D(outer, upper, lower)


@glyph("nine", NW, SBR, SBR)
def _(w):
    outer = rrect(0, 0, w, CAP, R, R, R, R)
    upper = rrect(V, MID_T, w - V, CAP - HS, RI, RI, RI, RI, KI)
    lower = rrect(-5, HS, w - V, MID_B, 0, RI, 0, 0, KI)
    return D(outer, upper, lower)


# ---------- pontuação ----------
SQ = V  # o "sinal": quadrado do tamanho da haste


@glyph("period", SQ, 30, 30)
def _(w):
    return rect(0, 0, SQ, SQ)


@glyph("uni25A0", SQ, 30, 30)
def _(w):
    return rect(0, 0, SQ, SQ)


@glyph("colon", SQ, 30, 30)
def _(w):
    return U(rect(0, 0, SQ, SQ), rect(0, 420, SQ, 420 + SQ))


@glyph("comma", SQ, 30, 30)
def _(w):
    return U(rect(0, 0, SQ, SQ), poly((40, 2), (SQ, 2), (60, -150), (-20, -150)))


@glyph("hyphen", 340, 30, 30)
def _(w):
    return rect(0, 290, w, 290 + H)


@glyph("emdash", 900, 20, 20)
def _(w):
    return rect(0, 290, w, 290 + H)


@glyph("slash", 520, 0, 0)
def _(w):
    return band(w - DX, CAP + 40, 0, -60)


@glyph("ampersand", 780, SBR, SBD)
def _(w):
    up = rrect(40, 330, w - 190, CAP, R * 0.6, R * 0.6, R * 0.8, R * 0.8)
    upc = rrect(40 + V, 330 + H, w - 190 - V, CAP - H, RI, RI, RI, RI, KI)
    low = rrect(0, 0, w - 120, 420, R, R, 0, R * 0.7)
    lowc = rrect(V, H, w - 120 - V, 420 - H + 10, RI, RI, 0, RI, KI)
    leg = band(w * 0.32, 470, w - DX, 0)
    return D(U(D(up, upc), D(low, lowc), leg), rect(w - 120 - V - 2, H + 60, w - 100, 300))


@glyph("registered", 470, 30, 30)
def _(w):
    # ® sobrescrito: anel + R simplificado
    s = 470
    y0 = CAP - s
    ring = D(rrect(0, y0, s, CAP, 230, 230, 230, 230, 0.56),
             rrect(52, y0 + 52, s - 52, CAP - 52, 180, 180, 180, 180, 0.56))
    st = rect(140, y0 + 110, 200, CAP - 110)
    bowl_ = D(rrect(140, y0 + 230, 330, CAP - 110, 0, 70, 70, 0),
              rrect(200, y0 + 280, 280, CAP - 160, 0, 30, 30, 0))
    leg = poly((215, y0 + 236), (275, y0 + 236), (340, y0 + 110), (280, y0 + 110))
    return U(ring, st, bowl_, leg)


def space(_):
    return Path()


G["space"] = (Path(), 220, 0, 0)

# ---------- montagem ----------
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
order = [".notdef", "space"] + list(LETTERS) + DIGITS + ["period", "comma", "colon", "hyphen", "emdash", "slash", "ampersand", "registered", "uni25A0"]

cmap = {32: "space"}
for c in LETTERS:
    cmap[ord(c)] = c
    cmap[ord(c.lower())] = c
for i, n in enumerate(DIGITS):
    cmap[ord("0") + i] = n
cmap.update({ord("."): "period", ord(","): "comma", ord(":"): "colon", ord("-"): "hyphen",
             0x2014: "emdash", 0x2013: "emdash", ord("/"): "slash", ord("&"): "ampersand",
             0xAE: "registered", 0x25A0: "uni25A0"})

charstrings = {}
metrics = {}

nd = T2CharStringPen(500, None)
rect(50, 0, 450, CAP).draw(nd)
charstrings[".notdef"] = nd.getCharString()
metrics[".notdef"] = (500, 50)

for name in order[1:]:
    path, w, lsb, rsb = G[name]
    adv = int(round(w + lsb + rsb))
    p = Path()
    p.addPath(path)
    p.transform(1, 0, 0, 1, lsb, 0) if False else None
    shifted = Path()
    pen = shifted.getPen()
    from fontTools.pens.transformPen import TransformPen
    path.draw(TransformPen(pen, (1, 0, 0, 1, lsb, 0)))
    shifted = op(shifted, Path(), PathOp.UNION, clockwise=False) if name != "space" else shifted
    cs_pen = T2CharStringPen(adv, None)
    from fontTools.pens.roundingPen import RoundingPen
    shifted.draw(RoundingPen(cs_pen))
    charstrings[name] = cs_pen.getCharString()
    b = shifted.bounds if name != "space" else (0, 0, 0, 0)
    metrics[name] = (adv, int(round(b[0])) if name != "space" else 0)

fb = FontBuilder(1000, isTTF=False)
fb.setupGlyphOrder(order)
fb.setupCharacterMap(cmap)
FAM = os.environ.get("FAM", "Sodium Grotesk")
fb.setupCFF(FAM.replace(" ", "") + "-Black", {"FullName": FAM + " Black"}, charstrings, {})
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=860, descent=-200)
fb.setupNameTable({"familyName": FAM, "styleName": "Black",
                   "version": "Version 0.1", "copyright": "SODIUM — draft v0.1"})
fb.setupOS2(sTypoAscender=860, sTypoDescender=-200, usWinAscent=900, usWinDescent=220,
            sCapHeight=CAP, sxHeight=CAP, usWeightClass=900)
fb.setupPost()
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
FEA = """
languagesystem DFLT dflt;
languagesystem latn dflt;
feature kern {
  pos A [V W Y T] -50; pos [V W Y T] A -50;
  pos L [T Y V W] -70; pos [P F] A -40; pos [T] [O C G Q] -10;
  pos [V Y W] [O C G Q] -20; pos [O C G Q D] [V W Y A X] -20; pos [O D Q] [A] -24;
  pos R [V W Y T] -24; pos [K X] [O C G Q] -24;
} kern;
"""
addOpenTypeFeaturesFromString(fb.font, FEA)
out = sys.argv[1] if len(sys.argv) > 1 else "SodiumGrotesk-Black"
fb.save(out + ".otf")
f = TTFont(out + ".otf")
f.flavor = "woff2"
f.save(out + ".woff2")
print("ok", len(order), "glyphs")
