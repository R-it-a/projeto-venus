"""Projeto Vênus — vídeo "A virada do ano" v2: mortes (vermelho) e agressões por parceiro (amarelo).

Uso:
  python -I relogio_v2.py <numeros.json> <saida.mp4>            # vídeo (layout Stories, 9:16, até 60 s)
  python -I relogio_v2.py <numeros.json> <pasta_png> --frames   # só alguns quadros de teste

Os números vêm de estudo/numeros.py (arquivos oficiais do DATASUS):
- Pontos vermelhos: mulheres mortas por agressão (SIM, CID-10 X85-Y09), com hora do óbito registrada,
  somando as viradas de 2016 a 2024. 1 ponto = 1 mulher.
- Pontos amarelos: agressões contra mulheres por parceiro ou ex notificadas em serviços de saúde (SINAN),
  só notificações feitas no dia da agressão ou no seguinte, com hora registrada, viradas de 2016 a 2024.
  1 ponto = 10 agressões.
- Relógio de baixo: noite comum = média dos dias do ano, na mesma base (mesmos 9 anos).
- Dentro de cada hora os pontos são distribuídos por igual (não é o minuto exato).
"""
import sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

NUM, OUT = sys.argv[1], sys.argv[2]
FRAMES_ONLY = "--frames" in sys.argv
R = json.load(open(NUM, encoding="utf-8"))
SIM, SIN = R["sim_mulheres_relogio_2016_2024"], R["sinan_mulheres_parceiro"]["virada_por_hora_2016_2024"]
HOURS = list(range(18, 24)) + list(range(6))
def round_block(vals):  # maior resto: arredonda mantendo o total
    vals = np.asarray(vals, float); base = np.floor(vals).astype(int)
    for i in np.argsort(-(vals - base))[:int(round(vals.sum())) - base.sum()]: base[i] += 1
    return base.tolist()
def split(v): return round_block(v[:6]) + round_block(v[6:])
RED_A = SIM["31dez"] + SIM["1jan"];            RED_B = split(SIM["comum"])
YEL_A = split([v / 10 for v in SIN["31dez"] + SIN["1jan"]]); YEL_B = split([v / 10 for v in SIN["comum"]])
SM, SP = R["sim_mulheres"], R["sinan_mulheres_parceiro"]
print("vermelho virada/comum:", RED_A, RED_B, "| amarelo:", YEL_A, YEL_B)
print("madrugada: vermelho", sum(RED_A[6:]), "vs", sum(RED_B[6:]), "| amarelo", sum(YEL_A[6:]), "vs", sum(YEL_B[6:]))

# ---------------- visual ----------------
W, H, SS, FPS = 1080, 1920, 2, 30
BG = (12, 8, 10); INK = (246, 238, 241); MUTED = (208, 198, 202); DIAL = (92, 78, 84)
RED = (255, 58, 98); YEL = (255, 196, 64); ROSE = (244, 176, 190)
F = "C:/Windows/Fonts/"
def font(name, size): return ImageFont.truetype(F + name, size * SS)
f_title = font("georgia.ttf", 62); f_q = font("georgia.ttf", 50); f_lab = font("georgiai.ttf", 40)
f_time = font("segoeui.ttf", 30); f_small = font("segoeui.ttf", 28); f_num = font("georgia.ttf", 20)
f_end = font("segoeui.ttf", 36); f_tag = font("segoeui.ttf", 26); f_src = font("segoeui.ttf", 21)
f_exp = font("georgia.ttf", 44); f_fin = font("segoeui.ttf", 30); f_hot = font("georgia.ttf", 38)
f_leg = font("segoeui.ttf", 20)
# área segura do Stories: conteúdo entre y=250 e y=1584
R0 = 140; COLS, GAP0, ROWSTEP, DOT = 6, 16, 11.5, 3.6
CLOCK_A = (540, 650); CLOCK_B = (540, 1186)
L = dict(tag=268, labA=314, labB=893, subB=940, time=360, tick=(9, 4), num=(24, 12), hand=5, hub=5)

