"""Projeto Vênus — vídeo "A virada do ano" (conscientização sobre a violência contra a mulher).

Uso:
  python -I relogio.py <pasta_data> <saida.mp4> --stories   # layout Stories (o vídeo publicado)
  python -I relogio.py <pasta_data> <saida.mp4>             # layout Reel
  python -I relogio.py <pasta_data> <pasta_png> --frames    # só alguns quadros de teste

Dados: SIM/DATASUS (óbitos femininos por agressão, CID-10 X85-Y09), no recorte do projeto Flor de Aço.
- Texto final (dia inteiro): todos os registros 1996-2025, sem duplicatas exatas.
- Relógios: só registros com hora do óbito (campo existe a partir de 2006).
  Em cima, a virada (31/12 18h -> 1/1 6h), somando 2006-2025. Embaixo, noite comum = média dos dias do ano.
- Cada mulher da madrugada de 1/1 aparece no minuto registrado do óbito. Nada que identifique alguém é mostrado.
"""
import sys, math, subprocess
import numpy as np, pandas as pd
from PIL import Image, ImageDraw, ImageFont

DATA, OUT = sys.argv[1], sys.argv[2]
FRAMES_ONLY = "--frames" in sys.argv
STORIES = "--stories" in sys.argv   # layout com área segura do Stories

# ---------------- dados ----------------
s = pd.read_parquet(f"{DATA}/datasus_sim/proxy_sim_feminicidio.parquet").drop_duplicates()
s["dt"] = pd.to_datetime(s.DT_OBITO, format="%d%m%Y", errors="coerce")
s = s[s.dt.dt.year.between(1996, 2025)]
_nd = (pd.Timestamp("2025-12-31") - pd.Timestamp("1996-01-01")).days + 1
DIA_MEDIA = len(s) / _nd                                            # dia qualquer, 1996-2025
JAN1_MEDIA = (s.dt.dt.strftime("%m-%d") == "01-01").sum() / 30      # 1º de janeiro, 1996-2025
PCT = round(100 * (JAN1_MEDIA / DIA_MEDIA - 1))
ANUAL = len(s) / 30                                                 # média por ano, 1996-2025

s["h"] = pd.to_numeric(s.HORA_OBITO.str[:2], errors="coerce")
s["mi"] = pd.to_numeric(s.HORA_OBITO.str[2:4], errors="coerce").fillna(0).clip(0, 59)
s = s[s.h.between(0, 23)].copy()
s["h"] = s.h.astype(int)
s["md"] = s.dt.dt.strftime("%m-%d")
ANO_INI, ANO_FIM = int(s.dt.dt.year.min()), int(s.dt.dt.year.max())
NY = ANO_FIM - ANO_INI + 1
typ = (s.groupby("h").size() / 365.25).reindex(range(24), fill_value=0).values   # noite comum (média)
dec31 = s[s.md == "12-31"].groupby("h").size().reindex(range(24), fill_value=0).values

def round_block(vals):  # maior resto: arredonda cada hora mantendo o total do bloco
    vals = np.asarray(vals, float); base = np.floor(vals).astype(int)
    falta = int(round(vals.sum())) - base.sum()
    for i in np.argsort(-(vals - base))[:falta]: base[i] += 1
    return base
typ_r = dict(zip(range(18, 24), round_block(typ[18:24]))); typ_r.update(zip(range(0, 6), round_block(typ[0:6])))
MAD_TYP = int(round(typ[0:6].sum()))

# as mulheres da madrugada de 1º de janeiro, uma por uma, em ordem de hora
UF = {11: "Rondônia", 12: "Acre", 13: "Amazonas", 14: "Roraima", 15: "Pará", 16: "Amapá", 17: "Tocantins",
      21: "Maranhão", 22: "Piauí", 23: "Ceará", 24: "Rio Grande do Norte", 25: "Paraíba", 26: "Pernambuco",
      27: "Alagoas", 28: "Sergipe", 29: "Bahia", 31: "Minas Gerais", 32: "Espírito Santo", 33: "Rio de Janeiro",
      35: "São Paulo", 41: "Paraná", 42: "Santa Catarina", 43: "Rio Grande do Sul", 50: "Mato Grosso do Sul",
      51: "Mato Grosso", 52: "Goiás", 53: "Distrito Federal"}
