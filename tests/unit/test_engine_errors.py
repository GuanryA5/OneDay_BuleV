# -*- coding: utf-8 -*-
import pytest

from bluev.core.workflow_engine import CircularDependencyError, WorkflowEngine
from bluev.nodes.control.delay_node import DelayNode
from bluev.nodes.utility.log_node import LogNode


def test_connect_invalid_ports():
    eng = WorkflowEngine()
    d = DelayNode(node_id="d")
    log_node = LogNode(node_id="log_node")
    eng.add_node(d)
    eng.add_node(log_node)

    with pytest.raises(ValueError):
        eng.connect_nodes("d", "bad", "log_node", "message")
    with pytest.raises(ValueError):
        eng.connect_nodes("d", "actual_delay", "log_node", "bad")


def test_circular_dependency_detection():
    eng = WorkflowEngine()
    a = DelayNode(node_id="a")
    b = LogNode(node_id="b")
    a.set_input("duration", 0.01)
    b.set_input("message", "ok")

    eng.add_node(a)
    eng.add_node(b)

    # a -> b, b -> a 形成环
    eng.connect_nodes("a", "actual_delay", "b", "message")
    eng.connect_nodes("b", "log_level", "a", "duration")

    with pytest.raises(CircularDependencyError):
        eng.topological_sort()
