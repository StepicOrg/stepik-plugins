#!/usr/bin/env python
import signal
import sys

import oslo_messaging as messaging
import structlog

from functools import partial

from oslo_config import cfg

from stepic_plugins import settings
from stepic_plugins import rpc


logger = structlog.get_logger()


def init():
    messaging.set_transport_defaults(control_exchange='stepic.rpc')
    # cfg.CONF.rpc_acks_late = True


def register_shutdown_handler(handler):
    """Register a handler that will be called on process termination."""

    def _signal_handler(signum, frame):
        logger.info("Signal handler called with signal", signum=signum)
        handler()
        sys.exit(0)

    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, _signal_handler)


def stop_server(rpc_server):
    """Attempt to stop the RPC server gracefully."""
    logger.info("Stopping RPC server...")
    try:
        rpc_server.stop()
        rpc_server.wait()
    except Exception:
        pass


def main():
    init()
    rpc_server = rpc.get_server(settings.RPC_TRANSPORT_URL)
    cfg.CONF.oslo_messaging_rabbit.rabbit_prefetch_count = 1

    shutdown_handler = partial(stop_server, rpc_server)
    register_shutdown_handler(shutdown_handler)
    logger.info("Starting stepic-plugins RPC server...")
    rpc_server.start()
    rpc_server.wait()


if __name__ == '__main__':
    main()
