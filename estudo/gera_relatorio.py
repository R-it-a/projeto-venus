"""Projeto Vênus — gera o relatório (HTML para imprimir em PDF) a partir de numeros.json.
Uso: python -I gera_relatorio.py <numeros.json> <saida.html>"""
import sys, json, html
R = json.load(open(sys.argv[1], encoding="utf-8"))
SM, SH = R["sim_mulheres"], R["sim_homens"]
P, PH = R["sinan_mulheres_parceiro"], R["sinan_homens_parceiro"]
MT, HT, MD, MP = R["sinan_mulheres_todas"], R["sinan_homens_todas"], R["sinan_mulheres_desconhecido"], R["sinan_mulheres_pai_mae"]
def n(x, d=0):
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s
def pct(x): return f"{'+' if x > 0 else '−' if x < 0 else ''}{abs(x)}%"
def ic(e): return f"{pct(e['ic'][0])} a {pct(e['ic'][1])}"

# ---------- gráficos SVG ----------
RED, YEL, GRY, INK = "#d6334f", "#c98a00", "#9a9297", "#222"
def bars_hours(title, a, b, la, lb, ca, unit=""):
    hrs = ["18h", "19h", "20h", "21h", "22h", "23h", "0h", "1h", "2h", "3h", "4h", "5h"]
    W, H, L, B, T = 640, 270, 46, 34, 48; mx = max(max(a), max(b)) * 1.12; bw = (W - L - 10) / 12
    s = [f'<svg viewBox="0 0 {W} {H}" class="chart"><text x="{L}" y="16" class="ct">{html.escape(title)}</text>']
    for k in range(5):
        v = mx * k / 4; y = H - B - (H - B - T) * k / 4
        s.append(f'<line x1="{L}" x2="{W-10}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e6e1e3"/><text x="{L-6}" y="{y+4:.1f}" class="ax" text-anchor="end">{n(v)}</text>')
    for i in range(12):
        x = L + i * bw; ha = (H - B - T) * a[i] / mx; hb = (H - B - T) * b[i] / mx
        s.append(f'<rect x="{x+bw*0.12:.1f}" y="{H-B-ha:.1f}" width="{bw*0.38:.1f}" height="{ha:.1f}" fill="{ca}"/>')
        s.append(f'<rect x="{x+bw*0.5:.1f}" y="{H-B-hb:.1f}" width="{bw*0.38:.1f}" height="{hb:.1f}" fill="{GRY}"/>')
        s.append(f'<text x="{x+bw/2:.1f}" y="{H-B+16}" class="ax" text-anchor="middle">{hrs[i]}</text>')
    s.append(f'<line x1="{L+6*bw:.1f}" x2="{L+6*bw:.1f}" y1="{T}" y2="{H-B}" stroke="{INK}" stroke-dasharray="3 3"/><text x="{L+6*bw+4:.1f}" y="{T+10}" class="ax">meia-noite</text>')
    s.append(f'<rect x="{L}" y="24" width="10" height="10" fill="{ca}"/><text x="{L+14}" y="33" class="ax">{la}</text><rect x="{L+110}" y="24" width="10" height="10" fill="{GRY}"/><text x="{L+124}" y="33" class="ax">{lb}</text>')
    return "".join(s) + "</svg>"
def bars_cat(title, rows, color, share=False):  # rows: [(rótulo, valor %)]
    W, rh, L = 640, 24, 230; H = 30 + rh * len(rows); mx = max(abs(v) for _, v in rows); mn = min(0, min(v for _, v in rows))
    z = L + (W - L - 60) * (-mn) / (mx - mn); sc = (W - L - 60) / (mx - mn)
    s = [f'<svg viewBox="0 0 {W} {H}" class="chart"><text x="0" y="16" class="ct">{html.escape(title)}</text>']
    for i, (lab, v) in enumerate(rows):
        y = 28 + i * rh; x0 = z if v >= 0 else z + v * sc; w = abs(v) * sc
        s.append(f'<text x="{min(L, x0)-8:.1f}" y="{y+15}" class="ax" text-anchor="end">{html.escape(lab)}</text><rect x="{x0:.1f}" y="{y+3}" width="{w:.1f}" height="{rh-8}" fill="{color if v>=0 else GRY}"/><text x="{(x0+w+5) if v>=0 else (z+5):.1f}" y="{y+15}" class="ax" text-anchor="start">{(str(v)+"%") if share else pct(v)}</text>')
    s.append(f'<line x1="{z:.1f}" x2="{z:.1f}" y1="24" y2="{H}" stroke="{INK}"/>')
    return "".join(s) + "</svg>"
def line_years(title, series):  # series: [(rótulo, {ano: razão}, cor)]
    W, H, L, B, T = 640, 250, 40, 30, 46
    yrs = sorted({y for _, d, _ in series for y in d}); x0, x1 = min(yrs), max(yrs); mx = max(v for _, d, _ in series for v in d.values()) * 1.1
    X = lambda y: L + (W - L - 20) * (y - x0) / (x1 - x0); Y = lambda v: H - B - (H - B - T) * v / mx
    s = [f'<svg viewBox="0 0 {W} {H}" class="chart"><text x="{L}" y="16" class="ct">{html.escape(title)}</text>']
    for k in range(0, int(mx) + 1):
        s.append(f'<line x1="{L}" x2="{W-20}" y1="{Y(k):.1f}" y2="{Y(k):.1f}" stroke="{"#999" if k==1 else "#e6e1e3"}"/><text x="{L-6}" y="{Y(k)+4:.1f}" class="ax" text-anchor="end">{k}x</text>')
    for y in yrs[::2] if len(yrs) > 16 else yrs:
        s.append(f'<text x="{X(y):.1f}" y="{H-B+16}" class="ax" text-anchor="middle">{y}</text>')
    for j, (lab, d, c) in enumerate(series):
        pts = " ".join(f"{X(y):.1f},{Y(v):.1f}" for y, v in sorted(d.items()))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2"/>' + "".join(f'<circle cx="{X(y):.1f}" cy="{Y(v):.1f}" r="2.5" fill="{c}"/>' for y, v in d.items()))
        s.append(f'<rect x="{L+j*110}" y="24" width="10" height="10" fill="{c}"/><text x="{L+14+j*110}" y="33" class="ax">{lab}</text>')
    return "".join(s) + "</svg>"

