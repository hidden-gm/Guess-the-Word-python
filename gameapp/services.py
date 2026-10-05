import random
import re
from collections import Counter

from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone

from .authentication import create_token
from .models import Game, Guess, User, Word

DAILY_LIMIT = 3
MAX_GUESSES = 5
USERNAME_RE = re.compile(r'^[A-Za-z]{5,40}$')
PASSWORD_RE = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$%*]).{5,72}$')
WORD_RE = re.compile(r'^[A-Z]{5}$')


def safe(value):
    return '' if value is None else str(value).strip()


def auth_response(user):
    return {'token': create_token(user), 'username': user.username, 'role': user.role}


def register(username, password):
    username = safe(username)
    if not USERNAME_RE.fullmatch(username):
        raise ValueError('Username must contain only letters and be 5-40 characters long.')
    if password is None or not PASSWORD_RE.fullmatch(password):
        raise ValueError('Password must be at least 5 characters with letters, numbers, and one of $, %, *.')
    if User.objects.filter(username=username).exists():
        raise ValueError('Username is already registered.')

    user = User.objects.create_user(username=username, password=password, role=User.Role.PLAYER)
    return auth_response(user)


def login(username, password):
    username = safe(username)
    user = authenticate(username=username, password=password)
    if user is None:
        raise PermissionError('Invalid username or password.')
    return auth_response(user)


def today():
    return timezone.localdate()


def status(user):
    current_day = today()
    used = Game.objects.filter(user=user, game_date=current_day).count()
    active = (Game.objects.filter(user=user, game_date=current_day, completed=False)
              .order_by('-id').first())
    return {
        'gamesUsedToday': used,
        'gamesRemainingToday': max(0, DAILY_LIMIT - used),
        'activeGameId': active.id if active else None,
    }


def start_game(user):
    current_day = today()
    active = (Game.objects.filter(user=user, game_date=current_day, completed=False)
              .order_by('-id').first())
    if active:
        used = Game.objects.filter(user=user, game_date=current_day).count()
        return {
            'gameId': active.id,
            'gamesUsedToday': used,
            'gamesRemainingToday': max(0, DAILY_LIMIT - used),
            'status': 'RESUMED',
        }

    used = Game.objects.filter(user=user, game_date=current_day).count()
    if used >= DAILY_LIMIT:
        raise RuntimeError('Daily limit reached. You can play at most 3 games per day.')

    words = list(Word.objects.all())
    if not words:
        raise RuntimeError('No words are configured by the admin.')
    target = random.choice(words)
    game = Game.objects.create(user=user, word=target, game_date=current_day)
    new_used = used + 1
    return {
        'gameId': game.id,
        'gamesUsedToday': new_used,
        'gamesRemainingToday': DAILY_LIMIT - new_used,
        'status': 'STARTED',
    }


def owned_game(user, game_id):
    try:
        game = Game.objects.select_related('user', 'word').get(id=game_id)
    except Game.DoesNotExist as exc:
        raise ValueError('Game not found.') from exc
    if game.user_id != user.id:
        raise ValueError('You do not have access to this game.')
    return game


def evaluate(guess, target):
    result = [None] * 5
    remaining = Counter()

    for i in range(5):
        if guess[i] == target[i]:
            result[i] = 'GREEN'
        else:
            remaining[target[i]] += 1

    for i in range(5):
        if result[i] is not None:
            continue
        if remaining[guess[i]] > 0:
            result[i] = 'ORANGE'
            remaining[guess[i]] -= 1
        else:
            result[i] = 'GREY'
    return result


def game_response(game, message=''):
    rows = [
        {'guess': guess.value, 'tiles': guess.result.split(',')}
        for guess in game.guesses.order_by('id')
    ]
    return {
        'gameId': game.id,
        'guessCount': game.guesses_used,
        'maxGuesses': MAX_GUESSES,
        'completed': game.completed,
        'won': game.won,
        'message': message,
        'guesses': rows,
    }


@transaction.atomic
def submit_guess(user, game_id, guess):
    game = owned_game(user, game_id)
    if game.completed:
        raise RuntimeError('This game has already ended.')
    if not WORD_RE.fullmatch(guess or ''):
        raise ValueError('Guess must be exactly 5 uppercase letters.')
    if game.guesses_used >= MAX_GUESSES:
        raise RuntimeError('Maximum of 5 guesses reached.')

    tiles = evaluate(guess, game.word.value)
    won = guess == game.word.value
    game.guesses_used += 1
    game.won = won
    message = ''

    if won:
        game.completed = True
        game.completed_at = timezone.now()
        message = 'CONGRATULATIONS! You found the word.'
    elif game.guesses_used == MAX_GUESSES:
        game.completed = True
        game.completed_at = timezone.now()
        message = 'BETTER LUCK NEXT TIME!'

    Guess.objects.create(game=game, value=guess, result=','.join(tiles))
    game.save(update_fields=['guesses_used', 'won', 'completed', 'completed_at'])
    return game_response(game, message)


def day_report(date):
    qs = Game.objects.filter(game_date=date)
    return {
        'users': qs.values('user_id').distinct().count(),
        'correctGuesses': qs.filter(won=True).count(),
    }


def user_report(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist as exc:
        raise ValueError('User not found.') from exc

    rows = []
    # Keep this explicit and portable across SQLite/PostgreSQL/MySQL.
    dates = sorted(Game.objects.filter(user=user).values_list('game_date', flat=True).distinct(), reverse=True)
    for game_date in dates:
        games = Game.objects.filter(user=user, game_date=game_date)
        rows.append({
            'date': game_date.isoformat(),
            'wordsTried': games.count(),
            'correctGuesses': games.filter(won=True).count(),
        })
    return rows


def words():
    return list(Word.objects.order_by('id').values('id', 'value'))


def add_word(value):
    normalized = safe(value).upper()
    if not WORD_RE.fullmatch(normalized):
        raise ValueError('Word must be exactly 5 uppercase letters.')
    if Word.objects.filter(value=normalized).exists():
        raise ValueError('Word already exists.')
    word = Word.objects.create(value=normalized)
    return {'id': word.id, 'value': word.value}


def delete_word(word_id):
    try:
        word = Word.objects.get(id=word_id)
    except Word.DoesNotExist as exc:
        raise ValueError('Word not found.') from exc
    if Word.objects.count() <= 1:
        raise RuntimeError('At least one word must remain configured.')
    if Game.objects.filter(word=word).exists():
        raise RuntimeError('This word is already attached to a game and cannot be deleted.')
    word.delete()
