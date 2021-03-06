import pygame as p
from Xadrez import XadrezRegras

WIDTH = HEIGHT = 512  # 400 OUTRA OPÇÃO DE TAMANHO
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = XadrezRegras.GameState()
    carregaImagens()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        interfaceGame(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def carregaImagens():
    pecas = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for peca in pecas:
        IMAGES[peca] = p.transform.scale(p.image.load("assets/" + peca + ".png"), (SQ_SIZE, SQ_SIZE))


def interfaceGame(screen, gs):
    criaTabuleiro(screen)
    criaPecas(screen, gs.board)


def criaTabuleiro(screen):
    colors = [p.Color("white"), p.Color("darkred")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def criaPecas(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            peca = board[r][c]
            if peca != "--":
                screen.blit(IMAGES[peca], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == '__main__':
    main()
