#!/usr/bin/env python
import signal
import sys

import structlog

from functools import partial

from oslo import messaging
from stepic_plugins import settings
from stepic_plugins import rpc


logger = structlog.get_logger()


def init():
    messaging.set_transport_defaults(control_exchange='stepic.rpc')


def register_shutdown_handler(handler):
    """Register a handler that will be called on process termination."""

    def _signal_handler(signum, frame):
        print('Signal handler called with signal', signum)
        handler()
        sys.exit(0)

    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, _signal_handler)


def stop_server(rpc_server):
    """Attempt to stop the RPC server gracefully."""
    # TODO: configure logging
    print("Stopping RPC server...")
    try:
        rpc_server.stop()
        rpc_server.wait()
    except Exception:
        pass


def main():
    init()
    rpc_server = rpc.get_server(settings.RPC_TRANSPORT_URL)
    shutdown_handler = partial(stop_server, rpc_server)
    register_shutdown_handler(shutdown_handler)
    logger.info("Starting stepic-plugins RPC server...")
    rpc_server.start()
    rpc_server.wait()


if __name__ == '__main__':
    main()
