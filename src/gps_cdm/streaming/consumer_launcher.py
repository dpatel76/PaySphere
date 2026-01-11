"""
GPS CDM - Multi-Consumer Launcher
=================================

Launches dedicated Kafka consumers for each message type.
Each consumer runs as a separate process, subscribing to its specific topic.

Benefits:
- Message type isolation (no mixing of different payment types)
- Independent scaling per message type
- Priority-based processing (can allocate more workers to high-volume types)
- Easier debugging and monitoring per type

Usage:
    # Launch consumers for all message types
    python -m gps_cdm.streaming.consumer_launcher --all

    # Launch consumer for specific types
    python -m gps_cdm.streaming.consumer_launcher --types pain.001,MT103,FEDWIRE

    # Launch with custom configuration
    python -m gps_cdm.streaming.consumer_launcher --types pain.001 --workers 8
"""

import os
import sys
import signal
import subprocess
import argparse
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# All supported message types with their priority (higher = more workers)
MESSAGE_TYPES: Dict[str, int] = {
    # ISO 20022
    'pain.001': 3,  # High volume
    'pacs.008': 3,
    'camt.053': 1,

    # NOTE: All SWIFT MT messages decommissioned Nov 2025 - use ISO 20022 equivalents

    # US Domestic
    'FEDWIRE': 3,
    'ACH': 3,
    'CHIPS': 2,
    'RTP': 2,
    'FEDNOW': 2,

    # UK
    'CHAPS': 2,
    'BACS': 2,
    'FPS': 2,

    # Europe
    'SEPA': 3,
    'TARGET2': 2,

    # APAC
    'NPP': 2,      # Australia
    'UPI': 2,      # India
    'RTGS_HK': 1,  # Hong Kong
    'MEPS_PLUS': 1, # Singapore (also MEPS)
    'BOJNET': 1,   # Japan
    'KFTC': 1,     # Korea
    'CNAPS': 1,    # China

    # Middle East
    'SARIE': 1,    # Saudi
    'UAEFTS': 1,   # UAE

    # Latin America & SE Asia
    'PIX': 2,       # Brazil
    'PROMPTPAY': 1, # Thailand
    'PAYNOW': 1,    # Singapore
    'INSTAPAY': 1,  # Philippines
}


@dataclass
class ConsumerProcess:
    """Represents a running consumer process."""
    message_type: str
    process: subprocess.Popen
    topic: str
    workers: int


