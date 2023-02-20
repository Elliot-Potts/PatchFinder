"""
TODO
- Confirm reliability of in+out packets for usage checks
- Confirm reliability parsing stackable switches
"""

from netmiko import ConnectHandler, exceptions
from dotenv import load_dotenv
import os


def handle_connection(switch_ip):
    load_dotenv()
    # print(os.environ.get("S_USERNAME"), os.environ.get("S_PASSWORD"))
    return ConnectHandler(host=switch_ip, username=os.environ.get("S_USERNAME"), password=os.environ.get("S_PASSWORD"), device_type="cisco_ios")


def main():
    get_ip_address = input("Enter switch IP: ")

    try:
        switch_connect = handle_connection(get_ip_address)
    except exceptions.NetmikoAuthenticationException:
        print("[-] Invalid username or password.")
        return
    except exceptions.NetmikoTimeoutException:
        print("[-] Connection timeout.")
        return

    print("Connected to {}\n".format(get_ip_address))
    switch_uptime = switch_connect.send_command("sh version", use_textfsm=True)[0]['uptime']
    int_status = switch_connect.send_command("sh int status", use_textfsm=True)
    print("Switch uptime is:\t{}\n".format(switch_uptime))

    all_stats = []
    unconnected_switchports = {}

    for interface in int_status:
        get_int_stats = switch_connect.send_command('show int {}'.format(interface['port']), use_textfsm=True)[0]
        get_int_stats = (get_int_stats['input_packets'], get_int_stats['output_packets'])

        if interface['status'] == "notconnect":
            # print("\tInterface [ {sp} ] is notconnect.".format(sp=interface['port']))
            unconnected_switchports[interface['port']] = get_int_stats

        stats_total = int(get_int_stats[0]) + int(get_int_stats[1])
        all_stats.append(stats_total)

    print("Not-connect switchports\n" + "-"*23)
    print("{:<10} {:<10} {:<10} {:<10}".format("Port", "Input", "Output", "Difference"))

    for dc_switchport in unconnected_switchports:
        in_packets = unconnected_switchports[dc_switchport][0]
        out_packets = unconnected_switchports[dc_switchport][1]

        print("{:<10} {:<10} {:<10} {:<10}%".format(
            dc_switchport,
            in_packets,
            out_packets,
            str(round(((int(in_packets)+int(out_packets)) / int(max(all_stats))) * 100, 2)
        )))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Exiting via keyboard input.")

