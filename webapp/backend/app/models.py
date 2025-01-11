from typing import Optional, List
from pydantic import BaseModel

class SwitchConnection(BaseModel):
    ip: str
    username: str
    password: str

class DisconnectedPort(BaseModel):
    port: str
    description: str
    vlan: str
    last_input: str
    input_packets: str
    output_packets: str
    usage_percentage: float

class PoEStatus(BaseModel):
    switch_no: str
    available: str
    used: str
    free: str

class LowestUsage(BaseModel):
    interface: str
    usage_percentage: float

class SwitchResponse(BaseModel):
    hostname: str
    uptime: str
    disconnected_ports: List[DisconnectedPort]
    poe_status: Optional[List[PoEStatus]] = None
    lowest_usage_interface: Optional[LowestUsage] = None 