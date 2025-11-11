from enum import Enum
from typing import Optional
from abc import ABC, abstractmethod
import threading

class InvalidMoveException(Exception):
    def __init__(self, message:str):
        super().__init__(message)

class GameStatus(Enum):
    InProgress='InProgress'
    Draw='Draw'
    X_Won='X_Won'
    O_Won='O_Won'

class Symbol(Enum):
    X='X'
    O='O'
    Empty='_'

    def get_char(self)->str:
        return self.value

class Player:
    def __init__(self, name:str, symbol:Symbol):
        self.name=name
        self.symbol=symbol

    def get_name(self)->str:
        return self.name
    
    def get_symbol(self)->Symbol:
        return self.symbol
    
class Cell:
    def __init__(self):
        self.symbol=Symbol.Empty
        
    def set_symbol(self, symbol:Symbol):
        self.symbol=symbol

    def get_symbol(self)->Symbol:
        return self.symbol
    
class Board:
    def __init__(self, size:int):
        self.size=size
        self.board=[]
        self.moves_made=0

        for _ in range(self.size):
            board_row=[]
            for _ in range(self.size):
                board_row.append(Cell())
            self.board.append(board_row)

    def get_size(self)->int:
        return self.size
    
    def get_cell(self, row:int, col:int)->Optional[Cell]:
        if row<0 or row>=self.size or col<0 or col>=self.size:
            return None
        return self.board[row][col]
    
    def print_board(self):
        print("--------------------")
        for row in range(self.size):
            print("| ", end="")
            for col in range(self.size):
                symbol=self.board[row][col].get_symbol()
                print(f"{symbol.get_char()} | ", end="")
            print("\n--------------------")

    def make_move(self, row:int, col:int, player:Player)->bool:
        if row<0 or row>=self.size or col<0 or col>=self.size:
            raise InvalidMoveException("Invalid position: Out of bounds")
        if self.board[row][col].get_symbol()!=Symbol.Empty:
            raise InvalidMoveException("Invalid position: Cell already occupied")
        
        self.board[row][col].set_symbol(player.get_symbol())
        self.moves_made+=1
        return True
    
    def is_full(self)->bool:
        return self.moves_made==self.size*self.size

# Strategy Pattern for winning condition
class WinningStrategy(ABC):
    @abstractmethod
    def check_winner(self, board:Board, player:Player)->bool:
        pass
# Concrete Strategies
# Strategy 1: Row Winning Strategy
class RowWinningStrategy(WinningStrategy):
    def check_winner(self, board:Board, player:Player)->bool:
        size=board.get_size()
        symbol=player.get_symbol()

        for row in range(size):
            win=True
            for col in range(size):
                    cell = board.get_cell(row, col)
                    if cell.get_symbol()!=symbol:
                        win=False
                        break
            if win:
                return True
        return False
    
# Strategy 2: Column Winning Strategy
class ColumnWinningStrategy(WinningStrategy):
    def check_winner(self, board:Board, player:Player)->bool:
        size=board.get_size()
        symbol=player.get_symbol()

        for col in range(size):
            win=True
            for row in range(size):
                    cell = board.get_cell(row, col)
                    if cell.get_symbol()!=symbol:
                        win=False
                        break
            if win:
                return True
        return False
    
# Strategy 3: Diagonal Winning Strategy
class DiagonalWinningStrategy(WinningStrategy):
    def check_winner(self, board:Board, player:Player)->bool:
        size=board.get_size()
        symbol=player.get_symbol()

        diag_win=True
        for row in range(size):
                cell = board.get_cell(row, row)
                if cell.get_symbol()!=symbol:
                    diag_win=False
                    break
        if diag_win:
            return True
        
        anti_diag_win=True
        for row in range(size):
                cell = board.get_cell(row, size-row-1)
                if cell.get_symbol()!=symbol:
                    anti_diag_win=False
                    break
        return anti_diag_win
    

# Observer Pattern for game state changes
class GameObserver(ABC):
    @abstractmethod
    def update(self, game):
        pass
# Subject for the observers
class GameSubject(ABC):
    def __init__(self):
        self.observers=[]

    def add_observer(self, observer:GameObserver):
        self.observers.append(observer)

    def remove_observer(self, observer:GameObserver):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

# Concrete Observer: Scoreboard
class Scoreboard(GameObserver):
    def __init__(self):
        self.scores={}

    def update(self, game):
        if game.get_winner() is not None:
            winner=game.get_winner().get_name()
            self.scores[winner]=self.scores.get(winner,0)+1
            print(f"[Scoreboard] {winner} wins! Their new score is {self.scores[winner]}.")
    
    def print_scores(self):
        print("\n--- Overall Scoreboard ---")
        if not self.scores:
            print("No games with a winner have been played yet.")
            return
        
        for player_name, score in self.scores.items():
            print(f"Player: {player_name:<10} | Wins: {score}")
        print("--------------------------\n")
        

class Game(GameSubject):
    def __init__(self, player1:Player, player2:Player):
        super().__init__()
        self.board=Board(3)
        self.player1=player1
        self.player2=player2
        self.state=InProgressState()
        self.status=GameStatus.InProgress
        self.winner=None
        self.winning_strategies=[RowWinningStrategy(), ColumnWinningStrategy(), DiagonalWinningStrategy()]
        self.current_player=player1

    def make_move(self, player:Player, row:int, col:int):
        self.state.handle_move(self, player, row, col)
    
    def switch_player(self):
        if self.current_player==self.player1:
            self.current_player=self.player2
        else:
            self.current_player=self.player1
    
    def check_winner(self, player:Player)->bool:
        for strategy in self.winning_strategies:
            if strategy.check_winner(self.board, player):
                return True
        return False
    
    def set_state(self, state:'GameState'):
        self.state=state

    def get_state(self)->'GameState':
        return self.state
    
    def get_status(self)->GameStatus:
        return self.status
    
    def set_status(self, status:GameStatus):
        self.status=status
        if status != GameStatus.InProgress:
            self.notify_observers()

    def get_winner(self)->Optional[Player]:
        return self.winner
    
    def set_winner(self, player:Player):
        self.winner=player

    def get_board(self)->Board:
        return self.board
    
    def get_current_player(self)->Player:
        return self.current_player


    
# State Pattern for game states
class GameState(ABC):
    @abstractmethod
    def handle_move(self, game, player:Player, row:int, col:int):
        pass

class InProgressState(GameState):
    def handle_move(self, game, player:Player, row:int, col:int):
        if player != game.get_current_player():
            raise InvalidMoveException("It's not your turn")
        
        board=game.get_board()
        board.make_move(row, col, player)
        if game.check_winner(player):
            game.set_winner(player)
            game.set_state(WinningState())
            game.set_status(GameStatus.X_Won if player.get_symbol()==Symbol.X else GameStatus.O_Won)
        elif board.is_full():
            game.set_state(DrawState())
            game.set_status(GameStatus.Draw)
        else:
            game.switch_player()


class DrawState(GameState):
    def handle_move(self, game, player:Player, row:int, col:int):
        raise InvalidMoveException("Game is a draw. No more moves allowed.")
    
class WinningState(GameState):
    def handle_move(self, game, player:Player, row:int, col:int):
        raise InvalidMoveException(f"Game is over. player {game.get_winner().get_name()} has already won. No more moves allowed.")
    
