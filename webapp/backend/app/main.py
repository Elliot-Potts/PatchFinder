"""Main module for the FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from netmiko import exceptions
from .models import SwitchConnection, SwitchResponse
from .session_manager import SessionManager

app = FastAPI()
session_manager = SessionManager()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/connect")
async def connect_switch(connection: SwitchConnection):
    try:
        session = session_manager.create_session(
            connection.ip,
            connection.username,
            connection.password
        )

        # Gather switch information
        hostname = session.send_command("sh run | include hostname").split()[1]
        uptime = session.send_command("sh version", use_textfsm=True)[0]['uptime']
        int_status = session.send_command("sh int status", use_textfsm=True)
        poe_status = session.send_command("sh power inline")

        # Process disconnected ports
        disconnected_ports = []
        for interface in int_status:
            if interface['status'] == "notconnect":
                stats = session.send_command(f'show int {interface["port"]}', use_textfsm=True)[0]
                disconnected_ports.append({
                    "port": interface["port"],
                    "description": interface.get("name", ""),
                    "vlan": interface.get("vlan") or interface.get("vlan_id"),
                    "last_input": stats["last_input"],
                    "input_packets": stats["input_packets"],
                    "output_packets": stats["output_packets"]
                })

        return SwitchResponse(
            hostname=hostname,
            uptime=uptime,
            disconnected_ports=disconnected_ports,
            poe_status=process_poe_status(poe_status),
            lowest_usage_interface=find_lowest_usage(disconnected_ports)
        )

    except exceptions.NetmikoAuthenticationException:
        raise HTTPException(status_code=401, detail="Authentication failed")
    except exceptions.NetmikoTimeoutException:
        raise HTTPException(status_code=408, detail="Connection timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_poe_status(poe_output: str):
    """Process PoE status output and return structured data"""
    switch_power = poe_output.replace("-", "").split()
    switch_power_parsed = []

    try:
        for item in range(7, switch_power.index("Interface")):
            if switch_power[item].isdigit():
                switch_power_parsed.append(switch_power[item:item+4])

        if not switch_power_parsed:
            if (switch_power[0].startswith("Available") and
                switch_power[1].startswith("Used") and
                switch_power[2].startswith("Remaining")):

                get_available = switch_power[0].split(":")[1].replace("(w)", "")
                get_used = switch_power[1].split(":")[1].replace("(w)", "")
                get_remaining = switch_power[2].split(":")[1].replace("(w)", "")
                switch_power_parsed.append(["System Total", get_available, get_used, get_remaining])

        return [{
            "switch_no": switch[0],
            "available": switch[1],
            "used": switch[2],
            "free": switch[3]
        } for switch in switch_power_parsed]

    except (IndexError, ValueError):
        return None

def find_lowest_usage(ports: list):
    """Find interface with lowest usage percentage"""
    try:
        all_stats = []
        interface_stats = {}

        for port in ports:
            try:
                total_packets = int(port['input_packets']) + int(port['output_packets'])
                all_stats.append(total_packets)
                interface_stats[port['port']] = total_packets
            except ValueError:
                continue

        if not all_stats or not interface_stats:
            return None

        max_usage = max(all_stats)
        lowest_usage = float('inf')
        lowest_interface = None

        for interface, usage in interface_stats.items():
            percentage = round((usage / max_usage) * 100, 2)
            if percentage < lowest_usage:
                lowest_usage = percentage
                lowest_interface = interface

        return {
            "interface": lowest_interface,
            "usage_percentage": lowest_usage
        }
    except Exception:
        return None

@app.post("/api/disconnect")
async def disconnect_switch():
    try:
        session_manager.close_session()
        return {"status": "disconnected"}
    except Exception:
        # Log the error if needed
        raise HTTPException(status_code=500, detail="Failed to disconnect properly")
