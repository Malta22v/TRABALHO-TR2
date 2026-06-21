import requests


class ServerManager:

    def __init__(self, servers):

        self.servers = sorted(
            servers,
            key=lambda s: s["priority"]
        )

        self.current_index = 0

    def get_current_server(self):

        return self.servers[self.current_index]

    def get_base_url(self):

        return self.get_current_server()["url"]

    def get_server_id(self):

        return self.get_current_server()["id"]

    def failover(self):

        if self.current_index + 1 >= len(self.servers):
            return None

        next_server = self.servers[
            self.current_index + 1
        ]

        try:

            response = requests.get(
                f"{next_server['url']}/health",
                timeout=2
            )

            if response.status_code == 200:

                self.current_index += 1

                print(
                    f"FAILOVER -> "
                    f"{next_server['id']}"
                )

                return next_server

        except:
            pass

        return None