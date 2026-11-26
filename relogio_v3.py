"""Projeto Vênus — vídeo "A virada do ano" v3: a virada MÉDIA (2016-2024).

Uso:
  python -I relogio_v3.py <numeros.json> <saida.mp4>            # vídeo (Stories, 9:16, até 60 s)
  python -I relogio_v3.py <numeros.json> <pasta_png> --frames   # só alguns quadros de teste

Números de estudo/numeros.py (arquivos oficiais do DATASUS), média por noite de 2016 a 2024:
- Vermelho, DENTRO do mostrador: mulheres mortas por agressão (SIM, CID-10 X85-Y09), hora do óbito.
  1 ponto = 1 mulher, em média por noite.
- Amarelo, FORA do mostrador: mulheres atendidas na saúde após agressão de parceiro ou ex (SINAN),
  notificações no dia da agressão ou no seguinte, com hora. 1 ponto = 1 atendimento, em média por noite.
- Em cima: a noite de 31/12 (18h) a 1/1 (6h). Embaixo: noite comum = média de todas as noites.
- Só registros com hora. Médias arredondadas por bloco (18h-0h e 0h-6h) preservando o total.
- Dentro de cada hora os pontos são distribuídos por igual (não é o minuto exato).
"""
import sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

NUM, OUT = sys.argv[1], sys.argv[2]
FRAMES_ONLY = "--frames" in sys.argv
R = json.load(open(NUM, encoding="utf-8"))
NV = 9  # viradas 2016-2024
SIM, SIN = R["sim_mulheres_relogio_2016_2024"], R["sinan_mulheres_parceiro"]["virada_por_hora_2016_2024"]
SP = R["sinan_mulheres_parceiro"]
HOURS = list(range(18, 24)) + list(range(6))
SUB_B = "média de todos os dias do ano"
def round_block(vals):
    vals = np.asarray(vals, float); base = np.floor(vals).astype(int)
    for i in np.argsort(-(vals - base))[:int(round(vals.sum())) - base.sum()]: base[i] += 1
    return base.tolist()
def per_night(v): v = [x / NV for x in v]; return round_block(v[:6]) + round_block(v[6:])
RED_A = per_night(SIM["31dez"] + SIM["1jan"]); RED_B = per_night(SIM["comum"])
YEL_A = per_night(SIN["31dez"] + SIN["1jan"]); YEL_B = per_night(SIN["comum"])
print("vermelho virada/comum:", RED_A, sum(RED_A), "|", RED_B, sum(RED_B))
print("amarelo virada/comum:", YEL_A, sum(YEL_A), "|", YEL_B, sum(YEL_B))

# ---------------- visual ----------------
W, H, SS, FPS = 1080, 1920, 2, 30
BG = (12, 8, 10); INK = (246, 238, 241); MUTED = (208, 198, 202); DIAL = (92, 78, 84)
RED = (255, 58, 98); YEL = (255, 196, 64); ROSE = (244, 176, 190)
F = "C:/Windows/Fonts/"
def font(name, size): return ImageFont.truetype(F + name, size * SS)
f_title = font("georgia.ttf", 62); f_q = font("georgia.ttf", 50); f_lab = font("georgiai.ttf", 40)
f_time = font("segoeui.ttf", 30); f_small = font("segoeui.ttf", 26); f_num = font("georgia.ttf", 18)
f_end = font("segoeui.ttf", 36); f_tag = font("segoeui.ttf", 26); f_src = font("segoeui.ttf", 21)
f_exp = font("georgia.ttf", 44); f_fin = font("segoeui.ttf", 29); f_leg = font("segoeui.ttf", 21)
# área segura do Stories: conteúdo entre y=250 e y=1584
R0 = 150; COLS, GAP0, ROWSTEP, DOT = 6, 16, 13.5, 4.8     # pontos por fora do mostrador
RED_R = 11.0                                             # ponto que ficou vermelho (bem maior)
f_cnt = font("segoeui.ttf", 27)
CLOCK_A = (540, 680); CLOCK_B = (540, 1230)
L = dict(tag=268, labA=314, time=360, leg=398, labB=896, subB=982, tick=(9, 4), num=(22, 11), hand=5, hub=5)

def pol(c, r, h):
    a = (h % 12) / 12 * 2 * math.pi
    return c[0] + r * math.sin(a), c[1] - r * math.cos(a)
def yel_pos(c, h, i):
    row, col = divmod(i, COLS)
    return pol(c, R0 + GAP0 + row * ROWSTEP, h + (col + 0.5) / COLS)
def red_pos(c, h, i, n):
    row, col = divmod(i, 3); m = min(3, n - row * 3)
    return pol(c, R_IN - row * RED_ROW, h + (col + 0.5) / m)
def S(v): return v * SS
def text_c(d, y, txt, f, fill, x=540):
    tw = d.textlength(txt, font=f); d.text((S(x) - tw / 2, S(y)), txt, font=f, fill=fill)
def text_rich(d, y, parts, f):
    tw = sum(d.textlength(t, font=f) for t, _ in parts); x = S(540) - tw / 2
    for t, c in parts: d.text((x, S(y)), t, font=f, fill=c); x += d.textlength(t, font=f)
