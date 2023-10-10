import logging
import canopen
import argparse
import sys


class Epos:
    channel = 'can0'
    bustype = 'socketcan'
    nodeID = 1
    network = None
    connected = False
    errorDetected = False

    # List of motor types
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

    objectIndex = {
        ### [0x1xxx]
        'Device Type': 0x1000,
        'Error Register': 0x1001,
        'Error History': 0x1003,
        'COB-ID SYNC': 0x1005,
        'Manufacter Device Name': 0x1008,
        'Store Parameters': 0x1010,
        'Restore Default Parameters': 0x1011,
        'COB_ID EMCY': 0x1014,
        'Consumer Heartbeat Time': 0x1016,
        'Producer Heartbeat Time': 0x1017,
        'Identify Object': 0x1018,
        'Error Behavior': 0x1029,
        'SDO Server Parameter': 0x1200,
        'Receive PDO 1 Parameter': 0x1400,
        'Receive PDO 2 Parameter': 0x1401,
        'Receive PDO 3 Parameter': 0x1402,
        'Receive PDO 4 Parameter': 0x1403,
        'Receive PDO 1 Mapping': 0x1600,
        'Receive PDO 2 Mapping': 0x1601,
        'Receive PDO 3 Mapping': 0x1602,
        'Receive PDO 4 Mapping': 0x1603,
        'Transmit PDO 1 Parameter': 0x1800,
        'Transmit PDO 2 Parameter': 0x1802,
        'Transmit PDO 3 Parameter': 0x1803,
        'Transmit PDO 4 Parameter': 0x1804,
        'Transmit PDO 1 Mapping': 0x1A00,
        'Transmit PDO 2 Mapping': 0x1A01,
        'Transmit PDO 3 Mapping': 0x1802,
        'Transmit PDO 4 Mapping': 0x1A03,
        'Program Data': 0x1F51,
        'Program Software Identification': 0x1F56,
        'Flash Status Identification': 0x1F57,
        ### [0x2xxx]
        'Node ID': 0x2000,
        'CAN Bit Rate': 0x2001,
        'RS232 Bit Rate': 0x2002,
        'RS232 Frame Timeout': 0x2005,
        'USB Frame Timeout': 0x2006,
        'CAN Bit Rate Display': 0x200A,
        'Active FieldBus': 0x2010,
        'Additional Identity': 0x2100,
    }

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
             9: 'fault reaction active (disabled)', 10: 'fault reaction active (enable)', 11: 'fault',
             -1: 'Unknown'}

    def __int__(self, network=None):
        if not network:
            self.network = canopen.Network()
        else:
            self.network=network

    def begin(self, nodeID, channel='can0', bustype='socketcan',
              dictionary='dcf/MAXON_EPOS_DCF_11092023_1122.eds'):
        try:
            self.node = self.network.add_node(
                nodeID, object_dictionary=dictionary)
            self.node.emcy.add_callback(self.emcy_error_print)
            if not self.network.bus:
                self.network.connect(channel=channel, bustype=bustype)
            val, _ = self.read_statusword()
            if val is None:
                self.channel=False
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


    def read_statusword(self):
        """Read StatusWord

        Request current statusword from device.

        Returns:
            tuple: A tuple containing:

            :statusword:  the current statusword or None if any error.
            :ok: A boolean if all went ok.
        """
        index = self.objectIndex['StatusWord']
        subindex = 0
        statusword = self.read_object(index, subindex)
        # failed to request?
        if not statusword:
            self.log_info('Error trying to read {0} statusword'.format(
                self.__class__.__name__))
            return statusword, False

        # return statusword as an int type
        statusword = int.from_bytes(statusword, 'little')
        return statusword, True

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
    parser.add_argument('--objDict', action='store', default=None,
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

    if not (epos.begin(args.nodeID, dictionary=args.objDict)):
        logging.info('Failed to begin connection with EPOS device')
        logging.info('Exiting now')
        return


if __name__ == '__main__':
    print("Running epos.py\n")
    main()
    print("end of epos.py\n")
