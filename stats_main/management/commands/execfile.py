import sys
import os

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Executes a Python file."
    args = "script"

    def handle(self, *args, **options):
        if len(args) < 1:
            print self.style.ERROR("Script file name required")
            return

        script = args[0]
        if not os.path.isfile(script):
            print self.style.ERROR("Invalid file name: %s" % script)
            return

        sys.argv = args
        execfile(
            script, {
                "__builtins__": __builtins__,
                "__name__": "__main__",
                "__doc__": None,
                "__package__": None,
            })
