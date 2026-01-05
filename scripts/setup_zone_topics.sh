#!/bin/bash
# GPS CDM - Zone-Separated Kafka Topic Setup
# ==========================================
# Creates Kafka topics for each zone (bronze, silver, gold) and message type.
#
# Usage:
#   ./scripts/setup_zone_topics.sh [--bootstrap-server BROKER] [--partitions N] [--replication N]
#
# Examples:
#   ./scripts/setup_zone_topics.sh
#   ./scripts/setup_zone_topics.sh --bootstrap-server localhost:9092 --partitions 3

set -e

# Default configuration
BOOTSTRAP_SERVER="${BOOTSTRAP_SERVER:-localhost:9092}"
PARTITIONS="${PARTITIONS:-3}"
REPLICATION="${REPLICATION:-1}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --bootstrap-server)
            BOOTSTRAP_SERVER="$2"
            shift 2
            ;;
        --partitions)
            PARTITIONS="$2"
            shift 2
            ;;
        --replication)
            REPLICATION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Message types (29 supported types)
MESSAGE_TYPES=(
    # ISO 20022
    "pain.001" "pain.002" "pain.008"
    "pacs.002" "pacs.003" "pacs.004" "pacs.008" "pacs.009"
    "camt.052" "camt.053" "camt.054"

    # SWIFT MT
    "MT103" "MT202" "MT940" "MT101" "MT199"

    # US Domestic
    "FEDWIRE" "ACH" "CHIPS" "RTP" "FEDNOW"

    # UK
    "CHAPS" "BACS" "FPS"

    # Europe
    "SEPA" "TARGET2"

    # APAC
    "NPP" "UPI" "PIX" "INSTAPAY" "PAYNOW" "PROMPTPAY"
    "MEPS_PLUS" "CNAPS" "BOJNET" "KFTC" "RTGS_HK"

    # Middle East
    "SARIE" "UAEFTS"
)

# Zones
ZONES=("bronze" "silver" "gold")

# Function to check if running in Docker
check_kafka_cli() {
    if command -v kafka-topics &> /dev/null; then
        KAFKA_TOPICS_CMD="kafka-topics"
    elif docker ps --format '{{.Names}}' | grep -q "gps-cdm-kafka"; then
        KAFKA_TOPICS_CMD="docker exec gps-cdm-kafka kafka-topics"
        echo "Using Docker Kafka..."
    else
        echo "Error: Kafka CLI not found. Please install Kafka or start Docker containers."
        exit 1
    fi
}

# Function to create a topic
create_topic() {
    local topic=$1
    echo "Creating topic: $topic"

    $KAFKA_TOPICS_CMD --bootstrap-server "$BOOTSTRAP_SERVER" \
        --create \
        --topic "$topic" \
        --partitions "$PARTITIONS" \
        --replication-factor "$REPLICATION" \
        --if-not-exists \
        2>/dev/null || true
}

# Main
echo "=============================================="
echo "GPS CDM - Zone-Separated Kafka Topic Setup"
echo "=============================================="
echo "Bootstrap Server: $BOOTSTRAP_SERVER"
echo "Partitions: $PARTITIONS"
echo "Replication Factor: $REPLICATION"
echo "Message Types: ${#MESSAGE_TYPES[@]}"
echo "Zones: ${ZONES[*]}"
echo "=============================================="
echo

check_kafka_cli

# Create topics for each zone and message type
TOTAL_TOPICS=0
for zone in "${ZONES[@]}"; do
    echo
    echo "=== Creating $zone topics ==="

    for msg_type in "${MESSAGE_TYPES[@]}"; do
        topic="${zone}.${msg_type}"
        create_topic "$topic"
        ((TOTAL_TOPICS++))
    done
done

# Create Dead Letter Queue topics
echo
echo "=== Creating DLQ topics ==="
for zone in "${ZONES[@]}"; do
    create_topic "dlq.${zone}"
    ((TOTAL_TOPICS++))
done

# List all created topics
echo
echo "=============================================="
echo "Topic Summary"
echo "=============================================="
echo "Total topics created: $TOTAL_TOPICS"
echo
echo "Topics by zone:"
for zone in "${ZONES[@]}"; do
    count=$(echo "${MESSAGE_TYPES[@]}" | wc -w | tr -d ' ')
    echo "  ${zone}: ${count} topics + 1 DLQ"
done
echo
echo "Listing topics:"
$KAFKA_TOPICS_CMD --bootstrap-server "$BOOTSTRAP_SERVER" --list | grep -E "^(bronze|silver|gold|dlq)\." | sort

echo
echo "Topic setup complete!"
