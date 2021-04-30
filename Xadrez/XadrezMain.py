import pygame as p
from Xadrez import XadrezRegras, XadrezMovimentos, XadrezIA
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512  # 400 OUTRA OPÇÃO DE TAMANHO
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_WIDTH))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = XadrezRegras.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    carregaImagens()
    waiting = True
    running = False
    sqSelected = ()
    player_clicks = []
    game_over = False
    playerOne = False
    playerTwo = False
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    while waiting:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN:
                if e.key == p.K_1:
                    playerOne = True
                    playerTwo = False
                    waiting = False
                elif e.key == p.K_2:
                    playerOne = False
                    playerTwo = True
                    waiting = False
                elif e.key == p.K_3:
                    playerOne = False
                    playerTwo = False
                    waiting = False
        drawInstructionsText(screen)

        clock.tick(MAX_FPS)
        p.display.flip()   
        
    running = True

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >=8:
                        sqSelected = ()
                        player_clicks = []
                    else:
                        sqSelected = (row, col)
                        player_clicks.append(sqSelected)
                    if len(player_clicks) == 2 and humanTurn:
                        move = XadrezRegras.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves [i]:
                                print(move.getChessNotation())
                                gs.makeMove(validMoves [i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                player_clicks = []
                        if not moveMade:
                            player_clicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    game_over = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  # reinicia o jogo caso o r seja pressionado
                    gs = XadrezRegras.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    player_clicks = []
                    moveMade = False
                    animate = False
                    game_over = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        if not game_over and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()
                moveFinderProcess = Process(target = XadrezIA.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = XadrezIA.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False
        interfaceGame(screen, gs, validMoves ,  sqSelected, moveLogFont)

        if gs.checkMate or gs.staleMate:
            game_over = True
            drawEndGameText(screen, 'Rei afogado' if gs.staleMate else 'VENCEDOR: PRETO(via checkmate)' if gs.whiteToMove else 'VENCEDOR: BRANCO(via checkmate)' )

        clock.tick(MAX_FPS)
        p.display.flip()

def criaTabuleiro(screen):
    global colors
    colors = [p.Color("white"), p.Color("darkred")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def carregaImagens():
    pecas = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for peca in pecas:
        IMAGES[peca] = p.transform.scale(p.image.load("assets/" + peca + ".png"), (SQ_SIZE, SQ_SIZE))

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitica", 32, True, False)
    text_object = font.render(text, 0, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('black'))
    screen.blit(text_object, text_location.move(2,2))

def interfaceGame(screen, gs , validMoves, sqSelected, moveLogFont):
    criaTabuleiro(screen)
    highlightSquares(screen, gs, validMoves , sqSelected)
    criaPecas(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)

def highlightSquares(screen, gs, validMoves , sqSelected):
    '''
    Aplica um highlight no quadro selecionado e move a peça para ele.
    '''
    if (len(gs.moveLog)) > 0:
        last_move = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.endCol*SQ_SIZE, last_move.endRow*SQ_SIZE))
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'): #peça que pode ser movida
            #quadro destacado
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
            #destaca movimentos
            s.fill(p.Color('yellow'))
            for move in validMoves :
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))



def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        text_object = font.render(text, True, p.Color("white"))
        text_location = moveLogRect.move(padding, textY)
        screen.blit(text_object, text_location)
        textY += text_object.get_height() + lineSpacing

def drawInstructionsText(screen):
    font = p.font.SysFont("Arial", 14, False, False)
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    texts = [
        "---- INSTRUÇÕES ----", 
        "",
        "Pressione:",
        "1 - Jogar como Brancas",
        "2 - Jogar como Pretas",
        "3 - IA vs IA",
        ]
    
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(texts)):
        text = texts[i]
        text_object = font.render(text, True, p.Color("white"))
        text_location = moveLogRect.move(padding, textY)
        screen.blit(text_object, text_location)
        textY += text_object.get_height() + lineSpacing


def criaPecas(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            peca = board[r][c]
            if peca != "--":
                screen.blit(IMAGES[peca], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    '''
    Animating a move
    '''
    global colors
    d_row = move.endRow - move.startRow
    d_col = move.endCol - move.startCol
    frames_per_square = 10 #frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.startRow + d_row * frame / frame_count, move.startCol + d_col * frame / frame_count)
        criaTabuleiro(screen)
        criaPecas(screen, board)
        #erease the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        end_square = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                end_square = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured ], end_square)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

        
if __name__ == '__main__':
    main()
