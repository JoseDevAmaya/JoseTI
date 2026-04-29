from dataclasses import dataclass, field


@dataclass
class Mission:
    mission_id: int
    name: str
    briefing: str
    target_ip: str
    vulnerable_service: str
    files: dict[str, str]
    required_file: str
    reward_reputation: int
    reward_exp: int


@dataclass
class SessionState:
    connected_ip: str | None = None
    scanned_target: str | None = None
    exploit_success: bool = False
    disconnected_reason: str = ""


@dataclass
class PlayerProgress:
    mission_index: int = 0
    reputation: int = 0
    level: int = 1
    exp: int = 0
    max_alerts: int = 4
    alerts: int = 0
    command_count: int = 0
    logs: list[str] = field(default_factory=list)

