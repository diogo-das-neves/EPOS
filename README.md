# EPOS Notes for VIENA Project

**BEFORE CONNECTING YOUR COMPUTER MAKE SURE THE CONTROLLER IS TURNED OFF**

**Connect the controller to the PC first then switch on the power supply of the controller**

# Connectors

## How to read data

X1 | 2 means connector X1 pin 2

## Power Supply


| Connector |      Signal      |     Description     |
| :-------: |:----------------:| :------------------: |
|  X1\| 1  |       GND        |        Ground        |
|  X1\| 2  | +V<sub>>cc<sub/> | Power Supply Voltage |

## Logic Supply


| Connector |     Signal     |     Description     |
| :-------: |:--------------:| :------------------: |
|  X2\| 1  |      GND       |        Ground        |
|  X2\| 2  | +V<sub>c<sub/> | Logic Supply Voltage |

## Motor


| Connector |    Signal    |     Description     |
| :-------: | :----------: | :------------------: |
|  X3\| 1  |  Motor(+M)  |        Ground        |
|  X3\| 2  |  Motor(-M)  | Logic Supply Voltage |
|  X3\| 3  |              |    Not Conneceted    |
|  X3\| 4  | Motor Shield |     Cable Shield     |

## Encoder


| Connector |       Signal       |      Description      |
| :-------: |:------------------:| :-------------------: |
|  X5\| 1  |                    |     Not Connected     |
|  X5\| 2  | V<sub>sensor<sub/> | Sensor Supply Voltage |
|  X5\| 3  |        GND         |        Ground        |
|  X5\| 4  |                    |     Not Connected     |
|  X5\| 5  |     Channel A\     | Channel A Complement |
|  X5\| 6  |     Channel A      |       Channel A       |
|  X5\| 7  |     Channel B\     | Channel B Complement |
|  X5\| 8  |     Channel B      |       Channel B       |
|  X5\| 9  |     Channel I\     | Channel I Complement |
|  X5\| 10  |     Channel I      |       Channel I       |

## RS232


| Connector |  Signal  |     Description     |
| :-------: | :------: | :-----------------: |
|  X10\| 1  | EPOS_RxD | EPOS RS232 Receive |
|  X10\| 2  |   GND   |       Ground       |
|  X10\| 3  | EPOS_RxD | EPOS RS232 Transmit |
|  X10\| 4  |   GND   |       Ground       |
|  X10\| 5  |  Shield  |    Cable Shield    |

## CAN1(X11) or CAN2(X12)


| Connector |  Signal  |    Description    | CAN-COM<br/>Cable Pin | CAN-CAN<br/>Cable Pin |
| :-------: | :------: | :---------------: | :-------------------: | :-------------------: |
|  X11\| 1  | CAN High | CAN High Bus line |           7           |           1           |
|  X11\| 2  | CAN Low | CAN Low Bus line |           2           |           2           |
|  X11\| 3  |   GND   |      Ground      |           3           |           3           |
|  X11\| 4  |  Shield  |   Cable Shield   |           5           |           4           |