def pol(c, r, h):
    a = (h % 12) / 12 * 2 * math.pi
    return c[0] + r * math.sin(a), c[1] - r * math.cos(a)
def dot_pos(c, h, i):
    row, col = divmod(i, COLS)
    return pol(c, R0 + GAP0 + row * ROWSTEP, h + (col + 0.5) / COLS)
def S(v): return v * SS
def text_c(d, y, txt, f, fill, x=540):
    tw = d.textlength(txt, font=f); d.text((S(x) - tw / 2, S(y)), txt, font=f, fill=fill)
def text_rich(d, y, parts, f):  # [(texto, cor), ...] centralizado numa linha
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

base = Image.new("RGB", (S(W), S(H)), BG); bd = ImageDraw.Draw(base)
tag(bd); draw_dial(bd, CLOCK_A); draw_dial(bd, CLOCK_B)
text_c(bd, L["labA"], "A virada do ano", f_lab, INK)
text_c(bd, L["labB"], "Uma noite comum", f_lab, INK)
text_c(bd, L["subB"], "média dos dias do ano · só registros com hora", f_small, MUTED)
# legenda fixa: o amarelo tem outra escala
_lw = bd.textlength("●  1 mulher morta        ○  10 atendimentos (parceiro/ex)", font=f_leg)
_x = S(540) - _lw / 2
bd.ellipse([_x, S(406), _x + S(10), S(416)], fill=RED)
bd.text((_x + S(18), S(399)), "1 mulher morta", font=f_leg, fill=INK)
_x2 = _x + bd.textlength("●  1 mulher morta        ", font=f_leg)
bd.ellipse([_x2, S(406), _x2 + S(10), S(416)], outline=YEL, width=3)
bd.text((_x2 + S(18), S(399)), "10 atendimentos (parceiro/ex)", font=f_leg, fill=INK)

# ---------------- linha do tempo ----------------
T_HOOK, T_EXP, T_PAUSE, T_SWEEP, T_HOLD, T_HELP = 8.0, 20.0, 0.8, 14.0, 9.5, 7.0
T1 = T_HOOK + T_EXP; T2 = T1 + T_PAUSE; T3 = T2 + T_SWEEP; T4 = T3 + T_HOLD
N = int((T4 + T_HELP) * FPS)
def el_at(t): return float(np.interp(t, [T2, T3], [0.0, 12.0]))   # horas decorridas desde 18h
# eventos: (instante em horas desde 18h, relógio, hora, índice na pilha, cor)
def events(clock, reds, yels):
    ev = []
    for k, h in enumerate(HOURS):
        n_r, n_y = reds[k], yels[k]; tot = n_r + n_y
        order = ["r"] * n_r + ["y"] * n_y   # vermelho por dentro, amarelo por fora
        for i, c in enumerate(order):
            ev.append((k + (i + 0.5) / max(tot, 1), clock, h, i, c))
    return ev
EV = events(CLOCK_A, RED_A, YEL_A) + events(CLOCK_B, RED_B, YEL_B)

HOOK = [("Você sabia que o 1º de janeiro", INK), ("é o dia do ano com mais", INK),
        ("mulheres mortas por", ROSE), ("agressão no Brasil?", ROSE)]
