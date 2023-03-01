
class SMADProc:

    def __init__(self,
                 location="localhost",
                 port=2625,
                 ):
        """
        """
        self.locetion = location
        self.port = port
        self.socket = None
        self.clock_rate = 0  # randomly generate it

        self.other_procs = []
        self.log_file = None

        # setup the process
        self.init_socket()
        self.init_log()
        self.init_clock()

    def init_socket(self):
        """
        """
        pass

    def init_log(self):
        """
        """
        pass

    def init_clock(self):
        """
        """
        pass

    def send_msg(self, msg, dest):
        """
        """
        pass

    def recv_msg(self):
        """
        """
        pass

    def log(self):
        """
        """
        pass

    def sleep(self, time):
        """
        """
        pass

    def add_proc(self, proc):
        """
        """
        pass

    def run(self):
        """
        """
        pass
