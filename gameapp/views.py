import json
from functools import wraps

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .authentication import JWTAuthenticationError, get_authenticated_user, require_admin
from .services import (
    add_word,
    day_report,
    delete_word,
    game_response,
    login,
    register,
    start_game,
    status,
    submit_guess,
    user_report,
    words,
)


def page(template):
    def view(request):
        return render(request, template)
    return view


def api_errors(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except JWTAuthenticationError as exc:
            status_code = 403 if str(exc) == 'Admin access required.' else 401
            return JsonResponse({'message': str(exc)}, status=status_code)
        except PermissionError as exc:
            return JsonResponse({'message': str(exc)}, status=401)
        except (ValueError, RuntimeError) as exc:
            return JsonResponse({'message': str(exc)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON body.'}, status=400)
    return wrapper


def body(request):
    return json.loads(request.body.decode('utf-8') or '{}')


@csrf_exempt
@api_errors
def auth_register(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    payload = body(request)
    return JsonResponse(register(payload.get('username'), payload.get('password')), status=201)


@csrf_exempt
@api_errors
def auth_login(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    payload = body(request)
    return JsonResponse(login(payload.get('username'), payload.get('password')))


@api_errors
def game_status(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    user = get_authenticated_user(request)
    return JsonResponse(status(user))


@api_errors
@csrf_exempt
def game_start(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    user = get_authenticated_user(request)
    return JsonResponse(start_game(user))


@api_errors
def game_get(request, game_id):
    if request.method != 'GET':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    user = get_authenticated_user(request)
    from .services import owned_game
    return JsonResponse(game_response(owned_game(user, game_id)))


@api_errors
@csrf_exempt
def game_guess(request, game_id):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    user = get_authenticated_user(request)
    payload = body(request)
    return JsonResponse(submit_guess(user, game_id, payload.get('guess')))


@api_errors
def admin_day_report(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    from datetime import date
    require_admin(request)
    raw = request.GET.get('date')
    if not raw:
        raise ValueError('Date is required.')
    try:
        selected = date.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError('Date must be in YYYY-MM-DD format.') from exc
    return JsonResponse(day_report(selected))


@api_errors
def admin_user_report(request, username):
    if request.method != 'GET':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    require_admin(request)
    return JsonResponse(user_report(username), safe=False)


@api_errors
def admin_words(request):
    if request.method == 'GET':
        require_admin(request)
        return JsonResponse(words(), safe=False)
    if request.method == 'POST':
        require_admin(request)
        payload = body(request)
        return JsonResponse(add_word(payload.get('value')), status=201)
    return JsonResponse({'message': 'Method not allowed.'}, status=405)


@api_errors
@csrf_exempt
def admin_delete_word(request, word_id):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    require_admin(request)
    delete_word(word_id)
    return HttpResponse(status=204)
