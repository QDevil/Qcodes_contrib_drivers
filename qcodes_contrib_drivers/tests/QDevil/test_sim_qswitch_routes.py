import pytest
from .sim_qswitch_fixtures import qswitch  # noqa
from qcodes_contrib_drivers.drivers.QDevil.QSwitch import (
    _state_diff,
    channel_list_to_state,
    compress_channel_list,
    expand_channel_list)


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
    unpacked = channel_list_to_state(input)
    # -----------------------------------------------------------------------
    assert unpacked == output


@pytest.mark.wip
def test_channel_list_can_be_unpacked():  # noqa
    # -----------------------------------------------------------------------
    unpacked = expand_channel_list('(@1!0:3!0,4!9,23!7:24!7)')
    # -----------------------------------------------------------------------
    assert unpacked == '(@1!0,2!0,3!0,4!9,23!7,24!7)'


@pytest.mark.wip
@pytest.mark.parametrize(('input', 'output'), [
    ('(@)', '(@)'),
    ('(@1!2)', '(@1!2)'),
    ('(@1!2,3!2)', '(@1!2,3!2)'),
    ('(@1!0,2!0,3!0,4!9,23!7,24!7)', '(@1!0:3!0,23!7:24!7,4!9)')
])
def test_channel_list_can_be_packed(input, output):  # noqa
    # -----------------------------------------------------------------------
    packed = compress_channel_list(input)
    # -----------------------------------------------------------------------
    assert packed == output


@pytest.mark.wip
@pytest.mark.parametrize(('before', 'after', 'positive', 'negative'), [
    ([], [], [], []),
    ([], [(1,2)], [(1,2)], []),
    ([(7,5)], [(1,2)], [(1,2)], [(7,5)]),
])
def test_state_diff(before, after, positive, negative):  # noqa
    # -----------------------------------------------------------------------
    pos, neg, _ = _state_diff(before, after)
    # -----------------------------------------------------------------------
    assert pos == positive
    assert neg == negative


@pytest.mark.wip
def test_update_cached_state(qswitch):  # noqa
    # -----------------------------------------------------------------------
    state = qswitch.state_force_update()
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['stat?']
    assert state == '(@1!0:24!0)'


@pytest.mark.wip
def test_get_state(qswitch):  # noqa
    # -----------------------------------------------------------------------
    state = qswitch.state()
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == []
    assert state == '(@1!0:24!0)'


@pytest.mark.wip
def test_set_state_changes_the_state(qswitch):  # noqa
    # -----------------------------------------------------------------------
    qswitch.set_state([(24,8), (24,8), (22,7), (20,6), (1,9), (2,0)])
    # -----------------------------------------------------------------------
    assert qswitch.state() == '(@2!0,20!6,22!7,24!8,1!9)'


@pytest.mark.wip
def test_set_state_only_sends_diff(qswitch):  # noqa
    # -----------------------------------------------------------------------
    qswitch.set_state([(24,8), (24,8), (22,7), (20,6), (1,9), (2,0)])
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == [
        'clos (@20!6,22!7,24!8,1!9)',
        'open (@1!0,3!0:24!0)'
    ]


@pytest.mark.wip
def test_set_state_ignores_empty_diff(qswitch):  # noqa
    qswitch.set_state([(24,8), (24,8), (22,7), (20,6), (1,9), (2,0)])
    qswitch.start_recording_scpi()
    # -----------------------------------------------------------------------
    qswitch.set_state([(24,8), (22,7), (20,6), (1,9), (2,0)])
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == []


@pytest.mark.wip
def test_states_are_sanitised(qswitch):  # noqa
    # -----------------------------------------------------------------------
    qswitch.set_state([(24,8), (22,7), (20,6), (1,9), (2,0), (24,8), (20,6)])
    # -----------------------------------------------------------------------
    assert qswitch._state == [(1,9), (2,0), (20,6), (22,7), (24,8)]