def blend(c, a): return tuple(int(BG[k] + (c[k] - BG[k]) * a) for k in range(3))
def tag(d): text_c(d, L["tag"], "PROJETO VÊNUS  ·  conscientização sobre a violência contra a mulher", f_tag, ROSE)
def blank():
    im = Image.new("RGB", (S(W), S(H)), BG); d = ImageDraw.Draw(im); tag(d); return im, d
def draw_dial(d, c):
    d.ellipse([S(c[0] - R0), S(c[1] - R0), S(c[0] + R0), S(c[1] + R0)], outline=DIAL, width=S(3))
    for m in range(60):
        big = m % 5 == 0
        x1, y1 = pol(c, R0 - (L['tick'][0] if big else L['tick'][1]), m / 5); x2, y2 = pol(c, R0, m / 5)
        d.line([S(x1), S(y1), S(x2), S(y2)], fill=MUTED if big else DIAL, width=S(3 if big else 1))
    for n in range(1, 13):
        x, y = pol(c, R0 - L['num'][0], n); tw = d.textlength(str(n), font=f_num)
        d.text((S(x) - tw / 2, S(y) - S(L['num'][1])), str(n), font=f_num, fill=MUTED)
def counter(d, y, ny, nr):  # contador ao vivo, que também serve de legenda
    p1 = f"{ny} {'agressão' if ny == 1 else 'agressões'}"; p2 = f"{nr} {'morte' if nr == 1 else 'mortes'}"
    gap = S(46); w1 = d.textlength(p1, font=f_cnt); w2 = d.textlength(p2, font=f_cnt)
    x = S(540) - (S(20) + w1 + gap + S(26) + w2) / 2
    d.ellipse([x, S(y + 11), x + S(12), S(y + 23)], fill=YEL); d.text((x + S(20), S(y)), p1, font=f_cnt, fill=INK)
    x2 = x + S(20) + w1 + gap
    d.ellipse([x2, S(y + 6), x2 + S(20), S(y + 26)], fill=RED, outline=INK, width=S(2)); d.text((x2 + S(28), S(y)), p2, font=f_cnt, fill=INK)

base = Image.new("RGB", (S(W), S(H)), BG); bd = ImageDraw.Draw(base)
tag(bd); draw_dial(bd, CLOCK_A); draw_dial(bd, CLOCK_B)
text_c(bd, L["labA"], "A virada do ano", f_lab, INK)
text_c(bd, L["labB"], "Uma noite comum", f_lab, INK)
text_c(bd, L["labB"] + 47, SUB_B, f_small, MUTED)
text_c(bd, 1496, "Médias por noite, de 2016 a 2024 · só registros com hora", f_src, MUTED)
text_c(bd, 1528, "Fontes: SIM e SINAN/DATASUS, Ministério da Saúde · análise: Rita Farias", f_src, MUTED)

# ---------------- linha do tempo ----------------
T_HOOK, T_EXP, T_PAUSE, T_SWEEP, T_HOLD, T_HELP = 8.0, 20.0, 0.8, 14.0, 9.5, 7.0
T1 = T_HOOK + T_EXP; T2 = T1 + T_PAUSE; T3 = T2 + T_SWEEP; T4 = T3 + T_HOLD
N = int((T4 + T_HELP) * FPS)
def el_at(t): return float(np.interp(t, [T2, T3], [0.0, 12.0]))
TURN = 0.45  # horas entre o ponto aparecer amarelo e ficar vermelho
def events(clock, reds, yels):  # (aparece, relógio, hora, índice, vira_vermelho_em ou None)
    ev = []
    for k, h in enumerate(HOURS):
        ny, nr = yels[k], reds[k]
        turn = {int((j + 0.5) * ny / nr) for j in range(nr)} if nr else set()  # espalhados na hora
        for i in range(ny):
            e = k + (i + 0.5) / max(ny, 1)
            ev.append((e, clock, h, i, min(e + TURN, 11.9) if i in turn else None))
    return ev
EV = events(CLOCK_A, RED_A, YEL_A) + events(CLOCK_B, RED_B, YEL_B)

HOOK = [("Você sabia que o 1º de janeiro", INK), ("é o dia do ano com mais", INK),
        ("mulheres mortas por", ROSE), ("agressão no Brasil?", ROSE)]
EXP = [
    (0.3, ["Estes relógios mostram a noite", "de 31 de dezembro para 1º de janeiro,", "das 18h às 6h."], INK),
    (4.4, ["Em cima, o que acontece", "numa virada do ano.", "Embaixo, numa noite comum:", "a média de todos os dias do ano.", "Médias de 2016 a 2024."], INK),
    (9.4, [[("Cada ponto ", INK), ("amarelo", YEL), (" é uma mulher", INK)], "agredida pelo parceiro ou ex", "e atendida num serviço de saúde."], INK),
    (13.8, [[("Cada ponto ", INK), ("vermelho", RED), (" é uma mulher", INK)], "assassinada."], INK),
    (17.4, ["Respire fundo."], INK),
]

