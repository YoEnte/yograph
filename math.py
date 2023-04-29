from socha import *
import random
import math
import time

class Logic(IClientHandler):

    gameState: GameState

    def __init__(self) -> None:
        pass
        
    def calculate_move(self) -> Move:

        test_vecs = [
            Vector(1, -1),
            Vector(5, -5),
            Vector(20, 0),
            Vector(-11, -1),
            Vector(-51, -51),
        ]

        for v in test_vecs:
            print(v, v.magnitude, (v / v.magnitude))


        return random.choice(self.gameState.possible_moves)

    def on_update(self, state: GameState):
        self.gameState = state

# ////////////////    Starter    ////////////////
        
if __name__ == "__main__":
    Starter(Logic())