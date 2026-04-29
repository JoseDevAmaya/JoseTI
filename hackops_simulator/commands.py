from game_logic import GameLogic


class CommandProcessor:
    def __init__(self, logic: GameLogic):
        self.logic = logic

    def process(self, raw_command: str) -> tuple[list[str], bool]:
        """Returns output lines and whether play_success_sound should be true."""
        line = raw_command.strip()
        if not line:
            return [], False

        self.logic.progress.command_count += 1
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "help":
            return self._help_lines(), True
        if cmd == "clear":
            return ["__CLEAR__"], False
        if cmd == "scan":
            return self._scan(args)
        if cmd == "connect":
            return self._connect(args)
        if cmd == "exploit":
            return self._exploit(args)
        if cmd == "ls":
            return self._ls()
        if cmd == "cat":
            return self._cat(args)
        return [f"Unknown command: {cmd}. Type 'help'."], False

    def _help_lines(self) -> tuple[list[str], bool]:
        return (
            [
                "Available commands:",
                "  help               -> show command list",
                "  scan [ip]          -> simulate target scan",
                "  connect [ip]       -> connect to target",
                "  exploit [service]  -> run exploit routine",
                "  ls                 -> list remote files",
                "  cat [file]         -> read file content",
                "  clear              -> clear terminal",
            ],
            True,
        )

    def _scan(self, args) -> tuple[list[str], bool]:
        if len(args) != 1:
            return ["Usage: scan [ip]"], False
        ok, lines = self.logic.simulate_scan(args[0])
        self.logic.add_log(f"[CMD] scan {args[0]} -> {'ok' if ok else 'fail'}")
        return lines, ok

    def _connect(self, args) -> tuple[list[str], bool]:
        if len(args) != 1:
            return ["Usage: connect [ip]"], False
        ok, msg = self.logic.simulate_connect(args[0])
        self.logic.add_log(f"[CMD] connect {args[0]} -> {'ok' if ok else 'fail'}")
        return [msg], ok

    def _exploit(self, args) -> tuple[list[str], bool]:
        if len(args) != 1:
            return ["Usage: exploit [service]"], False
        ok, msg = self.logic.simulate_exploit(args[0].lower())
        self.logic.add_log(f"[CMD] exploit {args[0].lower()} -> {'ok' if ok else 'fail'}")
        return [msg], ok

    def _ls(self) -> tuple[list[str], bool]:
        mission = self.logic.current_mission()
        if not self.logic.session.connected_ip:
            return ["Not connected to a host."], False
        if not self.logic.session.exploit_success:
            return ["Permission denied. Run exploit first."], False
        files = sorted(mission.files.keys())
        return [f"[{idx}] {name}" for idx, name in enumerate(files, 1)], True

    def _cat(self, args) -> tuple[list[str], bool]:
        if len(args) != 1:
            return ["Usage: cat [file]"], False
        mission = self.logic.current_mission()
        if not self.logic.session.connected_ip or not self.logic.session.exploit_success:
            return ["Access denied. Need active exploited connection."], False
        file_name = args[0]
        if file_name not in mission.files:
            return [f"File not found: {file_name}"], False

        text = mission.files[file_name]
        completed, msg = self.logic.mission_complete(file_name)
        if completed:
            self.logic.add_log(f"[MISSION] {mission.name} complete")
            return [f"{file_name}:", text, msg, "Proceed to next mission..."], True
        return [f"{file_name}:", text, msg], True

