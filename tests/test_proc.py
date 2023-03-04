

import json
import queue
import socket
import threading
import time
import unittest

import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from src.smad import SMADProc, FileLogger

FREE_PORT = 26190


class TestSMADproc(unittest.TestCase):

    def recieve_msg(self):
        # continuously recieve messages unless the socket is closed
        # or thread is interrupted
        while not self._stop_thread.is_set():

            conn, addr = self.serv_sock.accept()
            data = conn.recv(1024)
            self.msg_queue.put((addr, data))

    def setUp(self):
        global FREE_PORT
        # create socket for testing
        FREE_PORT += 1
        self.test_address = ('localhost', FREE_PORT)
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_sock.bind(self.test_address)
        self.serv_sock.listen(2)

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
        self.proc2 = SMADProc(name="proc2", location="localhost", port=FREE_PORT,
                              clock_rate=1, logger=self.file_logger2)

        # introduce the processes to each other
        self.proc1.add_proc([self.proc2.address])
        self.proc2.add_proc([self.proc1.address])

    def tearDown(self):
        self._stop_thread.set()

        # self.reciever_thread.join()
        # self.serv_sock.shutdown(socket.SHUT_RDWR)
        # self.client_sock.shutdown(socket.SHUT_RDWR)
        # self.client_sock.close()
        # self.serv_sock.close()
        self.proc1.kill()
        self.proc2.kill()
        self.file_logger1.close()
        self.file_logger2.close()

    def test_add_proc(self):
        # test if the process is added
        self.assertIn(self.proc2.address, self.proc1.other_procs)
        self.assertIn(self.proc1.address, self.proc2.other_procs)

    def test_send(self):
        # test if the message is sent
        test_msg = "Test message from proc 1"
        self.proc1.send_msg(self.test_address, test_msg)

        # wait for the message to be sent for the clock rate + some buffer
        # if not raise an error
        try:
            # print("sending test msg\n")
            sender, msg = self.msg_queue.get(
                timeout=1 / self.proc1.clock_rate + 2)
        except queue.Empty:
            self.fail(
                "Message not sent! This could be due to the clock rate being tobreako high. Try increasing the timeout in the test.")
        else:
            msg = json.loads(msg)
            self.assertEqual(msg['msg'], test_msg)

    def test_log(self):
        """Checks if the log is written to the file
        """
        test_msg = "Log message test"
        self.proc1.log(test_msg)
        log = self.proc1.logger.read()

        self.assertIn(test_msg, log)
        
    def test_recv(self):
        test_msg = "Test message from proc 1"
        self.proc1.send_msg(self.proc2.address, test_msg)
        time.sleep(1 / self.proc1.clock_rate + 1/ self.proc2.clock_rate + 2)
        
        addr, msg = self.proc2._msg_queue.get()
        self.assertEqual(msg['msg'], test_msg)
        


if __name__ == '__main__':
    unittest.main()
