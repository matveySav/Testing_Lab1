import pytest
from Game import Game, Figure, GameMixin, WrongMove


class TestChessGame:
    @pytest.fixture
    def game(self):
        game = Game()
        game.board = [['_' for _ in range(8)] for _ in range(8)]
        return game
    
    @pytest.mark.parametrize("algebraic,expected_matrix", [
        ('a1', [7, 0]),
        ('h1', [7, 7]),
        ('a8', [0, 0]),
        ('h8', [0, 7])
    ])
    def test_translate_coordinates_correct(self, algebraic, expected_matrix):
        # Act
        result = GameMixin.translate_to_pos(algebraic)
        back_result = GameMixin.translate_to_str(expected_matrix)
        # Assert
        assert result == expected_matrix, f"Failed for {algebraic}: expected{expected_matrix}, got {result}"
        assert back_result == algebraic, f"Reverse failed for {expected_matrix}: expected {algebraic}, got {back_result}"

    @pytest.mark.parametrize("invalid_coord", ['', 'a', 'a9', 'i1', 'a0', 'a10', 'z5'])
    def test_translate_coordinates_invalid(self, invalid_coord):
        # Act & Assert
        with pytest.raises(WrongMove):
            GameMixin.translate_to_pos(invalid_coord)

    def test_pawn_possible_moves_initial_white(self, game):
        # Arrange
        game.board[6][4] = Figure('pawn', 'white')  # e2
        expected_moves = [[5, 4], [4, 4]]  # e3, e4
        
        # Act
        possible_moves = game.possible_moves([6, 4])
        
        # Assert
        assert len(possible_moves) == len(expected_moves)
        for move in expected_moves:
            assert move in possible_moves

    def test_rook_edge_of_board_moves(self, game):
        # Arrange
        game.board[0][0] = Figure('rook', 'white')  # a8
        
        # Act
        possible_moves = game.possible_moves([0, 0])
        
        # Assert
        for move in possible_moves:
            assert 0 <= move[0] <= 7
            assert 0 <= move[1] <= 7

    def test_capture_moves(self, game):
        # Arrange
        game.board[4][4] = Figure('pawn', 'white')  # e4
        game.board[3][3] = Figure('pawn', 'black')  # d5
        game.board[3][5] = Figure('pawn', 'black')  # f5
        
        # Act
        possible_moves = game.possible_moves([4, 4])
        
        # Assert
        capture_moves = [[3, 3], [3, 5]]
        for capture_move in capture_moves:
            assert capture_move in possible_moves

    def test_empty_square_move_attempt(self, game):
        # Act
        result = game.rules([4, 4], [3, 4])  # Попытка хода пустой клеткой
        
        # Assert
        assert result == 0, "Moving empty square"

    def test_king_in_check_situation(self, game):
        """Тест ситуации шаха королю"""
        # Arrange
        game.board[7][4] = Figure('king', 'white')  # e1
        game.board[0][4] = Figure('rook', 'black')  # e8
        
        # Act
        is_king_in_check = game.is_check([7, 4])  # Позиция белого короля
        
        # Assert
        assert is_king_in_check == 1, "King should be in check"

    def test_knight_possible_moves_corner(self, game):
        # Arrange
        game.board[7][0] = Figure('knight', 'white')  # a1
        expected_moves = [[5, 1], [6, 2]]  # b3, c2
        
        # Act
        possible_moves = game.possible_moves([7, 0])
        
        # Assert
        assert len(possible_moves) == len(expected_moves)
        for move in expected_moves:
            assert move in possible_moves

    def test_rules_invalid_move_wrong_turn(self, game):
        """Тест правил для хода не в свою очередь"""
        # Arrange
        game.board[6][4] = Figure('pawn', 'white')  # e2
        game.board[1][4] = Figure('pawn', 'black')  # e7
        game.move_num = 1  # Ход черных
        
        # Act
        result = game.rules([6, 4], [5, 4])  # Белые пытаются ходить в очередь черных
        
        # Assert
        assert result == 0, "Wrong turn move should return 0"

    def test_checkmate_detection_simplified(self, game):
        # Arrange 
        game.board[7][4] = Figure('king', 'white')  # e1
        game.board[6][0] = Figure('queen', 'black')  # a2
        game.board[7][1] = Figure('queen', 'black')  # b1
        
        # Act
        is_checkmate = game.checkmate([7, 4])  # Позиция белого короля
        
        # Assert
        assert is_checkmate, "Should detect checkmate"

class TestChessFigure:
    @pytest.mark.parametrize("figure_type,color", [
        ('pawn', 'white'),
        ('king', 'black'),
        ('queen', 'white')
    ])
    def test_figure_creation(self, figure_type, color):
        # Act
        figure = Figure(figure_type, color)
        
        # Assert
        assert figure.type == figure_type
        assert figure.color == color

    def test_figure_comparison(self):
        # Arrange
        pawn = Figure('pawn', 'white', value=1)
        queen = Figure('queen', 'white', value=9)
        
        # Assert
        assert pawn < queen
        assert queen > pawn

class MockGame(Game):
    def __init__(self):
        super().__init__()
        self.rules_called = False
        self.is_check_called = False
        self.is_checkmate_called = False

class TestChessFunctions:
    @pytest.fixture
    def game(self):
        game = MockGame()
        game.board = [['_' for _ in range(8)] for _ in range(8)]
        game.board[7][4] = Figure('king', 'white')  # e1
        game.board[0][4] = Figure('king', 'black')  # e1
        game.board[6][0] = Figure('queen', 'black')  # a2
        game.board[0][1] = Figure('queen', 'black')  # b8
        game.move_num = 1 # ход черных
        return game

    def test_rules_call_when_move(self,game):
        # Arrange
        def rules(self,*args):
            self.rules_called = True
        game.rules = rules.__get__(game)
        # Act
        game.move([0,1],[7,1])
        game.move_num += 1
        # Assert
        assert game.rules_called == True

    def test_is_check_call_when_move(self,game):
        # Arrange
        def is_check(self,king_pos):
            self.is_check_called = True
        game.is_check = is_check.__get__(game)
        # Act
        game.move([0,1],[7,1])
        # Assert
        assert game.is_check_called == True

    def test_is_checkmate_call_when_move(self,game):
        # Arrange
        def is_checkmate(self,pos):
            self.is_checkmate_called = True
        game.checkmate = is_checkmate.__get__(game)
        # Act
        game.move([0,1],[7,1])
        # Assert
        assert game.is_checkmate_called == True