"""Loaded automatically (via PYTHONPATH) by the gate to prove the engine needs no network."""
import socket


def _blocked(*args, **kwargs):
    raise OSError("network disabled by StackSense gate")


socket.socket.connect = _blocked
socket.create_connection = _blocked
socket.getaddrinfo = _blocked
