import sys

from makemigrations import main as makemigrations
from migrate import main as migrate

#sys.tracebacklimit = 0

tasks = {
    'makemigrations': makemigrations,
    'migrate': migrate
}

if len(sys.argv) == 1:
    raise RuntimeError(f"You must provide a task to run.\nTasks available: {', '.join(tasks)}.")

task = sys.argv[1]
if task in tasks.keys():
    tasks[task]()
else:
    raise RuntimeError(f"There's no task called {task} available.")
