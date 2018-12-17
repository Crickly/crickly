# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django Imports
from django.core.management.base import BaseCommand
from django.conf import settings

# App imports
from cricket.models import Performance

# Python imports
from Queue import Queue
from threading import Thread


class Command(BaseCommand):
    help = 'will fetch all current and previous matches'
    API_URL = 'http://www.play-cricket.com/api/v2/'
    queue = Queue(maxsize=0)

    def createMVPScores(self):
        """ Worker Function """
        while not self.queue.empty():  # Run continuously
            performance_id = self.queue.get()  # gets performance id from queue
            Performance.objects.filter(id=performance_id)[0].generate_mvp_scores()  # gen mvp score
            self.queue.task_done()  # tell queue job has been done

    def createWorkers(self):
        """ Creates workers/threads """
        for i in range(settings.PC_MAX_WORKERS):  # creates as many workers as defined in settings
            worker = Thread(target=self.createMVPScores)
#            worker.setDaemon(True)  # allows worker to run in background
            worker.start()  # Starts worker

    def handle(self, *args, **options):  # run after __init__
        # Selects performances without mvp score generated
        performances = Performance.objects.filter(mvp=False, match__fk_team__fantasy_league=True)
        for i in performances:
            if not i.match.is_live_score():
                self.queue.put(i.id)  # adds each performance id to queue for processing
        self.createWorkers()
        self.queue.join()  # joins back of queue. (waits till queue is empty)
        self.stdout.write('MVP scores generated')
