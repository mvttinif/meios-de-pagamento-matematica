#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════╗
║   π VINTAGE CALCULATOR — 7-Segment Display           ║
║   Semana da Matemática — Atividade Prática           ║
║   Maurício Freitas, Nº17, 11F, GPSI                 ║
╚══════════════════════════════════════════════════════╝

Requisitos: pip install mpmath
"""

import time
import os
import sys
import subprocess
import random
import re

# Activar suporte de cores ANSI no CMD/PowerShell do Windows
if os.name == 'nt':
    os.system('')

# ─── Importar mpmath ─────────────────────────────────────────────────────────
try:
    from mpmath import mp
except ImportError:
    print("⚠  mpmath não encontrado. A instalar...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mpmath"])
    from mpmath import mp

mp.dps = 1050
PI_STR = mp.nstr(mp.pi, 1005, strip_zeros=False)

# ══════════════════════════════════════════════════════════════════════════════
#  PALETA — Ecrã Âmbar Vintage (Fósforo P3)
# ══════════════════════════════════════════════════════════════════════════════
C_ON    = '\033[38;2;255;176;0m'
C_OFF   = '\033[38;2;40;28;0m'
C_GLOW  = '\033[38;2;255;200;60m'
C_FRAME = '\033[38;2;100;70;10m'
C_INFO  = '\033[38;2;180;130;30m'
C_DIM   = '\033[38;2;60;42;5m'
C_WHITE = '\033[38;2;220;210;180m'
C_BOLD  = '\033[1m'
RST     = '\033[0m'

# ══════════════════════════════════════════════════════════════════════════════
#  DEFINIÇÃO DOS 7 SEGMENTOS  —  (a, b, c, d, e, f, g)
# ══════════════════════════════════════════════════════════════════════════════
#
#      aaaa          a = topo       f = vert. sup. esq.
#     f    b         b = vert. sup. dir.   g = meio
#     f    b         c = vert. inf. dir.
#      gggg          d = base
#     e    c         e = vert. inf. esq.
#     e    c
#      dddd

SEGMENTS = {
    '0': (1, 1, 1, 1, 1, 1, 0),
    '1': (0, 1, 1, 0, 0, 0, 0),
    '2': (1, 1, 0, 1, 1, 0, 1),
    '3': (1, 1, 1, 1, 0, 0, 1),
    '4': (0, 1, 1, 0, 0, 1, 1),
    '5': (1, 0, 1, 1, 0, 1, 1),
    '6': (1, 0, 1, 1, 1, 1, 1),
    '7': (1, 1, 1, 0, 0, 0, 0),
    '8': (1, 1, 1, 1, 1, 1, 1),
    '9': (1, 1, 1, 1, 0, 1, 1),
}


# ══════════════════════════════════════════════════════════════════════════════
#  DESENHO DOS DÍGITOS
# ══════════════════════════════════════════════════════════════════════════════

def _h(on):
    """Segmento horizontal — 6 blocos."""
    return f"{C_ON if on else C_OFF}██████{RST}"

def _v(on):
    """Segmento vertical — 2 blocos."""
    return f"{C_ON if on else C_OFF}██{RST}"

# Cada dígito: 10 colunas visuais × 7 linhas
# Horizontal:  "  ██████  "  = 2 + 6 + 2 = 10
# Vertical:    "██      ██"  = 2 + 6 + 2 = 10

DIGIT_W = 10   # largura visual de um dígito
DOT_W   = 4    # largura visual do ponto decimal
GAP     = 1    # espaço entre dígitos
NUM_ROWS = 7


def draw_digit(char):
    """
    Devolve lista de 7 strings (linhas) para um dígito 7-segmentos.
    Dígitos: 10 colunas visuais.  Ponto: 4 colunas visuais.
    """
    if char == '.':
        return [
            "    ",
            "    ",
            "    ",
            "    ",
            "    ",
            "    ",
            f" {C_ON}██{RST} ",
        ]

    if char not in SEGMENTS:
        return [" " * DIGIT_W] * NUM_ROWS

    a, b, c, d, e, f, g = SEGMENTS[char]

    return [
        f"  {_h(a)}  ",             # topo
        f"{_v(f)}      {_v(b)}",    # vert. sup.
        f"{_v(f)}      {_v(b)}",    # vert. sup. (dupla)
        f"  {_h(g)}  ",             # meio
        f"{_v(e)}      {_v(c)}",    # vert. inf.
        f"{_v(e)}      {_v(c)}",    # vert. inf. (dupla)
        f"  {_h(d)}  ",             # base
    ]


# ══════════════════════════════════════════════════════════════════════════════
#  UTILIDADES DE RENDERIZAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

_ANSI_RE = re.compile(r'\033\[[^m]*m')

def vlen(s):
    """Comprimento visual de uma string (sem contar códigos ANSI)."""
    return len(_ANSI_RE.sub('', s))


# Largura interior fixa da moldura
FI = 86


def fline(content):
    """Envolve conteúdo numa linha de moldura, com padding automático."""
    pad = max(0, FI - vlen(content))
    return f"   {C_FRAME}║{RST}{content}{' ' * pad}{C_FRAME}║{RST}\n"


def fsep(char='═'):
    """Separador horizontal da moldura."""
    return f"   {C_FRAME}╔{char * FI}╗{RST}\n" if char == '═' else f"   {C_FRAME}╠{'═' * FI}╣{RST}\n"


def ftop():
    return f"   {C_FRAME}╔{'═' * FI}╗{RST}\n"

def fmid():
    return f"   {C_FRAME}╠{'═' * FI}╣{RST}\n"

def fbot():
    return f"   {C_FRAME}╚{'═' * FI}╝{RST}\n"


# ══════════════════════════════════════════════════════════════════════════════
#  DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

DISPLAY_WIDTH = 8


def render(ecra, pi_shown, digit_idx, total):
    """Renderiza todo o ecrã."""
    buf = []
    buf.append('\033[H\n')

    # ─── Banner π ASCII art ──────────────────────────────────────────────
    banner = [
        f"   {C_GLOW}  ██████╗ ██╗     {C_ON}  ██████╗  █████╗ ██╗      ██████╗{RST}      {C_ON}████████████████{RST}",
        f"   {C_GLOW}  ██╔══██╗██║     {C_ON} ██╔════╝ ██╔══██╗██║     ██╔════╝{RST}      {C_ON}║   ██    ██   ║{RST}",
        f"   {C_GLOW}  ██████╔╝██║     {C_ON} ██║      ███████║██║     ██║     {RST}      {C_ON}    ██    ██{RST}",
        f"   {C_GLOW}  ██╔═══╝ ██║     {C_ON} ██║      ██╔══██║██║     ██║     {RST}      {C_ON}    ██    ██{RST}",
        f"   {C_GLOW}  ██║     ██║     {C_ON} ╚██████╗ ██║  ██║███████╗╚██████╗{RST}      {C_ON}    ██    ██{RST}",
        f"   {C_GLOW}  ╚═╝     ╚═╝     {C_ON}  ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝{RST}      {C_ON}   ████  ████{RST}",
    ]
    for line in banner:
        buf.append(line + '\n')
    buf.append('\n')

    # ─── Cabeçalho escolar ───────────────────────────────────────────────
    buf.append(ftop())
    buf.append(fline(f"  {C_GLOW}{C_BOLD}Maurício Freitas{RST}  {C_FRAME}│{RST}  {C_INFO}Nº17{RST}  {C_FRAME}│{RST}  {C_INFO}11F — GPSI{RST}  {C_FRAME}│{RST}  {C_INFO}Profª Isabel Margarida{RST}  "))
    buf.append(fmid())
    buf.append(fline(f"  {C_WHITE}Semana da Matemática — Atividade Prática e Criativa{RST}"))
    buf.append(fline(f"  {C_INFO}«Explorar o símbolo π e seus dígitos de forma digital e visual,{RST}"))
    buf.append(fline(f"  {C_INFO} unindo programação e matemática.»{RST}"))
    buf.append(fmid())

    # ─── Título da calculadora ───────────────────────────────────────────
    buf.append(fline(f"  {C_GLOW}★  CALCULADORA VINTAGE DE π  —  REVELANDO DÍGITOS...  ★{RST}"))
    buf.append(fmid())

    # ─── Ecrã LCD ────────────────────────────────────────────────────────
    buf.append(fline(""))

    # Compor as 7 linhas dos dígitos
    digit_rows = [""] * NUM_ROWS
    for ch in ecra:
        d = draw_digit(ch)
        for i in range(NUM_ROWS):
            digit_rows[i] += d[i] + " "   # 1 espaço de gap

    left = "     "
    for row in digit_rows:
        buf.append(fline(f"{left}{row}"))

    buf.append(fline(""))

    # ─── Informação + progresso ──────────────────────────────────────────
    buf.append(fmid())

    # Linha π ≈ ...
    shown = ''.join(pi_shown[-50:])
    dots = "..." if len(pi_shown) > 50 else ""
    pi_text = f"  π ≈ {dots}{shown}  [dígito #{digit_idx}]"
    buf.append(fline(f"{C_INFO}{pi_text}{RST}"))

    # Barra de progresso
    pct = min(digit_idx / total, 1.0) if total > 0 else 0
    bar_w = FI - 28
    filled = int(bar_w * pct)
    bar = '█' * filled + '░' * (bar_w - filled)
    pct_s = f"{pct * 100:.1f}%"
    buf.append(fline(f"  {C_INFO}Progresso:{RST} {C_ON}{bar}{RST} {C_INFO}{pct_s}{RST}"))

    # ─── Rodapé ──────────────────────────────────────────────────────────
    buf.append(fbot())
    buf.append(f"\n   {C_DIM}  ◄ Pressione Ctrl+C para terminar ►{RST}\n")

    sys.stdout.write(''.join(buf))
    sys.stdout.write('\033[J')
    sys.stdout.flush()


# ══════════════════════════════════════════════════════════════════════════════
#  ANIMAÇÃO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def animate_pi():
    pi_chars = list(PI_STR)
    total = len([c for c in pi_chars if c != '.'])

    sys.stdout.write('\033[?25l')   # esconder cursor
    os.system('cls' if os.name == 'nt' else 'clear')

    ecra = []
    pi_shown = []
    count = 0

    try:
        # "3." inicial
        ecra.append('3')
        pi_shown.append('3')
        count = 1
        render(ecra, pi_shown, count, total)
        time.sleep(0.8)

        ecra.append('.')
        pi_shown.append('.')
        render(ecra, pi_shown, count, total)
        time.sleep(0.5)

        # Loop infinito
        while True:
            for ch in pi_chars[2:]:
                if len(ecra) >= DISPLAY_WIDTH:
                    ecra.pop(0)
                    if ecra and ecra[0] == '.':
                        ecra.pop(0)

                ecra.append('0')
                count += 1

                # Efeito "decoding"
                for _ in range(random.randint(3, 6)):
                    ecra[-1] = str(random.randint(0, 9))
                    render(ecra, pi_shown, count, total)
                    time.sleep(0.035)

                ecra[-1] = ch
                pi_shown.append(ch)
                render(ecra, pi_shown, count, total)
                time.sleep(0.3)

            # Recomeçar
            ecra.clear()
            pi_shown.clear()
            count = 0
            ecra.append('3')
            pi_shown.append('3')
            count = 1
            render(ecra, pi_shown, count, total)
            time.sleep(0.8)
            ecra.append('.')
            pi_shown.append('.')
            render(ecra, pi_shown, count, total)
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write('\033[?25h')
        pad_c = " " * max(0, 10 - len(str(count)))
        msg = f"""

   {C_GLOW}╔══════════════════════════════════════════════════════╗{RST}
   {C_GLOW}║                                                      ║{RST}
   {C_GLOW}║   {C_ON}π é irracional, infinito, e belo.{RST}                {C_GLOW}║{RST}
   {C_GLOW}║   {C_INFO}Explorámos {count} dígitos desta vez.{RST}{pad_c}    {C_GLOW}║{RST}
   {C_GLOW}║   {C_INFO}Obrigado por assistir. Até à próxima! 🧮{RST}         {C_GLOW}║{RST}
   {C_GLOW}║                                                      ║{RST}
   {C_GLOW}║   {C_DIM}Maurício Freitas — Nº17 — 11F GPSI{RST}              {C_GLOW}║{RST}
   {C_GLOW}║                                                      ║{RST}
   {C_GLOW}╚══════════════════════════════════════════════════════╝{RST}

"""
        sys.stdout.write(msg)
        sys.stdout.flush()


if __name__ == "__main__":
    animate_pi()
