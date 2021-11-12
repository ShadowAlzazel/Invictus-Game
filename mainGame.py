import pygame
from pygame.constants import K_ESCAPE, KEYDOWN, K_e
from gameField import *

#start game
def gameOperationSpace(turnGame):
    #turnGame = turnCombatGame(aoe)

    gameScreen = pygame.display.set_mode((LENGTH, WIDTH))
    gameScreen.fill(SCREEN_RGB)

    EMPTY_HEX_IMG.convert()
    SHIP_HERE_HEX_IMG.convert()
    SHIP_ENEMY_HERE_HEX_IMG.convert()

    pygame.init()

    combatGameBoard = spaceGameBoard(turnGame.opsSpace.l, turnGame.opsSpace.w)

    #create window
    pygame.display.update()
    pygame.display.set_caption("ASCS Fleet Manager")
    pygame.display.set_icon(GAME_ICON)

    gameRunning = True
    gameClock = pygame.time.Clock()

    while gameRunning:
        gameClock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gameRunning = False

            if event.type == KEYDOWN and event.key == K_e:
                print('Fleet Turn Ended')
                turnGame.fleetTurn()

            if event.type == pygame.MOUSEBUTTONDOWN:
                someMousePos = pygame.mouse.get_pos()
                hexIndex = combatGameBoard.getCoordMouse(someMousePos)
                if hexIndex >= 0:
                    result = turnGame.selectHex(turnGame.opsSpace.starSpaceHexes[hexIndex])
                    if result:
                        combatGameBoard.drawHexes

                print(hexIndex)

        combatGameBoard.drawHexes(gameScreen, turnGame.opsSpace)
        pygame.display.update()

    pygame.quit()
