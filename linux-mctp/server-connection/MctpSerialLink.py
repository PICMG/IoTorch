"""
MctpSerialLink.py
Description:
   This file includes a class definition for an MCTP serial link as established by
   the mctp usermode shell command.

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
import os
import signal
import subprocess
import time

class MctpSerialLink:
    """
    MctpSerialLink
        This class encapsulates the process of establishing and configuring a serial link that can be used
        with the MctpBusController class.  Much of the underlying implementation relies upon the mctp command line
        tool by Code Construct.

    Class Attributes (all protected):
        _assigned_links (static) - a list of MctpSerialLinks that have created
        _assigned_eids (static) - a list of EIDs that have been assigned
        _eid - the eid assigned to the object
        _link_pid - the process id associated with the "mctp link serial" command used to maintain this link
        _link_name - the name of the link (matches the one assigned by Linux)
        _device_path - the path to the Linux device associated with th object

    Class Methods:
        __init__ - constructor to initialize the object
        __del__ - destructor to tear down the object and release its OS resources
        get_eid - returns the eid of the object
        get_link_name - returns the link name of the object
        get_device_path - returns the device path for the serial port associated with the link
        close - close the link and deallocate any OS resources associated with it
    """
    # lists of link objects and eids that have been assigned
    _assigned_links = []
    _allocated_eids = []

    def __init__(self, device_path:str, allowed_eids: list[int]):
        """
        initialize the MctpSerialLink
        :param device_path: path to the serial device (e.g. /dev/ttyUSB0)
        :param allowed_eids: a list of all allowed eids that this device may be assigned to
        :return: None
        """
        self._eid = None
        self._link_pid = None
        self._link_name = None
        self._device_path = None

        # make sure there are still EIDs that can be assigned
        remaining_eids = list(set(allowed_eids)-set(MctpSerialLink._allocated_eids))
        assert len(remaining_eids)>0, "Unable to allocate EID for "+device_path+". All EIDs have been allocated."
        next_eid = remaining_eids[0]

        # validate the path
        assert os.path.exists(device_path), 'Device path not found for '+device_path
        self._device_path = device_path

        # get the initial set of interfaces
        initial_interfaces = self._get_interfaces()

        # Bind the serial device
        link_process = subprocess.Popen(["sudo", "mctp", "link", "serial", device_path],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._link_pid = link_process.pid

        # get the new interface associated with this link
        self._link_name = self._wait_for_new_interface(initial_interfaces)
        if self._link_name is None:
            assert False, "Timeout error waiting for newly bound network interface for "+device_path

        # configure the port address and bring it up
        if subprocess.run(["sudo", "mctp", "link", "set", self._link_name, "up"]).returncode != 0:
            assert False, "unable to bring up link associated with "+self._link_name

        if subprocess.run(["sudo", "mctp", "address", "add", str(next_eid), "dev", self._link_name]).returncode != 0:
            assert False, "unable to assign eid to link associated with " + device_path

        MctpSerialLink._assigned_links.append(self)
        self._eid = next_eid
        MctpSerialLink._allocated_eids.append(next_eid)

    def __del__(self):
        """
        clean up any running processes associated with this link.
        """
        self.close()

    @staticmethod
    def _get_interfaces():
        """
        get current network interfaces
        :return: a set of interfaces found
        """
        result = subprocess.run(['ip', '-o', 'link', 'show'], capture_output=True, text=True)

        # reset the terminal to fix issues with stdout
        os.system('tput sgr0')
        os.system('stty onlcr')
        os.system('stty sane')

        interfaces = set()
        for line in result.stdout.splitlines():
            # extract the name from the interface line
            name = line.split(':')[1].strip()
            # add the name to the set of names
            interfaces.add(name)
        return interfaces

    @staticmethod
    def _wait_for_new_interface(initial_interfaces: set, timeout=2):
        """
        wait up to a specified number of seconds for a new network interface to appear
        :param initial_interfaces: a set of interfaces that already exist
        :param timeout: the amount of time to wait
        :return: the name of the interface if a new one appears, otherwise None
        """
        # loop while not timed out
        start_time = time.time()
        while time.time() - start_time < timeout:
            # get the current interfaces
            current = MctpSerialLink._get_interfaces()
            # remove the ones that existed before
            new_interfaces = current - initial_interfaces
            # if there are new interfaces, return the name of the first one
            if new_interfaces:
                return new_interfaces.pop()
            time.sleep(0.1)  # Poll every 100ms
        return None

    def get_eid(self):
        """
        return the eid associated with this link
        :return: the eid assigned to this link
        """
        return self._eid

    def get_link_name(self):
        """
        return the link name associated with this link
        :return: the link name assigned to this link
        """
        return self._link_name

    def get_device_path(self):
        """
        return the device path for the serial port associated with this object
        :return: the device path
        """
        return self._device_path

    def close(self):
        """
        close the link and relinquish resources allocated to it.
        :return: None
        """
        if self._link_pid is not None:
            os.kill(self._link_pid, signal.SIGTERM)
        if self in MctpSerialLink._assigned_links:
            MctpSerialLink._assigned_links.remove(self)
        if self._eid in MctpSerialLink._allocated_eids:
            MctpSerialLink._allocated_eids.remove(self._eid)
        self._link_name = None
        self._eid = None
        self._link_pid = None
        self._device_path = None

# Example invocation
if __name__ == '__main__':
    serial_link = MctpSerialLink('/dev/ttyUSB0',list(range(8,254)))
    print("Device:    "+serial_link.get_device_path())
    print("Interface: "+serial_link.get_link_name())
    print("EID:       "+str(serial_link.get_eid()))