EXP = [  # (início em s, linhas, cor)
    (0.3, ["Estes relógios mostram a noite", "de 31 de dezembro para 1º de janeiro."], INK),
    (4.0, ["Em cima, a virada do ano.", "Embaixo, uma noite comum."], INK),
    (6.8, ["Nove viradas, de 2016 a 2024,", "numa noite só."], MUTED),
    (9.6, [[("Cada ponto ", INK), ("vermelho", RED), (" é uma mulher", INK)], "morta por agressão, na hora do óbito."], INK),
    (13.2, [[("Cada anel ", INK), ("amarelo", YEL), (" são dez atendimentos", INK)], "na saúde por agressão", "de parceiro ou ex."], INK),
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
        text_c(d, 1150, "(SIM/DATASUS), 1996–2025", f_small, blend(MUTED, a3))
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
    for e, c, h, i, col in EV:
        if e > el: continue
        x, y = dot_pos(c, h, i); C = RED if col == "r" else YEL
        mad = h < 6
        if hold: r, fc = (DOT + 0.8, C) if mad else (DOT, blend(C, 0.45))
        elif HOURS.index(h) == cur:
            a = min(1, (el - e) / 0.25); r, fc = (DOT + 1.6) * (0.6 + 0.4 * a) * (1.25 if c == CLOCK_A and mad else 1), C
        else: r, fc = DOT, blend(C, 0.7)
        if col == "r": d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=fc)
        else: d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], outline=fc, width=3)  # anel = 10 atendimentos
    for c in (CLOCK_A, CLOCK_B):
        clock = 18 + el
        hx, hy = pol(c, R0 * 0.45, clock); d.line([S(c[0]), S(c[1]), S(hx), S(hy)], fill=INK, width=S(L['hand']))
        mx, my = pol(c, R0 * 0.70, (clock % 1) * 12); d.line([S(c[0]), S(c[1]), S(mx), S(my)], fill=INK, width=S(2))
        hb = L['hub']; d.ellipse([S(c[0] - hb), S(c[1] - hb), S(c[0] + hb), S(c[1] + hb)], fill=INK)
    clock = 18 + el; hh = int(clock) % 24; mm = int((clock % 1) * 60)
    text_c(d, L["time"], f"{'31 de dezembro' if clock < 24 else '1º de janeiro'}  ·  {hh:02d}:{mm:02d}", f_time, MUTED)
    if hold:
        a = min(1, (t - T3) / 1.0)
        for c in (CLOCK_A, CLOCK_B):  # arco pontilhado da madrugada (0h-6h), por fora dos pontos
            rows = max((sum(1 for e_, cc, h, i, _ in EV if cc == c and h == hr) - 1) // COLS for hr in range(6)) + 1
            for k in range(61):
                x, y = pol(c, R0 + GAP0 + rows * ROWSTEP + 6, k / 10)
                d.ellipse([S(x - 1.2), S(y - 1.2), S(x + 1.2), S(y + 1.2)], fill=blend(INK, a))
        j = SM["jan1_2016_2024"]["pct"]
        text_c(d, 1394, "No 1º de janeiro, de 2016 a 2024:", f_fin, blend(INK, a))
        text_rich(d, 1430, [("mortes de mulheres por agressão ", blend(INK, a)), (f"+{j}%", blend(RED, a))], f_hot)
        text_rich(d, 1478, [("atendimentos por agressão de parceiro/ex: ", blend(INK, a)), ("cerca do dobro", blend(YEL, a))], f_fin)
        text_c(d, 1518, f"Suspeita de álcool pelo agressor: {SP['alcool_jan1']}% dos casos informados, contra {SP['alcool_dia_util']}% num dia útil.", f_src, blend(INK, a))
        text_c(d, 1548, "Fontes: SIM e SINAN/DATASUS, Ministério da Saúde · análise: Rita Farias", f_src, blend(MUTED, a))
    return im

def out(im): return im.resize((W, H), Image.LANCZOS)
if FRAMES_ONLY:
    for sec in [4.0, 26.0, T2 + 9, T3 + 4, T4 + 3]:
        out(frame(int(sec * FPS))).save(f"{OUT}/v2_{sec:05.1f}.png")
    print("total", N / FPS)
else:
    import imageio_ffmpeg
    p = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", OUT],
                         stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for fi in range(N): p.stdin.write(out(frame(fi)).tobytes())
    p.stdin.close(); p.wait(); print("ok", OUT, N, "quadros", f"{N / FPS:.1f}s")
