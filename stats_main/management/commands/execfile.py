import os

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Executes a Python file."
    args = "script"

    def handle(self, *scripts, **options):
        if len(scripts) != 1:
            print self.style.ERROR("Script file name required")
            return

        script = scripts[0]
        if not os.path.isfile(script):
            print self.style.ERROR("Invalid file name: %s" % script)
            return

        execfile(
            script, {
                "__builtins__": __builtins__,
                "__name__": "__main__",
                "__doc__": None,
                "__package__": None,
            })
