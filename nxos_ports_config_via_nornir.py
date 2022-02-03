"""
ports configuration using nornir
"""
import logging
from nornir.core.filter import F
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir.plugins.inventory.simple import SimpleInventory
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

logger = logging.getLogger('nornir')

    
def nxos_main_task(task: Task, dry_run=True) -> Result:
    
    task.run(
        name="Logging outputs",
        task=log_something,
    )
    
    task.run(
        name="nxos command_using_netmiko",
        task=nxos_command_using_netmiko
    )

    return Result(
        host=task.host,
        result="task finished",
    )


def eos_main_task(task: Task, dry_run=True) -> Result:

    task.run(
        name="Logging outputs",
        task=log_something,
    )

    task.run(
        name="eos command_using_netmiko",
        task=eos_command_using_netmiko
    )

    return Result(
        host=task.host,
        result="task finished",
    )


def log_something(task: Task,) -> Result:
    """
    Nornir will log to 'nornir.log' by default.
    """    
    logger.info(f"{task.host.name} says hi!")
    logger.warning("Warning %r is running task %r", task.host.name, task.name)    
    return Result(
        host=task.host,
        result=f"Task {task.name} made some log updates"
    )


def nxos_command_using_netmiko(task: Task,) -> Result:
    """
    nxos command using Netmiko.
    """
    cmd_ret = task.run(
        task=netmiko_send_config,
        config_commands=[
            "default interface Ethernet1/13 - 14",
            "interface Ethernet1/13",
            "switchport mode trunk",
            "switchport trunk allowed vlan 100, 200",
            "description compute01.example.com data",
            "no shutdown",
            "interface Ethernet1/14",
            "switchport mode trunk",
            "switchport trunk allowed vlan 300, 400",
            "description compute02.example.com data",
            "no shutdown",
            "copy running-config startup-config"
        ]
        )
    
    return Result(
        host=task.host,
        result=cmd_ret
    )


def eos_command_using_netmiko(task: Task,) -> Result:
    """
    nxos command using Netmiko.
    """
    cmd_ret = task.run(
        task=netmiko_send_config,
        config_commands=[
            "default interface Ethernet5 - 6",
            "interface Ethernet5",
            "switchport mode trunk",
            "switchport trunk allowed vlan 100, 200",
            "description compute01.example.com data",
            "no shutdown",
            "interface Ethernet6",
            "switchport mode trunk",
            "switchport trunk allowed vlan 300, 400",
            "description compute02.example.com data",
            "no shutdown",
            "wr"
        ]
    )

    return Result(
        host=task.host,
        result=cmd_ret
    )


def get_nornir_cfg():
    """
    Returns the Nornir object.
    """
    InventoryPluginRegister.register("SimpleInventory", SimpleInventory)
    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 30,
            },
        },
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                    "host_file": "inventory/hosts.yaml",
                    "group_file": "inventory/groups.yaml",
                    "defaults_file": "inventory/defaults.yaml"
            },
        }
    )
    return nr
    

if __name__ == "__main__":

    nr = get_nornir_cfg()
    nxos_group = nr.filter(F(groups__contains="cisco_nxos"))

    nxos_change_result = nxos_group.run(
        name="Cisco Nexus ports configuration task",
        task=nxos_main_task,
        dry_run=False
    )

    eos_group = nr.filter(F(groups__contains="arista"))

    eos_change_result = eos_group.run(
        name="Arista Eos ports configuration task",
        task=eos_main_task,
        dry_run=False
    )

    print_result(nxos_change_result)
    print_result(eos_change_result)
