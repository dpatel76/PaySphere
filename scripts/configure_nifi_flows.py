#!/usr/bin/env python3
"""
Configure NiFi flows for GPS CDM payment message routing.

This script programmatically creates NiFi processors and connections
to route all 72+ payment message types through the medallion pipeline.

Usage:
    python configure_nifi_flows.py [--base-url http://localhost:8080]
"""

import argparse
import json
import requests
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ProcessorConfig:
    """Configuration for a NiFi processor."""
    name: str
    type: str
    position: Tuple[int, int]
    properties: Dict[str, str]
    auto_terminate: List[str] = None
    scheduling_period: str = "0 sec"
    scheduling_strategy: str = "TIMER_DRIVEN"
    concurrent_tasks: int = 1


class NiFiConfigurator:
    """Configure NiFi flows via REST API."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/nifi-api"
        self.session = requests.Session()
        self.root_pg_id = None

    def check_connection(self) -> bool:
        """Check if NiFi is accessible."""
        try:
            resp = self.session.get(f"{self.api_url}/system-diagnostics", timeout=10)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def get_root_process_group(self) -> str:
        """Get the root process group ID."""
        resp = self.session.get(f"{self.api_url}/process-groups/root")
        resp.raise_for_status()
        self.root_pg_id = resp.json()["id"]
        return self.root_pg_id

    def create_process_group(
        self, parent_id: str, name: str, position: Tuple[int, int], comment: str = ""
    ) -> str:
        """Create a new process group."""
        payload = {
            "revision": {"version": 0},
            "component": {
                "name": name,
                "position": {"x": position[0], "y": position[1]},
                "comments": comment,
            },
        }
        resp = self.session.post(
            f"{self.api_url}/process-groups/{parent_id}/process-groups",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["id"]

    def create_processor(
        self, parent_id: str, config: ProcessorConfig
    ) -> Dict:
        """Create a processor in the specified process group."""
        payload = {
            "revision": {"version": 0},
            "component": {
                "type": config.type,
                "name": config.name,
                "position": {"x": config.position[0], "y": config.position[1]},
                "config": {
                    "properties": config.properties,
                    "schedulingPeriod": config.scheduling_period,
                    "schedulingStrategy": config.scheduling_strategy,
                    "concurrentlySchedulableTaskCount": config.concurrent_tasks,
                    "autoTerminatedRelationships": config.auto_terminate or [],
                },
            },
        }
        resp = self.session.post(
            f"{self.api_url}/process-groups/{parent_id}/processors",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    def create_connection(
        self,
        parent_id: str,
        source_id: str,
        dest_id: str,
        relationships: List[str],
        source_type: str = "PROCESSOR",
        dest_type: str = "PROCESSOR",
    ) -> Dict:
        """Create a connection between two components."""
        payload = {
            "revision": {"version": 0},
            "component": {
                "source": {"id": source_id, "type": source_type, "groupId": parent_id},
                "destination": {"id": dest_id, "type": dest_type, "groupId": parent_id},
                "selectedRelationships": relationships,
            },
        }
        resp = self.session.post(
            f"{self.api_url}/process-groups/{parent_id}/connections",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    def create_funnel(self, parent_id: str, position: Tuple[int, int]) -> Dict:
        """Create a funnel for merging flows."""
        payload = {
            "revision": {"version": 0},
            "component": {
                "position": {"x": position[0], "y": position[1]},
            },
        }
        resp = self.session.post(
            f"{self.api_url}/process-groups/{parent_id}/funnels",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    def configure_gps_cdm_flow(self):
        """Configure the complete GPS CDM payment routing flow."""
        print("Configuring GPS CDM NiFi flows...")

        # Get root process group
        root_id = self.get_root_process_group()
        print(f"Root process group: {root_id}")

        # Create main GPS CDM process group
        gps_cdm_pg = self.create_process_group(
            root_id,
            "GPS CDM Payment Pipeline",
            (100, 100),
            "Comprehensive payment message routing for 72+ standards",
        )
        print(f"Created GPS CDM process group: {gps_cdm_pg}")

        # Create sub-process groups for each routing category
        process_groups = {}

        pg_configs = [
            ("Message Ingestion", (100, 100), "Kafka and file ingestion"),
            ("Message Type Detection", (400, 100), "Detect payment message type"),
            ("ISO 20022 Routing", (100, 300), "Route ISO 20022 messages (PAIN, PACS, CAMT, ACMT)"),
            ("SWIFT MT Routing", (400, 300), "Route SWIFT MT messages (MT1xx-MT9xx)"),
            ("Domestic Scheme Routing", (700, 300), "Route domestic payment schemes"),
            ("Real-Time Payment Routing", (100, 500), "Route real-time payment messages"),
            ("RTGS Routing", (400, 500), "Route RTGS system messages"),
            ("Celery Task Dispatch", (700, 100), "Submit tasks to Celery workers"),
            ("Error Handling", (700, 500), "Handle failures and dead-letter queue"),
        ]

        for name, position, comment in pg_configs:
            pg_id = self.create_process_group(gps_cdm_pg, name, position, comment)
            process_groups[name] = pg_id
            print(f"  Created: {name}")

        # Create processors in Message Type Detection group
        detection_pg = process_groups["Message Type Detection"]

        # GenerateFlowFile for testing
        generate_config = ProcessorConfig(
            name="Generate Test Message",
            type="org.apache.nifi.processors.standard.GenerateFlowFile",
            position=(100, 100),
            properties={
                "generate-ff-custom-text": '{"messageType": "pain.001", "messageId": "TEST-001"}',
                "character-set": "UTF-8",
            },
            scheduling_period="5 sec",
        )
        generate_proc = self.create_processor(detection_pg, generate_config)
        print(f"  Created processor: Generate Test Message")

        # EvaluateJsonPath to extract message type
        eval_config = ProcessorConfig(
            name="Extract Message Type",
            type="org.apache.nifi.processors.standard.EvaluateJsonPath",
            position=(100, 250),
            properties={
                "Destination": "flowfile-attribute",
                "message.type": "$.messageType",
                "message.id": "$.messageId",
            },
            auto_terminate=["failure", "unmatched"],
        )
        eval_proc = self.create_processor(detection_pg, eval_config)
        print(f"  Created processor: Extract Message Type")

        # RouteOnAttribute for message type routing
        route_config = ProcessorConfig(
            name="Route by Message Type",
            type="org.apache.nifi.processors.standard.RouteOnAttribute",
            position=(100, 400),
            properties={
                # ISO 20022 routes
                "pain.001": "${message.type:equals('pain.001')}",
                "pain.002": "${message.type:equals('pain.002')}",
                "pain.008": "${message.type:equals('pain.008')}",
                "pacs.002": "${message.type:equals('pacs.002')}",
                "pacs.004": "${message.type:equals('pacs.004')}",
                "pacs.008": "${message.type:equals('pacs.008')}",
                "camt.053": "${message.type:equals('camt.053')}",
                "camt.054": "${message.type:equals('camt.054')}",
                # SWIFT MT
                "mt103": "${message.type:toUpper():equals('MT103')}",
                "mt202": "${message.type:toUpper():equals('MT202')}",
                "mt940": "${message.type:toUpper():equals('MT940')}",
                # Domestic
                "ach": "${message.type:toUpper():equals('ACH') || message.type:toUpper():equals('NACHA')}",
                "fedwire": "${message.type:toUpper():equals('FEDWIRE')}",
                "sepa": "${message.type:toUpper():contains('SEPA')}",
                # Real-time
                "fednow": "${message.type:toUpper():equals('FEDNOW')}",
                "rtp": "${message.type:toUpper():equals('RTP')}",
                # Match all others
                "other": "${message.type:isEmpty():not()}",
            },
        )
        route_proc = self.create_processor(detection_pg, route_config)
        print(f"  Created processor: Route by Message Type")

        # Create connections within detection group
        self.create_connection(
            detection_pg,
            generate_proc["id"],
            eval_proc["id"],
            ["success"],
        )
        self.create_connection(
            detection_pg,
            eval_proc["id"],
            route_proc["id"],
            ["matched"],
        )
        print("  Created connections in Message Type Detection")

        # Create processors in Celery Task Dispatch group
        celery_pg = process_groups["Celery Task Dispatch"]

        # UpdateAttribute to prepare Celery payload
        update_config = ProcessorConfig(
            name="Prepare Celery Payload",
            type="org.apache.nifi.processors.attributes.UpdateAttribute",
            position=(100, 100),
            properties={
                "batch.id": "${UUID()}",
                "celery.task": "gps_cdm.orchestration.celery_tasks.process_bronze_partition",
                "celery.queue": "bronze",
            },
        )
        update_proc = self.create_processor(celery_pg, update_config)
        print(f"  Created processor: Prepare Celery Payload")

        # ReplaceText to format Celery task body
        replace_config = ProcessorConfig(
            name="Format Task Body",
            type="org.apache.nifi.processors.standard.ReplaceText",
            position=(100, 250),
            properties={
                "Replacement Value": '{"args": ["${batch.id}", [], "${message.type}", "${batch.id}", {}]}',
                "Replacement Strategy": "Always Replace",
            },
            auto_terminate=["failure"],
        )
        replace_proc = self.create_processor(celery_pg, replace_config)
        print(f"  Created processor: Format Task Body")

        # InvokeHTTP to call Celery Flower API
        invoke_config = ProcessorConfig(
            name="Submit to Celery",
            type="org.apache.nifi.processors.standard.InvokeHTTP",
            position=(100, 400),
            properties={
                "HTTP Method": "POST",
                "Remote URL": "http://flower:5555/api/task/send-task/${celery.task}",
                "Content-Type": "application/json",
            },
            auto_terminate=["Original", "No Retry", "Retry"],
        )
        invoke_proc = self.create_processor(celery_pg, invoke_config)
        print(f"  Created processor: Submit to Celery")

        # LogAttribute for successful submissions
        log_config = ProcessorConfig(
            name="Log Success",
            type="org.apache.nifi.processors.standard.LogAttribute",
            position=(100, 550),
            properties={
                "Log Level": "info",
                "Log Prefix": "Celery task submitted: ",
            },
            auto_terminate=["success"],
        )
        log_proc = self.create_processor(celery_pg, log_config)
        print(f"  Created processor: Log Success")

        # Create connections in Celery dispatch group
        self.create_connection(celery_pg, update_proc["id"], replace_proc["id"], ["success"])
        self.create_connection(celery_pg, replace_proc["id"], invoke_proc["id"], ["success"])
        self.create_connection(celery_pg, invoke_proc["id"], log_proc["id"], ["Response"])
        print("  Created connections in Celery Task Dispatch")

        # Create Error Handling processors
        error_pg = process_groups["Error Handling"]

        # LogAttribute for errors
        error_log_config = ProcessorConfig(
            name="Log Error",
            type="org.apache.nifi.processors.standard.LogAttribute",
            position=(100, 100),
            properties={
                "Log Level": "error",
                "Log Prefix": "Processing error: ",
            },
        )
        error_log = self.create_processor(error_pg, error_log_config)
        print(f"  Created processor: Log Error")

        # PutFile for dead-letter queue
        dlq_config = ProcessorConfig(
            name="Write to DLQ",
            type="org.apache.nifi.processors.standard.PutFile",
            position=(100, 250),
            properties={
                "Directory": "/opt/nifi/nifi-current/data/dlq/${message.type:replaceNull('unknown')}",
                "Conflict Resolution Strategy": "replace",
            },
            auto_terminate=["success", "failure"],
        )
        dlq_proc = self.create_processor(error_pg, dlq_config)
        print(f"  Created processor: Write to DLQ")

        # Connect error handling
        self.create_connection(error_pg, error_log["id"], dlq_proc["id"], ["success"])
        print("  Created connections in Error Handling")

        print("\nGPS CDM NiFi flow configuration complete!")
        print(f"\nCreated {len(process_groups)} process groups with processors and connections.")
        print("\nNext steps:")
        print("  1. Access NiFi UI at http://localhost:8080/nifi")
        print("  2. Review and start the GPS CDM Payment Pipeline process group")
        print("  3. Configure Kafka consumers for production ingestion")
        print("  4. Start Celery workers: celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold -l info")

        return process_groups


def main():
    parser = argparse.ArgumentParser(description="Configure NiFi flows for GPS CDM")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8080",
        help="NiFi base URL (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check NiFi connectivity, don't configure",
    )
    args = parser.parse_args()

    configurator = NiFiConfigurator(args.base_url)

    print(f"Checking NiFi connectivity at {args.base_url}...")
    if not configurator.check_connection():
        print("ERROR: Cannot connect to NiFi. Is it running?")
        return 1

    print("NiFi is accessible.\n")

    if args.check_only:
        root_id = configurator.get_root_process_group()
        print(f"Root process group ID: {root_id}")
        return 0

    try:
        configurator.configure_gps_cdm_flow()
        return 0
    except requests.HTTPError as e:
        print(f"ERROR: HTTP error during configuration: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
