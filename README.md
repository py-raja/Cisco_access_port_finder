# Cisco_access_port_finder

This Python script is designed to extract and analyze VLAN and MAC address information from Cisco network devices using SSH. It provides an interactive interface to filter VLANs and optionally fetch MAC address details from specific VLANs.

## Features

- Connects to Cisco switches via SSH using `Netmiko`.
- Retrieves VLAN details (ID and interface) from the running configuration.
- Filters VLANs based on user input.
- Fetches MAC addresses associated with specific VLAN interfaces.
- Handles connection, authentication, and parsing errors gracefully.

## Prerequisites

- Python 3.7+
- Cisco network devices configured for SSH access.
- `Netmiko` library installed.

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required Python library:
   ```bash
   pip install netmiko
   ```

## Files

- `vlan_checker.py`: The main script.
- `input.txt`: Contains the list of switch IP addresses, one per line.
- `credentials.txt`: Stores the username and password for SSH, with the username on the first line and password on the second line.

## Usage

1. Populate `input.txt` with the IP addresses of the Cisco switches you want to analyze.

2. Create a `credentials.txt` file with the SSH username and password:
   ```
   username
   password
   ```

3. Run the script:
   ```bash
   python vlan_checker.py
   ```

4. Follow the interactive prompts:
   - Enter a VLAN ID to filter by, or type `all` to view all VLANs.
   - Choose whether to fetch MAC address details for filtered VLANs.
   - Type `exit` to quit the script.

## Example Interaction

```text
Filter by VLAN ID (or type 'exit' to quit, 'all' for all VLANs): 10
Filtered results for VLAN ID 10:
You want to extract mac address of this VLAN Y/N: Y
switch_ip: 192.168.1.1, Interface: GigabitEthernet0/1, VLAN ID: 10, mac_address: aabb.ccdd.eeff, int_status: up
```

## Error Handling

- Connection errors are logged with descriptive messages.
- Authentication failures prompt for rechecking credentials.
- VLANs with no associated MAC address are indicated with `mac_address: None` and interface status.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