def frame(fi):
    t = fi / FPS
    if t < T_HOOK:
        im, d = blank(); out_a = min(1, (T_HOOK - t) / 0.5)
        text_c(d, 660, "O ano está acabando.", f_title, blend(INK, min(1, t / 0.6) * out_a))
        a2 = max(0, min(1, (t - 1.8) / 0.8)) * out_a
        for i, (txt, c) in enumerate(HOOK): text_c(d, 800 + i * 66, txt, f_q, blend(c, a2))
        a3 = max(0, min(1, (t - 3.4) / 0.8)) * out_a
        text_c(d, 1110, "Fonte: declarações de óbito do Ministério da Saúde", f_small, blend(MUTED, a3))
        text_c(d, 1148, "(SIM/DATASUS), 1996–2025", f_small, blend(MUTED, a3))
        return im
    if t < T1:
        im, d = blank(); te = t - T_HOOK; out_a = min(1, (T_EXP - te) / 0.6); y = 360
        for t0, lines, c in EXP:
            a = max(0, min(1, (te - t0) / 0.7)) * out_a
            for ln in lines:
                if isinstance(ln, list): text_rich(d, y, [(s_, blend(cc, a)) for s_, cc in ln], f_exp)
                else: text_c(d, y, ln, f_exp, blend(c, a))
                y += 58
            y += 40
        return im
    if t >= T4:
        im, d = blank(); a = min(1, (t - T4) / 0.8)
        text_c(d, 640, "Se você ou alguém próxima precisa de ajuda:", f_end, blend(INK, a))
        text_c(d, 740, "Ligue 180", f_title, blend(ROSE, a))
        text_c(d, 830, "Central de Atendimento à Mulher", f_end, blend(INK, a))
        text_c(d, 878, "gratuito · 24 horas · sigiloso", f_end, blend(MUTED, a))
        text_c(d, 990, "WhatsApp: (61) 99610-0180", f_q, blend(INK, a))
        text_c(d, 1070, "Emergência: 190", f_q, blend(INK, a))
        return im
    im = base.copy(); fade = min(1, (t - T1) / 0.6)
    if fade < 1: im = Image.blend(Image.new("RGB", im.size, BG), im, fade)
    d = ImageDraw.Draw(im); el = el_at(t); hold = t >= T3; cur = min(int(el), 11)
    reds_now = []
    for e, c, h, i, tr in EV:
        if e > el: continue
        mad = h < 6; x, y = yel_pos(c, h, i)
        if tr is not None and el >= tr:   # virou vermelho: desenhado por cima, depois
            reds_now.append((x, y, tr, mad)); continue
        if hold: r, fc = (DOT, YEL) if mad else (DOT, blend(YEL, 0.45))
        elif HOURS.index(h) == cur:
            a = min(1, (el - e) / 0.25); r, fc = DOT * 1.3 * (0.6 + 0.4 * a), YEL
        else: r, fc = DOT, blend(YEL, 0.75)
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=fc)
    for x, y, tr, mad in reds_now:
        a = 1 if hold else min(1, (el - tr) / 0.2)
        r = RED_R * (1 + 0.7 * (1 - a))
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=RED, outline=INK, width=S(2))
    for c, yv in ((CLOCK_A, L["leg"]), (CLOCK_B, L["subB"])):
        ny = sum(1 for e, cc, *_ in EV if cc == c and e <= el)
        nr = sum(1 for e, cc, h, i, tr in EV if cc == c and tr is not None and tr <= el)
        counter(d, yv, ny, nr)
    for c in (CLOCK_A, CLOCK_B):
        clock = 18 + el
        hx, hy = pol(c, R0 * 0.40, clock); d.line([S(c[0]), S(c[1]), S(hx), S(hy)], fill=INK, width=S(L['hand']))
        mx, my = pol(c, R0 * 0.62, (clock % 1) * 12); d.line([S(c[0]), S(c[1]), S(mx), S(my)], fill=INK, width=S(2))
        hb = L['hub']; d.ellipse([S(c[0] - hb), S(c[1] - hb), S(c[0] + hb), S(c[1] + hb)], fill=INK)
    clock = 18 + el; hh = int(clock) % 24; mm = int((clock % 1) * 60)
    text_c(d, L["time"], f"{'31 de dezembro' if clock < 24 else '1º de janeiro'}  ·  {hh:02d}:{mm:02d}", f_time, MUTED)
    return im

def out(im): return im.resize((W, H), Image.LANCZOS)
if FRAMES_ONLY:
    for sec in [26.0, T2 + 4, T2 + 9, T3 + 4]:
        out(frame(int(sec * FPS))).save(f"{OUT}/v3_{sec:05.1f}.png")
    print("total", N / FPS)
else:
    import imageio_ffmpeg
    p = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", OUT],
                         stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for fi in range(N): p.stdin.write(out(frame(fi)).tobytes())
    p.stdin.close(); p.wait(); print("ok", OUT, N, "quadros", f"{N / FPS:.1f}s")
