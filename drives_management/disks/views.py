import logging
from typing import List, Dict

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from .disk_manager import DiskManager

logging.basicConfig(filename="log/log.log", level=logging.DEBUG)
decorators = [never_cache, login_required]


@method_decorator(decorators, name="dispatch")
class PartitionsView(TemplateView):
    def get(self, request, *args, **kwargs):
        dm = DiskManager()
        partitions: List[Dict] = dm.list_block_devices()
        context = {"partitions": partitions, "result": "", "debug": ""}
        return render(request, "disks.html", context=context)

    @staticmethod
    def post(request, *args, **kwargs):
        logging.debug(f"request.POST: {request.POST}")
        disk = request.POST["disk"].strip()
        command = request.POST["command"]

        dm = DiskManager()
        if command == "Mount":
            debug = dm.mount(disk)
            result = "Mount success" if debug.exit_code == 0 else "Mount failure, please check stdout/stderr logs"

        elif command == "Unmount":
            debug = dm.unmount(disk)
            result = "Unmount success" if debug.exit_code == 0 else "Unmount failure, please check stdout/stderr logs"
        elif command == "Format":
            debug = dm.format(disk)
            result = "Format success" if debug.exit_code == 0 else "Format failure, please check stdout/stderr logs"
        else:
            debug = None
            result = ""

        partitions: List[Dict] = dm.list_block_devices()
        context = {"partitions": partitions, "result": result, "debug": debug}

        return render(request, "disks.html", context=context)
