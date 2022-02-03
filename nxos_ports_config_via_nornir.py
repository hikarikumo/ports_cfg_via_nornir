"""
ports configuration using nornir
"""
import logging
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir.plugins.inventory.simple import SimpleInventory
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

logger = logging.getLogger('nornir')

    
def main_task(task: Task, dry_run=True) -> Result:
    
    task.run(
        name="Logging outputs",
        task=log_something,
    )
    
    task.run(
        name="command_using_netmiko",
        task=command_using_netmiko
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


def command_using_netmiko(task: Task,) -> Result:
    """
    command using Netmiko.
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
    result = nr.run(
        name="Task example and explanation function.",
        task=main_task,
        dry_run=False
    )
    print_result(result)