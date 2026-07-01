import json


OLD_INTENT_TEMPLATE_PATH = "datafortraining/outputs/oldintent_template.json"

with open(OLD_INTENT_TEMPLATE_PATH, "r") as f:
    OLD_TEMPLATES = json.load(f)


VERB_CLASSES = {
    "enable": ["enable", "activate", "allow", "configure", "set", "turn on", "apply", "assign"],
    "disable": ["disable", "deactivate", "remove", "delete", "block", "deny", "turn off", "clear"],
    "read": ["show", "get", "display", "fetch", "retrieve", "view", "list", "inspect", "query", "check"],
    "update": ["modify", "change", "update", "edit", "replace", "adjust"],
    "create": ["create", "add", "make", "define", "establish"],
    "delete": ["delete", "remove", "erase", "purge", "destroy"],
    "reset": ["reset", "restart", "reinitialize", "restore defaults", "clear state"],
    "save": ["save", "write", "commit", "store"],
    "load": ["load", "import", "restore", "read"],
    "export": ["export", "backup", "dump", "copy"],
    "copy": ["copy", "clone", "duplicate", "replicate"],
    "verify": ["verify", "validate", "confirm", "ensure"],
    "execute": ["run", "execute", "trigger", "perform"],
    "monitor": ["monitor", "watch", "observe", "poll"]
}

# ---------------------------------------------------------
# 3. Verb classes allowed per domain
# ---------------------------------------------------------
INTENT_VERB_MAP = {
    "system_mgmt": ["update", "read", "reset"],
    "user_mgmt": ["create", "delete", "update", "read"],
    "interface": ["update", "read", "reset"],
    "vlan": ["create", "delete", "update", "read"],
    "mac_table": ["create", "delete", "read"],
    "port_security": ["enable", "disable", "update", "read"],
    "qos": ["update", "read"],
    "acl": ["create", "delete", "update", "read"],
    "traffic_control": ["update", "read"],
    "lldp": ["enable", "disable", "update", "read"],
    "lldp_med": ["enable", "disable", "update", "read"],
    "spanning_tree": ["enable", "disable", "update", "read"],
    "lacp": ["create", "delete", "update", "read"],
    "mrp": ["enable", "disable", "update", "read"],
    "hsr": ["enable", "disable", "read"],
    "prp": ["enable", "disable", "read"],
    "routing": ["create", "delete", "update", "read"],
    "dhcp": ["enable", "disable", "update", "read"],
    "dns": ["create", "delete", "read"],
    "sntp": ["create", "delete", "read"],
    "syslog": ["create", "delete", "update", "read"],
    "snmp": ["enable", "disable", "update", "read"],
    "igmp_mld": ["enable", "disable", "update", "read"],
    "dhcp_snooping": ["enable", "disable", "update", "read"],
    "arp_inspection": ["enable", "disable", "update", "read"],
    "industrial_protocols": ["enable", "disable", "read"],
    "monitoring": ["monitor", "read"],
    "poe": ["enable", "disable", "update", "read"],
    "firmware_file_mgmt": ["load", "save", "export", "copy", "read"],
    "usb_sd": ["load", "save", "copy", "read"],
    "config_mgmt": ["save", "load", "export", "delete", "read"]
}

# ---------------------------------------------------------
# 4. Sub-intents per domain
# ---------------------------------------------------------
SUB_INTENTS = {
    "system_mgmt": ["hostname", "mgmt_ip", "gateway", "timezone"],
    "user_mgmt": ["user", "password", "role"],
    "interface": ["admin_state", "speed", "duplex", "mtu", "flow_control", "description"],
    "vlan": ["vlan"],
    "mac_table": ["static_entry", "delete_entry", "aging_time"],
    "port_security": ["service", "mac_limit", "violation_action"],
    "qos": ["queue", "dscp_map", "rate_limit", "shaping", "policing"],
    "acl": ["create_rule", "delete_rule", "apply_acl"],
    "traffic_control": ["storm_control", "null_scan_filter", "broadcast_limit"],
    "lldp": ["service", "tlv"],
    "lldp_med": ["service", "policy"],
    "spanning_tree": ["service", "priority"],
    "lacp": ["create_lag", "delete_lag", "add_port", "remove_port"],
    "mrp": ["service", "role"],
    "hsr": ["service", "supervision"],
    "prp": ["service", "supervision"],
    "routing": ["static_route", "default_route", "arp"],
    "dhcp": ["server", "relay", "snooping"],
    "dns": ["server"],
    "sntp": ["server"],
    "syslog": ["server", "forwarding"],
    "snmp": ["community", "trap", "service"],
    "igmp_mld": ["service", "querier"],
    "dhcp_snooping": ["service", "trust_port"],
    "arp_inspection": ["service", "trust_port"],
    "industrial_protocols": ["profinet", "modbus", "goose", "dcp"],
    "monitoring": ["port_mirror", "counters", "logs"],
    "poe": ["service", "power_limit"],
    "firmware_file_mgmt": ["dual_image", "service"],
    "usb_sd": ["service"],
    "config_mgmt": ["service"]
}


# ---------------------------------------------------------
# 5. Generate NEW intent template using OLD templates
# ---------------------------------------------------------
def generate_intent_template():
    new_template = {}

    for domain, subtypes in SUB_INTENTS.items():
        new_template[domain] = {}

        verb_classes = INTENT_VERB_MAP[domain]

        for subtype in subtypes:
            new_template[domain][subtype] = {}

            old_block = OLD_TEMPLATES[domain][subtype]

            for verb_class in verb_classes:
                new_template[domain][subtype][verb_class] = []

                # Map old allow → new verb class
                if "allow" in old_block:
                    new_template[domain][subtype][verb_class].extend(old_block["allow"])

                # Map old deny → new disable/delete
                if "deny" in old_block and verb_class in ["disable", "delete"]:
                    new_template[domain][subtype][verb_class].extend(old_block["deny"])

                # Map old get → new read
                if "get" in old_block and verb_class == "read":
                    new_template[domain][subtype][verb_class].extend(old_block["get"])

    return new_template


# 6. Save output

if __name__ == "__main__":
    intent_template = generate_intent_template()

    with open("datafortraining/outputs/intent_template.json", "w") as f:
        json.dump(intent_template, f, indent=4)

    print("Generated NEW intent_template.json using OLD templates + 14 verb classes!")
