"""
TODO
- Remove duplicate ValueError handling for management interfaces
- Test this program against Cisco 9200L switches
"""

from netmiko import ConnectHandler, exceptions
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
import sys
import os

rich_console = Console(highlight=False)
switches = {}


def auth_handler(ip_addresses):
    load_dotenv()
    rich_console.print("[grey19 italic]\nLeave empty to use environment variables")

    for address in ip_addresses:
        rich_console.print(f"[bold]{address}")
        get_username = Prompt.ask("[bold][>][/bold] Enter SSH username ")

        if get_username:
            get_password = Prompt.ask("[bold][>][/bold] Enter SSH password ", password=True)
            switches[address] = [get_username, get_password]
            rich_console.print(f"[bold green][+][/] Switch {address} added with username '{get_username}'")
        else:
            environment_username = os.environ.get("S_USERNAME")
            environment_password = os.environ.get("S_PASSWORD")
            switches[address] = [environment_username, environment_password]
            rich_console.print(f"[bold green][+][/] Switch {address} added with environment username '{environment_username}'")

        rich_console.print("\n")


def main(ip_address):
    test_power_2960 = """Module   Available     Used     Remaining
          (Watts)     (Watts)    (Watts)
------   ---------   --------   ---------
1           740.0      404.0       336.0
2           740.0       45.8       694.2
3             n/a        n/a         n/a
4             n/a        n/a         n/a
5           740.0      120.8       619.2
Interface Admin  Oper       Power   Device              Class Max
                            (Watts)
--------- ------ ---------- ------- ------------------- ----- ----
Gi1/0/1   auto   on         30.0    AIR-AP3802I-E-K9    4     30.0
Gi1/0/2   auto   on         30.0    AIR-AP3802I-E-K9    4     30.0
Gi1/0/3   auto   on         30.0    AIR-AP3802I-E-K9    4     30.0
"""  # Power inline parsing debug

    try:
        switch_connection = ConnectHandler(
            host=ip_address,
            username=switches[ip_address][0],
            password=switches[ip_address][1],
            device_type="cisco_ios"
        )
    except exceptions.NetmikoAuthenticationException:
        rich_console.print(f"[bold red][-][/] Invalid username or password ({ip_address}).")
        return
    except exceptions.NetmikoTimeoutException:
        rich_console.print(f"[bold red][-][/] Connection timeout ({ip_address}).")
        return

    switch_hostname = switch_connection.send_command("sh run | include hostname").split()[1]
    rich_console.print("[bold green][+][/bold green] Connected to {ip}  ([italic green]{hostn}[/])\n".format(ip=ip_address, hostn=switch_hostname))
    switch_uptime = switch_connection.send_command("sh version", use_textfsm=True)[0]['uptime']
    switch_power = switch_connection.send_command("sh power inline", use_textfsm=True).replace("-", "").split()
    # switch_power = test_power_2960.replace("-", "").split()  # Power inline parsing debug
    int_status = switch_connection.send_command("sh int status", use_textfsm=True)

    switch_power_parsed = []

    for item in range(7, switch_power.index("Interface")):
        if switch_power[item].isdigit():
            switch_power_parsed.append(switch_power[item:item+4])
        
    if not switch_power_parsed:
        if switch_power[0].startswith("Available") and switch_power[1].startswith("Used") and switch_power[2].startswith("Remaining"):
            get_available = switch_power[0].split(":")[1].replace("(w)", "")
            get_used = switch_power[1].split(":")[1].replace("(w)", "")
            get_remaining = switch_power[2].split(":")[1].replace("(w)", "")
            switch_power_parsed.append(["System Total", get_available, get_used, get_remaining])
        else:
            rich_console.print(f"[bold red][-][/] Unable to fetch PoE details for ({ip_address}).")

    if len(switch_power_parsed) > 0:
        poe_table = Table(show_header=True, header_style="bold white")
        poe_table.add_column("Switch No.")    
        poe_table.add_column("Available")
        poe_table.add_column("Used")
        poe_table.add_column("Free")

        for switch in switch_power_parsed:
            if switch[3] == "n/a" or switch[3] == "0.0":
                poe_free = f"[red]{switch[3]}[/]"
            else:
                poe_free = switch[3]

            poe_table.add_row(
                switch[0],
                switch[1],
                switch[2],
                poe_free
            )
    
    all_stats = []
    unconnected_switchports = {}

    for interface in int_status:
        get_int_stats = switch_connection.send_command('show int {}'.format(interface['port']), use_textfsm=True)[0]

        if interface['status'] == "notconnect":
            unconnected_switchports[interface['port']] = [get_int_stats["input_packets"], get_int_stats["output_packets"], interface['name'], interface['vlan'], get_int_stats['last_input']]
        try:
            stats_total = int(get_int_stats['input_packets']) + int(get_int_stats['output_packets'])
            all_stats.append(stats_total)
        except ValueError:
            # TODO Remove duplicate ValueError exception, need to test on a 2960x management port
            rich_console.print("[bold red][-][/bold red] Unable to calculate stats for interface [red]{int}[/red]. Likely a manegement interface...\n".format(int=interface['port']))

    interface_percentages = []

    rich_console.print("[bold]Nonconnect Switchports[/]")

    table = Table(show_header=True, header_style="bold white")
    table.add_column("Port")    
    table.add_column("Port Description")
    table.add_column("VLAN")
    table.add_column("Last Input")
    table.add_column("Input Packets")
    table.add_column("Output Packets")
    table.add_column("Percentage Use (%)")

    for dc_switchport in unconnected_switchports:
        # Dict ?
        in_packets = unconnected_switchports[dc_switchport][0]
        out_packets = unconnected_switchports[dc_switchport][1]
        port_desc = unconnected_switchports[dc_switchport][2]
        port_vlan = unconnected_switchports[dc_switchport][3]
        last_input = unconnected_switchports[dc_switchport][4]

        try:
            make_percentage = round(((int(in_packets)+int(out_packets)) / int(max(all_stats))) * 100, 2)
        except ValueError:
            rich_console.print("[bold red][-][/bold red] Unable to calculate stats for interface [red]{int}[/red]. Likely a manegement interface...\n".format(int=dc_switchport))

        if make_percentage == 0:
            percentage_string = "[green]{}[/]".format(str(make_percentage))
        else:
            percentage_string = str(make_percentage)

        table.add_row(
            f"[grey]{dc_switchport}[/]",
            f"[grey19]{port_desc}[/]",
            f"[grey19]{port_vlan}[/]",
            f"[grey19]{last_input}[/]",
            f"[grey19]{in_packets}[/]",
            f"[grey19]{out_packets}[/]",
            percentage_string
        )

        interface_percentages.append([make_percentage, dc_switchport])
    
    interface_percentages = sorted(interface_percentages, key=lambda x: x[0])
    
    rich_console.print(table)

    if len(switch_power_parsed) > 0:
        rich_console.print("[bold]PoE Details[/]")
        rich_console.print(poe_table)

    rich_console.print(Panel.fit("Switch uptime is: [bold]{}[/]".format(switch_uptime)))

    rich_console.print("\nInterface [bold green] {int} [/] has [bold green] {usage}% [/] the usage of the highest on the switch.\n".format(
        int=interface_percentages[0][1],
        usage=interface_percentages[0][0]
    ))


if __name__ == "__main__":
    try:
        rich_console.print("[grey19 italic]You can enter multiple IPs seperated by a space")
        get_ip_address = Prompt.ask("[bold][>][/bold] Enter switch IP(s) ").split()

        if get_ip_address:
            auth_handler(get_ip_address)

            for address in switches:
                Prompt.ask(f"[grey19]Press [bold][ENTER][/] to connect to [bold]{address}[/]")                
                main(address)
        else:
            rich_console.print("[bold red][-][/] No input provided.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[!] Exiting via keyboard input.")

