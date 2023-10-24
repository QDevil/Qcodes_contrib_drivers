import pytest
from .common import assert_items_equal
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
    ([(7,5), (3,4)], [(1,2), (3,4)], [(1,2)], [(7,5)]),
])
def test_state_diff(before, after, positive, negative):  # noqa
    # -----------------------------------------------------------------------
    pos, neg, _ = _state_diff(before, after)
    # -----------------------------------------------------------------------
    assert pos == positive
    assert neg == negative


@pytest.mark.wip
def test_cached_state_can_be_updated(qswitch):  # noqa
    # -----------------------------------------------------------------------
    qswitch.state_force_update()
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['stat?']


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
    qswitch.all_closed_relays([(24,8), (24,8), (22,7), (20,6), (1,9), (2,0)])
    # -----------------------------------------------------------------------
    assert qswitch.state() == '(@2!0,20!6,22!7,24!8,1!9)'


@pytest.mark.wip
def test_set_state_only_sends_diff(qswitch):  # noqa
    # -----------------------------------------------------------------------
    qswitch.all_closed_relays([(24,8), (24,8), (22,7), (20,6), (1,9), (2,0)])
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == [
        'clos (@20!6,22!7,24!8,1!9)',
        'open (@1!0,3!0:24!0)'
    ]


@pytest.mark.wip
def test_set_state_ignores_empty_diff(qswitch):  # noqa
    qswitch.all_closed_relays([(24,8), (24,8), (22,7), (20,6), (1,9), (2,0)])
    qswitch.start_recording_scpi()
    # -----------------------------------------------------------------------
    qswitch.all_closed_relays([(24,8), (22,7), (20,6), (1,9), (2,0)])
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == []


@pytest.mark.wip
def test_states_are_sanitised(qswitch):  # noqa
    # -----------------------------------------------------------------------
    qswitch.all_closed_relays([(24,8), (22,7), (20,6), (1,9), (2,0), (24,8), (20,6)])
    # -----------------------------------------------------------------------
    assert_items_equal(
        qswitch.all_closed_relays(),
        [(1,9), (2,0), (20,6), (22,7), (24,8)]
    )


@pytest.mark.wip
def test_individual_relays_can_be_closed(qswitch):  # noqa
    qswitch.start_recording_scpi()
    # -----------------------------------------------------------------------
    qswitch.close_relays([(14,1), (22,7)])
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['clos (@14!1,22!7)']


@pytest.mark.wip
def test_individual_relay_can_be_closed(qswitch):  # noqa
    qswitch.start_recording_scpi()
    # -----------------------------------------------------------------------
    qswitch.close_relay(22, 7)
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['clos (@22!7)']


@pytest.mark.wip
def test_individual_relays_can_be_opened(qswitch):  # noqa
    qswitch.start_recording_scpi()
    # -----------------------------------------------------------------------
    qswitch.open_relays([(14,0), (22,0), (1,1)])
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['open (@14!0,22!0)']


@pytest.mark.wip
def test_individual_relay_can_be_opened(qswitch):  # noqa
    qswitch.start_recording_scpi()
    # -----------------------------------------------------------------------
    qswitch.open_relay(14, 0)
    # -----------------------------------------------------------------------
    commands = qswitch.get_recorded_scpi_commands()
    assert commands == ['open (@14!0)']
