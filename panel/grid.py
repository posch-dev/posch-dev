#!/usr/bin/env python3

GRID_W, GRID_H = 512, 144
OUT_W, OUT_H = GRID_W * 2, GRID_H * 2

BORDER = 1
PAD = 4

GLYPH_H = 9
ROW_GAP = 2

C_BG = "#000000"
C_GREY = "#3c3c3c"
C_WHITE = "#b4b4b4"
C_BRIGHT = "#ffffff"
C_DIM = "#6e6e6e"

C_GREEN = "#00ff00"
C_LIME = "#00d24b"
C_YELLOW = "#ffc800"
C_ORANGE = "#ff8c00"
C_RED = "#dc3232"
C_LIGHTBLUE = "#64beff"
C_PURPLE = "#aa3cdc"
C_PINK = "#ff5ac8"

HEADER_H = GLYPH_H * 2

HEADER_BLOCK_H = HEADER_H + 1

COMMIT_ROW_H = 12
COMMIT_H = 2 * COMMIT_ROW_H + GLYPH_H

SHELL_ROW_H = GLYPH_H
SHELL_MAX_ROWS = 9

def block_positions(shell_rows):
    blocks = [HEADER_BLOCK_H, COMMIT_H, shell_rows * SHELL_ROW_H]
    padding = max((GRID_H - 2 * BORDER - sum(blocks)) // len(blocks), 0)
    half = padding // 2

    first_rule = BORDER + padding + HEADER_BLOCK_H
    second_rule = first_rule + padding + COMMIT_H
    return {
        "header": BORDER + half + 1,
        "first_rule": first_rule,
        "commit": first_rule + half,
        "second_rule": second_rule,
        "shell": second_rule + half,
        "padding": padding,
    }
