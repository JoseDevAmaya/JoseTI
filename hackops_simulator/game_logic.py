import random

from models import Mission, PlayerProgress, SessionState


def build_missions() -> list[Mission]:
    return [
        Mission(
            mission_id=1,
            name="Operation Neon Key",
            briefing=(
                "Target: corp relay node 10.0.4.21. Gain foothold and recover the file "
                "'flag.txt' from the host. Stay stealthy."
            ),
            target_ip="10.0.4.21",
            vulnerable_service="ftp",
            files={
                "readme.txt": "Legacy relay node. Maintenance pending.",
                "users.db": "Encrypted entries... checksum mismatch.",
                "flag.txt": "FLAG{NEON_RELAY_BREACH_CONFIRMED}",
            },
            required_file="flag.txt",
            reward_reputation=25,
            reward_exp=60,
        ),
        Mission(
            mission_id=2,
            name="Operation Cold Stack",
            briefing=(
                "Target: database bridge 172.16.33.9. Enumerate services and extract "
                "'intel.log' from the backend filesystem."
            ),
            target_ip="172.16.33.9",
            vulnerable_service="mysql",
            files={
                "backup.zip": "Corrupted archive blocks detected.",
                "intel.log": "TX routes + auth notes. FLAG{COLD_STACK_INTEL}",
                "todo.md": "Disable old DB port before audit.",
            },
            required_file="intel.log",
            reward_reputation=30,
            reward_exp=70,
        ),
        Mission(
            mission_id=3,
            name="Operation Ghost Mirror",
            briefing=(
                "Target: exposed mirror 192.168.77.40. Compromise web service and retrieve "
                "'mirror.key' to complete your campaign."
            ),
            target_ip="192.168.77.40",
            vulnerable_service="http",
            files={
                "index.html": "<!-- outdated build marker -->",
                "notes.txt": "Mirror sync at 03:00 UTC.",
                "mirror.key": "FLAG{GHOST_MIRROR_ROOT_ACCESS}",
            },
            required_file="mirror.key",
            reward_reputation=40,
            reward_exp=90,
        ),
    ]


class GameLogic:
    def __init__(self):
        self.missions = build_missions()
        self.progress = PlayerProgress()
        self.session = SessionState()
        self.last_scanned_ports: list[int] = []

    def current_mission(self) -> Mission:
        return self.missions[self.progress.mission_index]

    def reset_session(self):
        self.session = SessionState()
        self.last_scanned_ports = []

    def add_log(self, text: str):
        self.progress.logs.append(text)
        if len(self.progress.logs) > 250:
            self.progress.logs = self.progress.logs[-250:]

    def level_up_if_needed(self):
        needed = self.progress.level * 100
        while self.progress.exp >= needed:
            self.progress.exp -= needed
            self.progress.level += 1
            self.progress.max_alerts += 1
            self.add_log(f"[SYS] Level up -> {self.progress.level}, max alerts +1")
            needed = self.progress.level * 100

    def register_failed_action(self, reason: str):
        self.progress.alerts += 1
        self.session.disconnected_reason = reason
        if self.progress.alerts >= self.progress.max_alerts:
            self.add_log("[ALERT] Counter-intel locked your operation.")

    def reduce_alert(self):
        if self.progress.alerts > 0:
            self.progress.alerts -= 1

    def simulate_scan(self, ip: str) -> tuple[bool, list[str]]:
        mission = self.current_mission()
        self.session.scanned_target = ip
        if ip != mission.target_ip:
            return False, [
                f"Scanning {ip}...",
                "No useful ports found. Host appears hardened or irrelevant.",
            ]

        self.last_scanned_ports = [22, 80, 443, 3306, 21]
        random.shuffle(self.last_scanned_ports)
        shown = self.last_scanned_ports[:3]
        lines = [f"Scanning {ip}..."]
        for p in shown:
            lines.append(f"Port {p}/tcp open")
        lines.append("Fingerprint complete.")
        return True, lines

    def simulate_connect(self, ip: str) -> tuple[bool, str]:
        mission = self.current_mission()
        if ip != mission.target_ip:
            self.register_failed_action("Wrong host connection attempt.")
            return False, "Connection refused: host unknown for this mission."
        if self.session.scanned_target != ip:
            return False, "Hint: scan target first to reduce risk."

        self.session.connected_ip = ip
        return True, f"Connected to {ip}. Remote shell stub opened."

    def simulate_exploit(self, service: str) -> tuple[bool, str]:
        mission = self.current_mission()
        if not self.session.connected_ip:
            return False, "Not connected. Use connect [ip] first."
        if service != mission.vulnerable_service:
            self.register_failed_action("Invalid exploit vector.")
            return False, f"Exploit failed on service '{service}'. Intrusion alert raised."

        chance = min(0.85, 0.45 + self.progress.level * 0.08)
        if random.random() <= chance:
            self.session.exploit_success = True
            self.reduce_alert()
            return True, f"Exploit succeeded on {service}. Privilege elevated."

        self.register_failed_action("Exploit attempt traced.")
        return False, "Exploit crashed. Target triggered anomaly sensors."

    def mission_complete(self, required_file: str) -> tuple[bool, str]:
        mission = self.current_mission()
        if required_file != mission.required_file:
            return False, "That file is not the mission objective."
        self.progress.reputation += mission.reward_reputation
        self.progress.exp += mission.reward_exp
        self.level_up_if_needed()
        self.progress.mission_index += 1
        self.reset_session()
        return True, f"Mission complete: {mission.name}. Reputation +{mission.reward_reputation}."

    def is_game_over(self) -> bool:
        return self.progress.alerts >= self.progress.max_alerts

    def is_victory(self) -> bool:
        return self.progress.mission_index >= len(self.missions)

