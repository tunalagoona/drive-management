import random

from django.shortcuts import render
import subprocess
from django.views.generic import TemplateView
import string


class View1(TemplateView):
    def get(self, request, *args, **kwargs):
        """Dividing lsblk into a core library (*.so) and binary is not supported yet
        so a new subprocess is created instead."""
        process = subprocess.Popen(['/bin/lsblk -o NAME,SIZE,MOUNTPOINT -n -l | grep -v "^loop" | grep -v "^sr0" '],
                                   stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        attributes = []

        res = out.splitlines()

        for disk in res:
            d_attributes = disk.split()
            disk_name = d_attributes[0].decode("utf-8").strip()
            disk_size = d_attributes[1].decode("utf-8").strip()
            disk_mountpoint = ''
            if len(d_attributes) > 2:
                disk_mountpoint = d_attributes[2].decode("utf-8").strip()
            attr = {'name': disk_name, 'size': disk_size, 'mountpoint': disk_mountpoint}
            attributes.append(attr)

        sda_partitions = attributes[1:6]
        sdb_partitions = attributes[7:]

        context = {
            'disks': attributes,
            'sda_partitions': sda_partitions,
            'sdb_partitions': sdb_partitions
        }
        return render(request, 'disks.html', context=context)
