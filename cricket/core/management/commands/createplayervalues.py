# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django Imports
from django.core.management.base import BaseCommand
from django.conf import settings

# App Imports
from cricket.models import Player

# Python Imports
from Queue import Queue
from threading import Thread
from datetime import date


class Command(BaseCommand):
    help = 'will fetch all current and previous matches'  # help message
    queue = Queue(maxsize=0)  # Creates infinite size queue

    def createPlayerValues(self):
        """ Worker function """
        while not self.queue.empty():
            player_id = self.queue.get()  # Gets id from queue
            Player.objects.filter(id=player_id)[0].set_value()  # Sets Value
            self.queue.task_done()

    def createWorkers(self):
        for i in range(settings.PC_MAX_WORKERS):
            worker = Thread(target=self.createPlayerValues)
            worker.start()  # starts worker

    def handle(self, *args, **options):
        """ Default command handler. Run after __init__ """
        players = Player.objects.filter(kvcc_player=True)  # Gets all players in club
        for i in players:
            if i.played_game([date.today().year - 1]):  # Checks if player has played last season
                self.queue.put(i.id)  # Adds player to queue
        self.createWorkers()
        self.queue.join()
        self.stdout.write('Player values generated')
