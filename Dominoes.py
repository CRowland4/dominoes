import random


def _get_numbers(lists):
    """Takes a list of lists, and returns a list of all numbers within the internal lists (with repeats)"""
    numbers = []
    for nums in lists:
        for num in nums:
            numbers.append(num)

    return numbers


class DominoesGame:

    def __init__(self):
        """Initializes a game of dominoes."""
        self.stock = []
        self.player_hand = []
        self.computer_hand = []
        self.snake = []
        self.status = ''
        self.computer_hand_scores = {}

    def main_loop(self):
        """The main loop of the game."""
        self._setup()

        while True:
            self._update_computer_scores()
            status = self._get_status_message()
            self._print_interface()
            print('\nStatus: ' + status)

            if status.startswith("The game is over."):
                return

            self._execute_play()
            self._flip_status()

    def _update_computer_scores(self):
        """Updates computer_hand_scores attribute."""
        snake_nums = _get_numbers(self.snake)
        com_hand_nums = _get_numbers(self.computer_hand)
        self._update_domino_scores(snake_nums, com_hand_nums)

        return

    def _update_domino_scores(self, list1, list2):
        """Calculates individual domino scores for the computer hand, and updates the computer hand scores attribute"""
        self.computer_hand_scores.clear()
        for i, dom in enumerate(self.computer_hand):
            score = 0

            score += sum(
                [
                    list1.count(dom[0]),
                    list1.count(dom[1]),
                    list2.count(dom[0]),
                    list2.count(dom[1])
                ]
            )

            self.computer_hand_scores[str(i + 1)] = score

        return

    def _execute_play(self):
        """Moves the game forward by one turn."""
        method = getattr(self, '_get_' + self.status + '_move')
        play = method()
        domino, position = play[0], play[1]
        hand = getattr(self, self.status + "_hand")
        if not domino:
            self._skip_turn()
            return

        hand.remove(domino)
        domino = self._orient_domino(domino, position)

        if position == 'left':
            self.snake.insert(0, domino)
        elif position == 'right':
            self.snake.append(domino)

        return

    def _orient_domino(self, domino, position):
        """Returns a rotated domino to line up with the snake, or returns the same domino if no rotation is needed."""
        if domino[1] == self.snake[0][0] and position == 'left':
            return domino
        if domino[0] == self.snake[0][0] and position == 'left':
            domino.reverse()
            return domino
        if domino[0] == self.snake[-1][1] and position == 'right':
            return domino
        if domino[1] == self.snake[-1][1] and position == 'right':
            domino.reverse()
            return domino

    def _skip_turn(self):
        """Adds a piece from the stockpile to the appropriate hand."""
        if not self.stock:
            return

        hand = getattr(self, self.status + '_hand')
        piece = random.choice(self.stock)
        self.stock.remove(piece)
        hand.append(piece)
        return

    def _validate_choice(self, move):
        """Boolean, verifies that the chosen domino is a legal play."""
        hand = getattr(self, self.status + "_hand")
        domino = hand[abs(int(move)) - 1]
        if int(move) == 0:
            return True
        if int(move) < 0:
            return any((domino[0] == self.snake[0][0], domino[1] == self.snake[0][0]))
        if int(move) > 0:
            return any((domino[0] == self.snake[-1][1], domino[1] == self.snake[-1][1]))

    def _get_player_move(self):
        """Returns the player-selected domino and location, or returns '0' if the player skips."""
        move = input()
        if not self._validate_input(move):
            print("Invalid input. Please try again.")
            return self._get_player_move()
        if not self._validate_choice(move):
            print("Illegal move. Please try again.")
            return self._get_player_move()

        return self._domino_selection(move)

    def _get_computer_move(self):
        """Returns the playable domino with the highest score based on the algorithm, or '0' if no playable pieces."""
        _ = input()

        scores_dict = dict(self.computer_hand_scores)
        while True:
            if not scores_dict:
                return self._domino_selection('0')

            max_score = max(scores_dict.values())
            moves = [move for move in scores_dict.keys() if scores_dict[move] == max_score]

            if self._validate_choice(moves[0]):
                return self._domino_selection(moves[0])
            else:
                del scores_dict[moves[0]]

    def _domino_selection(self, move):
        """Reusable code for getting the domino and location or '0' for skip from either the player or the computer."""
        if move == '0':
            return [0, None]

        hand = getattr(self, self.status + '_hand')

        if int(move) < 0:
            return hand[abs(int(move)) - 1], 'left'
        if int(move) > 0:
            return hand[int(move) - 1], 'right'

    def _validate_input(self, move):
        """Boolean, validates that the player input is of the correct format."""
        hand = getattr(self, self.status + '_hand')
        if move and move[-1].isnumeric() and int(move) in range(-len(hand), len(hand) + 1):
            return True
        else:
            return False

    def _setup(self):
        """Sets up the game with a stockpile and dealt hands."""
        self._create_stock()
        self._deal_dominoes()

        if self._validate_hands():
            self._find_starter()
            return
        else:
            self._reset()
            return self._setup()

    def _reset(self):
        """Resets the game attributes and status for a re-deal."""
        self.stock = []
        self.computer_hand = []
        self.player_hand = []
        self.snake = []
        self.status = ''

        return

    def _create_stock(self):
        """Creates the initial set of dominoes from which the game will be played."""
        i = 0
        while i < 7:

            for num in range(i, 7):
                self.stock.append([i, num])

            i += 1

        return

    def _deal_dominoes(self):
        """Deals 7 dominoes to both the player and the computer from the stock."""
        for _ in range(7):
            domino = random.choice(self.stock)
            self.computer_hand.append(domino)
            self.stock.remove(domino)

        for _ in range(7):
            domino = random.choice(self.stock)
            self.player_hand.append(domino)
            self.stock.remove(domino)

        return

    def _validate_hands(self):
        """Makes sure that at least one hand dealt has a double."""
        for domino in (self.computer_hand + self.player_hand):
            if domino[0] == domino[1]:
                return True
            else:
                continue

        return False

    def _find_starter(self):
        """Determines who has the starting piece and updates the game status and snake accordingly."""
        doubles = list(filter(lambda dom: dom[0] == dom[1], self.computer_hand + self.player_hand))
        max_double = max([dom[0] for dom in doubles])
        self.snake.append([max_double, max_double])

        if self.snake[0] in self.computer_hand:
            self.computer_hand.remove(self.snake[0])
            self.status = 'player'
        elif self.snake[0] in self.player_hand:
            self.player_hand.remove(self.snake[0])
            self.status = 'computer'

        return

    def _print_interface(self):
        """Prints the game interface with the current snake and player hand."""
        print("=" * 70)
        print(f'Stock size: {len(self.stock)}')
        print(f'Computer pieces: {len(self.computer_hand)}\n')

        self._print_snake()

        print("\n\nYour pieces:")

        for i, domino in enumerate(self.player_hand):
            print(f'{i + 1}: {domino}')

        return

    def _print_snake(self):
        """Print out the snake in the specified format."""
        if len(self.snake) <= 6:
            print(*self.snake, sep='')
        else:
            print(*self.snake[:3], '...', *self.snake[-3:], sep='')

        return

    def _get_status_message(self):
        """Returns the appropriate status message for the state of the game."""
        if not self.player_hand:
            return "The game is over. You won!"
        if not self.computer_hand:
            return "The game is over. The computer won!"
        if self._check_draw():
            return "The game is over. It's a draw!"
        if self.status == 'player':
            return "It's your turn to make a move. Enter your command."
        if self.status == 'computer':
            return "Computer is about to make a move. Press Enter to continue..."

    def _check_draw(self):
        """Checks to see if the game is a draw."""
        numbers_played = []

        for dom in self.snake:
            numbers_played.append(dom[0])
            numbers_played.append(dom[1])

        if numbers_played[0] == numbers_played[-1] and numbers_played.count(numbers_played[0]) == 8:
            return True

        return False

    def _flip_status(self):
        """Flips the status of the game between 'player' and 'computer.'"""
        if self.status == 'player':
            self.status = 'computer'
            return
        if self.status == 'computer':
            self.status = 'player'
            return

        return


game1 = DominoesGame()
game1.main_loop()