va, vb = SM["virada_por_hora_2006_2025"], P["virada_por_hora_2016_2024"]
g1 = bars_hours("Mulheres mortas por agressão, por hora (SIM, soma das viradas 2006–2025)", va["31dez"] + va["1jan"], va["comum"], "virada", "noite comum", RED)
g2 = bars_hours("Agressões a mulheres por parceiro/ex, por hora (SINAN, soma das viradas 2016–2024)", vb["31dez"] + vb["1jan"], vb["comum"], "virada", "noite comum", YEL)
g3 = bars_cat("SINAN 2016–2024: aumento no 1º de janeiro, por quem agrediu a mulher", [("Parceiro ou ex", P["jan1"]["pct"]), ("Desconhecido", MD["jan1"]["pct"]), ("Todas as agressões", MT["jan1"]["pct"]), ("Pai ou mãe", MP["jan1"]["pct"])], YEL)
def ratio(aa): return {int(y): round(v["jan1"] / (v["total"] / 365.25), 2) for y, v in aa.items()}
g4 = line_years("1º de janeiro ÷ dia médio do ano (SIM, 1996–2025)", [("mulheres", ratio(SM["ano_a_ano"]), RED), ("homens", ratio(SH["ano_a_ano"]), GRY)])
g5 = bars_cat("Suspeita de uso de álcool pelo agressor parceiro/ex (% entre informados)", [("Dia comum", P["alcool_comum"]), ("Domingos", P["alcool_domingo"]), ("Natal", P["alcool_natal"]), ("1º de janeiro", P["alcool_jan1"])], YEL, share=True)

FBSP = [(2016, 4245, 929), (2017, 4556, 1075), (2018, 4340, 1229), (2019, 3966, 1330), (2020, 3999, 1354), (2021, 3869, 1347), (2022, 3934, 1455), (2023, 3937, 1475), (2024, 3728, 1504), (2025, 3539, 1571)]
anos = "".join(f"<tr><td>{y}</td><td>{n(v['total'])}</td><td>{v['jan1']}</td><td>{v['natal']}</td><td>{n(SH['ano_a_ano'][y]['total'])}</td><td>{SH['ano_a_ano'][y]['jan1']}</td><td>{SH['ano_a_ano'][y]['natal']}</td></tr>" for y, v in SM["ano_a_ano"].items())
sinan_anos = "".join(f"<tr><td>{y}</td><td>{n(v['media_dia'],1)}</td><td>{v['jan1']}</td><td>{n(v['jan1']/v['media_dia'],1)}x</td></tr>" for y, v in P["ano_a_ano_jan1"].items())
fb = "".join(f"<tr><td>{a}</td><td>{n(h)}</td><td>{n(f)}</td><td>{round(100*f/h)}%</td></tr>" for a, h, f in FBSP)

AUD = open(sys.argv[3], encoding="utf-8").read() if len(sys.argv) > 3 else "<p><i>(auditoria em andamento)</i></p>"

HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Projeto Vênus — Violência contra a mulher no Natal e no Ano Novo</title>
<style>
@page {{ size: A4; margin: 18mm 17mm 18mm 17mm; }}
body {{ font-family: Georgia, serif; color:#222; font-size:10.6pt; line-height:1.48; }}
h1 {{ font-size:25pt; line-height:1.15; margin:0 0 6px; color:#7a1430; }}
h2 {{ font-size:15pt; color:#7a1430; border-bottom:1px solid #e3cbd2; padding-bottom:3px; margin-top:26px; page-break-after:avoid; }}
h3 {{ font-size:11.5pt; margin:16px 0 4px; page-break-after:avoid; }}
p, li {{ text-align: left; }}
table {{ border-collapse:collapse; width:100%; font-family: "Segoe UI", sans-serif; font-size:8.8pt; margin:6px 0 10px; page-break-inside:avoid; }}
th, td {{ border-bottom:1px solid #e6e1e3; padding:3px 6px; text-align:right; }}
th:first-child, td:first-child {{ text-align:left; }}
th {{ background:#f6eef1; }}
.chart {{ width:100%; font-family:"Segoe UI",sans-serif; margin:8px 0 4px; page-break-inside:avoid; }}
.ct {{ font-size:12px; font-weight:600; fill:#222; }} .ax {{ font-size:10px; fill:#555; }}
.box {{ background:#f8f3f5; border-left:4px solid #b02a4a; padding:8px 12px; margin:10px 0; page-break-inside:avoid; }}
.ok {{ border-left-color:#2e7d32; background:#f2f8f2; }} .no {{ border-left-color:#c62828; background:#fbf1f1; }}
.small {{ font-size:8.6pt; color:#555; }} .cover {{ page-break-after:always; padding-top:120px; }}
.key {{ font-family:"Segoe UI",sans-serif; font-size:9.5pt; }}
a {{ color:#7a1430; word-break: break-all; }}
.pb {{ page-break-before:always; }}
.txt th, .txt td {{ text-align:left; vertical-align:top; }}
</style></head><body>
<div class="cover">
<p class="small">PROJETO VÊNUS · conscientização sobre a violência contra a mulher</p>
<h1>A noite mais violenta do ano</h1>
<p style="font-size:14pt">Mortes e agressões de mulheres no Natal e no Ano Novo no Brasil, comparadas às dos homens</p>
<p style="margin-top:40px">Análise e visualização: <b>Rita Farias</b><br>Relatório técnico · novembro de 2026</p>
<p class="small" style="margin-top:80px">Fontes: Sistema de Informações sobre Mortalidade (SIM) e Sistema de Informação de Agravos de Notificação (SINAN), Ministério da Saúde/DATASUS — microdados oficiais baixados diretamente do DATASUS; Anuário Brasileiro de Segurança Pública 2026 (Fórum Brasileiro de Segurança Pública). Todos os números deste relatório foram recalculados a partir dos arquivos originais e conferidos por uma auditoria independente. Código e dados de reprodução: github.com/R-it-a/projeto-venus</p>
</div>

<h2>Resumo</h2>
<p>O estudo separa três coisas diferentes, que costumam ser confundidas: <b>mortes de mulheres por agressão</b> (todos os assassinatos de mulheres), <b>agressões contra mulheres</b> (atendidas na saúde, quase sempre não fatais) e <b>feminicídio</b> (assassinato de mulher por ser mulher, segundo a polícia).</p>
<div class="box key">
<b>A. Mortes de mulheres por agressão (SIM, 1996–2025)</b><br>
O 1º de janeiro é o dia do ano com mais mulheres assassinadas: em média {n(SM['jan1']['media'],1)}, contra {n(SM['por_dia'],1)} num dia comum (<b>{pct(SM['jan1']['pct'])}</b>; IC 95%: {pct(SM['jan1_ic_boot'][0])} a {pct(SM['jan1_ic_boot'][1])}), em todos os 30 anos. O Natal é o segundo ({pct(SM['natal']['pct'])}). O excesso se concentra na madrugada da virada. Com os homens acontece o mesmo ({pct(SH['jan1']['pct'])}): é um pico geral de violência, e as mulheres estão dentro dele. O que difere é o lugar: ao longo do ano, {n(SM['casa'],0)}% das mulheres assassinadas morrem em casa, contra {n(SH['casa'],0)}% dos homens.<br><br>
<b>B. Agressões contra mulheres atendidas na saúde (SINAN, 2016–2024)</b><br>
O 1º de janeiro também é o dia com mais mulheres atendidas por agressão ({pct(MT['jan1']['pct'])}). A agressão por parceiro ou ex, a mais comum contra mulheres adultas, fica em <b>cerca do dobro</b> ({pct(P['jan1']['pct'])}; IC 95%: {pct(P['jan1_ic_boot'][0])} a {pct(P['jan1_ic_boot'][1])}); as de desconhecidos sobem na mesma proporção. {n(P['autor_homem_pct'],0)}% dos agressores parceiros são homens. Nessas agressões de parceiro no 1º de janeiro, houve suspeita de uso de álcool pelo agressor em <b>{P['alcool_jan1']}%</b> dos casos informados, contra {P['alcool_dia_util']}% num dia útil (associação, não causa).<br><br>
<b>C. Feminicídio (Anuário Brasileiro de Segurança Pública 2026)</b><br>
Em 2025, 1.571 feminicídios, o maior número da série; 8 em cada 10 autores identificados eram companheiros ou ex. <b>Não existe dado público de feminicídio por dia</b>, então não é possível saber se ele aumenta no Natal ou no Ano Novo. A ligação com as partes A e B é indireta: o feminicídio está contido nas mortes de mulheres por agressão, e o perfil dele (parceiro, casa) é o mesmo das agressões que dobram no 1º de janeiro.
</div>

<h2>1. Pergunta e conceitos</h2>
<p>O estudo nasceu de um achado: nas declarações de óbito, o 1º de janeiro concentra quase o dobro de mortes de mulheres por agressão. A pergunta é se o Natal e o Ano Novo são de fato mais perigosos para as mulheres, se isso é diferente do que acontece com os homens, e o que os dados permitem dizer sobre violência por parceiro, feminicídio e álcool. O estudo descreve <i>quando</i> a violência acontece. Ele não explica <i>por quê</i>.</p>
<h3>Homicídio, feminicídio e agressão</h3>
<ul>
<li><b>Homicídio</b> é matar alguém, por qualquer motivo (art. 121 do Código Penal): briga, assalto, tráfico, vingança, violência doméstica.</li>
<li><b>Feminicídio</b> é matar uma mulher por razões da condição do sexo feminino: em contexto de violência doméstica e familiar, ou por menosprezo ou discriminação à condição de mulher. Entrou no Código Penal em 2015 como qualificadora do homicídio e, desde a Lei 14.994/2024, é um crime autônomo, com pena maior. Quem classifica uma morte como feminicídio é a polícia e, depois, a Justiça, ao investigar o autor e o motivo. O médico que preenche a declaração de óbito não registra isso.</li>
<li><b>Agressão</b>, neste estudo, é a violência atendida num serviço de saúde e notificada ao SINAN. Quase sempre a vítima sobrevive.</li>
</ul>
<p>Todo feminicídio é um homicídio de mulher, mas nem todo homicídio de mulher é feminicídio: em 2025, a polícia classificou 44% dos assassinatos de mulheres como feminicídio.</p>
<table class="txt"><tr><th>Parte</th><th>O que mede</th><th>Fonte</th><th>Tem o dia?</th><th>Tem o autor e o motivo?</th><th>Tem álcool?</th></tr>
<tr><td>A. Mortes por agressão</td><td>Todos os assassinatos de mulheres (inclui os feminicídios, sem separá-los)</td><td>SIM (declarações de óbito)</td><td>Sim</td><td>Não</td><td>Não</td></tr>
<tr><td>B. Agressões</td><td>Mulheres atendidas na saúde após agressão</td><td>SINAN (notificações)</td><td>Sim</td><td>O vínculo do autor, sim; o motivo, não</td><td>Suspeita, sim</td></tr>
<tr><td>C. Feminicídio</td><td>Assassinatos classificados pela polícia como feminicídio</td><td>Anuário FBSP (polícias estaduais)</td><td>Não (só total anual)</td><td>Sim (perfil anual)</td><td>Não analisado</td></tr>
</table>

<h2 class="pb">Parte A — Mortes de mulheres por agressão (SIM)</h2>
<h3>A.1 Fonte</h3>

<p>Toda morte no Brasil gera uma declaração de óbito, preenchida por um médico; em mortes violentas, normalmente pelo médico-legista do IML. As secretarias de saúde coletam as declarações, e o Ministério da Saúde publica os microdados anônimos. Usamos os arquivos de óbitos por causas externas (DOEXT96 a DOEXT25), baixados em 25/11/2026 de <a>ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DOFET/</a>.</p>
<ul>
<li><b>Recorte:</b> causa básica "agressões" da CID-10 (códigos X85 a Y09), que corresponde aos homicídios. Sexo feminino e masculino; anos de óbito de 1996 a 2025.</li>
<li><b>Campos usados:</b> data do óbito, hora do óbito (existe a partir de 2006), sexo, causa básica, local do óbito, idade, raça/cor.</li>
<li><b>Status:</b> o arquivo de 2025 também está na pasta PRELIM do DATASUS, ou seja, ainda é preliminar e pode mudar.</li>
<li><b>Sem nomes:</b> a base é anônima. Nenhum dado que identifique pessoas é usado ou mostrado.</li>
<li><b>Relação com o Flor de Aço:</b> o projeto Flor de Aço (Gabrielle Urcioli e Rafael Trindade) publicou um recorte do SIM com os óbitos femininos por agressão (Kaggle: rafatrindade/feminicidio-br). Conferimos esse recorte contra os arquivos oficiais: de 1999 a 2025, ele bate registro por registro, e de 1996 a 1998 difere em até 3 casos por ano. Todos os números deste relatório vêm dos arquivos oficiais.</li>
</ul>
<h3>A.2 Resultados</h3>
<table><tr><th></th><th>Mulheres</th><th>Homens</th></tr>
<tr><td>Mortes por agressão, 1996–2025</td><td>{n(SM['total'])}</td><td>{n(SH['total'])}</td></tr>
<tr><td>Por ano / por dia (média)</td><td>{n(SM['por_ano'])} / {n(SM['por_dia'],1)}</td><td>{n(SH['por_ano'])} / {n(SH['por_dia'],1)}</td></tr>
<tr><td><b>1º de janeiro</b> (média no dia; aumento; IC 95%)</td><td><b>{n(SM['jan1']['media'],1)}; {pct(SM['jan1']['pct'])}</b>; {ic(SM['jan1'])}</td><td><b>{n(SH['jan1']['media'],1)}; {pct(SH['jan1']['pct'])}</b>; {ic(SH['jan1'])}</td></tr>
<tr><td><b>Natal</b> (25/12)</td><td><b>{n(SM['natal']['media'],1)}; {pct(SM['natal']['pct'])}</b>; {ic(SM['natal'])}</td><td><b>{n(SH['natal']['media'],1)}; {pct(SH['natal']['pct'])}</b>; {ic(SH['natal'])}</td></tr>
<tr><td>Véspera de Natal (24/12)</td><td>{pct(SM['vespera_natal']['pct'])}</td><td>{pct(SH['vespera_natal']['pct'])}</td></tr>
<tr><td>Réveillon (31/12)</td><td>{pct(SM['reveillon']['pct'])}</td><td>{pct(SH['reveillon']['pct'])}</td></tr>
<tr><td>1º de janeiro, só 2016–2024 (período do relógio)</td><td>{pct(SM['jan1_2016_2024']['pct'])} (IC {pct(SM['jan1_2016_2024']['ic_boot'][0])} a {pct(SM['jan1_2016_2024']['ic_boot'][1])})</td><td>—</td></tr>
<tr><td>1º de janeiro comparado a um domingo médio</td><td>{pct(SM['jan1_vs_domingo'])}</td><td>—</td></tr>
<tr><td>Noite 18h→6h: virada ÷ noite comum / ÷ noite de sábado→domingo (2006–2025)</td><td>{n(SM['janela_2006_2025']['x_comum'],1)}x / {n(SM['janela_2006_2025']['x_sab'],1)}x</td><td>—</td></tr>
<tr><td>Fatia de mulheres entre as vítimas: 1/1 / resto do ano</td><td colspan="2">{n(SM['pct_mulheres_jan1_vs_resto'][0],1)}% / {n(SM['pct_mulheres_jan1_vs_resto'][1],1)}%</td></tr>
<tr><td>Madrugada 0h–6h do 1/1, soma 2006–2025 (vs noite comum)</td><td>{SM['madrugada_jan1']} vs {n(SM['madrugada_comum'],1)}</td><td>{n(SH['madrugada_jan1'])} vs {n(SH['madrugada_comum'],1)}</td></tr>
<tr><td>Madrugada 0h–6h do Natal, soma 2006–2025</td><td>{SM['madrugada_natal']}</td><td>{n(SH['madrugada_natal'])}</td></tr>
<tr><td>Morrem em casa (ano todo)</td><td>{n(SM['casa'],1)}%</td><td>{n(SH['casa'],1)}%</td></tr>
<tr><td>Faca/objeto cortante: ano todo → 1º de janeiro</td><td>{n(SM['faca'],1)}% → {n(SM['faca_jan1'],1)}%</td><td>{n(SH['faca'],1)}% → {n(SH['faca_jan1'],1)}%</td></tr>
<tr><td>Aumento do 1/1 por década: 1996–2005 / 2006–2015 / 2016–2025</td><td>{pct(SM['jan1_1996_2005'])} / {pct(SM['jan1_2006_2015'])} / {pct(SM['jan1_2016_2025'])}</td><td>{pct(SH['jan1_1996_2005'])} / {pct(SH['jan1_2006_2015'])} / {pct(SH['jan1_2016_2025'])}</td></tr>
</table>
<p><b>O que isso mostra.</b> O 1º de janeiro é a data mais letal do ano para os dois sexos, e o Natal é a segunda. As vésperas (24 e 31/12) ficam perto do normal: o excesso começa depois da meia-noite. Controlando pelo dia da semana, o aumento do 1/1 continua o mesmo (mulheres +94%; homens +92%). Mas o comparador importa: domingos já são mais violentos, e contra um domingo médio o 1/1 fica {SM['jan1_vs_domingo']}% acima; contra a madrugada de um domingo, a madrugada do 1/1 tem cerca de 2,2 vezes as mortes, e não 3,3. Parte do "1º de janeiro" é a noite de 31 que passou da meia-noite: somando 31/12 e 1/1, o excesso dos dois dias juntos é de cerca de +50%. O padrão se repetiu em todos os 30 anos, mas vem diminuindo: entre as mulheres, foi de {pct(SM['jan1_1996_2005'])} na primeira década para {pct(SM['jan1_2016_2025'])} na última.</p>
<p><b>O que isso não mostra.</b> O local da morte no 1/1 é igual ao de um dia comum (mulheres: {n(SM['casa'],1)}% em casa nos dois casos). Ou seja, não dá para dizer que "no Ano Novo as mulheres morrem mais em casa". A declaração de óbito não registra quem matou nem o motivo, então esses números não são feminicídios.</p>
{g1}
{g4}


<h2 class="pb">Parte B — Agressões contra mulheres atendidas na saúde (SINAN)</h2>
<h3>B.1 Fonte</h3>

<p>Todo serviço de saúde, público ou privado, deve notificar casos suspeitos ou confirmados de violência atendidos. A ficha registra a data e a hora da ocorrência, o local, o tipo de violência, o meio, o vínculo do provável autor com a vítima e a "suspeita de uso de álcool" pelo provável autor (1-Sim, 2-Não, 9-Ignorado). Usamos os arquivos VIOLBR09 a VIOLBR24 (dados finais), baixados em 25/11/2026 de <a>ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/DADOS/FINAIS/</a>.</p>
<ul>
<li><b>O que é:</b> são casos <b>não fatais (na maioria) que chegaram a um serviço de saúde</b>. Não é o total de agressões que acontecem: a maior parte da violência não chega à saúde.</li>
<li><b>Recorte:</b> vítimas do sexo feminino e masculino; exclui lesão autoprovocada; "parceiro ou ex" = cônjuge, ex-cônjuge, namorado(a) ou ex-namorado(a).</li>
<li><b>Período:</b> só 2016–2024, e só notificações feitas no dia da agressão ou no dia seguinte. A justificativa está na seção "Armadilhas encontradas nos dados".</li>
</ul>
<h3>B.2 Resultados</h3>
<table><tr><th>Grupo</th><th>Dia comum</th><th>1º de janeiro (média)</th><th>Aumento 1/1 (IC 95%)</th><th>Natal</th><th>2 de janeiro</th></tr>
<tr><td>Mulheres, por parceiro ou ex</td><td>{n(P['por_dia'],1)}</td><td>{n(P['jan1']['media'],0)}</td><td><b>{pct(P['jan1']['pct'])}</b> ({pct(P['jan1_ic_boot'][0])} a {pct(P['jan1_ic_boot'][1])})</td><td>{pct(P['natal']['pct'])}</td><td>{pct(P['jan2']['pct'])}</td></tr>
<tr><td>Mulheres, por desconhecido</td><td>{n(MD['por_dia'],1)}</td><td>{n(MD['jan1']['media'],0)}</td><td>{pct(MD['jan1']['pct'])} ({ic(MD['jan1'])})</td><td>{pct(MD['natal']['pct'])}</td><td>{pct(MD['jan2']['pct'])}</td></tr>
<tr><td>Mulheres, por pai ou mãe</td><td>{n(MP['por_dia'],1)}</td><td>{n(MP['jan1']['media'],0)}</td><td>{pct(MP['jan1']['pct'])}</td><td>{pct(MP['natal']['pct'])}</td><td>{pct(MP['jan2']['pct'])}</td></tr>
<tr><td>Mulheres, todas as agressões</td><td>{n(MT['por_dia'],1)}</td><td>{n(MT['jan1']['media'],0)}</td><td>{pct(MT['jan1']['pct'])}</td><td>{pct(MT['natal']['pct'])}</td><td>{pct(MT['jan2']['pct'])}</td></tr>
<tr><td>Homens, todas as agressões</td><td>{n(HT['por_dia'],1)}</td><td>{n(HT['jan1']['media'],0)}</td><td>{pct(HT['jan1']['pct'])}</td><td>{pct(HT['natal']['pct'])}</td><td>{pct(HT['jan2']['pct'])}</td></tr>
<tr><td>Homens, por parceira ou ex</td><td>{n(PH['por_dia'],1)}</td><td>{n(PH['jan1']['media'],0)}</td><td>{pct(PH['jan1']['pct'])}</td><td>{pct(PH['natal']['pct'])}</td><td>{pct(PH['jan2']['pct'])}</td></tr>
</table>
<p class="small">Contagens de notificações com data confiável (no dia da agressão ou no seguinte), cerca de {R['sinan_pct_confiavel']}% do total. O número absoluto real é maior; a comparação entre dias é o que vale. Intervalo de confiança da linha de parceiro ou ex: bootstrap reamostrando anos (o intervalo de Poisson, mais estreito, ignora a variação entre anos). Nas demais linhas, o intervalo mostrado é de Poisson e deve ser lido como estreito demais.</p>
{g3}
<p><b>O que isso mostra.</b> O 1º de janeiro é o dia do ano com mais notificações de agressão contra mulheres, e o Natal é o segundo. A agressão por parceiro ou ex fica em cerca do dobro de um dia médio ({pct(P['jan1']['pct'])}; controlando o dia da semana, entre +93% e +99% conforme o método; contra um domingo médio, {P['jan1_vs_domingo']}% acima). Não há "compensação" no dia seguinte (2 de janeiro: {pct(P['jan2']['pct'])}). A véspera fica abaixo do normal (31/12: {pct(R['sinan_31dez_parceiro']['pct'])}), inclusive à noite: todo o excesso está na madrugada do dia 1º. Na noite inteira, das 18h às 6h, a virada tem {n(P['janela']['x_comum'],1)} vezes as notificações de uma noite comum e {n(P['janela']['x_sab'],1)} vezes as de uma noite de sábado para domingo.</p>
<p><b>Cuidado: o aumento não é específico dos parceiros.</b> Agressões por desconhecidos sobem tanto quanto ({pct(MD['jan1']['pct'])}). A fatia do parceiro entre as agressões a mulheres sobe de {n(R['sinan_composicao_todas']['parceiro_pct'][1],0)}% para {n(R['sinan_composicao_todas']['parceiro_pct'][0],0)}% no 1/1, mas isso é quase todo efeito de composição: a violência contra crianças (por pai ou mãe) cai no feriado. Entre mulheres adultas, todas as agressões dobram juntas ({pct(R['sinan_composicao_adultas']['total_jan1'])}), e a fatia do parceiro quase não muda ({n(R['sinan_composicao_adultas']['parceiro_pct'][1],1)}% → {n(R['sinan_composicao_adultas']['parceiro_pct'][0],1)}%). A fatia de mulheres entre todas as vítimas também quase não muda ({n(R['sinan_pct_mulheres_jan1_vs_resto'][1],1)}% → {n(R['sinan_pct_mulheres_jan1_vs_resto'][0],1)}%). O que é específico das mulheres é o volume e o tipo de agressor: o parceiro ou ex responde por mais da metade das agressões contra mulheres adultas, e {n(P['autor_homem_pct'],0)}% desses agressores são homens. Os homens agredidos por parceira ou ex ({n(PH['por_dia'],1)} por dia, {pct(PH['jan1']['pct'])} no 1/1) são poucos casos, com possível erro de registro de sexo; não destacamos esse número.</p>
<h3>Hora, local e forma da agressão (parceiro ou ex)</h3>
{g2}
<table><tr><th></th><th>Dia comum</th><th>1º de janeiro</th></tr>
<tr><td>Madrugada 0h–6h (soma 2016–2024)</td><td>{n(P['madrugada_comum'],0)}</td><td>{P['madrugada_jan1']}</td></tr>
<tr><td>Na residência</td><td>{n(P['casa_pct']['comum'],1)}%</td><td>{n(P['casa_pct']['jan1'],1)}%</td></tr>
<tr><td>Na via pública</td><td>{n(P['via_publica_pct']['comum'],1)}%</td><td>{n(P['via_publica_pct']['jan1'],1)}%</td></tr>
<tr><td>Em bar ou similar</td><td>{n(P['bar_pct']['comum'],1)}%</td><td>{n(P['bar_pct']['jan1'],1)}%</td></tr>
<tr><td>Violência física</td><td>{n(P['fisica_pct']['comum'],1)}%</td><td>{n(P['fisica_pct']['jan1'],1)}%</td></tr>
<tr><td>Faca ou objeto perfurocortante</td><td>{n(P['faca_pct']['comum'],1)}%</td><td>{n(P['faca_pct']['jan1'],1)}%</td></tr>
</table>
<h3>Álcool</h3>
{g5}
<p>O campo é preenchido pelo profissional de saúde com base no relato e na observação; não é exame. Em {P['alcool_ign_pct']}% das agressões de parceiro ou ex ele está em branco ou "ignorado", e os percentuais acima consideram só os casos informados; essa falta de informação pode não ser aleatória. A comparação justa é com um dia útil sem feriado ({P['alcool_dia_util']}%): a média de todos os dias ({P['alcool_comum']}%) já inclui fins de semana. O aumento da suspeita de álcool no 1º de janeiro aparece em todos os grupos de agressores, inclusive contra homens (homens, todas as agressões: {HT['alcool_comum']}% num dia comum, {HT['alcool_jan1']}% no 1/1). O dado é compatível com o consumo de álcool das festas, mas mostra associação, não causa.</p>


<h2 class="pb">Parte C — Feminicídio (registros policiais)</h2>
<h3>C.1 Fonte</h3>

<p>É a fonte dos números de <b>feminicídio</b>, classificação feita pelas polícias civis estaduais a partir dos boletins de ocorrência e inquéritos. Usamos a série de homicídios de mulheres e feminicídios de 2016 a 2025 (Gráfico 35, p. 159) e o perfil das vítimas de 2025 (p. 163–169). <a>https://forumseguranca.org.br/wp-content/uploads/2026/07/anuario-2026.pdf</a>. O Anuário publica totais anuais por estado; não publica dados por dia.</p>
<h3>C.2 O que se sabe</h3>
<table><tr><th>Ano</th><th>Homicídios de mulheres (inclui feminicídios)</th><th>Feminicídios</th><th>% feminicídio</th></tr>{fb}</table>
<p class="small">Fonte: Anuário Brasileiro de Segurança Pública 2026, Gráfico 35 (secretarias estaduais de segurança pública).</p>
<p>Em 2025, segundo o Anuário: 1.571 feminicídios (recorde da série, +4% sobre 2024); 79,8% dos autores identificados eram companheiros ou ex-companheiros; 62,5% dos feminicídios ocorreram na residência; 50,8% foram cometidos com arma branca; 65,1% das vítimas eram negras; e houve 4.189 tentativas de feminicídio. O próprio Anuário registra limitações: a relação entre vítima e autor fica sem informação em 74,8% dos feminicídios, e a proporção de mortes de mulheres classificadas como feminicídio varia de 15,8% (Ceará) a quase 70% (Acre, DF, Sergipe), o que reflete também práticas de registro diferentes entre as polícias.</p>
<div class="box no"><b>Limite deste estudo:</b> o Anuário não publica dados por dia, e o SIM não registra a motivação. Por isso <b>não é possível medir se o feminicídio aumenta no Natal ou no Ano Novo</b>. O que os dados permitem dizer é mais limitado: o feminicídio é cometido sobretudo por parceiros e ex-parceiros (Anuário), e as agressões de parceiros contra mulheres atendidas na saúde ficam em cerca do dobro no 1º de janeiro, assim como as demais agressões (SINAN).</div>


<h2>Como as três partes se ligam</h2>
<p>Em 2025, o SIM registra {n(SM['ano_a_ano']['2025']['total'] if '2025' in SM['ano_a_ano'] else SM['ano_a_ano'][2025]['total'])} mulheres mortas por agressão, e o Anuário registra 3.539 homicídios de mulheres. As diferenças vêm de definições diferentes (o Anuário conta mortes violentas intencionais pela classificação policial; o SIM, a causa médica da morte), de quem registra (polícia ou médico) e do fato de 2025 ser preliminar no SIM. Nenhuma das duas está "errada"; elas medem coisas próximas, mas diferentes.</p>

<p>As três fontes não se somam nem se substituem. O feminicídio (C) está contido nas mortes de mulheres por agressão (A), mas a declaração de óbito não diz quais mortes foram feminicídio. As agressões (B) são outra população: mulheres que sobreviveram e foram atendidas. Nenhuma das três mede diretamente "feminicídio no Ano Novo". O que temos são dois indícios, que não são prova: os assassinatos de mulheres quase dobram no 1º de janeiro (A), e as agressões de parceiros, que são o perfil típico do feminicídio (C), também dobram nesse dia (B).</p>

<h2>O que pode e o que não pode ser dito</h2>
<div class="box ok"><b>Pode ser dito (com a fonte):</b><ul>
<li><b>Mortes (A):</b> "Em 30 anos de dados, o 1º de janeiro é o dia com mais mulheres mortas por agressão no Brasil: em média 21,5, contra 11 num dia comum. Quase o dobro, em todos os 30 anos. O Natal é o segundo, cerca de 50% acima." (SIM/DATASUS, 1996–2025)</li>
<li><b>Mortes (A):</b> "É um pico geral de violência: com os homens acontece o mesmo. Mesmo comparado a um domingo, o 1º de janeiro fica cerca de 45% acima. Boa parte do excesso acontece na madrugada da virada." (SIM)</li>
<li><b>Mortes (A):</b> "Ao longo do ano, quase uma em cada três mulheres assassinadas morre dentro de casa; entre os homens, uma em cada dez." (SIM)</li>
<li><b>Agressões (B):</b> "Entre 2016 e 2024, os atendimentos de saúde por agressão de parceiro ou ex contra mulheres foram, no 1º de janeiro, cerca do dobro de um dia médio." (SINAN; margem: +83% a +137%)</li>
<li><b>Agressões (B):</b> "Nas notificações, a suspeita de que o agressor tinha bebido aparece em 75% dos casos informados no 1º de janeiro, contra 48% num dia útil." (SINAN, agressões de parceiro ou ex)</li>
<li><b>Feminicídio (C):</b> "Em 2025, o Brasil registrou 1.571 feminicídios, o maior número da série; 8 em cada 10 autores identificados eram companheiros ou ex." (Anuário FBSP 2026)</li>
<li><b>Feminicídio (C):</b> "Não existe no Brasil dado público de feminicídio por dia. Por isso não sabemos se ele acompanha o pico do Ano Novo."</li></ul></div>
<div class="box no"><b>Não deve ser dito:</b><ul>
<li>"O feminicídio dobra no Ano Novo." Não existe dado diário de feminicídio; os números de mortes (A) são de todos os assassinatos de mulheres.</li>
<li>"A violência doméstica dobra no Ano Novo." O SINAN conta atendimentos notificados na saúde, não todas as ocorrências.</li>
<li>"O álcool causa a violência" ou "o álcool aparece nas mortes". O dado de álcool é uma suspeita registrada nas agressões atendidas (B); as declarações de óbito não registram álcool.</li>
<li>"No Ano Novo as mulheres morrem mais em casa." A proporção é a mesma de um dia comum.</li>
<li>"A violência contra mulheres cresce mais que contra homens no Ano Novo" ou "o pico é específico dos parceiros". O aumento é igual nos dois sexos e igual entre parceiro e desconhecido.</li>
<li>"Três vezes mais mortes na madrugada" sem dizer o comparador. Contra a madrugada de um domingo, é cerca de duas vezes.</li>
<li>"O Natal tem +91% de agressões de parceiros" sem ressalva. Esse número varia de +55% a +94% conforme o filtro de data.</li>
<li>Números absolutos do SINAN como "total de agressões", ou qualquer número de um ano isolado (são só 11 a 35 mortes de mulheres por 1º de janeiro). Os dados de 2025 são preliminares.</li></ul></div>

<h2 class="pb">Método</h2>
<ul>
<li><b>Aumento de uma data:</b> (média de casos naquela data ao longo dos anos) ÷ (média de casos num dia qualquer do mesmo período) − 1. Por exemplo, no SIM, mulheres: ({SM['jan1']['n']} ÷ 30) ÷ ({n(SM['total'])} ÷ 10.958 dias) − 1 = {pct(SM['jan1']['pct'])}.</li>
<li><b>Intervalo de confiança de 95%:</b> calculado como contagem de Poisson (aproximação de Wilson–Hilferty). Mostra a margem de incerteza estatística, não erros de registro.</li>
<li><b>Relógio e horas:</b> para cada hora da noite, a "virada" soma os casos de 31/12 (18h–23h59) e de 1/1 (0h–5h59) em todos os anos do período. A "noite comum" é o total daquela hora em todos os dias do período dividido por 365,25, o que equivale a uma data qualquer somada pelo mesmo número de anos. Só entram registros com hora informada.</li>
<li><b>Controle de dia da semana:</b> comparamos o 1º de janeiro com o esperado para o dia da semana em que ele caiu em cada ano, porque domingos já são mais violentos.</li>
<li><b>Datas inválidas:</b> no SIM, 445 declarações de óbito por agressão (57 de mulheres) têm data incompleta ou inválida (por exemplo, só mês e ano) e foram descartadas. Uma primeira versão da análise (usada no vídeo publicado) contou por engano 3 delas como 1º de janeiro, o que deu +95% em vez de {pct(SM['jan1']['pct'])}.</li>
</ul>


<h2>Armadilhas encontradas nos dados e como foram tratadas</h2>
<table><tr><th>Problema</th><th>Evidência</th><th>Tratamento</th></tr>
<tr><td>SINAN: data desconhecida preenchida como 1º de janeiro</td><td>Usando todas as notificações de 2016–2024, o 1/1 aparece com +179% e os outros dias 1 do mês com +19%. Das "ocorrências em 1/1", 42% foram notificadas 5 ou mais dias depois.</td><td>Só notificações no dia da agressão ou no seguinte. Com esse filtro, os outros dias 1 ficam normais ({pct(P['outros_dia1'])}).</td></tr>
<tr><td>SINAN 2009–2015: data da ocorrência igual à da notificação</td><td>De 2009 a 2015, as duas datas são iguais em 99,5% a 100% dos casos que têm a data, e quase não há notificações com 1 a 30 dias de diferença; a partir de 2016 esse padrão muda (cerca de 48% no mesmo dia). Antes de 2016, o campo parece registrar o dia do atendimento, não o da agressão.</td><td>SINAN analisado só de 2016 a 2024.</td></tr>
<tr><td>Horas arredondadas</td><td>No SIM, 36% das horas terminam em ":00" (o esperado seria 1,7%); no SINAN, {P['minuto_00_pct']}%.</td><td>Os relógios mostram só a hora cheia, não o minuto. A concentração na madrugada se mantém excluindo os horários ":00" (SIM: 83 contra 25,4; SINAN: 294 contra 72).</td></tr>
<tr><td>SIM: data do óbito, não da agressão</td><td>Quem morre no hospital pode ter sido agredida horas ou dias antes.</td><td>Tratamos o horário como hora do óbito. A madrugada do 1º de janeiro inclui pessoas agredidas na noite de 31/12.</td></tr>
<tr><td>Feriado muda quem notifica</td><td>No feriado, escolas e ambulatórios fecham; ficam os prontos-socorros. Agressões de pai/mãe (em geral contra crianças, que chegam muito pela escola) caem {pct(MP['jan1']['pct'])} no 1/1.</td><td>A auditoria testou esse viés: a fatia de notificações feitas no mesmo dia ou no seguinte é igual no 1/1 e no resto do ano (73,7% contra 73,4%). No Natal é um pouco maior (76,7%), o que pode superestimar o Natal em cerca de 4%. Comparamos grupos de agressores separadamente.</td></tr>
<tr><td>Escolha do filtro de data</td><td>O resultado depende do intervalo entre agressão e notificação aceito?</td><td>Para parceiro ou ex no 1/1: mesmo dia +115%; dia seguinte +92%; 2 a 7 dias +98%; até 30 dias +109%. O 1/1 é robusto. O Natal é mais sensível: de +55% a +94%.</td></tr>
<tr><td>Hora mais preenchida no 1/1 (SINAN)</td><td>No 1/1, {P['hora_cobertura_jan1_pct']}% das notificações de parceiro ou ex têm hora, contra {P['hora_cobertura_pct']}% no geral.</td><td>Isso infla a comparação da madrugada do SINAN em cerca de 10%. No SIM o efeito é desprezível (74,8% contra 73,8%).</td></tr>
<tr><td>Duplicatas</td><td>A mesma pessoa pode ser notificada mais de uma vez.</td><td>Testado pela auditoria (chave de data, idade, raça, município, hora e local): 0,14% no geral e 0,26% no 1/1. Deduplicando, o 1/1 fica +109,5%.</td></tr>
<tr><td>Anos preliminares</td><td>SIM 2025 está na pasta PRELIM do DATASUS.</td><td>Testado: sem 2025, o 1/1 das mulheres fica em +96% (contra +94% com 2025).</td></tr>
</table>


<h2 class="pb">Auditoria independente</h2>
{AUD}


<h2>Limitações</h2>
<ul>
<li><b>Mortes por agressão não são feminicídios.</b> Incluem todos os homicídios de mulheres, por qualquer motivo, e de meninas de todas as idades: 12,9% das vítimas tinham menos de 18 anos.</li>
<li><b>Subregistro.</b> Mortes violentas registradas como "intenção indeterminada" não entram, então os totais do SIM são um piso. A cobertura do SIM também era menor nos anos 1990.</li>
<li><b>O SINAN mede atendimento, não ocorrência.</b> A notificação cresceu muito ao longo dos anos, e por isso não usamos o SINAN para tendências no tempo.</li>
<li><b>Horas:</b> faltam em cerca de um quarto das declarações de óbito (SIM) e em um terço das notificações (SINAN), e muitas são arredondadas.</li>
<li><b>Álcool:</b> é a suspeita de quem atendeu, com {P['alcool_ign_pct']}% sem informação.</li>
<li><b>Causalidade:</b> o estudo mostra quando a violência acontece, não por quê.</li>
</ul>


<h2>Apêndice A — SIM, ano a ano</h2>
<table><tr><th>Ano</th><th>Mulheres, total</th><th>Mulheres, 1/1</th><th>Mulheres, 25/12</th><th>Homens, total</th><th>Homens, 1/1</th><th>Homens, 25/12</th></tr>{anos}</table>
<p class="small">Pelo ano da data do óbito. 2025 é preliminar.</p>
<h2>Apêndice B — SINAN, agressões a mulheres por parceiro ou ex, ano a ano</h2>
<table><tr><th>Ano</th><th>Média por dia</th><th>1º de janeiro</th><th>Vezes a média</th></tr>{sinan_anos}</table>
<p class="small">Só notificações com data confiável. O 1/1 de cada ano é atribuído ao ano em que ocorre.</p>

<h2>Referências</h2>
<ul class="small">
<li>Ministério da Saúde. DATASUS. Sistema de Informações sobre Mortalidade (SIM): arquivos DOEXT 1996–2025. <a>ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DOFET/</a> (acesso em 25/11/2026).</li>
<li>Ministério da Saúde. DATASUS. Sistema de Informação de Agravos de Notificação (SINAN): Violência interpessoal/autoprovocada, arquivos VIOLBR 2009–2024. <a>ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/DADOS/FINAIS/</a> (acesso em 25/11/2026).</li>
<li>Ministério da Saúde. Ficha de notificação individual — violência interpessoal/autoprovocada, versão 5.1, e instrutivo de preenchimento. <a>https://www.saude.sp.gov.br/resources/cve-centro-de-vigilancia-epidemiologica/homepage/downloads/fichas/violencia_v5.pdf</a></li>
<li>Fórum Brasileiro de Segurança Pública. Anuário Brasileiro de Segurança Pública 2026. <a>https://forumseguranca.org.br/wp-content/uploads/2026/07/anuario-2026.pdf</a></li>
<li>ACT Promoção da Saúde; Fórum Brasileiro de Segurança Pública; Vital Strategies. Álcool e Violência, 2026. <a>https://actbr.org.br/wp-content/uploads/2026/10/ALCOOL-E-VIOLENCIA-1910.pdf</a></li>
<li>Urcioli, G.; Trindade, R. Flor de Aço — dados sobre violência contra a mulher. <a>https://github.com/rafa-trindade/flor-de-aco</a>; Kaggle: rafatrindade/feminicidio-br.</li>
<li>D'Ignazio, C.; Klein, L. Data Feminism. MIT Press, 2020. <a>https://data-feminism.mitpress.mit.edu/</a></li>
</ul>
<p class="small">Ajuda: Ligue 180 (Central de Atendimento à Mulher, gratuito, 24 horas, sigiloso) · WhatsApp (61) 99610-0180 · Emergência 190.</p>
</body></html>"""
open(sys.argv[2], "w", encoding="utf-8").write(HTML)
print("ok", sys.argv[2])
