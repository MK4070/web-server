import subprocess
import sys


def run_in_terminal(script_path, terminal_command):
    if sys.platform == "win32":
        command = f"start {terminal_command} /K python -m {script_path}"
    elif sys.platform == "darwin" or sys.platform == "linux":
        command = (
            f'{terminal_command} -c "python3 -m {script_path}; exec bash"'
        )
    else:
        raise OSError("Unsupported OS")

    subprocess.Popen(command, shell=True)


def run():
    server = "scripts.server"
    load_balancer = "scripts.load_balancer"

    if sys.platform == "win32":
        terminal = "cmd"
    elif sys.platform == "darwin":
        terminal = "osascript -e 'tell app \"Terminal\" to do script'"
    elif sys.platform == "linux":
        terminal = "sh"

    try:
        run_in_terminal(server, terminal)
        run_in_terminal(load_balancer, terminal)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    run()
