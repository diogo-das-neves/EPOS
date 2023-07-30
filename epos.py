import logging
import canopen


class Epos:
    channel = 'can0'
    bustype = 'socketcan'
    nodeID = 1
    network = None
    _connected = False
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
                  0x08000022: 'Error code: Data cannot be transfered or stored to application due to present device state',
                  # 0x0F00xxxx
                  0x0F00FFBE: 'Error code: Password is incorrect',
                  0x0F00FFBF: 'Error code: Command code is illegal (does not exist)',
                  0x0F00FFC0: 'Error code: Device is in wrong NMT state'

                  }

    def __int__(self, network=None, debug=False):
        if not network:
            self.network = canopen.Network()
        else:
            self.network=network
        self.logger = logging.getLogger('EPOS')
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)



if __name__ == '__main__':
    main()
