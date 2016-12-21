#!/usr/bin/env python
import signal
import sys
import time

import oslo_messaging as messaging
import structlog

from oslo_config import cfg

from stepic_plugins import settings
from stepic_plugins import rpc


logger = structlog.get_logger()


def init():
    messaging.set_transport_defaults(control_exchange='stepic.rpc')
    cfg.CONF.executor_thread_pool_size = 1
    cfg.CONF.rpc_acks_late = True


def register_shutdown_handler(handler):
    """Register a handler that will be called on process termination."""
    original_handlers = {}

    def _signal_handler(signum, frame):
        # Revert signal handlers to originals
        for sig in [signal.SIGTERM, signal.SIGINT]:
            signal.signal(sig, original_handlers[sig])
        logger.info("Signal handler called with signal", signum=signum)
        handler()
        sys.exit(0)

    for sig in [signal.SIGTERM, signal.SIGINT]:
        original_handlers[sig] = signal.getsignal(sig)
        signal.signal(sig, _signal_handler)


def stop_server(rpc_server):
    """Attempt to stop the RPC server gracefully."""
    logger.info("Stopping RPC server...")
    try:
        rpc_server.stop()
        rpc_server.wait()
    except Exception:
        pass


def init_timeout_killer():
    if settings.USE_RPC_TIMEOUT_KILLER:
        timeout_killer = rpc.TimeoutKillerThread(settings.RPC_DEFAULT_TIMEOUT)
        timeout_killer.start()
        return timeout_killer


def stop_timeout_killer(timeout_killer):
    if timeout_killer:
        logger.info("Stopping RPC timeout killer...")
        timeout_killer.stop()


def main():
    init()
    timeout_killer = init_timeout_killer()
    rpc_server = rpc.get_server(settings.RPC_TRANSPORT_URL,
                                timeout_killer=timeout_killer)
    cfg.CONF.oslo_messaging_rabbit.rabbit_qos_prefetch_count = 1

    def shutdown_handler():
        stop_timeout_killer(timeout_killer)
        stop_server(rpc_server)

    register_shutdown_handler(shutdown_handler)
    logger.info("Starting stepic-plugins RPC server...")
    try:
        rpc_server.start()
        logger.info("RPC server started")
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logger.warning("RPC server stopped ungracefully")
        sys.exit(1)


if __name__ == '__main__':
    main()
