"""
TODO
- Add POE info, budget etc.
-- No TextFSM support, need to test reliability of #show power on stack switches

- Build connection modules / remove hardcoding... make this more cohesive
- Add username/password entry (system for selecting env or manual input)
"""

from netmiko import ConnectHandler, exceptions
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
import os


def handle_connection(switch_ip):
    load_dotenv()
    return ConnectHandler(host=switch_ip, username=os.environ.get("S_USERNAME"), password=os.environ.get("S_PASSWORD"), device_type="cisco_ios")


def main():
    rich_console = Console(highlight=False)

    get_ip_address = Prompt.ask("\n[bold][>][/bold] Enter switch IP ")

    try:
        switch_connect = handle_connection(get_ip_address)
    except exceptions.NetmikoAuthenticationException:
        rich_console.print("[bold red][-][/] Invalid username or password.")
        return
    except exceptions.NetmikoTimeoutException:
        rich_console.print("[bold red][-][/] Connection timeout.")
        return
    except ValueError:
        rich_console.print("[bold red][-][/] No input provided.")
        return

    switch_hostname = switch_connect.send_command("sh run | include hostname").split()[1]
    rich_console.print("[bold green][+][/bold green] Connected to {ip}  ([italic green]{hostn}[/])\n".format(ip=get_ip_address, hostn=switch_hostname))
    switch_uptime = switch_connect.send_command("sh version", use_textfsm=True)[0]['uptime']
    switch_power = switch_connect.send_command("sh power", use_textfsm=True).split()
    int_status = switch_connect.send_command("sh int status", use_textfsm=True)
    
    all_stats = []
    unconnected_switchports = {}

    for interface in int_status:
        get_int_stats = switch_connect.send_command('show int {}'.format(interface['port']), use_textfsm=True)[0]

        if interface['status'] == "notconnect":
            unconnected_switchports[interface['port']] = [get_int_stats["input_packets"], get_int_stats["output_packets"], interface['name'], interface['vlan'], get_int_stats['last_input']]
        try:
            stats_total = int(get_int_stats['input_packets']) + int(get_int_stats['output_packets'])
            all_stats.append(stats_total)
        except ValueError:
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
            "[grey]{}[/]".format(dc_switchport),
            "[grey19]{}[/]".format(port_desc),
            "[grey19]{}[/]".format(port_vlan),
            "[grey19]{}[/]".format(last_input),
            "[grey19]{}[/]".format(in_packets),
            "[grey19]{}[/]".format(out_packets),
            percentage_string
        )

        interface_percentages.append([make_percentage, dc_switchport])
    
    interface_percentages = sorted(interface_percentages, key=lambda x: x[0])
    
    rich_console.print(table)
    rich_console.print(Panel.fit("Switch uptime is: [bold]{}[/]".format(switch_uptime)))

    # print(switch_power)  # Test reliability of this array on STACK switches, could break

    rich_console.print("\nInterface [bold green] {int} [/] has [bold green] {usage}% [/] the usage of the highest on the switch.\n".format(
        int=interface_percentages[0][1],
        usage=interface_percentages[0][0]
    ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Exiting via keyboard input.")

