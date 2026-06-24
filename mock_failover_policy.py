from collections import deque

from abr.abr_hybrid import (
    choose_quality_hybrid,
    median_throughput_for_hybrid
)
from core.server_manager import ServerManager


SERVERS = [
    {
        "id": "server1",
        "url": "http://localhost:8080",
        "priority": 1
    },
    {
        "id": "server2",
        "url": "http://localhost:8081",
        "priority": 2
    }
]

REPRESENTATIONS = [
    {
        "quality": "360p",
        "bitrate_kbps": 800
    },
    {
        "quality": "720p",
        "bitrate_kbps": 2500
    },
    {
        "quality": "1080p",
        "bitrate_kbps": 4500
    }
]


class MockHealth:

    def __init__(self, healthy_ids):
        self.healthy_ids = set(healthy_ids)

    def __call__(self, server):
        return server["id"] in self.healthy_ids


def assert_failover_bidirectional():
    health = MockHealth({"server2"})
    manager = ServerManager(SERVERS, health_checker=health)

    assert manager.get_server_id() == "server1"
    assert manager.failover()["id"] == "server2"
    assert manager.get_server_id() == "server2"

    health.healthy_ids = {"server1"}

    assert manager.failover()["id"] == "server1"
    assert manager.get_server_id() == "server1"


def assert_hybrid_policy_high_buffer_filters_low_throughput():
    history = deque(
        [4200, 4300, 120, 4400, 4500],
        maxlen=5
    )

    filtered_median = median_throughput_for_hybrid(
        history,
        buffer_level=15.0
    )

    chosen = choose_quality_hybrid(
        avg_throughput_kbps=filtered_median,
        representations=REPRESENTATIONS,
        buffer_level=15.0,
        jitter_ewma_kbps=100,
        debug=False
    )

    assert filtered_median == 4350.0
    assert chosen["quality"] == "1080p"


def assert_hybrid_policy_low_buffer_uses_jitter_conservatively():
    chosen = choose_quality_hybrid(
        avg_throughput_kbps=3000,
        representations=REPRESENTATIONS,
        buffer_level=6.0,
        jitter_ewma_kbps=900,
        debug=False
    )

    assert chosen["quality"] == "360p"


if __name__ == "__main__":
    assert_failover_bidirectional()
    assert_hybrid_policy_high_buffer_filters_low_throughput()
    assert_hybrid_policy_low_buffer_uses_jitter_conservatively()

    print("OK - mock de failover e politica HYBRID validado")
