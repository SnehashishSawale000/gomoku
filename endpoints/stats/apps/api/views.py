# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User

from .models import Round, PlayerPosition
from .decorators import expect_json


def save_player_stats(creator, opponent, winner):
    if winner:
        looser = opponent if winner == creator else creator

        player_pos, created = PlayerPosition.objects.get_or_create(
            player=winner, defaults={'wins': 1})
        if not created:
            player_pos.wins += 1
            player_pos.save(update_fields=['wins'])

        player_pos, created = PlayerPosition.objects.get_or_create(
            player=looser, defaults={'losses': 1})
        if not created:
            player_pos.losses += 1
            player_pos.save(update_fields=['losses'])
    else:
        for player in [creator, opponent]:
            player_pos, created = PlayerPosition.objects.get_or_create(
                player=player, defaults={'draws': 1})
            if not created:
                player_pos.draws += 1
                player_pos.save(update_fields=['draws'])


@require_http_methods(["POST"])
@expect_json
def round_save(request):
    ALLOWED_KEYS = [
        'creator', 'opponent', 'dimension', 'lineup',
        'black_stone_owner', 'moves', 'winner']
    data = request.json_post_data

    if set(ALLOWED_KEYS) != set(data.keys()):
        raise HttpResponseServerError('Wrong JSON keys.')

    creator, created = User.objects.get_or_create(username=data['creator'])
    opponent, created = User.objects.get_or_create(username=data['opponent'])
    dimension = data['dimension']
    lineup = data['lineup']
    black_stone_owner, created = User.objects.get_or_create(
        username=data['black_stone_owner'])
    moves = data['moves']

    winner = None
    if data['winner']:
        winner, created = User.objects.get_or_create(
            username=data['winner'])

    if (creator == opponent) or (winner not in [creator, opponent]):
        raise HttpResponseServerError('Wrong JSON value.')

    Round.objects.create(
        creator=creator, opponent=opponent, dimension=dimension,
        lineup=lineup, black_stone_owner=black_stone_owner,
        moves=moves, winner=winner)

    save_player_stats(creator, opponent, winner)

    return HttpResponse()