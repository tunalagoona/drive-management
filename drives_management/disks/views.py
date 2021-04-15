import random

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


@method_decorator(decorators, name='dispatch')
class View1(TemplateView):
    def get(self, request, *args, **kwargs):
        """Dividing lsblk into a core library (*.so) and binary is not supported yet
        so a new subprocess is created instead."""
        process = subprocess.Popen(
            ['/bin/lsblk -o NAME,SIZE,MOUNTPOINT -n -l | grep -v "^loop" | grep -v "^sr0" '],
            stdout=subprocess.PIPE,
            shell=True,
        )
        out, err = process.communicate()
        attributes = []

        res = out.splitlines()

        for disk in res:
            d_attributes = disk.split()
            disk_name = d_attributes[0].decode("utf-8").strip()
            disk_size = d_attributes[1].decode("utf-8").strip()
            disk_mountpoint = ""
            if len(d_attributes) > 2:
                disk_mountpoint = d_attributes[2].decode("utf-8").strip()
            attr = {"name": disk_name, "size": disk_size, "mountpoint": disk_mountpoint}
            attributes.append(attr)

        sda_partitions = attributes[1:6]
        sdb_partitions = attributes[7:]

        context = {"disks": attributes, "sda_partitions": sda_partitions, "sdb_partitions": sdb_partitions}
        return render(request, "disks.html", context=context)

    def post(self, request, *args, **kwargs):
        print(f"request.POST: {request.POST}")
        if request.POST["disk"] == "sda1" or request.POST["disk"] == "sda2":
            print("no action will be taken")
        else:
            disk = request.POST["disk"].strip()
            if request.POST["command"] == "Mount":
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

            elif request.POST["command"] == "Unmount":
                cmnd = "sudo umount " + "/dev/" + disk
                process = subprocess.Popen([cmnd], stdout=subprocess.PIPE, shell=True)
                out, err = process.communicate()
                print(f"command: {cmnd}")
                print(f"out: {out}, err: {err}")

            elif request.POST["command"] == "Format":
                cmnd = "sudo mkfs.xfs -f " + "/dev/" + disk
                print(f"command: {cmnd}")
                process = subprocess.Popen([cmnd], stdout=subprocess.PIPE, shell=True)
                out, err = process.communicate()
                print(f"out: {out}, err: {err}")

        return HttpResponseRedirect(reverse('disks'))