LOCAL = {"DOMICILIO": "em casa", "VIA PUBLICA": "na rua", "HOSPITAL": "no hospital",
         "OUTROS ESTABELECIMENTOS DE SAUDE": "em serviço de saúde", "OUTROS": "em outro local"}
RACA = {"BRANCA": "branca", "PARDA": "parda", "PRETA": "preta", "INDIGENA": "indígena", "AMARELA": "amarela"}
w = s[(s.md == "01-01") & (s.h < 6)].copy()
w["nasc"] = pd.to_datetime(w.DT_NASCIMENTO, format="%d%m%Y", errors="coerce")
def idade(r):
    if pd.isna(r["nasc"]): return None
    od, nb = r["dt"], r["nasc"]
    a = od.year - nb.year - ((od.month, od.day) < (nb.month, nb.day))
    return a if a >= 0 else None
w["idade"] = w.apply(idade, axis=1)
w = w.sort_values(["h", "mi", "dt"]).reset_index(drop=True)
WOMEN = []
for _, r in w.iterrows():
    a = r.idade
    l1 = ("idade não informada" if a is None or pd.isna(a) else ("menos de 1 ano" if a == 0 else f"{int(a)} {'ano' if a == 1 else 'anos'}"))
    if r.RACA_COR in RACA: l1 += f", {RACA[r.RACA_COR]}"
    uf = UF.get(int(str(r.COD_MUNICIPIO_OBITO)[:2]), "") if pd.notna(r.COD_MUNICIPIO_OBITO) else ""
    parts = [f"{r.h}h{int(r.mi):02d}", LOCAL.get(r.LOCAL_OCORRENCIA_OBITO, "local ignorado")]
    if uf: parts.append(uf)
    parts.append(str(r["dt"].year))
    WOMEN.append((r.h, int(r.mi), l1, "  ·  ".join(parts)))
MAD_OBS = len(WOMEN)
SEQ_B = [(h, int(typ_r[h])) for h in list(range(18, 24)) + list(range(0, 6))]
print(f"por ano {ANUAL:.0f} | dia qualquer {DIA_MEDIA:.2f} | 1/jan {JAN1_MEDIA:.2f} | +{PCT}%")
print(f"anos {ANO_INI}-{ANO_FIM} ({NY}) | virada 0-5h: {MAD_OBS} | noite comum 0-5h: {MAD_TYP}")

# ---------------- visual ----------------
W, H, SS, FPS = 1080, 1920, 2, 30
BG = (12, 8, 10); ROSE = (244, 176, 190); ROSE_HI = (255, 204, 216); INK = (246, 238, 241)
HOT = (255, 58, 98); MUTED = (208, 198, 202); DIAL = (92, 78, 84)
F = "C:/Windows/Fonts/"
def font(name, size): return ImageFont.truetype(F + name, size * SS)
f_title = font("georgia.ttf", 62); f_q = font("georgia.ttf", 50); f_lab = font("georgiai.ttf", 42)
f_time = font("segoeui.ttf", 30); f_small = font("segoeui.ttf", 28); f_num = font("georgia.ttf", 26)
f_end = font("segoeui.ttf", 36); f_tag = font("segoeui.ttf", 26); f_src = font("segoeui.ttf", 22)
f_exp = font("georgia.ttf", 46); f_who = font("georgia.ttf", 40); f_who2 = font("segoeui.ttf", 28)

