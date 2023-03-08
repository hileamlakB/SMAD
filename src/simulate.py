import signal
import threading
from smad import SMADProc, FileLogger

processes = []
threads = []


def handler(signum, frame):
    for proc in processes:
        proc.kill()
    # stop the threads
    for thread in threads:
        thread.join()


signal.signal(signal.SIGINT, handler)
start_port = 26582
num_procs = 3

address = [("localhost", i) for i in range(start_port, start_port + num_procs)]

if __name__ == "__main__":

    for i, (loc, port) in enumerate(address):
        proc = SMADProc(
            name=f"proc{i}", location=loc, port=port)
        processes.append(proc)
        proc.add_proc(address[:i] + address[i + 1:])
        # store the clock rates in a file
        with open("clock_rates.log", "a") as f:
            f.write(f"{proc.process_name} {proc.clock_rate}\n")

    for proc in processes:
        thread = threading.Thread(target=proc.run)
        threads.append(thread)
        thread.start()
