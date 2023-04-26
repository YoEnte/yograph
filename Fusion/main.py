from socha import *
from yograph import YoGraph
import random

class Logic(IClientHandler):

    gameState: GameState

    def __init__(self) -> None:
        
        self.init = False #for either constructing graph or making a move

    def calculate_move(self) -> Move:
        pass

        return random.choice(self.gameState.possible_moves)

    def on_update(self, state: GameState):
        self.gameState = state
        
        # custom init -> graph init / else: make move
        if not self.init:
            self.main_graph = YoGraph.full_construct_from_board(YoGraph(), self.gameState.board.board)
            self.main_graph.visual_game = True

            self.init = True
        else:
            self.main_graph.make_move(self.gameState.last_move)

        self.main_graph.get_blobs()

        # show graph if visual mode is on
        if self.main_graph.visual_game:
            self.main_graph.generate_maps()
            self.main_graph.draw('', 0.1, (self.gameState.first_team.fish, self.gameState.second_team.fish))
        


# ////////////////    Starter    ////////////////
        
if __name__ == "__main__":
    Starter(Logic())
