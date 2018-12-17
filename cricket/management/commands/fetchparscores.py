# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.conf import settings
from cricket.models import Match, Inning, Player, Performance
from Queue import Queue
from threading import Thread
from datetime import datetime, date
import requests
import json


class Command(BaseCommand):
    help = 'will fetch all current and previous matches'
    API_URL = 'http://www.play-cricket.com/api/v2/'
    queue = Queue(maxsize=0)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.createWorkers()

    def add_arguments(self, parser):
        pass

    def get_data(self, url):
        r = requests.get(
            self.API_URL + url + '&api_token={}'.format(settings.PC_API_KEY)
        )
        if r.ok:
            return json.loads(r.content)
        else:
            r.raise_for_status()

    def fetchMatch(self):
        while not self.queue.empty():
            pass

    def createWorkers(self):
        for i in range(settings.PC_MAX_WORKERS):
            worker = Thread(target=self.fetchMatch)
            worker.setDaemon(True)
            worker.start()

    def handle(self, *args, **options):
        self.stdout.write('Nothing Happened!!!!')
