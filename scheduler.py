import time

class Scheduler:
    def __init__(self):
        # no events
        self.events = []

    def sleep_ms(self, delay_ms):
        # calculate end time of sleep
        time_release = time.monotonic_ns() + delay_ms * 1000000
        # check if release is due
        while time.monotonic_ns() < time_release:
            # some delay to not interrupt
            time.sleep(0.2)
            for event in self.events:
                if len(event[1]) > 0:
                    event[0](event[1])
                else:
                    event[0]()
                # remove if only need to execute once
                if(event[2] == False):
                    self.events.remove(event)
                
        # time.sleep((time_release - time.monotonic_ns()) / 1000000 / 1000)
        # print("delay done")

    # schedule passive methods to run during delays
    def schedule_passive(self, function, args, repeat):
        # queue function
        self.events.append([function, args, repeat])
