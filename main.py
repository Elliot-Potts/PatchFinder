"""
TODO
- Add port descriptions, port VLAN, voice VLAN?
- Add switch hostname
- Add POE info, budget etc.

- Build connection modules / remove hardcoding... make this more cohesive
-- Better port/stat data structure
- Add username/password entry (remove environment var dependency)
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
    rich_console = Console(record=True)

    get_ip_address = Prompt.ask("\n[bold][?][/] Enter switch IP ")

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

    # print("Connected to {}\n".format(get_ip_address))
    rich_console.print("[green bold][+][/] Connected to {}\n".format(get_ip_address))
    switch_uptime = switch_connect.send_command("sh version", use_textfsm=True)[0]['uptime']
    int_status = switch_connect.send_command("sh int status", use_textfsm=True)
    
    all_stats = []
    unconnected_switchports = {}

    for interface in int_status:
        get_int_stats = switch_connect.send_command('show int {}'.format(interface['port']), use_textfsm=True)[0]
        get_int_stats = (get_int_stats['input_packets'], get_int_stats['output_packets'])

        if interface['status'] == "notconnect":
            unconnected_switchports[interface['port']] = get_int_stats

        stats_total = int(get_int_stats[0]) + int(get_int_stats[1])
        all_stats.append(stats_total)

    # print("Not-connect switchports")
    # print("{:-<50}\n{:<10} {:<10} {:<10} {:<10}".format("-","Port", "Input", "Output", "Difference"))

    interface_percentages = []

    rich_console.print("[bold]Nonconnect Switchports[/]")

    table = Table(show_header=True, header_style="bold dark_goldenrod")
    table.add_column("Port")
    table.add_column("Input Packets")
    table.add_column("Output Packets")
    table.add_column("Difference (%)")

    for dc_switchport in unconnected_switchports:
        in_packets = unconnected_switchports[dc_switchport][0]
        out_packets = unconnected_switchports[dc_switchport][1]
        make_percentage = round(((int(in_packets)+int(out_packets)) / int(max(all_stats))) * 100, 2)

        if make_percentage == 0:
            percentage_string = "[green]{}[/]".format(str(make_percentage))
        else:
            percentage_string = str(make_percentage)

        # print("{:<10} {:<10} {:<10} {:<10}%".format(
        #     dc_switchport,
        #     in_packets,
        #     out_packets,
        #     make_percentage
        # ))

        table.add_row(
            dc_switchport,
            in_packets,
            out_packets,
            percentage_string,
        )

        interface_percentages.append([make_percentage, dc_switchport])
    
    interface_percentages = sorted(interface_percentages, key=lambda x: x[0])
    
    rich_console.print(table)
    rich_console.print(Panel.fit("Switch uptime is: [bold]{}[/]".format(switch_uptime)))

    rich_console.print("\nInterface [bold dark_goldenrod] {int} [/] has [bold dark_goldenrod] {usage}% [/] the usage of the highest on the switch.\n".format(
        int=interface_percentages[0][1],
        usage=interface_percentages[0][0]
    ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Exiting via keyboard input.")