if STORIES:  # conteúdo entre y=250 e y=1584 (topo e pé ficam sob a interface do Instagram)
    R0 = 150; COLS, GAP0, ROWSTEP, DOT = 6, 16, 11.5, 3.4
    CLOCK_A = (540, 662); CLOCK_B = (540, 1192)
    f_num = font("georgia.ttf", 20); f_hot = font("georgia.ttf", 40); f_fin = f_small
    L = dict(tag=268, labA=318, labB=900, subB=950, time=370, src_exp=1500, tick=(9, 4), num=(26, 13),
             r_cur=4.6, r_hot=5.2, r_bhold=4.0, hand=5, hub=5, arc=((4, 1), 14, 1.2),
             fin=(1398, 1434, 1472, 1530, 1555))
else:        # Reel, tela cheia
    R0 = 205; COLS, GAP0, ROWSTEP, DOT = 6, 22, 15.5, 4.4
    CLOCK_A = (540, 700); CLOCK_B = (540, 1400)
    f_hot = font("georgia.ttf", 50); f_fin = f_end
    L = dict(tag=110, labA=172, labB=1040, subB=1090, time=224, src_exp=1760, tick=(12, 5), num=(36, 17),
             r_cur=6.0, r_hot=7.0, r_bhold=5.0, hand=6, hub=7, arc=((5, 1), 18, 1.4),
             fin=(1680, 1724, 1776, 1858, 1884))

def pol(c, r, h):  # relógio de 12h: 12 no topo, sentido horário
    a = (h % 12) / 12 * 2 * math.pi
    return c[0] + r * math.sin(a), c[1] - r * math.cos(a)
def dot_pos(c, h, i):
    row, col = divmod(i, COLS)
    return pol(c, R0 + GAP0 + row * ROWSTEP, h + (col + 0.5) / COLS)
def S(v): return v * SS
def text_c(d, y, txt, f, fill, x=540):
    tw = d.textlength(txt, font=f); d.text((S(x) - tw / 2, S(y)), txt, font=f, fill=fill)
def blend(c, a): return tuple(int(BG[k] + (c[k] - BG[k]) * a) for k in range(3))
def mix(c1, c2, a): return tuple(int(c1[k] + (c2[k] - c1[k]) * a) for k in range(3))
def tag(d):
    text_c(d, L["tag"], "FLOR DE AÇO  ·  conscientização sobre a violência contra a mulher", f_tag, ROSE)
FONTE = "Dados: SIM/DATASUS, Ministério da Saúde  ·  análise própria Flor de Aço"
def blank():
    im = Image.new("RGB", (S(W), S(H)), BG); d = ImageDraw.Draw(im); tag(d); return im, d

def draw_dial(d, c):
    cx, cy = c
    d.ellipse([S(cx - R0), S(cy - R0), S(cx + R0), S(cy + R0)], outline=DIAL, width=S(3))
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
text_c(bd, L["subB"], "média dos dias do ano", f_small, MUTED)

# ---------------- linha do tempo ----------------
T_HOOK, T_EXP, T_PAUSE, T_SWEEP, T_HOLD, T_HELP = 8.5, 18.0, 1.0, 15.0, 8.5, 8.0
T1 = T_HOOK + T_EXP            # relógios aparecem
T2 = T1 + T_PAUSE              # começam a andar (18h)
T3 = T2 + T_SWEEP              # fim da volta (6h)
T4 = T3 + T_HOLD               # cartão de ajuda
N = int((T4 + T_HELP) * FPS)
# cada mulher da madrugada aparece quando o relógio chega na hora e minuto em que ela morreu
t_w = [T2 + (6 + h + m / 60) / 12 * T_SWEEP for h, m, _, _ in WOMEN]
KN_T = [T2, T3]; KN_C = [0.0, 12.0]
def clock_el(t): return float(np.interp(t, KN_T, KN_C))
# posições dos pontos da virada
EVE_A = []  # antes da meia-noite (31/12)
for k, h in enumerate(range(18, 24)):
    n = int(dec31[h])
    for i in range(n): EVE_A.append((k + (i + 0.5) / max(n, 1), h, i))
