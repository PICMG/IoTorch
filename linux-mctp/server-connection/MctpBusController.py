"""
MctpBusController.py
Description:
   This file includes a class definition for an MCTP bus controller, established by
   the mctpd service.  At execution time, the service must be installed in the system, but not running

   NOTE: Because this class changes system resource configurations, it must be invoked
   with superuser status (sudo).

Author:
   Douglas Sandy

Date:
   2025-09-27

License:  MIT No Attribution (MIT-0)
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"""
import glob
import re
import socket
import struct
import subprocess
import time
import dbus
import xml.etree.ElementTree as ETree

import MctpSerialLink

class MctpBusController:
    """
    MctpBusController is a singleton class that manages the initialization and control of an MCTP (Management Component
    Transport Protocol) bus using serial interfaces. It is designed to interface with the `mctpd` system service and
    the D-Bus system bus to discover and manage MCTP endpoints.

    This controller is responsible for:
    - Parsing a configuration file to determine the dynamic EID (Endpoint ID) range.
    - Discovering and initializing serial devices that match user-specified patterns.
    - Starting and stopping the `mctpd` service to enable MCTP communication.
    - Connecting to the D-Bus system bus to introspect and retrieve endpoint properties.
    - Mapping EIDs to serial links for enhanced endpoint metadata.

    Note: This class modifies system-level resources and must be executed with superuser privileges (e.g., via `sudo`).
    The `mctpd` service must be installed but not running at the time of instantiation.

    Attributes:
        self._eid_range (list): The range of dynamic EIDs parsed from the configuration file.
        self._serial_links (list): List of MctpSerialLink objects representing active serial interfaces.
        self._dbus (dbus.SystemBus): Connection to the system D-Bus.
        self._service (str): D-Bus service name for MCTP.
        self._dbus_root (str): Root object path for MCTP introspection.
        MctpBusController._instance (MctpBusController): Singleton instance reference.

    Methods:
        __init__(config_file_path, *args):
            Initializes the controller, configures EIDs, discovers serial devices, and starts the MCTP service.
        close():
            Releases all resources, shuts down serial links, and stops the MCTP service.
        discover_endpoints():
            Returns a list of discovered MCTP endpoints with associated metadata.
        _configure_eid_range(config_file_path):
            Parses the configuration file to extract the dynamic EID range.
        _is_service_active():
            Checks if the `mctpd` service is currently active.
        _start_service():
            Starts the `mctpd` service using systemd.
        _stop_service():
            Stops the `mctpd` service using systemd.
        _introspect(path):
            Performs D-Bus introspection on a given object path to enumerate child nodes.
        _get_properties(path):
            Retrieves properties of an MCTP endpoint, including EID and network ID.
        _walk_tree(path):
            Recursively walks the D-Bus object tree to discover endpoints.
        _get_link_from_eid(eid):
            Maps an EID to its corresponding serial link object, if available.
    """
    _instance = None
    AF_MCTP = 45  # Linux kernel socket family for MCTP

    def __init__(self, config_file_path: str, *args: str):
        """
        Initialize the MctpBusController. This is a singleton class; attempts to create more than one
        will result in an exception.

        :param config_file_path: Path to the configuration file for the Bus Controller. This file will be used to
            configure the mctpd instance. For more information about the file format, view the sample mctpd.conf
            file in the https://github.com/CodeConstruct/mctp source repository.
        :param args: A variable list of arguments, each one specifying a path to serial devices that should be added
            to the control of this MCTP bus controller. Paths may include wild card characters.
        """
        self._eid_range = []
        self._serial_links = []

        assert MctpBusController._instance is None, "Invalid attempt to create a second MctpBusController object"
        assert len(args) > 0, "No serial device search patterns are specified"

        self._configure_eid_range(config_file_path)

        file_list = []
        for filespec in args:
            file_list = list(set(file_list + glob.glob(filespec)))
        assert len(file_list) > 0, "No serial devices match search pattern(s)"

        assert len(file_list) <= len(self._eid_range), "Not enough EIDs to support targeted interfaces"

        # create the serial devices
        for file_path in file_list:
            self._serial_links.append(MctpSerialLink.MctpSerialLink(file_path, self._eid_range))

        # Start mctpd using system bus
        if self._is_service_active():
            self._stop_service()
        self._start_service()

        # Connect to system bus
        self._dbus = dbus.SystemBus()
        self._service = 'au.com.codeconstruct.MCTP1'
        self._dbus_root = '/au/com/codeconstruct/mctp1'

        # Wait for bus enumeration to stabilize
        start_time = time.time()
        previous_count = -1
        timeout = 30
        while True:
            current_count = len(self.discover_endpoints())
            if current_count == previous_count:
                break
            if time.time() - start_time > timeout:
                self.close()
                raise AssertionError("Endpoint discovery did not stabilize within 30 seconds.")
            previous_count = current_count
            time.sleep(1)

        MctpBusController._instance = self

    def _configure_eid_range(self,config_file_path):
        """
        configure the eid_range from the contents of the config file
        :param config_file_path: the full path to the configuration file
        :return: None
        """
        try:
            with open(config_file_path, "r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith("dynamic_eid_range"):
                        # dynamic range line found, parse the line
                        pattern = r"\[\s*(\d+)\s*,\s*(\d+)\s*\]"
                        match = re.search(pattern, line)
                        if match:
                            # line parsed without error - assign value and return
                            num1, num2 = match.groups()
                            start = min(int(num1), int(num2))
                            end = max(int(num1), int(num2))
                            assert start > 0 and end > 0, "invalid values for dynamic_eid_range in "+config_file_path
                            self._eid_range = range(start,end+1)
                            return
                        assert False, "Error parsing dynamic_eid_range in "+config_file_path
                assert False, "dynamic_eid_range not found in "+config_file_path
        except FileNotFoundError:
            print(f"Error: File '{config_file_path}' not found.")
        except Exception as e:
            print(f"Error when reading {config_file_path}: {e}")

    @staticmethod
    def _is_service_active():
        """
        Check if a mctpd.service systemd service is active.

        :return: True if active, False otherwise
        """
        try:
            result = subprocess.run(
                ['sudo','systemctl', 'is-active', 'mctpd.service'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error checking mctpd.service status: {e}")
            assert False

    @staticmethod
    def _stop_service():
        """
        Check if a mctpd.service systemd service is active.

        :return: True if active, False otherwise
        """
        subprocess.run(
            ['sudo','systemctl', 'stop', 'mctpd.service'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @staticmethod
    def _start_service():
        """
        Check if a mctpd.service systemd service is active.

        :return: True if active, False otherwise
        """
        subprocess.run(
            ['sudo','systemctl', 'start', 'mctpd.service'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def close(self):
        """
        close and release all OS resources owned by this object.
        :return: None
        """
        # close and remove all serial links
        for link in self._serial_links:
            link.close()
        self._serial_links.clear()

        # shut down the mctp service
        self._stop_service()

        if MctpBusController._instance is not None:
            MctpBusController._instance = None

    def _introspect(self, path):
        """
        Perform D-Bus introspection on a given object path.

        :param path: D-Bus object path to introspect.
        :return: List of child node names under the specified path.
        """
        obj = self._dbus.get_object(self._service, path)
        iface = dbus.Interface(obj, 'org.freedesktop.DBus.Introspectable')
        xml_data = iface.Introspect()
        tree = ETree.fromstring(xml_data)
        return [node.attrib['name'] for node in tree.findall('node')]

    def _get_properties(self, path):
        """
        Retrieve properties of an MCTP endpoint.

        :param path: D-Bus object path of the endpoint.
        :return: Dictionary with 'eid', 'interface', and 'path' keys, or None if unavailable.
        """
        obj = self._dbus.get_object(self._service, path)
        props_iface = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
        try:
            eid = props_iface.Get('xyz.openbmc_project.MCTP.Endpoint','EID')
            network_id = props_iface.Get('xyz.openbmc_project.MCTP.Endpoint','NetworkId')
            result = {
                'eid': int(eid),
                'network_id': network_id,
                'path': path
            }
            serial_link = self._get_link_from_eid(eid)
            if serial_link is not None:
                result['link_name'] = serial_link.get_link_name()
                result['device_path'] = serial_link.get_device_path()
            return result
        except dbus.exceptions.DBusException:
            print("error getting props")
            return None

    def discover_endpoints(self):
        """
        Discover all MCTP endpoints in the D-Bus object tree.
        :return: List of endpoint property dictionaries.
        """
        return self._walk_tree(self._dbus_root)

    def _walk_tree(self, path):
        """
        Recursively walk the D-Bus object tree starting from a given path.

        :param path: Starting D-Bus object path.
        :return: List of endpoint property dictionaries discovered under the path.
        """
        results = []
        children = self._introspect(path)
        for child in children:
            child_path = f"{path}/{child}" if not path.endswith('/') else f"{path}{child}"
            if '/endpoints/' in child_path:
                props = self._get_properties(child_path)
                if props:
                    results.append(props)
            else:
                results.extend(self._walk_tree(child_path))
        return results

    def _get_link_from_eid(self,eid):
        """
        search the list of top-level serial ports to see if one has an EID that matches.
        if a match is found, return the object, otherwise None
        :param eid: the eid to search for
        :return: the corresponding MctpSerialObject, otherwise None
        """
        for link in self._serial_links:
            if link.get_eid() == eid:
                return link
        return None

    def send_raw_mctp_message(self, network_id: int, destination_eid: int, payload: bytes) -> bool:
        """
        Sends a raw MCTP message using AF_MCTP datagram socket.

        :param network_id: MCTP network ID (typically 1).
        :param destination_eid: Target endpoint ID.
        :param payload: Raw bytes to send.
        :return: True if successful, False otherwise.
        """
        # TODO: This needs debugging
        try:
            sock = socket.socket(self.AF_MCTP, socket.SOCK_DGRAM, 0)

            # Construct sockaddr_mctp (simplified)
            sockaddr = struct.pack("HHBBBBB",
                self.AF_MCTP,         # Address family
                network_id,             # Network ID
                0,                      # Addr type (0 = EID)
                0,                      # Reserved
                destination_eid,        # Destination EID
                1,                      # Tag owner
                1                       # Message type (e.g., 1 = PLDM)
            )

            sock.sendto(payload, sockaddr)
            sock.close()
            return True
        except Exception as e:
            print(f"Error sending raw MCTP message: {e}")
            return False

    def send_mctp_datagram(self, network_id: int, destination_eid: int, message_type: int, tag_owner: int, payload: bytes) -> bool:
        """
        Sends an MCTP datagram with specified message type and tag owner.

        :param network_id: MCTP network ID.
        :param destination_eid: Target endpoint ID.
        :param message_type: MCTP message type (e.g., 1 = PLDM).
        :param tag_owner: Tag owner bit (0 or 1).
        :param payload: Raw message payload.
        :return: True if successful, False otherwise.
        """
        # Todo: This needs debugging
        try:
            sock = socket.socket(self.AF_MCTP, socket.SOCK_DGRAM, 0)

            sockaddr = struct.pack("HHBBBBB",
                self.AF_MCTP,
                network_id,
                0,                      # Addr type
                0,                      # Reserved
                destination_eid,
                tag_owner,
                message_type
            )

            sock.sendto(payload, sockaddr)
            sock.close()
            return True
        except Exception as e:
            print(f"Error sending MCTP datagram: {e}")
            return False

if __name__ == '__main__':
    controller = MctpBusController("/etc/mctpd.conf","/dev/ttyUSB?")
    endpoints = controller.discover_endpoints()

    print("Discovered MCTP Endpoints:")
    for ep in endpoints:
        for key in ep.keys():
            print(f"  {key}: {ep[key]}")
        print()  # adds a blank line between endpoints
    controller.close()