import pytest
from .sim_qswitch_fixtures import qswitch  # noqa


@pytest.mark.wip
def test_unknown_line_name_gives_error(qswitch):  # noqa
    # -----------------------------------------------------------------------
    with pytest.raises(ValueError) as error:
        qswitch.break_out('plunger', '1')
    # -----------------------------------------------------------------------
    assert 'Unknown line' in repr(error)


@pytest.mark.wip
def test_unknown_tap_name_gives_error(qswitch):  # noqa
    # -----------------------------------------------------------------------
    with pytest.raises(ValueError) as error:
        qswitch.break_out('1', 'VNA')
    # -----------------------------------------------------------------------
    assert 'Unknown tap' in repr(error)