POS_W = []; cnt = {}
for h, m, _, _ in WOMEN:
    POS_W.append((h, cnt.get(h, 0))); cnt[h] = cnt.get(h, 0) + 1
EV_B = []
for k, (h, n) in enumerate(SEQ_B):
    for i in range(n): EV_B.append((k + (i + 0.5) / max(n, 1), k, h, i))

HOOK = [("Você sabia que as primeiras", INK), ("seis horas do ano são", INK),
        ("as mais letais para", ROSE), ("as mulheres no Brasil?", ROSE)]
EXP = [  # (início em s dentro da explicação, linhas, cor)
    (0.3, ["Enquanto o país conta os segundos", "para a meia-noite,", "estes relógios contam outra coisa."], INK),
    (4.6, ["Em cima, a virada do ano.", "Embaixo, uma noite comum."], INK),
    (7.6, ["Vinte anos de registros", "numa noite só."], MUTED),
    (10.4, ["Cada ponto é uma mulher", "morta por agressão."], ROSE),
    (13.2, ["Nenhuma viu o dia amanhecer."], ROSE),
    (15.6, ["Respire fundo."], INK),
]

def frame(fi):
    t = fi / FPS
    if t < T_HOOK:  # gancho
        im, d = blank()
        out_a = min(1, (T_HOOK - t) / 0.5)
        text_c(d, 680, "O ano está acabando.", f_title, blend(INK, min(1, t / 0.6) * out_a))
        a2 = max(0, min(1, (t - 2.0) / 0.8)) * out_a
        for i, (txt, c) in enumerate(HOOK):
            text_c(d, 820 + i * 66, txt, f_q, blend(c, a2))
        a3 = max(0, min(1, (t - 3.6) / 0.8)) * out_a
        text_c(d, 1130, "Fonte: declarações de óbito do Ministério da Saúde", f_small, blend(MUTED, a3))
        text_c(d, 1172, "(SIM/DATASUS), 1996–2025", f_small, blend(MUTED, a3))
        return im
    if t < T1:  # explicação em tela preta
        im, d = blank(); te = t - T_HOOK; out_a = min(1, (T_EXP - te) / 0.6)
        y = 400
        for t0, lines, c in EXP:
            a = max(0, min(1, (te - t0) / 0.7)) * out_a
            for ln in lines:
                text_c(d, y, ln, f_exp, blend(c, a)); y += 62
            y += 46
        text_c(d, L["src_exp"], "Fonte: declarações de óbito do Ministério da Saúde (SIM/DATASUS)", f_tag, blend(MUTED, out_a))
        return im
    if t >= T4:  # cartão de ajuda
        im, d = blank(); a = min(1, (t - T4) / 0.8)
        text_c(d, 640, "Se você ou alguém próxima precisa de ajuda:", f_end, blend(INK, a))
        text_c(d, 740, "Ligue 180", f_title, blend(ROSE, a))
        text_c(d, 830, "Central de Atendimento à Mulher", f_end, blend(INK, a))
        text_c(d, 878, "gratuito · 24 horas · sigiloso", f_end, blend(MUTED, a))
        text_c(d, 990, "WhatsApp: (61) 99610-0180", f_q, blend(INK, a))
        text_c(d, 1070, "Emergência: 190", f_q, blend(INK, a))
        return im
    # relógios
    im = base.copy()
    fade_in = min(1, (t - T1) / 0.6)
    if fade_in < 1: im = Image.blend(Image.new("RGB", im.size, BG), im, fade_in)
    d = ImageDraw.Draw(im)
    el = clock_el(t)
    hold = t >= T3
    cur_eve = min(int(el), 5)
    # virada, antes da meia-noite
    for e, h, i in EVE_A:
        if e <= el:
            x, y = dot_pos(CLOCK_A, h, i)
            if not hold and el < 6 and h - 18 == cur_eve:
                a = min(1, (el - e) / 0.25); r, col = L['r_cur'] * (0.6 + 0.4 * a), blend(ROSE_HI, a)
            else: r, col = DOT, blend(ROSE, 0.5)
            d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=col)
    # virada, depois da meia-noite: uma por uma
    cur_w = -1
    for i, (tw_, (h, j)) in enumerate(zip(t_w, POS_W)):
        if t >= tw_:
            cur_w = i
            a = 1 if hold else min(1, (t - tw_) / 0.35)
            x, y = dot_pos(CLOCK_A, h, j); r = L['r_hot'] * (1 + 0.9 * (1 - a))
            d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=mix(INK, HOT, a))
    # noite comum
    for e, k, h, i in EV_B:
        if e <= el:
            x, y = dot_pos(CLOCK_B, h, i)
            if hold: r, col = (L['r_bhold'], ROSE) if h < 6 else (DOT, blend(ROSE, 0.45))
            elif k == min(int(el), 11):
                a = min(1, (el - e) / 0.25); r, col = L['r_cur'] * (0.6 + 0.4 * a), blend(ROSE_HI, a)
            else: r, col = DOT, blend(ROSE, 0.6)
            d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=col)
    for c in (CLOCK_A, CLOCK_B):  # ponteiros
        clock = 18 + el
        hx, hy = pol(c, R0 * 0.45, clock); d.line([S(c[0]), S(c[1]), S(hx), S(hy)], fill=INK, width=S(L['hand']))
        mx, my = pol(c, R0 * 0.70, (clock % 1) * 12); d.line([S(c[0]), S(c[1]), S(mx), S(my)], fill=INK, width=S(2))
        hb = L['hub']; d.ellipse([S(c[0] - hb), S(c[1] - hb), S(c[0] + hb), S(c[1] + hb)], fill=INK)
    clock = 18 + el; hh = int(clock) % 24; mm = int((clock % 1) * 60)
    date = "31 de dezembro" if clock < 24 else "1º de janeiro"
    text_c(d, L["time"], f"{date}  ·  {hh:02d}:{mm:02d}", f_time, MUTED)
    if hold:
        a = min(1, (t - T3) / 1.0)
        (ra, rb), aoff, ad = L['arc']
        for c, rows in ((CLOCK_A, ra), (CLOCK_B, rb)):
            for k in range(61):  # arco pontilhado 0h-6h
                x, y = pol(c, R0 + GAP0 + rows * ROWSTEP + aoff, k / 10)
                d.ellipse([S(x - ad), S(y - ad), S(x + ad), S(y + ad)], fill=blend(INK, a))
        y1, y2, y3, y4, y5 = L["fin"]
        text_c(d, y1, f"Por ano, cerca de {round(ANUAL / 1000)} mil mulheres são mortas", f_fin, blend(INK, a))
        text_c(d, y2, f"por agressão no Brasil: {round(DIA_MEDIA)} por dia, em média.", f_fin, blend(INK, a))
        text_c(d, y3, f"No 1º de janeiro, {round(JAN1_MEDIA)}: {PCT}% a mais.", f_hot, blend(HOT, a))
        text_c(d, y4, "Fonte: declarações de óbito do Ministério da Saúde (SIM/DATASUS), 1996–2025.", f_src, blend(MUTED, a))
        text_c(d, y5, f"Análise própria, projeto Flor de Aço. Relógios: mortes com hora registrada, {ANO_INI}–{ANO_FIM}.", f_src, blend(MUTED, a))
    return im

def out(im): return im.resize((W, H), Image.LANCZOS)

if FRAMES_ONLY:
    secs = [3.5, 14.0, T2 + 15, T3 + 3, T4 + 3]
    for sec in secs:
        out(frame(int(sec * FPS))).save(f"{OUT}/f_{sec:05.1f}.png")
    print("T3", T3, "total", N / FPS)
else:
    import imageio_ffmpeg
    p = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", OUT],
                         stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for fi in range(N):
        p.stdin.write(out(frame(fi)).tobytes())
    p.stdin.close(); p.wait(); print("ok", OUT, N, "quadros", f"{N / FPS:.1f}s")
