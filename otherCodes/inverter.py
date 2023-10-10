import sys
import canopen
from time import sleep


class INVERTER:
    node = None
    network = None
    preop_command = None

    tpdo_channel = {
        'id_target': 1,
        'iq_target': 1,
        'id': 1,
        'iq': 1,
        'drive_state': 2,
        'torque_demand': 2,
        'torque_actual': 2,
        'torque_max': 2,
        'torque_target': 3,
        'throttle_value': 3,
        'throttle_input_voltage': 3,
        'motor_temperature': 3,
        'ud_actual': 4,
        'uq_actual': 4,
        'i_bat': 4,
        'v_bat': 4,
        'speed_max': 5,
        'speed': 5
    }

    tpdo_gain = {
        'id_target': 0.0625,
        'iq_target': 0.0625,
        'id': 0.0625,
        'iq': 0.0625,
        'drive_state': 1,
        'torque_demand': 0.0625,
        'torque_actual': 0.0625,
        'torque_max': 0.0625,
        'torque_target': 0.1,
        'throttle_value': 0.000030,
        'throttle_input_voltage': 0.0039,
        'motor_temperature': 0.0625,
        'ud_actual': 0.0625,
        'uq_actual': 0.0625,
        'i_bat': 0.0625,
        'v_bat': 0.0625,
        'speed_max': 1,
        'speed': 1
    }

    tpdo_signals = {
        'id_target': 'Additional Motor Measurements.Target Id (If)',
        'iq_target': 'Additional Motor Measurements.Target Iq (Ia)',
        'id': 'Additional Motor Measurements.Id (If)',
        'iq': 'Additional Motor Measurements.Iq (Ia)',
        'drive_state': 'Traction Application Status.Traction Drive State',
        'torque_demand': 'AC Motor Debug Information.Torque demand value (U.T_d)',
        'torque_actual': 'AC Motor Debug Information.Torque actual value (DWork.Td)',
        'torque_max': 'AC Motor Debug Information.Maximum torque (DWork.Td_max)',
        'torque_target': 'Target torque',
        'throttle_value': 'Throttle Value',
        'throttle_input_voltage': 'Throttle Input Voltage',
        'motor_temperature': 'Additional Motor Measurements.Motor Temperature 1 (Measured - T1)',
        'ud_actual': 'Additional Motor Measurements.Ud (Uf)',
        'uq_actual': 'Additional Motor Measurements.Uq (Ua)',
        'i_bat': 'Device Measurements.Battery Current',
        'v_bat': 'Device Measurements.Battery Voltage'
    }

    def __init__(self):
        return

    def begin(self, _channel='can0', _bustype='socketcan', id=1, DCF_file='viena_30_06_2022_2.dcf'):
        '''
        Recebe: canal canopen, tipo de transporte, id do no a incializar, ficheiro DCF do no
        Inicializa a rede canopen e cria o no do inversor
        Da nivel de acesso de engenheiro
        Por fim força o estado do inversor a pre-operacional
        '''
        try:
            self.network = canopen.Network()
            self.network.connect(channel=_channel, bustype=_bustype)
            # Add node to network
            self.node = self.network.add_node(id, DCF_file)

        except Exception as e:
            print(e)

        access = self.node.sdo['Password Entry'][
            'Access Level Indication']  # Para verificar se o no tem acesso de engenheiro
        if access.raw != 4:
            print('User not logged in, logging in as Engineering Access Level')
            password = self.node.sdo['Password Entry']['Password (16-bit)']
            password.raw = 0x4BDF  # Se n tiver acesso de engenheiro, muda a passa para ter esse acesso
            if access.raw == 4:
                print('User log in successfully')
            else:
                print('ERROR: Impossible to log in...')
                return -1

        self.node.tpdo.read()  # Descarta uma primeira leitura da data do TPDO do no
        self.preop_command = self.node.sdo['Force system to pre-operational state']

        return 1

    def set_pre_operational(self, _kp, _ki):
        '''
        Recebe: valores dos ganhos a definir do inversor
        Define o estado pre-operacional do inversor
        '''

        self.preop_command.raw = 1
        print('Setting inverter to PRE-OPERATIONAL')
        # Change Kp and Ki
        kp = self.node.sdo['AC Motor data (manufacturer specific)'][
            'Current control proportional gain (Kp)']  # aqui se nao estou em erro o nuno guarda a posição do parametro
        kp.raw = _kp  # 0.019531  aqui acede a posicao e faz um .raw= pra alterar o raw
        kp_true = kp.raw * 0.000030517578125
        ki = self.node.sdo['AC Motor data (manufacturer specific)'][
            'Current control integral gain (Ki)']
        ki.raw = _ki  # 0.002472
        ki_true = ki.raw * 0.000030517578125

        self.node.tpdo[1].event_timer = 10  # Frequencia com que tpdo e enviado se houvere mudancas
        self.node.tpdo[2].event_timer = 10  # o no tem 5 canais tpdo
        self.node.tpdo[3].event_timer = 10
        self.node.tpdo[4].event_timer = 10
        self.node.tpdo[5].event_timer = 10
        # If map is valid
        self.node.tpdo[1].enabled = True  # Enable normal, permitem enviar as mensagens tpdo
        self.node.tpdo[2].enabled = True
        self.node.tpdo[3].enabled = True
        self.node.tpdo[4].enabled = True
        self.node.tpdo[5].enabled = True
        # Save PDO config to node
        self.node.tpdo[1].save()  # Da save da configuracao dos 5 canais tpdo
        self.node.tpdo[2].save()
        self.node.tpdo[3].save()
        self.node.tpdo[4].save()
        self.node.tpdo[5].save()

        self.network.sync.start(1)  # Sincroniza os processo da rede com um ciclo de 1ms
        return 1

    def mqtt_recive_handler(self, client, userdata, message):
        print("\nMQQT DATA RECVIED")

    def mqtt_handler(self, msg, msg_id):
        channel = "VIENA/mqttController/inverter/" + self.mqttSubChannelsByID[msg_id]

    def send(self, channel, msg):
        # sends a string over mqtt
        self.client.publish(channel, msg)
        return

    def print_network(self, network):
        for node_id in network:
            print(network[node_id])

    def print_DCF(self):
        for obj in self.node.object_dictionary.values():
            print('0x%X: %s' % (obj.index, obj.name))
            if isinstance(obj, canopen.objectdictionary.Record):
                for subobj in obj.values():
                    print('  %d: %s' % (subobj.subindex, subobj.name))

    def receive_data_canopen(self, signal, max_wait_time):
        self.node.tpdo[self.tpdo_channel[signal]].wait_for_reception(max_wait_time)
        return self.node.tpdo[self.tpdo_signals[signal]].phys * self.tpdo_gain[signal]


def main():
    signals = ['throttle_value', 'id_target', 'iq_target', 'id', 'iq', 'drive_state',
               'torque_demand', 'torque_actual', 'torque_max', 'torque_target', 'throttle_value',
               'throttle_input_voltage', 'motor_temperature']
    inv = INVERTER()
    if (inv.begin() < 0):
        exit
    if (inv.set_pre_operational(640, 100) < 0):
        exit

    while True:
        # _signal = input("Signal to read: ")

        for _signal in signals:
            rec = inv.receive_data_canopen(_signal, 2)
            print(f"DATA RECEIVED ({_signal}):  {rec}")
        sleep(2)


# Program
if __name__ == '__main__':
    main()
