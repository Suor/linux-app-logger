#!/usr/bin/env python
import os, sys, commands, re, time
from datetime import datetime

from dateutil.tz import tzlocal
import daemon


log_file = os.path.abspath(sys.argv[1]) if sys.argv[1] != '-' else '-'
timeout = float(sys.argv[2] if len(sys.argv) >= 3 else 60)


def is_active():
    return 'is active' not in commands.getoutput("gnome-screensaver-command -q")

def get_active_program():
    active_window_string = commands.getoutput("xprop -root | grep '_NET_ACTIVE_WINDOW(WINDOW)'")
    active = re.findall(r'#\s+0x(\w+)', active_window_string)[0]
    active = "0x" + "0" * (8-len(active)) + active

    program = commands.getoutput("wmctrl -lx | grep %s" % active).splitlines()[0]
    _, _, app, _, title = program.split(None, 4)
    return app, title

def get_timestamp():
    return datetime.now(tzlocal()).strftime('%Y-%m-%dT%T%Z')


with daemon.DaemonContext():
    while True:
        try:
            if is_active():
                app, title = get_active_program()
                log_line = '%s\t%-30s\t%s\n' % (get_timestamp(), app, title)

                if log_file == '-':
                    print log_line,
                else:
                    with open(log_file, 'a') as f:
                        f.write(log_line)
        except Exception:
            import traceback
            with open(log_file + '.err', 'a') as f:
                traceback.print_exc(None, f);

        time.sleep(timeout)
