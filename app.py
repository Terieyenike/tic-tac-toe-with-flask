from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session handling

# Helper functions for game logic
def check_win(board, player):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                      (0, 3, 6), (1, 4, 7), (2, 5, 8),
                      (0, 4, 8), (2, 4, 6)]
    return any(board[i] == board[j] == board[k] == player for i, j, k in win_conditions)

def check_draw(board):
    return all(space != ' ' for space in board)

def available_moves(board):
    return [i for i, space in enumerate(board) if space == ' ']

def ai_move(board, player, opponent):
    # AI tries to win
    for move in available_moves(board):
        board[move] = player
        if check_win(board, player):
            return move
        board[move] = ' '

    # AI tries to block
    for move in available_moves(board):
        board[move] = opponent
        if check_win(board, opponent):
            board[move] = ' '
            return move
        board[move] = ' '

    # Otherwise, AI picks a random move
    return random.choice(available_moves(board))

@app.route('/')
def index():
    if 'board' not in session:
        reset_game()

    return render_template('index.html', board=session['board'], player_score=session['player_score'], ai_score=session['ai_score'], draw_count=session['draw_count'], message=session.get('message', ''))

@app.route('/play/<int:move>', methods=['POST'])
def play(move):
    board = session['board']
    current_player = session['current_player']

    if board[move] == ' ':  # Valid move
        board[move] = current_player
        session['message'] = ''

        # Check for a win or draw
        if check_win(board, current_player):
            if current_player == 'X':
                session['player_score'] += 1
                session['message'] = 'You win!'
                reset_game(False)  # Keep scores, reset board
                return redirect(url_for('index'))

            elif current_player == 'O':
                session['ai_score'] += 1
                session['message'] = 'AI wins!'
                reset_game(False)  # Keep scores, reset board
                return redirect(url_for('index'))

        elif check_draw(board):
            session['draw_count'] += 1
            session['message'] = 'It\'s a draw!'
            reset_game(False)
            return redirect(url_for('index'))

        # Switch player to AI
        if current_player == 'X':
            ai_move_pos = ai_move(board, 'O', 'X')
            board[ai_move_pos] = 'O'
            if check_win(board, 'O'):
                session['ai_score'] += 1
                session['message'] = 'AI wins!'
                reset_game(False)  # Automatically reset after AI wins
                return redirect(url_for('index'))
            elif check_draw(board):
                session['draw_count'] += 1
                session['message'] = 'It\'s a draw!'
                reset_game(False)
            session['current_player'] = 'X'
    else:
        session['message'] = 'Invalid move! Try again.'

    session['board'] = board
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    reset_game()
    return redirect(url_for('index'))

def reset_game(reset_scores=True):
    session['board'] = [' '] * 9
    session['current_player'] = 'X'  # Player starts as 'X'
    if reset_scores:
        session['player_score'] = 0
        session['ai_score'] = 0
        session['draw_count'] = 0

if __name__ == '__main__':
    app.run(debug=True)
