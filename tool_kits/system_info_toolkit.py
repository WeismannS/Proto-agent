import psutil
import platform
import json
from datetime import datetime
from tool_kit_registry import ToolKitRegistery
from types_llm import FunctionDeclaration, Tool

from .base_toolkit import ToolKit


def get_system_info(working_directory: str) -> str:
    """Get basic system information"""
    try:
        info = {
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "system": platform.system(),
            "release": platform.release(),
            "timestamp": datetime.now().isoformat(),
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error: Failed to get system info: {e}"


def get_memory_usage(working_directory: str) -> str:
    """Get memory usage statistics"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        info = {
            "virtual_memory": {
                "total": f"{memory.total / (1024**3):.2f} GB",
                "available": f"{memory.available / (1024**3):.2f} GB",
                "used": f"{memory.used / (1024**3):.2f} GB",
                "percentage": f"{memory.percent}%",
            },
            "swap_memory": {
                "total": f"{swap.total / (1024**3):.2f} GB",
                "used": f"{swap.used / (1024**3):.2f} GB",
                "percentage": f"{swap.percent}%",
            },
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error: Failed to get memory info: {e}"


def get_disk_usage(working_directory: str, path: str = "/") -> str:
    """Get disk usage for specified path"""
    try:
        usage = psutil.disk_usage(path)
        partitions = psutil.disk_partitions()

        info = {
            "target_path": path,
            "usage": {
                "total": f"{usage.total / (1024**3):.2f} GB",
                "used": f"{usage.used / (1024**3):.2f} GB",
                "free": f"{usage.free / (1024**3):.2f} GB",
                "percentage": f"{(usage.used / usage.total) * 100:.1f}%",
            },
            "partitions": [
                {"device": p.device, "mountpoint": p.mountpoint, "fstype": p.fstype}
                for p in partitions
            ],
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error: Failed to get disk usage for {path}: {e}"


def get_cpu_info(working_directory: str) -> str:
    """Get CPU information and current usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()

        info = {
            "cpu_count": {
                "logical": psutil.cpu_count(),
                "physical": psutil.cpu_count(logical=False),
            },
            "current_usage": {
                "overall": f"{psutil.cpu_percent(interval=1):.1f}%",
                "per_core": [f"{usage:.1f}%" for usage in cpu_percent],
            },
            "frequency": {
                "current": f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A",
                "min": f"{cpu_freq.min:.0f} MHz" if cpu_freq else "N/A",
                "max": f"{cpu_freq.max:.0f} MHz" if cpu_freq else "N/A",
            },
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error: Failed to get CPU info: {e}"


def get_network_info(working_directory: str) -> str:
    """Get network interface information"""
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)

        info = {"interfaces": {}}

        for interface_name, addresses in interfaces.items():
            interface_info = {
                "addresses": [],
                "is_up": stats[interface_name].isup
                if interface_name in stats
                else False,
                "speed": f"{stats[interface_name].speed} Mbps"
                if interface_name in stats
                else "Unknown",
            }

            for addr in addresses:
                interface_info["addresses"].append(
                    {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast,
                    }
                )

            if interface_name in io_counters:
                io = io_counters[interface_name]
                interface_info["io_counters"] = {
                    "bytes_sent": f"{io.bytes_sent / (1024**2):.2f} MB",
                    "bytes_recv": f"{io.bytes_recv / (1024**2):.2f} MB",
                    "packets_sent": io.packets_sent,
                    "packets_recv": io.packets_recv,
                }

            info["interfaces"][interface_name] = interface_info

        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error: Failed to get network info: {e}"


def list_processes(working_directory: str, limit: int = 10) -> str:
    """List running processes with CPU and memory usage"""
    try:
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent", "status", "create_time"]
        ):
            try:
                processes.append(
                    {
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "cpu_percent": f"{proc.info['cpu_percent']:.1f}%",
                        "memory_percent": f"{proc.info['memory_percent']:.1f}%",
                        "status": proc.info["status"],
                        "created": datetime.fromtimestamp(
                            proc.info["create_time"]
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: float(x["cpu_percent"].rstrip("%")), reverse=True)
        limited_processes = processes[:limit]

        info = {
            "process_count": len(processes),
            "showing_top": limit,
            "processes": limited_processes,
        }

        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error: Failed to list processes: {e}"


schema_get_system_info = FunctionDeclaration(
    name="get_system_info",
    description="Get basic system information including platform, architecture, and Python version",
    parameters={"type": "object", "properties": {}},
)

schema_get_memory_usage = FunctionDeclaration(
    name="get_memory_usage",
    description="Get current memory usage statistics including virtual and swap memory",
    parameters={"type": "object", "properties": {}},
)

schema_get_disk_usage = FunctionDeclaration(
    name="get_disk_usage",
    description="Get disk usage information for a specified path",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to check disk usage for (default: /)",
            }
        },
    },
)

