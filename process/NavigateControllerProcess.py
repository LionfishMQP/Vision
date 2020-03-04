from multiprocessing import Process
import time


class NavigateControllerProcess(Process):
    def __init__(self, nav_obj, queues):
        super(NavigateControllerProcess, self).__init__()
        self.__nav_obj = nav_obj
        self.__queues = queues

    def run(self):
        minObjectDistance = 2000
        start_time = time.time()
        last_message = ['']
        current_heading = 0
        original_heading = current_heading
        state = ''
        throttle = 0
        direction = 0
        desired_amount = 0
        roomba_state = 'straight'
        new_message = ['']
        mavlink_data = 0
        arduino_data = 0
        while True:
            if not self.__queues.ui_nav.empty():
                new_message = self.__queues.ui_nav.get_nowait()
            else:
                pass
            # todo checksafe to perseerve previous data if no data in queues
            if not self.__queues.mavlink_nav.empty():
                mavlink_data = self.__queues.mavlink_nav.get_nowait()
            else:
                pass

            # todo: make better standard messages for cmd passing and such,
            #  tuples for now
            if not last_message[0] == new_message[0]: # update state if new message
                state = new_message[0]
                '''
                    throtle:
                    tuple for roomba mode
                    index 0: straight
                    index 1: turn
                '''
                throttle = new_message[1]
                direction = new_message[2]
                desired_amount = new_message[3]  # time or angle
                original_heading = mavlink_data
                start_time = time.time()
                print("start: ", start_time)

            if state == 'straight':
                current_time = time.time()
                print("current: ", current_time)
                drive_time = current_time - start_time
                print("drive: ", drive_time)
                if drive_time <= desired_amount:
                    self.__nav_obj.drive_straight(throttle, direction)
                else:
                    self.__nav_obj.clear_motors()
                    last_message = new_message
                    state = 'stop'

            elif state == 'turn':
                current_heading = mavlink_data
                desired_rel_angle = direction * desired_amount
                if self.__nav_obj.continue_turn(original_heading, current_heading, desired_rel_angle):
                    self.__nav_obj.turn(throttle, desired_rel_angle)
                else:
                    last_message = new_message
                    self.__nav_obj.clear_motors()
                    state = 'stop'

            elif state == 'roomba':
                if roomba_state == 'straight':
                    if(arduino_data[0] > minObjectDistance):
                        self.__nav_obj.drive_straight(throttle[0], 1)
                    else:
                        self.__nav_obj.clear_motors()
                        roomba_state = 'turn'

                elif roomba_state == 'turn':
                    current_heading = mavlink_data
                    desired_rel_angle = direction * desired_amount
                    if(self.__nav_obj.continue_turn(original_heading, current_heading, 100)):
                        self.__nav_obj.turn(throttle[1], desired_amount)
                    else:
                        self.__nav_obj.clear_motors()
                        roomba_state = 'straight'
                else:
                    pass

            elif state == 'lionfish':
                pass
            elif state == 'stop':
                self.__nav_obj.clear_motors()
            else:
                pass
