import subprocess
import thread


def _track_process(sub, status_output=None, terminate_func=None, stdout_func=None, prefix=""):
    try:
        while True:
            text = sub.stdout.readline()
            text += sub.stderr.readline()
            if not text:
                status = sub.wait()
                if status_output:
                    status_output[0] = status
                if terminate_func:
                    terminate_func()
                return
            else:
                out = prefix + text.strip()
                if status_output:
                    status_output[1] += out
                if stdout_func:
                    stdout_func(out)
    except Exception:
        raise


def run_bg_shell_cmd(command, terminate_func=None, stdout_func=None, prefix=""):
    try:
        sub = subprocess.Popen(command, shell=True,  stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status_output = [None, ""]
        thread.start_new_thread(_track_process, (sub, status_output, terminate_func, stdout_func, prefix))
        if status_output[0] is not None:
            return (status_output[0], None, status_output[1])
        else:
            return (None, sub.pid, status_output[1])
    except Exception:
        raise



def run_shell_cmd(cmd, verbose=True):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = []
    for line in p.stdout:
        if verbose:
            print(line)
        out.append(line)
    err = []
    for line in p.stderr:
        if verbose:
            print(line)
        err.append(line)

    retval = p.wait()
    return (retval, ''.join(out).strip(), ''.join(err).strip())
