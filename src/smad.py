import json
import queue
import random
import socket
import threading
import time


from enum import Enum
from typing import List, Tuple, Any


class Tasks(Enum):
    SEND_MACHINE_ONE = 1
    SEND_MACHINE_TWO = 2
    BROADCAST = 3
    TWIDDLE = 4


class FileLogger:
    def __init__(self, filename: str) -> None:
        self.filename = filename

        # two streams are used to read and write to the file
        self.file = open(filename, 'a')
        self.read_stream = None

    def log(self, message: str) -> None:
        self.file.write(message + '\n')

    def close(self) -> None:
        self.file.close()
        if self.read_stream is not None:
            self.read_stream.close()

    def read(self) -> str:
        if self.read_stream is None:
            self.read_stream = open(self.filename, 'r')
        self.read_stream.seek(0)
        return self.read_stream.read()


class SMADProc:
    def __init__(self,
                 name: str = None,
                 location: str = "localhost",
                 port: int = 26262,
                 clock_rate: float = 0,
                 logger: FileLogger = None
                 ) -> None:
        """
        SMADProc is a process model  will run at a clock rate determined during initialization.
        On each clock cycle, if there is a message in the message queue for the machine (remember, the queue is not running at the same cycle speed) the virtual machine should take one message off the queue, update the local logical clock, and write in the log that it received a message, the global time (gotten from the system), the length of the message queue, and the logical clock time.

        If there is no message in the queue, the virtual machine should generate a random number in the range of 1-10, and

        if the value is 1, send to one of the other machines a message that is the local logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock time
        if the value is 2, send to the other virtual machine a message that is the local logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock time.
        if the value is 3, send to both of the other virtual machines a message that is the logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock time.
        if the value is other than 1-3, treat the cycle as an internal event; update the local logical clock, and log the internal event, the system time, and the logical clock value.
        """
        self.process_name = name
        self.address: Tuple[str, int] = (location, port)
        self.serv_sock: socket.socket = None
        self.client_sock: socket.socket = None
        self.clock_rate = clock_rate  # randomly generate it

        self.other_procs: List[Tuple[str, int]] = []
        self.logger: FileLogger = logger
        self.logger_created = False

        # setup the processf
        self.init_socket()
        self.init_log()
        self.init_clock()

    def recv_thread(self) -> None:
        """
        A thread to receive messages while the main thread is busy
        """
        while not self._stop_thread.is_set():
            try:
                conn, addr = self.serv_sock.accept()
                data = conn.recv(1024)
                json_msg = json.loads(data)
                self._msg_queue.put((addr, json_msg))
            except:
                pass
                # the break is when the socket is closed

    def init_socket(self) -> None:
        """
        creates a socket for connection with other process
        """
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_sock.bind(self.address)
        self.serv_sock.listen(5)

        # setup receiver thread
        self._stop_thread = threading.Event()
        self._msg_queue: queue.Queue = queue.Queue()
        self._recv_thread = threading.Thread(target=self.recv_thread)
        self._recv_thread.start()

    def init_log(self) -> None:
        """
        Sets up file logging if a logger is not provided
        """
        if self.logger is None:
            self.logger = FileLogger(f"{self.process_name}.log")
            self.logger_created = True

    def init_clock(self) -> None:
        """
        If clock rate is not provided, it will be randomly generated
        """
        if not self.clock_rate:
            self.clock_rate = 1
        self.sleep_time = 1 / self.clock_rate
        self.internal_clock = 0

    def send_msg(self, dest: Tuple[str, int], msg: str) -> None:
        """
        sends a json file containing the msg along with the internal clock
        """
        msg = json.dumps({
            "msg": msg,
            'clock': self.internal_clock
        })

        # print("trying to connect:\n", dest)

        # connect to desitnation and send the message

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.client_sock.connect(dest)
        self.client_sock.send(msg.encode())
        self.client_sock.close()

    def log(self, msg: str) -> None:
        """
        logs the message using the logger
        """
        self.logger.log(msg)

    def add_proc(self, adds: List[Tuple[str, int]]) -> None:
        """
            Intorduce other process that are currently running open at sockets
            add: [(address, port), ...]

        """
        self.other_procs += adds

    def log_formater(self, sender, msg):
        c_time = time.strftime("%b %d %H:%M:%S")
        # replace all - with _ in process_name and msg to prevent users
        # from messing up the log file format
        pname = self.process_name.replace("-", "_")
        msg = msg.replace("-", "_")

        return f"{c_time}-{pname}-{self.address[0]}:{self.address[1]}-{self.internal_clock}-{sender[0]}:{sender[1]}-{msg}"

    def run(self) -> None:
        """
        Run: runs the process model as described in the class docstring
        """
        self.stop_main = threading.Event()
        while not self.stop_main.is_set():

            # check if there is a message in the queue
            if not self._msg_queue.empty():
                sender, msg = self._msg_queue.get()
                self.internal_clock = max(
                    self.internal_clock, msg['clock']) + 1
                self.log(
                    self.log_formater(sender, msg['msg']))
                # sleep for the sleeping time
                time.sleep(self.sleep_time)
                continue

            # Decide what to do if there is no message in the queue
            task = random.randint(1, 20)
            msg = ""
            if task == Tasks.SEND_MACHINE_ONE.value:
                self.send_msg(self.other_procs[0],
                              f"{self.process_name}:Holla")
                msg = "SEND TO MACHINE ONE"
            elif task == Tasks.SEND_MACHINE_TWO.value:
                self.send_msg(self.other_procs[1],
                              f"{self.process_name}:Holla")
                msg = "SEND TO MACHINE TWO"
            elif task == Tasks.BROADCAST:
                for proc in self.other_procs:
                    self.send_msg(proc, f"{self.process_name}:Holla")
                msg = "BROADCAST"
            else:
                # sleep for point one second to simuulate internal event
                time.sleep(.1)
                msg = "INTERNAL EVENT"

            print(self.process_name, task, msg)
            self.internal_clock += 1
            self.log(self.log_formater(self.address, msg))
            time.sleep(self.sleep_time)

    def kill(self) -> None:
        """
        Cleans up modle process before exitsing
        Cleaning includes:
            closing sockets
            closing log files
            closing threads
        """
        self.serv_sock.shutdown(socket.SHUT_RDWR)
        self.serv_sock.close()

        self._stop_thread.set()
        self._recv_thread.join()

        if self.logger_created:
            print("closing logger")
            self.logger.close()
