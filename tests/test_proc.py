
import json
import queue
import socket
import threading
import time
import unittest


from src.smad import SMADProc, FileLogger

FREE_PORT = 26250


class TestSMADproc(unittest.TestCase):

    def recieve_msg(self):
        # continuously recieve messages unless the socket is closed
        # or thread is interrupted
        while self._stop_thread.is_set():
            try:
                conn, addr = self.sock.accept()
                data = conn.recv(1024)
                print(addr)
                self.msg_queue.append(data)
            except Exception as err:
                print(err)
                break

    def setUp(self):
        global FREE_PORT
        # create socket for testing
        FREE_PORT += 1
        self.test_address = ('localhost', FREE_PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.test_address)
        self.sock.listen(2)

        # setup a litning server
        self.msg_queue = queue.Queue()
        self._stop_thread = threading.Event()
        self.reciever_thread = threading.Thread(target=self.recieve_msg)
        self.reciever_thread.start()

        # create file loggers
        self.file_logger1 = FileLogger("proc1.log")
        self.file_logger2 = FileLogger("proc2.log")

        FREE_PORT += 2
        # create a process for testing
        self.proc1 = SMADProc(name="proc1", location="localhost", port=FREE_PORT - 1,
                              clock_rate=1, logger=self.file_logger1)
        self.proc2 = SMADProc(name2="proc2", location="localhost", port=FREE_PORT,
                              clock_rate=1, logger=self.file_logger2)

        # introduce the processes to each other
        self.proc1.add_proc(self.proc2.address)
        self.proc2.add_proc(self.proc1.address)

    def tearDown(self):
        self._stop_thread.set()
        self.reciever_thread.join()
        print("Before close:", self.sock.fileno())
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("After close:", self.sock.fileno())
        self.proc1.kill()
        self.proc2.kill()
        self.file_logger1.close()
        self.file_logger2.close()

    def test_add_proc(self):
        # test if the process is added
        self.assertIn(self.proc2.address, self.proc1.other_procs)
        self.assertIn(self.proc1.address, self.proc2.other_procs)

    def test_send_recieve_msg(self):
        # test if the message is sent
        test_msg = "Test message from proc 1"
        self.proc1.send_msg(test_msg, self.test_address)

        # wait for the message to be sent for the clock rate + some buffer
        # if not raise an error
        try:
            sender, msg = self.msg_queue.get(
                timeout=1/self.proc1.clock_rate + 2)
        except queue.Empty:
            self.fail(
                "Message not sent! This could be due to the clock rate being tobreako high. Try increasing the timeout in the test.")
        else:
            msg = json.loads(msg)
            self.checkEqual(msg, test_msg)

    def test_log(self):
        """Checks if the log is written to the file
        """
        test_msg = "Log message test"
        self.proc1.log(test_msg)
        log = self.proc1.logger.read()

        self.assertIn(test_msg, log)


if __name__ == '__main__':
    unittest.main()
