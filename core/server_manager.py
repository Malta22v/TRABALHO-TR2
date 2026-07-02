class ServerManager:

    def __init__(self, servers, health_checker=None):

        self.servers = sorted(
            servers,
            key=lambda s: s["priority"]
        )

        self.current_index = 0
        self.health_checker = (
            health_checker
            or self._default_health_checker
        )

    def get_current_server(self):

        return self.servers[self.current_index]

    def get_base_url(self):

        return self.get_current_server()["url"]

    def get_server_id(self):

        return self.get_current_server()["id"]

    def is_on_primary(self):

        return self.current_index == 0

    def _default_health_checker(self, server):

        import requests

        response = requests.get(
            f"{server['url']}/health",
            timeout=2
        )

        return response.status_code == 200

    def failover(self):

        total_servers = len(self.servers)

        for offset in range(1, total_servers):

            candidate_index = (
                self.current_index + offset
            ) % total_servers

            candidate = self.servers[candidate_index]

            try:

                if not self.health_checker(candidate):
                    continue

                self.current_index = candidate_index

                print(
                    f"FAILOVER -> "
                    f"{candidate['id']}"
                )

                return candidate

            except Exception:
                continue

        return None

    def failback_to_primary(self):

        if self.is_on_primary():
            return None

        primary = self.servers[0]

        try:

            if not self.health_checker(primary):
                return None

            self.current_index = 0

            print(
                f"FAILBACK -> "
                f"{primary['id']}"
            )

            return primary

        except Exception:
            return None
