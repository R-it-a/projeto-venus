# Projeto Vênus

**A virada do ano:** um vídeo sobre as mulheres mortas por agressão no Brasil na madrugada de 1º de janeiro.

Análise e visualização: **Rita Farias**

![](https://img.shields.io/badge/dados-SIM%2FDATASUS-b0465e) ![](https://img.shields.io/badge/licen%C3%A7a-MIT-555)

## O que o vídeo mostra

São dois relógios, que vão das 18h às 6h. Em cima fica a virada do ano (31/12 → 1/1), somando as viradas de 2006 a 2025. Embaixo fica uma noite comum, a média dos dias do ano na mesma base. Cada ponto é uma mulher morta por agressão.

| | Valor |
|---|---|
| Mulheres mortas por agressão por ano (média 1996–2025) | ~4 mil (4.047) |
| Por dia, em média | 11 |
| No 1º de janeiro, em média | 21,5 (+94%) |
| Madrugada de 1º de janeiro (0h–6h), soma 2006–2025 | 139 |
| Madrugada comum, mesma base | 42 |

O primeiro vídeo publicado está em [`virada_stories.mp4`](virada_stories.mp4). Ele diz "95% a mais"; o número correto é **94%** (um erro de leitura de datas incompletas, corrigido no estudo abaixo).

## Estudo completo (novembro de 2026)

Depois do primeiro vídeo, os números foram refeitos **direto dos arquivos oficiais do DATASUS** e conferidos por uma auditoria independente. O estudo separa três coisas:

- **A. Mortes de mulheres por agressão** (SIM, 1996–2025): o 1º de janeiro tem +94% em relação a um dia médio; o Natal, +53%. Com os homens acontece o mesmo (+90%).
- **B. Agressões contra mulheres atendidas na saúde** (SINAN, 2016–2024): agressões de parceiro ou ex ficam em cerca do dobro no 1º de janeiro (+110%); suspeita de álcool do agressor em 75% dos casos informados, contra 48% num dia útil.
- **C. Feminicídio** (Anuário Brasileiro de Segurança Pública 2026): não existe dado público de feminicídio por dia.

| Arquivo | O que é |
|---|---|
| [`Projeto Venus - relatorio.pdf`](Projeto%20Venus%20-%20relatorio.pdf) | Relatório com fontes, método, armadilhas dos dados e auditoria |
| [`virada_v3_stories.mp4`](virada_v3_stories.mp4) | Vídeo novo: **média por noite**, 2016–2024 (pontos amarelos = agressões de parceiro ou ex; vermelhos = mortes por agressão) |
| [`virada_v4_soma_stories.mp4`](virada_v4_soma_stories.mp4) | Mesma ideia, com a **soma** de todos os anos |
| `estudo/` | Extração dos arquivos oficiais, cálculo dos números (`numeros.json`), geração do relatório e scripts da auditoria |
| `relogio_v2.py`, `relogio_v3.py`, `relogio_v4.py` | Scripts dos vídeos novos |

Arquivos oficiais usados (FTP do DATASUS): `SIM/CID10/DOFET/DOEXTyy.dbc` e `SINAN/DADOS/FINAIS/VIOLBRyy.dbc`.

```bash
pip install pandas pyarrow numpy pillow imageio-ffmpeg dbfread datasus-dbc
python -I estudo/extrai_sim.py   <pasta_dbc_sim>   sim_oficial.parquet
python -I estudo/extrai_sinan.py <pasta_dbc_sinan> sinan_oficial.parquet
python -I estudo/numeros.py sim_oficial.parquet sinan_oficial.parquet numeros.json
python -I estudo/gera_relatorio.py numeros.json relatorio.html estudo/auditoria.html
python -I relogio_v3.py numeros.json virada_media.mp4
```

Os scripts em `estudo/auditoria/` esperam os dados numa pasta `dados/`.

## Fonte dos dados

- **SIM – Sistema de Informações sobre Mortalidade**, do Ministério da Saúde, publicado pelo DATASUS. Cada registro é uma declaração de óbito, sem nome nem qualquer dado que identifique a pessoa.
- Recorte: óbitos do sexo feminino com causa básica "agressões" (CID-10 X85–Y09).
- Os dados foram baixados, filtrados e convertidos pelo projeto **[Flor de Aço](https://github.com/rafa-trindade/flor-de-aco)**, de Gabrielle Urcioli e Rafael Trindade, e estão publicados no Kaggle: [rafatrindade/feminicidio-br](https://www.kaggle.com/datasets/rafatrindade/feminicidio-br) (CC0).

## Limitações

- **Não é só feminicídio.** A declaração de óbito não registra o motivo do crime. "Mortas por agressão" inclui todos os homicídios de mulheres.
- **Inclui meninas.** Os números cobrem todas as idades; 84% das vítimas tinham 18 anos ou mais. Contando só adultas, o 1º de janeiro tem +91%.
- **É um piso.** Mortes violentas registradas como "intenção indeterminada" não entram na conta.
- **A hora do óbito só existe a partir de 2006,** e falta em 17% a 37% dos registros, conforme o ano. Por isso os relógios usam 2006–2025 e mostram menos mortes do que de fato houve. É a hora do óbito, não a da agressão.
- **Os anos recentes são preliminares.** 2025 e 2026 ainda devem subir com as atualizações do DATASUS. Mesmo variando o período, o excesso do 1º de janeiro fica entre +87% e +97%.
- Os dados mostram **quando** essas mortes acontecem, não **por quê**.

## Como rodar

Requisitos: Python 3.8+ com `pandas`, `pyarrow`, `numpy`, `pillow` e `imageio-ffmpeg`.

```bash
pip install pandas pyarrow numpy pillow imageio-ffmpeg
```

Baixe o dataset do Kaggle e descompacte. A pasta precisa conter `datasus_sim/proxy_sim_feminicidio.parquet`.

```bash
# vídeo (layout Stories, o publicado)
python -I relogio.py <pasta_data> virada.mp4 --stories

# tabelas da análise
python -I analises/anual.py  <pasta_data>   # mortes por ano e no 1º de janeiro
python -I analises/natal.py  <pasta_data>   # Natal, véspera, réveillon e Ano Novo
python -I analises/horas.py  <pasta_data>   # hora a hora: Natal, Ano Novo e noite comum
python -I analises/idade.py  <pasta_data>   # faixa etária e resultado só com adultas
python -I analises/ultimo.py <pasta_data>   # a virada 2025 → 2026 (preliminar)
```

O script do vídeo usa as fontes Georgia e Segoe UI do Windows (`C:/Windows/Fonts/`). Em outro sistema, ajuste a variável `F` em `relogio.py`.

## Por que este projeto

Esta proposta surgiu a partir das conversas de um grupo de estudos sobre IA e sociedade e da leitura do livro *[Data Feminism](https://data-feminism.mitpress.mit.edu/)*, de Catherine D'Ignazio e Lauren Klein. A ideia é mostrar que dados não são isentos de emoção, e que são, sim, impactantes. Afinal, estamos falando da vida de mulheres que foram violentamente assassinadas e que merecem a nossa atenção e o nosso sentimento.

## Precisa de ajuda?

**Ligue 180**: Central de Atendimento à Mulher (gratuito, 24h, sigiloso) · WhatsApp (61) 99610-0180 · Emergência: **190**