class ConsumerManager:
    """
    Manages multiple Kafka consumer processes.

    Each message type gets its own consumer process that subscribes
    to the topic gps-cdm-{message_type}.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        base_workers: int = 2,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.base_workers = base_workers
        self.consumers: Dict[str, ConsumerProcess] = {}
        self.shutting_down = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down all consumers...")
        self.shutting_down = True
        self.stop_all()

    def start_consumer(
        self,
        message_type: str,
        workers: Optional[int] = None
    ) -> bool:
        """
        Start a consumer for a specific message type.

        Args:
            message_type: The payment message type (e.g., 'pain.001', 'MT103')
            workers: Number of worker threads (default: base_workers * priority)

        Returns:
            True if consumer started successfully
        """
        if message_type in self.consumers:
            logger.warning(f"Consumer for {message_type} already running")
            return False

        # Calculate workers based on priority
        priority = MESSAGE_TYPES.get(message_type, 1)
        num_workers = workers or (self.base_workers * priority)

        topic = f"gps-cdm-{message_type}"
        group_id = f"gps-cdm-{message_type.lower().replace('.', '-')}-consumer"

        # Build command
        cmd = [
            sys.executable, '-m', 'gps_cdm.streaming.kafka_consumer',
            '--topic', topic,
            '--type', message_type,
            '--bootstrap-servers', self.bootstrap_servers,
            '--group-id', group_id,
            '--workers', str(num_workers),
        ]

        # Build environment
        env = os.environ.copy()
        env.update({
            'GPS_CDM_DATA_SOURCE': os.environ.get('GPS_CDM_DATA_SOURCE', 'postgresql'),
            'POSTGRES_HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'POSTGRES_PORT': os.environ.get('POSTGRES_PORT', '5433'),
            'POSTGRES_DB': os.environ.get('POSTGRES_DB', 'gps_cdm'),
            'POSTGRES_USER': os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
            'POSTGRES_PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password'),
            'NEO4J_URI': os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
            'NEO4J_USER': os.environ.get('NEO4J_USER', 'neo4j'),
            'NEO4J_PASSWORD': os.environ.get('NEO4J_PASSWORD', 'neo4jpassword123'),
            'PYTHONPATH': f"src:{os.environ.get('PYTHONPATH', '')}",
        })

        try:
            # Start process
            log_file = f"/tmp/kafka_consumer_{message_type.replace('.', '_')}.log"
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                )

            self.consumers[message_type] = ConsumerProcess(
                message_type=message_type,
                process=process,
                topic=topic,
                workers=num_workers,
            )

            logger.info(f"Started consumer for {message_type} (topic={topic}, workers={num_workers}, pid={process.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to start consumer for {message_type}: {e}")
            return False

    def stop_consumer(self, message_type: str) -> bool:
        """Stop a specific consumer."""
        if message_type not in self.consumers:
            logger.warning(f"No consumer running for {message_type}")
            return False

        consumer = self.consumers[message_type]
        try:
            consumer.process.terminate()
            consumer.process.wait(timeout=10)
            logger.info(f"Stopped consumer for {message_type}")
        except subprocess.TimeoutExpired:
            consumer.process.kill()
            logger.warning(f"Killed consumer for {message_type} (didn't stop gracefully)")

        del self.consumers[message_type]
        return True

    def stop_all(self):
        """Stop all running consumers."""
        for message_type in list(self.consumers.keys()):
            self.stop_consumer(message_type)

    def start_all(self, message_types: Optional[List[str]] = None):
        """
        Start consumers for all (or specified) message types.

        Args:
            message_types: List of types to start, or None for all
        """
        types_to_start = message_types or list(MESSAGE_TYPES.keys())

        for msg_type in types_to_start:
            if msg_type not in MESSAGE_TYPES:
                logger.warning(f"Unknown message type: {msg_type}, skipping")
                continue
            self.start_consumer(msg_type)
            time.sleep(0.5)  # Small delay between starts

    def monitor(self):
        """Monitor running consumers and restart failed ones."""
        while not self.shutting_down:
            for msg_type, consumer in list(self.consumers.items()):
                if consumer.process.poll() is not None:
                    # Process has exited
                    exit_code = consumer.process.returncode
                    logger.warning(f"Consumer for {msg_type} exited with code {exit_code}, restarting...")
                    del self.consumers[msg_type]
                    self.start_consumer(msg_type, consumer.workers)

            time.sleep(5)

    def status(self) -> Dict[str, Dict]:
        """Get status of all consumers."""
        status = {}
        for msg_type, consumer in self.consumers.items():
            running = consumer.process.poll() is None
            status[msg_type] = {
                'topic': consumer.topic,
                'workers': consumer.workers,
                'pid': consumer.process.pid,
                'running': running,
            }
        return status


def main():
    parser = argparse.ArgumentParser(
        description='GPS CDM Multi-Consumer Launcher'
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Start consumers for all message types'
    )
    parser.add_argument(
        '--types', type=str,
        help='Comma-separated list of message types to start'
    )
    parser.add_argument(
        '--bootstrap-servers', default='localhost:9092',
        help='Kafka bootstrap servers'
    )
    parser.add_argument(
        '--base-workers', type=int, default=2,
        help='Base number of workers (multiplied by priority)'
    )
    parser.add_argument(
        '--monitor', action='store_true',
        help='Monitor and restart failed consumers'
    )

    args = parser.parse_args()

    if not args.all and not args.types:
        parser.error("Must specify --all or --types")

    manager = ConsumerManager(
        bootstrap_servers=args.bootstrap_servers,
        base_workers=args.base_workers,
    )

    # Determine which types to start
    if args.all:
        types_to_start = None  # All types
    else:
        types_to_start = [t.strip() for t in args.types.split(',')]

    # Start consumers
    manager.start_all(types_to_start)

    # Show status
    logger.info("Consumer status:")
    for msg_type, status in manager.status().items():
        logger.info(f"  {msg_type}: pid={status['pid']}, workers={status['workers']}, topic={status['topic']}")

    # Monitor if requested
    if args.monitor:
        logger.info("Monitoring consumers (Ctrl+C to stop)...")
        try:
            manager.monitor()
        except KeyboardInterrupt:
            pass
    else:
        logger.info("Consumers started. Use --monitor to keep running and auto-restart failed consumers.")
        logger.info("Consumer logs are in /tmp/kafka_consumer_*.log")

    # Cleanup
    manager.stop_all()


if __name__ == '__main__':
    main()
