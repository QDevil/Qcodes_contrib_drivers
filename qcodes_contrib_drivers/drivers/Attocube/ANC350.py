from qcodes import Instrument
from qcodes.instrument.channel import InstrumentChannel
from qcodes.utils.validators import Numbers

from qcodes_contrib_drivers.drivers.Attocube.ANC350Lib import v3


class Anc350Axis(InstrumentChannel):

    def __init__(self, parent: "ANC350", name: str, axis: int):
        super().__init__(parent, name)

        self._axis = axis
        self._parent = parent

        self.add_parameter("position",
                           label="Position",
                           get_cmd=self._get_position,
                           docstring="""
                           
                           """)

        self.add_parameter("frequency",
                           label="Frequency",
                           get_cmd=self._get_frequency,
                           set_cmd=self._set_frequency,
                           vals=,
                           unit="Hz",
                           docstring="""
                           
                           """)

        self.add_parameter("amplitude",
                           label="Amplitude",
                           get_cmd=self._get_amplitude,
                           set_cmd=self._set_amplitude,
                           vals=Numbers(0, 70),
                           unit="V",
                           docstring="""
                           
                           """)

        self.add_parameter("status",
                           label="",
                           get_cmd=self._get_status,
                           docstring="""

                            """)

        self.add_parameter("output",
                           label="",
                           #output True, false oder 0,1???
                           set_cmd=parent.lib.set_axis_output(dev_handle=parent.device_handle),
                           vals=, #True und False / 0 und 1
                           docstring="""
                           
                           """)

        self.add_parameter("voltage",
                           label="",
                           set_cmd=self._set_voltage,
                           docstring="""
                           
                           """)

        self.add_parameter("target_postion",
                           label="",
                           set_cmd=self._set_target_position,
                           docstring="""
                           
                           """)

        self.add_parameter("target_range",
                           label="",
                           set_cmd=self._set_target_range,
                           docstring="""
                           
                           """)

        # Kann man actuator und actuator name kombinieren auch wenn sie nicht den selben Datentypen zurückgeben
        self.add_parameter("actuator",
                           label="",
                           set_cmd=self,
                           vals=Numbers(0, 255),
                           docstring="""
                           
                           """)

        self.add_parameter("actuator_name",
                           label="",
                           get_cmd=self._get_actuator_name,
                           docstring="""
                           
                           """)

        self.add_parameter("capacitance",
                           label="",
                           get_cmd=self._get_capacitance,
                           unit="F",
                           docstring="""

                            """)

        # start_single_step
        # start_continuous_move
        # start_auto_move

    def _get_position(self):
        self._parent.lib.set_target_postion(dev_handle=self._parent.device_handle, axis_no=self._axis)

    def _get_frequency(self):
        self._parent.lib.get_frequency(dev_handle=self._parent.device_handle, axis_no=self._axis)

    def _set_frequency(self, frequency):
        self._parent.lib.set_frequency(dev_handle=self._parent.device_handle, axis_no=self._axis, frequency=frequency)

    def _get_amplitude(self):
        self._parent.lib.get_amplitude(dev_handle=self._parent.device_handle, axis_no=self._axis)

    def _set_amplitude(self, amplitude):
        self._parent.lib.get_amplitude(dev_handle=self._parent.device_handle, axis_no=self._axis, amplitude=amplitude)

    def _get_status(self):
        self._parent.lib.get_axis_status(dev_handle=self._parent.device_handle, axis_no=self._axis)

    #wie macht man das mit zwei unbekannten? in zwei parameter aufteilen? Und Problem mit True/ False
    def _set_axis_output(self, enable):
        self._parent.lib.get_axis_status(dev_handle=self._parent.device_handle, axis_no=self._axis, enable = enable)

    def _set_voltage(self, voltage):
        self._parent.lib.set_dc_voltage(dev_handle=self._parent.device_handle,axis_no=self._axis,voltage = voltage)

    def _set_target_position(self, target):
        self._parent.lib.set_target_postion(dev_handle=self._parent.device_handle,axis_no=self._axis, target = target)

    def _set_target_range(self, target_range):
        self._parent.lib.set_target_range(dev_handle=self._parent.device_handle, axis_no=self._axis, target = target_range)

    def _set_actuator(self, actuator):
        self._parent.lib.select_actuator(dev_handle=self._parent.device_handle, axis_no=self._axis, actuator=actuator)

    def _get_actuator_name(self):
        self._parent.lib.get_actuator_name(dev_handle=self._parent.device_handle, axis_no=self._axis)

    def _get_capacitance(self):
        self._parent.lib.measure_capacitance(dev_handle=self._parent.device_handle, axis_no=self._axis)



class ANC350(Instrument):
    def __init__(self, name: str, num: int = 0, search_usb: bool = True, search_tcp: bool = True):
        super().__init__(name)  # Fehlende Parameter?

        lib = v3.ANC350v3Lib()

        if lib.discover(search_usb=search_usb, search_tcp=search_tcp) < num:
            pass
            # Eigene Excepition werfen
        else:
            self.device_handle = lib.connect(num)

    # Postion x,y,z wahrscheinlich in einem Channel
    # _parse_direction_arg
    # device info
    # start_auto_move
    # get acturator
    # save params
    # discconect

    pass
