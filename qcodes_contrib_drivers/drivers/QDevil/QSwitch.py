import uuid
import re
from time import sleep as sleep_s
from qcodes.instrument.channel import InstrumentChannel, ChannelList
from qcodes.instrument.visa import VisaInstrument
from pyvisa.errors import VisaIOError
from qcodes.utils import validators
from typing import NewType, Tuple, Sequence, List, Dict, Optional
from packaging.version import Version, parse
# import abc

# Version 0.1.0
#
# Guiding principles for this driver for Quantum Machines QSwitch
# ---------------------------------------------------------------
#


#
# Future improvements
# -------------------
#


def _line_tap_split(input: str) -> Tuple[int, int]:
    pair = input.split('!')
    if len(pair) != 2:
        raise ValueError(f'Expected channel pair, got {input}')
    if not pair[0].isdecimal():
        raise ValueError(f'Expected channel, got {pair[0]}')
    if not pair[1].isdecimal():
        raise ValueError(f'Expected channel, got {pair[1]}')
    return int(pair[0]), int(pair[1])


def channel_list_to_map(channel_list: str) -> Sequence[Tuple[int, int]]:
    outer = re.match(r'\(@([0-9,:! ]*)\)', channel_list)
    if not outer:
        raise ValueError(f'Expected channel list, got {channel_list}')
    result = []
    sequences = outer[1].split(',')
    if sequences == ['']:
        return result
    for sequence in sequences:
        limits = sequence.split(':')
        if limits == ['']:
            raise ValueError(f'Expected channel sequence, got {limits}')
        line_start, tap_start = _line_tap_split(limits[0])
        line_stop, tap_stop = line_start, tap_start
        if len(limits) == 2:
            line_stop, tap_stop = _line_tap_split(limits[1])
        if len(limits) > 2:
            raise ValueError(f'Expected channel sequence, got {limits}')
        if tap_start != tap_stop:
            raise ValueError(f'Expected same breakout in sequence, got {limits}')
        for line in range(line_start, line_stop+1):
            result.append((line, tap_start))
    return result


def map_to_channel_list(channel_map: Dict[int, int]) -> str:
    return \
        '(@' + \
        ','.join([f'{line}!{tap}' for (line,tap) in channel_map]) + \
        ')'


class QSwitchChannel(InstrumentChannel):

    def __init__(self, parent: 'QSwitch', name: str, channum: int):
        super().__init__(parent, name)
        self._channum = channum
        self.add_function(
            name='on',
            call_cmd=f'clos (@{channum}!9)'
        )
        self.add_function(
            name='off',
            call_cmd=f'open (@{channum}!9)'
        )
        # self.add_parameter(
        #     name='off',
        #     label='off',
        #     call_cmd=f'clos (@{channum}!9)'
        # )


class QSwitch(VisaInstrument):

    def __init__(self, name: str, address: str, **kwargs) -> None:
        """Connect to a QSwitch

        Args:
            name (str): Name for instrument
            address (str): Visa identification string
            **kwargs: additional argument to the Visa driver
        """
        self._check_instrument_name(name)
        super().__init__(name, address, terminator='\n', **kwargs)
        self._set_up_serial()
        self._set_up_debug_settings()
        self._set_up_simple_functions()
        self.connect_message()
        self._check_for_wrong_model()
        self._check_for_incompatiable_firmware()
        self._set_up_channels()

    # -----------------------------------------------------------------------
    # Instrument-wide functions
    # -----------------------------------------------------------------------

    def reset(self) -> None:
        self.write('*rst')
        sleep_s(1)

    def errors(self) -> str:
        """Retrieve and clear all previous errors

        Returns:
            str: Comma separated list of errors or '0, "No error"'
        """
        return self.ask('all?')

    def error(self) -> str:
        """Retrieve next error

        Returns:
            str: The next error or '0, "No error"'
        """
        return self.ask('next?')

    @staticmethod
    def unpack(channel_list: str) -> str:
        return map_to_channel_list(channel_list_to_map(channel_list))

    # -----------------------------------------------------------------------
    # Debugging and testing

    def start_recording_scpi(self) -> None:
        """Record all SCPI commands sent to the instrument

        Any previous recordings are removed.  To inspect the SCPI commands sent
        to the instrument, call get_recorded_scpi_commands().
        """
        self._scpi_sent: List[str] = list()
        self._record_commands = True

    def get_recorded_scpi_commands(self) -> List[str]:
        """
        Returns:
            Sequence[str]: SCPI commands sent to the instrument
        """
        commands = self._scpi_sent
        self._scpi_sent = list()
        return commands

    def clear(self) -> None:
        """Reset the VISA message queue of the instrument
        """
        self.visa_handle.clear()

    def clear_read_queue(self) -> Sequence[str]:
        """Flush the VISA message queue of the instrument

        Takes at least _message_flush_timeout_ms to carry out.

        Returns:
            Sequence[str]: Messages lingering in queue
        """
        lingering = list()
        original_timeout = self.visa_handle.timeout
        self.visa_handle.timeout = self._message_flush_timeout_ms
        while True:
            try:
                message = self.visa_handle.read()
            except VisaIOError:
                break
            else:
                lingering.append(message)
        self.visa_handle.timeout = original_timeout
        return lingering

    def state(self) -> str:
        return self.ask('stat?')

    # -----------------------------------------------------------------------
    # Override communication methods to make it possible to record the
    # communication with the instrument.

    def write(self, cmd: str) -> None:
        """Send SCPI command to instrument

        Args:
            cmd (str): SCPI command
        """
        if self._record_commands:
            self._scpi_sent.append(cmd)
        super().write(cmd)

    def ask(self, cmd: str) -> str:
        """Send SCPI query to instrument

        Args:
            cmd (str): SCPI query

        Returns:
            str: SCPI answer
        """
        if self._record_commands:
            self._scpi_sent.append(cmd)
        answer = super().ask(cmd)
        return answer

    # -----------------------------------------------------------------------

    def _set_up_debug_settings(self) -> None:
        self._record_commands = False
        self._scpi_sent = list()
        self._message_flush_timeout_ms = 1
        self._round_off = None

    def _set_up_serial(self) -> None:
        # No harm in setting the speed even if the connection is not serial.
        self.visa_handle.baud_rate = 9600  # type: ignore

    def _check_for_wrong_model(self) -> None:
        model = self.IDN()['model']
        if model != 'QSwitch':
            raise ValueError(f'Unknown model {model}. Are you using the right'
                             ' driver for your instrument?')

    def _check_for_incompatiable_firmware(self) -> None:
        firmware = self.IDN()['firmware']
        least_compatible_fw = '0.1.0'
        if parse(firmware) < parse(least_compatible_fw):
            raise ValueError(f'Incompatible firmware {firmware}. You need at '
                             f'least {least_compatible_fw}')

    def _set_up_channels(self) -> None:
        channels = ChannelList(self, 'Lines', QSwitchChannel)
        for i in range(1, 24 + 1):
            name = f'line{i:02}'
            channel = QSwitchChannel(self, name, i)
            self.add_submodule(name, channel)
            channels.append(channel)
        channels.lock()
        self.add_submodule('lines', channels)

    def _set_up_simple_functions(self) -> None:
        self.add_function('abort', call_cmd='abor')

    def _check_instrument_name(self, name: str) -> None:
        if name.isidentifier():
            return
        raise ValueError(
            f'Instrument name "{name}" is incompatible with QCoDeS parameter '
            'generation (no spaces, punctuation, prepended numbers, etc)')
