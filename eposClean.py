import logging
import canopen
import argparse
import sys


class Epos():
    channel = 'can0'
    bustype = 'socketcan'
    nodeID = 1
    network = None
    connected = False
    errorDetected = False

    motorType = {'DC motor': 1, 'Sinusoidal PM BL motor': 10,
                 'Trapezoidal PM BL motor': 11}

    errorIndex = {0x00000000: 'Error Code: Communication Successful',
                  # 0x050xxxxx
                  0x05030000: 'Error code: Toggle bit not alternated',
                  0x05040001: 'Error code: Command specifier unknown',
                  0x05040004: 'Error code: CRC check failed',
                  # 0x060xxxxx
                  0x06010000: 'Error code: Unsupported access to an object',
                  0x06010001: 'Error code: Read command to a write only object',
                  0x06010002: 'Error code: Write command to a read only object',
                  0x06020000: 'Error code: Last read/write command had wrong object index or subindex',
                  0x06040041: 'Error code: Object is not mappable to the PDO',
                  0x06040042: 'Error code: Number and length of objects to be mapped would exceed PDO length',
                  0x06040043: 'Error code: General parameter incompatibility',
                  0x06040047: 'Error code: General internal incompatibility in device',
                  0x06060000: 'Error code: Access failed due to hardware error',
                  0x06070010: 'Error code: Data type does not match, length or service parameter do not match',
                  0x06090011: 'Error code: Last read or write object had wrong object subindex',
                  0x06090030: 'Error code: Value range of parameter exceeded',
                  # 0x0800xxxx
                  0x08000000: 'Error code: General error',
                  0x08000020: 'Error code: Data cannot be transferred or stored',
                  0x08000022: 'Error code: Data cannot be transferred or stored to application due to present device state',
                  # 0x0F00xxxx
                  0x0F00FFBE: 'Error code: Password is incorrect',
                  0x0F00FFBF: 'Error code: Command code is illegal (does not exist)',
                  0x0F00FFC0: 'Error code: Device is in wrong NMT state'
                  }

    # Object Index will be given the DCF file

    emcy_descriptions = [
        # Code   Description
        (0x0000, "Error Reset / No Error"),
        (0x1000, "Generic Error"),
        (0x2310, "Over Current Error"),
        (0x3210, "Over Voltage Error"),
        (0x3220, "Under Voltage"),
        (0x4210, "Over Temperature"),
        (0x5113, "Supply Voltage (+5V) too low"),
        (0x6100, "Internal Software Error"),
        (0x6320, "Software Parameter Error"),
        (0x7320, "Sensor Position Error"),
        (0x8110, "CAN Overrun Error (Objects lost)"),
        (0x8111, "CAN Overrun Error"),
        (0x8120, "CAN Passive Mode Error"),
        (0x8130, "CAN Life Guard Error"),
        (0x8150, "CAN Transmit COB-ID collision"),
        (0x81FD, "CAN Bus Off"),
        (0x81FE, "CAN Rx Queue Overrun"),
        (0x81FF, "CAN Tx Queue Overrun"),
        (0x8210, "CAN PDO length Error"),
        (0x8611, "Following Error"),
        (0x9000, "External Error"),
        (0xF001, "Hall Sensor Error"),
        (0xFF02, "Index Processing Error"),
        (0xFF03, "Encoder Resolution Error"),
        (0xFF04, "Hall Sensor not found Error"),
        (0xFF06, "Negative Limit Error"),
        (0xFF07, "Positive Limit Error"),
        (0xFF08, "Hall Angle detection Error"),
        (0xFF09, "Software Position Limit Error"),
        (0xFF0A, "Position Sensor Breach"),
        (0xFF0B, "System Overloaded")
    ]

    # dictionary describing opMode
    opModes = {6: 'Homing Mode', 3: 'Profile Velocity Mode', 1: 'Profile Position Mode',
               -1: 'Position Mode', -2: 'Velocity Mode', -3: 'Current Mode', -4: 'Diagnostic Mode',
               -5: 'MasterEncoder Mode', -6: 'Step/Direction Mode'}
    node = []
    # dictionary object to describe state of EPOS device
    state = {0: 'start', 1: 'not ready to switch on', 2: 'switch on disable',
             3: 'ready to switch on', 4: 'switched on', 5: 'refresh',
             6: 'measure init', 7: 'operation enable', 8: 'quick stop active',
             9: 'fault reaction active (disabled)', 10: 'fault reaction active (enable)',
             11: 'fault',
             -1: 'Unknown'}

    def __init__(self):
        if not self.network:
            self.network = canopen.Network()

    def start(self, nodeID=1, channel='can0', bustype='socketcan', dcf_file='dcf/latestDCF.dcf'):
        try:
            self.node = self.network.add_node(node=nodeID, object_dictionary=dcf_file)
            if not self.network.bus:
                self.network.connect(channel=channel, bustype=bustype)
        except Exception as e:
            self.log_info("Exception caught:{0}".format(str(e)))
            self.connected = False
        finally:
            return self.connected

    def emcy_error_print(self, emcy_error):
        if emcy_error.code == 0:
            self.errorDetected = False
        else:
            for code, description in self.emcy_descriptions:
                if emcy_error.code == code:
                    self.errorDetected = True
                    self.log_info(
                        "Got an EMCY message: Code: 0x{0:04X} {1}".format(code, description))
                    return
            # if no description was found, print generic info
            self.errorDetected = True
            self.log_info('Got an EMCY message: {0}'.format(emcy_error))
        return

    def log_info(self, message=None):
        """ Log a message

        A wrap around logging.
        The log message will have the following structure\:
        [class name \: function name ] message

        Args:
            message: a string with the message.
        """
        if message is None:
            # do nothing
            return
        self.logger.info('[{0}:{1}] {2}'.format(
            self.__class__.__name__,
            sys._getframe(1).f_code.co_name,
            message))
        return


def main():
    parser = argparse.ArgumentParser(add_help=True,
                                     description='Test Epos CANopen Communication')
    parser.add_argument('--channel', '-c', action='store', default='can0',
                        type=str, help='Channel to be used', dest='channel')
    parser.add_argument('--bus', '-b', action='store',
                        default='socketcan', type=str, help='Bus type', dest='bus')
    parser.add_argument('--rate', '-r', action='store', default=None,
                        type=int, help='bitrate, if applicable', dest='bitrate')
    parser.add_argument('--nodeID', action='store', default=1, type=int,
                        help='Node ID [ must be between 1- 127]', dest='nodeID')
    parser.add_argument('--objDict', '-d', action='store', default=None,
                        type=str, help='Object dictionary file', dest='objDict')
    args = parser.parse_args()

    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s.%(msecs)03d] [%(name)-20s]: %(levelname)-8s %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        filename='epos.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-20s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    epos = Epos()

    if not (epos.start(nodeID=args.nodeID, dcf_file=args.objDict)):
        logging.info('Failed to begin connection with EPOS device')
        logging.info('Exiting now')
        return

    '''TODO:
    Deal with PDO's
    Position Demand Value: 6062
    Position Actual Value: 6064
    Velocity Demand Value: 606B
    Velocity Actual Value: 606C
    '''


if __name__ == '__main__':
    main()
