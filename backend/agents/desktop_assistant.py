from typing import List, Dict, Any, Tuple, Optional
from backend.models import AgentType, ToolExecutionResult
from backend.agents.base import BaseVoiceAgent

class DesktopAssistantAgent(BaseVoiceAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.DESKTOP_ASSISTANT,
            name="Desktop Assistant",
            default_system_prompt=(
                "You are an intelligent Desktop Assistant. "
                "You execute voice commands to control the operating system, launch applications, "
                "inspect system telemetry, and automate routine workflows. "
                "Respond like a swift, capable personal DevOps and desktop orchestrator."
            )
        )

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "launch_application",
                    "description": "Launches a desktop app (e.g., VS Code, Chrome, Terminal, Slack, Figma).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "Application name"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "inspect_system_telemetry",
                    "description": "Checks local host CPU load, memory usage, and running services.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric": {"type": "string", "enum": ["cpu", "memory", "disk", "all"]}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "automate_workspace_task",
                    "description": "Runs a safe automation script such as cleaning temp files or opening git status.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_type": {"type": "string", "enum": ["git_status", "clean_temp", "rebuild_assets", "notify"]}
                        },
                        "required": ["task_type"]
                    }
                }
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Any, Optional[str]]:
        if tool_name == "launch_application":
            app = arguments.get("app_name", "Terminal")
            return {
                "status": "launched",
                "app": app,
                "process_id": 49201
            }, f"Desktop Action: Launched application '{app}'"

        elif tool_name == "inspect_system_telemetry":
            return {
                "cpu_usage": "14.2%",
                "ram_usage": "8.4 GB / 32 GB (26%)",
                "thermal_status": "Nominal (42°C)",
                "disk_free": "148 GB available"
            }, "System Health: CPU at 14%, RAM at 26%, Thermals nominal"

        elif tool_name == "automate_workspace_task":
            task = arguments.get("task_type", "git_status")
            return {
                "status": "completed",
                "task": task,
                "exit_code": 0
            }, f"Automated Task: Executed '{task}' successfully"

        return {"error": "Unknown tool"}, None

    def _generate_fallback(self, user_message: str) -> Tuple[str, List[ToolExecutionResult], List[str]]:
        msg = user_message.lower()
        if "launch" in msg or "open" in msg or "app" in msg:
            target = "VS Code" if "code" in msg else ("Chrome" if "chrome" in msg or "browser" in msg else "Terminal")
            tool = ToolExecutionResult(
                tool_name="launch_application",
                arguments={"app_name": target},
                output={"status": "launched", "pid": 58210},
                latency_ms=9.8
            )
            return (
                f"Opening {target} on your main monitor now.",
                [tool],
                [f"Launched desktop app: {target}"]
            )
        elif "status" in msg or "cpu" in msg or "memory" in msg or "system" in msg:
            tool = ToolExecutionResult(
                tool_name="inspect_system_telemetry",
                arguments={"metric": "all"},
                output={"cpu": "12%", "ram": "28%", "status": "optimal"},
                latency_ms=6.4
            )
            return (
                "Your workstation is running smoothly: CPU is at 12%, memory pressure is low at 28%, and no thermal throttling detected.",
                [tool],
                ["Inspected system health: CPU 12%, RAM 28%"]
            )
        else:
            return (
                "Desktop Assistant online and standing by. Say 'launch VS Code', 'open Terminal', or 'check system stats' to trigger automation.",
                [],
                []
            )

