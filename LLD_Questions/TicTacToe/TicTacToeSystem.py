import threading
from TicTacToeAbstraction import Scoreboard, Game, Player, InvalidMoveException

class TicTacToeSystem:
    _instance=None
    _lock=threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance=super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.games={}
            self.scoreboard=Scoreboard()  # The system now manages a scoreboard
            self.initialized=True

    @classmethod
    def get_instance(cls):
        return cls._instance or cls()
    
    def create_game(self, player1:Player, player2:Player)->Game:
        self.game = Game(player1, player2)
        self.game.add_observer(self.scoreboard)
        # self.game = game  # Track the current game instance
        print(f"Game started between {player1.get_name()} (X) and {player2.get_name()} (O).")

    def make_move(self,player:Player, row:int, col:int):
        game=self.game
        if game is None:
            print("No game in progress. Please create a game first.")
            return
        
        try:
            print(f"{player.get_name()} plays at ({row}, {col})")
            self.game.make_move(player, row, col)
            self.print_board()
            print(f"Game Status: {self.game.get_status().value}")
            if self.game.get_winner() is not None:
                print(f"Winner: {self.game.get_winner().get_name()}")
        except InvalidMoveException as e:
            print(f"Error: {e}")

    def print_board(self):
        if hasattr(self, 'game') and self.game is not None:
            self.game.get_board().print_board()
        else:
            print("No game in progress. Please create a game first.")
    
    def print_score_board(self):
        self.scoreboard.print_scores()