schema_get_cpu_info = FunctionDeclaration(
    name="get_cpu_info",
    description="Get CPU information including core count, frequency, and current usage",
    parameters={"type": "object", "properties": {}},
)

schema_get_network_info = FunctionDeclaration(
    name="get_network_info",
    description="Get network interface information including addresses and statistics",
    parameters={"type": "object", "properties": {}},
)

schema_list_processes = FunctionDeclaration(
    name="list_processes",
    description="List running processes with CPU and memory usage",
    parameters={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of processes to return (default: 10)",
            }
        },
    },
)


class SystemInfoToolkit(ToolKit):
    """System information toolkit providing system monitoring capabilities"""

    def __init__(
        self,
        enable_basic: bool = True,
        enable_memory: bool = True,
        enable_disk: bool = True,
        enable_cpu: bool = True,
        enable_network: bool = True,
        enable_processes: bool = True,
    ):
        """
        Initialize SystemInfoToolkit with capability flags.

        Args:
            enable_basic: Allow basic system information (platform, hostname, etc.)
            enable_memory: Allow memory usage monitoring
            enable_disk: Allow disk usage monitoring
            enable_cpu: Allow CPU information and monitoring
            enable_network: Allow network interface information
            enable_processes: Allow process listing and monitoring
        """
        super().__init__()
        self.enable_basic = enable_basic
        self.enable_memory = enable_memory
        self.enable_disk = enable_disk
        self.enable_cpu = enable_cpu
        self.enable_network = enable_network
        self.enable_processes = enable_processes
        self._register_functions()

    def _register_functions(self):
        """Register system information functions with the global registry based on enabled capabilities"""

        # Then register our system info functions
        if self.enable_basic:
            self.schemas.append(schema_get_system_info)
            ToolKitRegistery.register(
                "get_system_info", get_system_info, schema_get_system_info
            )

        if self.enable_memory:
            self.schemas.append(schema_get_memory_usage)
            ToolKitRegistery.register(
                "get_memory_usage", get_memory_usage, schema_get_memory_usage
            )

        if self.enable_disk:
            self.schemas.append(schema_get_disk_usage)
            ToolKitRegistery.register(
                "get_disk_usage", get_disk_usage, schema_get_disk_usage
            )

        if self.enable_cpu:
            self.schemas.append(schema_get_cpu_info)
            ToolKitRegistery.register("get_cpu_info", get_cpu_info, schema_get_cpu_info)

        if self.enable_network:
            self.schemas.append(schema_get_network_info)
            ToolKitRegistery.register(
                "get_network_info", get_network_info, schema_get_network_info
            )

        if self.enable_processes:
            self.schemas.append(schema_list_processes)
            ToolKitRegistery.register(
                "list_processes", list_processes, schema_list_processes
            )

    @property
    def tool(self) -> Tool:
        """Get the Tool instance for this toolkit"""
        return Tool(function_declarations=self.schemas)
