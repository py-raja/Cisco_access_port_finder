import netmiko
import re
from collections import Counter


def find_access_vlan(switch_ip, username, password):
    """Extracts access VLAN information from a Cisco device.

    Args:
        switch_ip: IP address of the Cisco device.
        username: Username for SSH authentication.
        password: Password for SSH authentication.

    Returns:
        List of VLAN details, each containing the VLAN ID and interface.
    """
    vlan_details = []
    device = None
    try:
        # Connect to the device
        device = netmiko.ConnectHandler(
            device_type='cisco_ios',
            ip=switch_ip,
            username=username,
            password=password
        )

        # Send command and process output
        output = device.send_command("show run | b interface")
        pattern = r"interface (\S+).*?switchport access vlan (\d+)"
        matches = re.findall(pattern, output, re.DOTALL)
        for interface, vlan_id in matches:         
            vlan_info = {
                'vlan_id': vlan_id,
                'interface': interface,
                'switch_ip': switch_ip
            }
            vlan_details.append(vlan_info)
             

    except netmiko.NetmikoTimeoutException as e:
        print(f"Timeout connecting to {switch_ip}: {str(e)}")
    except netmiko.NetmikoAuthenticationException as e:
        print(f"Authentication failure for {switch_ip}: {str(e)}")
    except Exception as e:
        print(f"An error occurred for {switch_ip}: {str(e)}")
    finally:
        # Disconnect from the device
        if device:
            try:
                device.disconnect()
            except Exception as e:
                print(f"Error disconnecting from {switch_ip}: {str(e)}")

    return vlan_details


def read_input_file(file_path):
    """Reads IP addresses from a text file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]


def read_credentials(file_path):
    """Reads username and password from a text file."""
    with open(file_path, 'r') as file:
        username = file.readline().strip()
        password = file.readline().strip()
    return username, password
    
def find_mac_address(filtered_vlans, username, password):
    mac_details = []
    for vlan in filtered_vlans:
        switch_ip = vlan['switch_ip']
        interface = vlan['interface']
        vlan_id = vlan['vlan_id']
        device = None
        try:
            # Connect to the device
            device = netmiko.ConnectHandler(
                device_type='cisco_ios',
                ip=switch_ip,
                username=username,
                password=password
            )

            # Send command and process output
            output = device.send_command(f"show mac address-table interface {interface}")
            mac_match = re.search(r"([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}", output)
            if mac_match:
                mac_info = {
                    'vlan_id': vlan_id,
                    'interface': interface,
                    'switch_ip': switch_ip,
                    'mac_address': mac_match.group(0),
                    'int_status' : 'up'
                }
                
            else:
                interface_status = device.send_command(f"sh int {interface} | i {interface}")
                int_status = re.search(r"line protocol is\s+(.+?)\s*(\(.*\))?$", interface_status)
                mac_info = {
                    'vlan_id': vlan_id,
                    'interface': interface,
                    'switch_ip': switch_ip,
                    'mac_address': None,
                    'int_status' : int_status.group(1)
                }               
            mac_details.append(mac_info)
        except netmiko.NetmikoTimeoutException as e:
            print(f"Timeout connecting to {switch_ip}: {str(e)}")
        except netmiko.NetmikoAuthenticationException as e:
            print(f"Authentication failure for {switch_ip}: {str(e)}")
        except Exception as e:
            print(f"An error occurred for {switch_ip}: {str(e)}")
        finally:
            if device:
                try:
                    device.disconnect()
                except Exception as e:
                    print(f"Error disconnecting from {switch_ip}: {str(e)}")
    return mac_details

# File paths for input and credentials
input_file = "input.txt"
credentials_file = "credentials.txt"

# Read switch IP addresses and credentials
switch_ips = read_input_file(input_file)
username, password = read_credentials(credentials_file)

# Collect VLAN data from all switches
vlan_list = []
for switch_ip in switch_ips:
    vlan_details = find_access_vlan(switch_ip, username, password)
    if vlan_details:
        vlan_list.extend(vlan_details)


# Main loop to filter VLANs
while True:
    vlan_id_to_filter = input("Filter by VLAN ID (or type 'exit' to quit, 'all' for all VLANs):").strip()
    if vlan_id_to_filter.lower() == 'exit':
        print("Exiting Advance Access vlan checker. Goodbye!")
        break

    # Filter the results based on the VLAN ID
    filtered_vlans = [vlan for vlan in vlan_list if vlan['vlan_id'] == vlan_id_to_filter]

    if filtered_vlans:
        # Display filtered VLANs
        print(f"Filtered results for VLAN ID {vlan_id_to_filter}:")
        value = input("You want't to extract mac address of this vlan Y/N: ").upper()
        if value == "Y":
            mac_details = find_mac_address(filtered_vlans, username, password)
            for vlan in mac_details:
                print(f"switch_ip: {vlan['switch_ip']}, Interface: {vlan['interface']}, VLAN ID: {vlan['vlan_id']} , mac_address: {vlan['mac_address']} , int_status: {vlan['int_status']}")
        else:
            for vlan in filtered_vlans:
                print(f"switch_ip: {vlan['switch_ip']}, Interface: {vlan['interface']}, VLAN ID: {vlan['vlan_id']} ")
    elif vlan_id_to_filter == 'all':
        value = input("You want't to extract mac address of this vlan Y/N: ").upper()
        if value == "Y":
            mac_details = find_mac_address(filtered_vlans, username, password)
            for vlan in mac_details:
                print(f"switch_ip: {vlan['switch_ip']}, Interface: {vlan['interface']}, VLAN ID: {vlan['vlan_id']} , mac_address: {vlan['mac_address']} , int_status: {vlan['int_status']}")
        else:
        for vlan in vlan_list:
            print(f"switch_ip: {vlan['switch_ip']}, Interface: {vlan['interface']}, VLAN ID: {vlan['vlan_id']}")
    else:
        # Count the occurrences of each VLAN ID if no match found
        print(f"No interfaces found with VLAN ID {vlan_id_to_filter}. Showing VLAN counts:")
        vlan_counts = Counter(vlan['vlan_id'] for vlan in vlan_list)
        for vlan_id, count in vlan_counts.items():
            print(f"VLAN {vlan_id}: {count}")
