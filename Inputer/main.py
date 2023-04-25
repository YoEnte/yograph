from socha import *
import random
import time

class Logic(IClientHandler):

    gameState: GameState

    def __init__(self) -> None:
        pass

    def calculate_move(self) -> Move:
        '''Uses the inputs `f_in` and `t_in` to create a new board graph without the selected node'''

        m = None

        while m not in self.gameState.possible_moves:

            if m != None:
                print('wrong move\n')
        
            f_in = input('From: ')
            t_in = input('To: ')

            try:
                f = None if f_in == '' else CartesianCoordinate(int(f_in[0]), int(f_in[-1])).to_hex()
                t = CartesianCoordinate(int(t_in[0]), int(t_in[-1])).to_hex()
            except:
                f = None
                t = HexCoordinate(999, 999)

            m = Move(self.gameState.current_team.team(), t, f)

        return m

    def on_update(self, state: GameState):
        self.gameState = state

# ////////////////    Starter    ////////////////
        
if __name__ == "__main__":
    Starter(Logic())