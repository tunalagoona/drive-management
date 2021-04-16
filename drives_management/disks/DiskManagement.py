import subprocess
import random
import json
import string
import logging
from typing import List, Dict

logger = logging.getLogger()


class DM:
    @staticmethod
    def call_subprocess(command):
        process = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        return out, err

    def mount(self, disk) -> None:
        letters = string.ascii_lowercase
        dir_name = "".join(random.choice(letters) for i in range(4))
        mkdir = "mkdir /mnt/" + dir_name.strip()
        out, err = self.call_subprocess(mkdir)
        logging.debug(f"mkdir output: {out}, err: {err}")

        mount_cmnd = "mount " + "/dev/" + disk + " /mnt/" + dir_name.strip()
        logging.debug(f"mount command: {mount_cmnd}")
        out, err = self.call_subprocess(mount_cmnd)
        logging.debug(f"mount output: {out}, err: {err}")

    def unmount(self, disk) -> None:
        umount_cmnd = "umount " + "/dev/" + disk
        out, err = self.call_subprocess(umount_cmnd)
        logging.debug(f"unmount command: {umount_cmnd}")
        logging.debug(f"unmount output: {out}, err: {err}")

    def format(self, disk) -> None:
        format_cmnd = "mkfs.xfs -f " + "/dev/" + disk
        logging.debug(f"format command: {format_cmnd}")
        out, err = self.call_subprocess(format_cmnd)
        logging.debug(f"format output: {out}, err: {err}")

    def list_block_devices(self) -> List[Dict]:
        get_part_cmnd = "/bin/lsblk -o NAME,SIZE,MOUNTPOINT,TYPE -n  -J -l"
        out, err = self.call_subprocess(get_part_cmnd)
        output = json.loads(out.decode("UTF-8"))
        output = output["blockdevices"]

        partitions = []
        for line in output:
            if line["type"] != "part":
                continue
            attr = {"name": line["name"], "size": line["size"], "mountpoint": line["mountpoint"]}
            partitions.append(attr)
        return partitions
