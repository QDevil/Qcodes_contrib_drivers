import pytest
from unittest.mock import MagicMock, call
from .sim_qdac2_fixtures import qdac  # noqa
import numpy as np
import itertools
import math


# def test_current_mocks(qdac):  # noqa
#     gates = {'sensor1': 1, 'plunger2': 2, 'plunger3': 3}
#     currents = {'sensor1': 0.01, 'plunger2': 0.02, 'plunger3': 0.03}
#     for gate, current_A in currents.items():
#         qdac.channel(gates[gate]).read_current_A = MagicMock(return_value=current_A)
#     # -----------------------------------------------------------------------
#     fakes = [qdac.channel(i).read_current_A() for _, i in gates.items()]
#     # -----------------------------------------------------------------------
#     assert fakes == [0.01, 0.02, 0.03]
    

def test_arrangement_channel_numbers(qdac):
    gates = {'sensor1': 1, 'plunger2': 2, 'plunger3': 3}
    arrangement = qdac.arrange(gates)
    # -----------------------------------------------------------------------
    numbers = arrangement.channel_numbers
    # -----------------------------------------------------------------------
    assert numbers == [1,2,3]


def test_arrangement_steady_state(qdac, mocker):
    sleep_fn = mocker.patch('qcodes_contrib_drivers.drivers.QDevil.QDAC2.sleep_s')
    gates = {'sensor1': 1, 'plunger2': 2, 'plunger3': 3}
    arrangement = qdac.arrange(gates)
    qdac.start_recording_scpi()
    # -----------------------------------------------------------------------
    currents_A = arrangement.currents_A(nplc=2)
    # -----------------------------------------------------------------------
    assert currents_A == [0.1,0.2,0.3]  # Hard-coded in simulation
    sleep_fn.assert_called_once_with(2 * (1/50))
    commands = qdac.get_recorded_scpi_commands()
    assert commands == [
        'sens:rang low,(@1,2,3)',
        'sens:nplc 2,(@1,2,3)',
        # (Sleep NPLC / line_freq)
        'read? (@1,2,3)',
    ]

from qcodes_contrib_drivers.drivers.QDevil.QDAC2 import diff_matrix

def test_diff_matrix():
    # -----------------------------------------------------------------------
    diff = diff_matrix([0.1,0.2], [[0.1,0.3],[0.3,0.2]])
    # -----------------------------------------------------------------------
    expected = np.array([[0.0,0.1], [0.2,0.0]])
    assert np.allclose(diff, expected)
    # HERE:


def test_arrangement_leakage(qdac, mocker):  # noqa
    sleep_fn = mocker.patch('qcodes_contrib_drivers.drivers.QDevil.QDAC2.sleep_s')
    gates = {'sensor1': 1, 'plunger2': 2, 'plunger3': 3}
    # Mock current readings
    currents = {'sensor1': 0.1, 'plunger2': 0.2, 'plunger3': 0.3}
    for gate, current_A in currents.items():
        qdac.channel(gates[gate]).read_current_A = MagicMock(return_value=current_A)
    arrangement = qdac.arrange(gates)
    arrangement.set_virtual_voltage('sensor1', 0.3)
    arrangement.set_virtual_voltage('plunger3', 0.4)
    qdac.start_recording_scpi()
    # -----------------------------------------------------------------------
    leakage_matrix = arrangement.leakage(modulation_V=0.005, nplc=2)
    # -----------------------------------------------------------------------
    commands = qdac.get_recorded_scpi_commands()
    assert commands == [
        'sens:rang low,(@1,2,3)',
        'sens:nplc 2,(@1,2,3)',
        # (Sleep NPLC / line_freq)
        # Steady-state reading
        'read? (@1,2,3)',
        # First modulation
        'sour1:volt:mode fix',
        'sour1:volt 0.305',
        # (Sleep NPLC / line_freq)
        'sens:rang low,(@1,2,3)',
        'sens:nplc 2,(@1,2,3)',
        'read? (@1,2,3)',
        'sour1:volt:mode fix',
        'sour1:volt 0.3',
        # Second modulation
        'sour2:volt:mode fix',
        'sour2:volt 0.005',
        # (Sleep NPLC / line_freq)
        'sens:rang low,(@1,2,3)',
        'sens:nplc 2,(@1,2,3)',
        'read? (@1,2,3)',
        'sour2:volt:mode fix',
        'sour2:volt 0.0',
        # Third modulation
        'sour3:volt:mode fix',
        'sour3:volt 0.405',
        # (Sleep NPLC / line_freq)
        'sens:rang low,(@1,2,3)',
        'sens:nplc 2,(@1,2,3)',
        'read? (@1,2,3)',
        'sour3:volt:mode fix',
        'sour3:volt 0.4',
    ]
    delay_s = 2 * (1/50)
    sleep_fn.assert_has_calls(itertools.repeat(call(delay_s),4))
    inf = math.inf
    expected = [[inf, inf, inf], [inf, inf, inf], [inf, inf, inf]]
    assert np.allclose(leakage_matrix, np.array(expected))
