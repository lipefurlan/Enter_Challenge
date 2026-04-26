import json
import os

from vo.client_vo import ClientVO


CLIENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "clients")


class ClientDAO:
    def __init__(self, clients_dir: str = CLIENTS_DIR):
        self.clients_dir = os.path.abspath(clients_dir)

    def list_clients(self) -> list[ClientVO]:
        clients = []
        for folder in sorted(os.listdir(self.clients_dir)):
            metadata_path = os.path.join(self.clients_dir, folder, "metadata.json")
            if os.path.isfile(metadata_path):
                with open(metadata_path, encoding="utf-8") as f:
                    data = json.load(f)
                clients.append(ClientVO(
                    id=folder,
                    name=data["name"],
                    email=data["email"],
                    advisor_name=data["advisor_name"],
                ))
        return clients

    def get_client(self, client_id: str) -> ClientVO:
        metadata_path = os.path.join(self.clients_dir, client_id, "metadata.json")
        if not os.path.isfile(metadata_path):
            raise FileNotFoundError(f"Client '{client_id}' not found.")
        with open(metadata_path, encoding="utf-8") as f:
            data = json.load(f)
        return ClientVO(
            id=client_id,
            name=data["name"],
            email=data["email"],
            advisor_name=data["advisor_name"],
        )

    def get_client_files(self, client_id: str) -> dict[str, str]:
        client_dir = os.path.join(self.clients_dir, client_id)
        file_map = {
            "portfolio_text":    "portfolio.txt",
            "risk_profile_text": "risk_profile.txt",
            "macro_text":        "macro_analysis.txt",
            "dividend_csv":      "dividend_data.csv",
            "profitability_csv": "profitability_calc.csv",
        }
        result = {}
        for key, filename in file_map.items():
            path = os.path.join(client_dir, filename)
            with open(path, encoding="utf-8") as f:
                result[key] = f.read()
        return result