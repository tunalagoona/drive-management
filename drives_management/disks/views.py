from typing import List, Dict
import logging

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from .disk_management import DM


logging.basicConfig(filename="log/log.log", level=logging.DEBUG)
decorators = [never_cache, login_required]


@method_decorator(decorators, name="dispatch")
class PartitionsView(TemplateView):
    def get(self, request, *args, **kwargs):
        dm = DM()
        partitions: List[Dict] = dm.list_block_devices()
        context = {"partitions": partitions}
        return render(request, "disks.html", context=context)

    @staticmethod
    def post(request, *args, **kwargs):
        dm = DM()
        logging.debug(f"request.POST: {request.POST}")
        disk = request.POST["disk"].strip()
        if request.POST["command"] == "Mount":
            dm.mount(disk)
        elif request.POST["command"] == "Unmount":
            dm.unmount(disk)
        elif request.POST["command"] == "Format":
            dm.format(disk)
        return HttpResponseRedirect(reverse("disks"))
