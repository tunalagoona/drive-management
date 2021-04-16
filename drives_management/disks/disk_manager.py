import subprocess
import random
import json
import string
import logging
from pathlib import Path
from collections import namedtuple
from typing import List, Dict

logger = logging.getLogger()


CommandResults = namedtuple('CommandResults', ['stdout', 'stderr', 'exit_code'])


class DiskManager:
    @staticmethod
    def run_command(command: str) -> CommandResults:
        logging.debug(f"Executing command: '{command}'")
        process = subprocess.Popen([command],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   shell=True)
        stdout, stderr = process.communicate()
        logging.debug(f"Completed command: '{command}'\nstdout:\n{stdout}\n\nstderr:\n{stderr}\n")
        return CommandResults(stdout, stderr, process.returncode)

    def mount(self, disk):
        devices = self.list_block_devices()

        mnt_pnt = None
        for d in devices:
            if d["name"] == disk:
                mnt_pnt = d["mountpoint"]

        if mnt_pnt is None or len(mnt_pnt) == 0:
            letters = string.ascii_lowercase
            dir_name = "".join(random.choice(letters) for _ in range(4))
            Path(f"/mnt/{dir_name}").mkdir(parents=True, exist_ok=True)
            return self.run_command(f"mount /dev/{disk} /mnt/{dir_name}")
        else:
            return CommandResults("", f"mount: /dev/{disk}: already mounted.", "")

    def unmount(self, disk):
        return self.run_command(f"umount /dev/{disk}")

    def format(self, disk) -> CommandResults:
        return self.run_command(f"mkfs.xfs -f /dev/{disk}")

    def list_block_devices(self) -> List[Dict]:
        results = self.run_command("/bin/lsblk -o NAME,SIZE,MOUNTPOINT,TYPE -n  -J -l")
        output = json.loads(results.stdout)
        return [d for d in output["blockdevices"] if d["type"] == "part"]
