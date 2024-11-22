from socha import *
import random
import math
import time

class Meth:
    def get_lines_peng(p: Penguin) -> list:

        lines = []
            
        x = p.coordinate.x
        y = -(p.coordinate.y)
        
        for v in Vector().directions[0:3]:
            m = -int(v.d_y / v.d_x)
            b = y - (x * m)

            lines.append(str(m) + ' * x + ' + str(b))

        return lines
    
    def get_lines_team(t: Team) -> list:

        lines = []
        for p in t.penguins:
            lines.extend(Meth.get_lines_peng(p))

        return lines

class Logic(IClientHandler):

    gameState: GameState

    def __init__(self) -> None:
        pass
        
    def calculate_move(self) -> Move:

        print('\nmy team:')
        for l in Meth.get_lines_team(self.gameState.current_team):
            print(l)

        print('\nop team:')
        for l in Meth.get_lines_team(self.gameState.current_team.opponent):
            print(l)

        return random.choice(self.gameState.possible_moves)   

    def on_update(self, state: GameState):
        self.gameState = state

# ////////////////    Starter    ////////////////
        
if __name__ == "__main__":
    Starter(Logic())