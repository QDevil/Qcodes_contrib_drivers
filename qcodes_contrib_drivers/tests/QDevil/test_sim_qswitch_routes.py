import pytest
import re
from .sim_qswitch_fixtures import qswitch  # noqa
from qcodes_contrib_drivers.drivers.QDevil.QSwitch import channel_list_to_map

@pytest.mark.wip
def test_get_state(qswitch):  # noqa
    # -----------------------------------------------------------------------
    state = qswitch.state()
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['stat?']
    assert state == '(@1!0:24!0)'


@pytest.mark.wip
@pytest.mark.parametrize(('input', 'output'), [
    ('(@)', []),
    ('(@1!0,2!0)', [(1,0), (2,0)]),
    ('(@1!0:2!0)', [(1,0), (2,0)]),
    ('(@1!0,1!9)', [(1,0), (1,9)]),
    ('(@1!0:3!0,4!9,23!7:24!7)', [(1,0), (2,0), (3,0), (4,9), (23,7), (24,7)]),
])
def test_channel_list_to_map(input, output):  # noqa
    # -----------------------------------------------------------------------
    unpacked = channel_list_to_map(input)
    # -----------------------------------------------------------------------
    assert unpacked == output


@pytest.mark.wip
def test_channel_list_can_be_unpacked(qswitch):  # noqa
    # -----------------------------------------------------------------------
    unpacked = qswitch.unpack('(@1!0:3!0,4!9,23!7:24!7)')
    # -----------------------------------------------------------------------
    assert unpacked == '(@1!0,2!0,3!0,4!9,23!7,24!7)'


@pytest.mark.wip
@pytest.mark.parametrize("channel", [1,24])
def test_line_turn_on(qswitch, channel):  # noqa
    # -----------------------------------------------------------------------
    line = getattr(qswitch, f'line{channel:02}')
    line.on()
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == [f'clos (@{channel}!9)']


@pytest.mark.wip
@pytest.mark.parametrize("channel", [2,23])
def test_line_turn_off(qswitch, channel):  # noqa
    # -----------------------------------------------------------------------
    line = getattr(qswitch, f'line{channel:02}')
    line.off()
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == [f'open (@{channel}!9)']

