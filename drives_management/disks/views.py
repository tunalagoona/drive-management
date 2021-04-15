import random
from typing import List, Dict

from django.shortcuts import render
import subprocess
from django.views.generic import TemplateView
import string
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


decorators = [never_cache, login_required]


class DiskManagement:
    @staticmethod
    def mount(disk) -> None:
        letters = string.ascii_lowercase
        dir_name = "".join(random.choice(letters) for i in range(4))
        mkdir = "sudo mkdir /mnt/" + dir_name.strip()
        mkdir_process = subprocess.Popen([mkdir], stdout=subprocess.PIPE, shell=True)
        out, err = mkdir_process.communicate()
        print(f"mkdir out: {out}, err: {err}")
        cmnd = "sudo mount " + "/dev/" + disk + " /mnt/" + dir_name.strip()
        print(f"command: {cmnd}")
        mount_process = subprocess.Popen([cmnd], stdout=subprocess.PIPE, shell=True)
        out, err = mount_process.communicate()
        print(f"mount out: {out}, err: {err}")

    @staticmethod
    def unmount(disk) -> None:
        cmnd = "sudo umount " + "/dev/" + disk
        process = subprocess.Popen([cmnd], stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        print(f"command: {cmnd}")
        print(f"out: {out}, err: {err}")

    @staticmethod
    def format(disk) -> None:
        cmnd = "sudo mkfs.xfs -f " + "/dev/" + disk
        print(f"command: {cmnd}")
        process = subprocess.Popen([cmnd], stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        print(f"out: {out}, err: {err}")

    @staticmethod
    def list_block_devices() -> List[Dict]:
        """Dividing lsblk into a core library (*.so) and binary is not supported yet
        so a new subprocess is created instead."""
        process = subprocess.Popen(
            ['/bin/lsblk -o NAME,SIZE,MOUNTPOINT -n -l | grep -v "^loop" | grep -v "^sr0" '],
            stdout=subprocess.PIPE,
            shell=True,
        )
        out, err = process.communicate()
        output = out.splitlines()
        disks_and_partitions = []
        for line in output:
            d_attributes = line.split()
            disk_name = d_attributes[0].decode("utf-8").strip()
            disk_size = d_attributes[1].decode("utf-8").strip()
            disk_mountpoint = ""
            if len(d_attributes) > 2:
                disk_mountpoint = d_attributes[2].decode("utf-8").strip()
            attr = {"name": disk_name, "size": disk_size, "mountpoint": disk_mountpoint}
            disks_and_partitions.append(attr)
        return disks_and_partitions


@method_decorator(decorators, name="dispatch")
class View1(TemplateView):
    def get(self, request, *args, **kwargs):
        dm = DiskManagement()
        disks: List[Dict] = dm.list_block_devices()
        sda_partitions = disks[1:6]
        sdb_partitions = disks[7:]
        context = {"sda_partitions": sda_partitions, "sdb_partitions": sdb_partitions}
        return render(request, "disks.html", context=context)

    def post(self, request, *args, **kwargs):
        print(f"request.POST: {request.POST}")
        if request.POST["disk"] == "sda1" or request.POST["disk"] == "sda2":
            print("no action will be taken")
        else:
            disk = request.POST["disk"].strip()
            dm = DiskManagement()
            if request.POST["command"] == "Mount":
                dm.mount(disk)
            elif request.POST["command"] == "Unmount":
                dm.unmount(disk)
            elif request.POST["command"] == "Format":
                dm.format(disk)
        return HttpResponseRedirect(reverse("disks"))
