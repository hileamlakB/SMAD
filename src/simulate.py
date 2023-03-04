import signal
import threading
from smad import SMADProc, FileLogger

processes = []


def handler(signum, frame):
    for proc in processes:
        proc.kill()
    print("Exiting")


address = [("localhost", 26262), ("localhost", 26263), ("localhost", 26264)]


if __name__ == "__main__":

    for i, (loc, port) in enumerate(address):
        proc = SMADProc(
            name=f"proc_{i}", location=loc, port=port)
        processes.append(proc)
        proc.add_proc(address[:i] + address[i + 1:])
        # store the clock rates in a file
        with open("clock_rates.log", "a") as f:
            f.write(f"{proc.process_name} {proc.clock_rate}\n")

    for proc in processes:
        threading.Thread(target=proc.run).start()
