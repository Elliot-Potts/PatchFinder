"""
TODO
- Add POE info, budget etc.
-- No TextFSM support, need to test reliability of #show power on stack switches
- Remove duplicate ValueError handling for management interfaces
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
    switch_power = switch_connection.send_command("sh power", use_textfsm=True).split()
    int_status = switch_connection.send_command("sh int status", use_textfsm=True)
    
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
    table.add_column("Difference (%)")

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
    rich_console.print(Panel.fit("Switch uptime is: [bold]{}[/]".format(switch_uptime)))

    # print(switch_power)  # TODO Test reliability of this array on STACK switches, could break, if not .split()[-1]

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

