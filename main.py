import pyray as pr
from game import Game

SCREENWIDTH = 310
SCREENHEIGHT = 310


if __name__ == "__main__":
    current_game = Game(screenWidth=SCREENWIDTH, screenHeight=SCREENHEIGHT)

    pr.init_window(SCREENWIDTH, SCREENHEIGHT, "Tic Tac Toe")
    pr.set_target_fps(60)

    current_game.startup()

    while not pr.window_should_close():
        current_game.update()
        pr.begin_drawing()
        pr.clear_background(pr.BLACK)
        current_game.render()
        pr.end_drawing()

    pr.close_window()
    current_game.shutdown()
