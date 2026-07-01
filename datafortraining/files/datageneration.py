import json
import random
import uuid
import re

# Load JSON files path
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

# Load templates
INTENT_TEMPLATES = load_json("datafortraining/outputs/intent_template.json")
POLICY_TEMPLATES = load_json("datafortraining/outputs/policy_template.json")
INTENT_ABBREVIATIONS = load_json("datafortraining/abbreviations.json")
PLATFORM_CAPABILITIES = {
    "hios": {
        "full_name": "Hirschmann Industrial Operating System",
        "vendor": "Hirschmann",
        "os_family": "HIOS",
        "description": "Full-featured Hirschmann switch OS has wide range of features.",
        "capabilities": [
            "system_mgmt", "user_mgmt", "interface", "vlan", "mac_table",
            "port_security", "qos", "acl", "traffic_control", "lldp",
            "lldp_med", "spanning_tree", "lacp", "mrp", "hsr","prp",
            "routing", "dhcp", "dns", "sntp", "syslog", "snmp",
            "igmp_mld", "dhcp_snooping", "arp_inspection",
            "industrial_protocols", "monitoring", "poe",
            "firmware_file_mgmt", "usb_sd", "config_mgmt"
        ]
    },
    "hieos": {
        "full_name": "Hirschmann Embedded Operating System",
        "vendor": "Hirschmann",
        "os_family": "HIEOS",
        "description": "Lightweight Hirschmann OS used on Lemur devices.",
        "capabilities": [
            "system_mgmt", "user_mgmt", "interface", "vlan", "mac_table",
            "port_security", "qos", "lldp", "lldp_med", "spanning_tree",
            "lacp", "mrp", "routing", "dhcp", "dns", "syslog", "snmp",
            "monitoring", "poe", "firmware_file_mgmt", "config_mgmt"
        ]
    },
    "classic": {
        "full_name": "Hirschmann Classic Operating System",
        "vendor": "Hirschmann",
        "os_family": "Classic",
        "description": "Legacy Hirschmann OS used on classic switches.",
        "capabilities": [
            "system_mgmt", "user_mgmt", "interface", "vlan",
            "lldp", "spanning_tree", "mrp", "routing", "dhcp",
            "dns", "syslog", "snmp", "firmware_file_mgmt","monitoring"
        ]
    },
    "raspberrypi": {
        "full_name": "Raspberry Pi Linux",
        "vendor": "Raspberry Pi Foundation",
        "os_family": "Linux",
        "description": "Generic Linux device used for testing.",
        "capabilities": [
            "system_mgmt", "user_mgmt",
            "vlan",
            "lldp",
            "snmp",
            "monitoring"
        ]
    },
    "edge": {
        "full_name": "Edge Compute Device",
        "vendor": "Generic",
        "os_family": "Linux",
        "description": "Non-switch edge compute node.",
        "capabilities": [
            "system_mgmt", "monitoring"
        ]
    },
    "bat": {
        "full_name": "Battery Powered IoT Device",
        "vendor": "Generic",
        "os_family": "Embedded",
        "description": "Minimal device with only system management.",
        "capabilities": [
            "system_mgmt"
        ]
    }
}

PLATFORM_PARAMETER_CONSTRAINTS = {
    "hios": {
        "port_range": [f"1/{i}" for i in range(1, 25)],
        "mtu_range": (576, 9000),
        "qos_supported": True,
        "poe_supported": True,
        "lldp_med_supported": True
    },
    "hieos": {
        "port_range": [f"1/{i}" for i in range(1, 17)],
        "mtu_range": (576, 9000),
        "qos_supported": True,
        "poe_supported": True,
        "lldp_med_supported": True
    },
    "classic": {
        "port_range": [f"1/{i}" for i in range(1, 9)],
        "mtu_range": (576, 1500),
        "qos_supported": False,
        "poe_supported": False,
        "lldp_med_supported": False
    },
    "raspberrypi": {
        "port_range": ["eth0", "wlan0"],
        "mtu_range": (576, 1500),
        "qos_supported": False,
        "poe_supported": False,
        "lldp_med_supported": False
    },
    "edge": {
        "port_range": ["1/1"],
        "mtu_range": (576, 1500),
        "qos_supported": False,
        "poe_supported": False,
        "lldp_med_supported": False
    },
    "bat": {
        "port_range": ["1/1"],
        "mtu_range": (576, 1500),
        "qos_supported": False,
        "poe_supported": False,
        "lldp_med_supported": False
    }
}
def load_devices(path="datafortraining/devices_list.json"):
    with open(path, "r") as f:
        data = json.load(f)

    devices = {}
    for platform, devs in data.items():
        for dev_name, info in devs.items():

            if isinstance(info, str):
                info = {"ip": info, "ports": ["1/1"]}

            raw_ports = info.get("ports", [])
            if isinstance(raw_ports, str):
                raw_ports = [raw_ports]

            ports = [p for p in raw_ports if isinstance(p, str)]
            if not ports:
                ports = ["1/1"]

            devices[dev_name] = {
                "platform": platform,
                "ip": info.get("ip", "0.0.0.0"),
                "ports": ports
            }

    return devices
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
NOISE_PREFIX = [
    "just to be clear,",
    "by the way,",
    "as far as I know,",
    "for this setup,",
    "if I understand correctly,",
    "for your information,"
]

NOISE_MID = ["basically", "sort of", "kind of", "technically", "somehow"]
NOISE_TRAIL = ["if possible", "when you get a chance", "as soon as you can", "whenever that works"]
NOISE_REDUNDANT = ["go ahead and", "please make sure to", "you can just", "go on and"]
NOISE_CONTEXT = ["for the maintenance window,", "as per earlier discussion,", "for the new deployment,"]

def inject_noise(sentence):
    r = random.random()
    if r < 0.10:
        return f"{random.choice(NOISE_PREFIX)} {sentence}"
    if r < 0.15:
        parts = sentence.split(" ", 1)
        if len(parts) > 1:
            return f"{parts[0]} {random.choice(NOISE_MID)} {parts[1]}"
        return sentence
    if r < 0.25:
        return f"{sentence}, {random.choice(NOISE_TRAIL)}"
    if r < 0.15:
        return f"{random.choice(NOISE_REDUNDANT)} {sentence}"
    if r < 0.15:
        return f"{random.choice(NOISE_CONTEXT)} {sentence}"
    if r < 0.15:
        return sentence.replace(" ", "  ")
    return sentence
def generate_value(param):
    if param == "vlan_id":
        return random.randint(1, 4094)
    if param == "vlan_name":
        return random.choice(["office", "iot", "guest", "camera", "prod", "dev", "lab"])
    if param == "tagging_mode":
        return random.choice(["tagged", "untagged"])

    if param in ["ip_address", "netmask", "gateway", "dns_server", "syslog_server", "sntp_server", "server_ip"]:
        return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    if param == "destination":
        return random.choice(["usb", "tftp://10.0.0.1", "/flash/configs"])
    if param == "source":
        return random.choice(["default", "manual", "static"])

    if param == "hostname":
        return f"sw-{random.randint(1, 999)}"
    if param == "timezone":
        return random.choice(["UTC", "CET", "EST", "PST", "IST", "JST", "CEST"])
    if param == "service_name":
        return random.choice(["ssh", "telnet", "http", "https", "snmp"])

    if param == "username":
        return f"user{random.randint(1, 999)}"
    if param == "role":
        return random.choice(["admin", "operator", "guest", "read-only"])

    if param == "speed":
        return random.choice(["10", "100", "1000", "2500", "10000"])
    if param == "operating_mode":
        return random.choice(["full", "half", "auto"])
    if param == "mtu":
        return random.randint(576, 9000)
    if param == "description":
        return random.choice(["uplink", "camera", "sensor", "server", "client"])

    if param == "macaddress":
        return "02:00:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(4))
    if param == "aging_time":
        return random.randint(60, 100000)
    if param == "limit":
        return random.randint(1, 64)
    if param == "violation_action":
        return random.choice(["shutdown", "restrict", "protect"])

    if param == "qnumber":
        return random.randint(0, 7)
    if param == "min_bandwidth":
        return random.randint(1, 100000)
    if param == "dscp":
        return random.randint(0, 63)
    if param == "rate":
        return random.randint(1, 1000000)

    if param == "lag_id":
        return random.randint(1, 64)
    if param == "ring_id":
        return random.randint(1, 64)
    
    if param == "priority":
        return random.choice([0, 4096, 8192, 16384, 32768, 61440])

    if param == "pool_name":
        return random.choice(["office_pool", "iot_pool", "guest_pool"])

    if param == "community":
        return random.choice(["public", "private", "monitor"])

    if param == "image_name":
        return random.choice(["imageA", "imageB", "hios-10.3", "hios-9.4"])
    if param == "image_slot":
        return random.choice(["primary", "secondary"])
    if param == "filename":
        return random.choice(["config.cfg", "backup.cfg", "startup.cfg"])

    if param == "policy_name":
        return random.choice(["voice", "video", "data"])
    if param == "tlv_type":
        return random.choice([
            "port-description", "system-name", "system-description",
            "system-capabilities", "management-address"
        ])

    if param == "power":
        return random.randint(5, 30)

    if param == "source_port":
        return f"1/{random.randint(1, 24)}"
    if param == "destination_port":
        return f"1/{random.randint(1, 24)}"

    if param == "null_scan_filter":
        return random.choice(["enable", "disable"])

    if param == "name":
        return random.choice(["rule10", "block_camera", "allow_iot", "deny_guest", "acl_001"])

    return f"{param}_{random.randint(1,999)}"
def elaborate_intent(intent_type, sub_intent_type, parameters, platform):
    meta = PLATFORM_CAPABILITIES[platform]
    vendor = meta["vendor"]
    full_name = meta["full_name"]
    os_family = meta["os_family"]

    device = parameters.get("device", "device")
    port = parameters.get("port")
    vlan_id = parameters.get("vlan_id")
    vlan_name = parameters.get("vlan_name")
    tagging = parameters.get("tagging_mode")

    if intent_type == "vlan":
        if sub_intent_type == "create":
            return (
                f"Create VLAN {vlan_id} named '{vlan_name}' on device {device}. "
                f"This adds a new VLAN entry in the {full_name} ({os_family}) "
                f"operating system from {vendor}."
            )

        if sub_intent_type == "assign_port":
            mode = "tagged trunk" if tagging == "tagged" else "untagged access"
            return (
                f"Assign VLAN {vlan_id} to port {port} on device {device} "
                f"using {mode} mode. This configures the port according to "
                f"{full_name} ({os_family}) behavior from {vendor}."
            )

        if sub_intent_type == "tagging_mode":
            return (
                f"Set tagging mode '{tagging}' for VLAN {vlan_id} on port {port} "
                f"on device {device} running {full_name} ({os_family})."
            )

    if intent_type == "interface":
        if sub_intent_type == "speed":
            speed = parameters.get("speed")
            return (
                f"Set interface {port} speed to {speed} Mbps on device {device}. "
                f"Applies interface configuration on {full_name} ({os_family}) "
                f"from {vendor}."
            )

        if sub_intent_type == "mtu":
            mtu = parameters.get("mtu")
            return (
                f"Configure MTU {mtu} on interface {port} for device {device}. "
                f"Ensures packet size compatibility for {full_name} ({os_family})."
            )

    if intent_type == "system_mgmt":
        if sub_intent_type == "hostname":
            hostname = parameters.get("hostname")
            return (
                f"Set hostname '{hostname}' on device {device}. "
                f"This updates system identity on {full_name} ({os_family}) "
                f"from {vendor}."
            )

    return (
        f"Perform {intent_type}/{sub_intent_type} operation on device {device} "
        f"running {full_name} ({os_family}) from {vendor} with parameters {parameters}."
    )
class IntentGenerator:
    def __init__(self, devices):
        self.devices = devices

    def _pick_device_and_port(self):
        device = random.choice(list(self.devices.keys()))
        ports = self.devices[device]["ports"]
        return device, random.choice(ports)

    def generate_intent(self):
        device, port = self._pick_device_and_port()
        platform = self.devices[device]["platform"]

        # Pick intent type based on platform capabilities
        allowed_intents = PLATFORM_CAPABILITIES[platform]["capabilities"]
        intent_type = random.choice(allowed_intents)
        


        # Pick sub-intent
        sub_intent_type = random.choice(list(INTENT_TEMPLATES[intent_type].keys()))

        # Action classes for this intent/sub-intent
        actions_dict = INTENT_TEMPLATES[intent_type][sub_intent_type]

        #  FIX: filter empty action classes BEFORE choosing
        valid_action_classes = [a for a, t in actions_dict.items() if t and len(t) > 0]

        # If nothing valid → regenerate safely
        if not valid_action_classes:
            return self.generate_intent()

        # Pick action class
        action_class = random.choice(valid_action_classes)

        # Pick template
        template = random.choice(actions_dict[action_class])

        # Pick policy
        policy = POLICY_TEMPLATES[intent_type][sub_intent_type][action_class]

        # Pick verb
        action_word = random.choice(VERB_CLASSES[action_class])

        # Build parameters
        parameters = {
            "device": device,
            "platform": {
                "id": platform,
                "vendor": PLATFORM_CAPABILITIES[platform]["vendor"],
                "full_name": PLATFORM_CAPABILITIES[platform]["full_name"],
                "os_family": PLATFORM_CAPABILITIES[platform]["os_family"],
                "description": PLATFORM_CAPABILITIES[platform]["description"]
            }
        }
        if intent_type in ["hsr","mrp", "prp"]:
            parameters["protocol"] = intent_type
        # Port handling
        if "port" in policy["required_parameters"] or "{port}" in template:
            parameters["port"] = port

        # Required parameters
        for req in policy["required_parameters"]:
            if req not in parameters:
                parameters[req] = generate_value(req)

        # Optional parameters
        for opt in policy["optional_parameters"]:
            if "{" + opt + "}" in template:
                parameters[opt] = generate_value(opt)

        # Fill missing placeholders
        placeholders = re.findall(r"{(.*?)}", template)
        for ph in placeholders:
            if ph == "action":
                continue
            if ph == "protocol":
                parameters["protocol"] = intent_type
                continue
            if ph not in parameters:
                parameters[ph] = generate_value(ph)

        # Apply platform constraints
        rules = PLATFORM_PARAMETER_CONSTRAINTS[platform]

        if "port" in parameters:
            parameters["port"] = random.choice(rules["port_range"])

        if "mtu" in parameters:
            lo, hi = rules["mtu_range"]
            parameters["mtu"] = random.randint(lo, hi)

        if not rules["qos_supported"]:
            for p in ["qnumber", "min_bandwidth", "dscp", "rate"]:
                parameters.pop(p, None)

        if not rules["poe_supported"]:
            parameters.pop("power", None)

        if not rules["lldp_med_supported"]:
            for p in ["policy_name", "tlv_type"]:
                parameters.pop(p, None)

        # Remove parameters not allowed by policy
        required = policy["required_parameters"]
        optional = policy["optional_parameters"]
        allowed = set(required + optional + ["device", "platform", "port"])

        for p in list(parameters.keys()):
            if p not in allowed:
                parameters.pop(p)

        # Remove placeholders for missing optional fields
        for ph in ["tlv_type", "policy_name"]:
            if ph not in parameters:
                template = template.replace("{" + ph + "}", "")

        # Build natural language sentence
        natural_language_str = template.format(action=action_word, **parameters)

        # Abbreviation replacement
        abbr_list = INTENT_ABBREVIATIONS.get(intent_type, [])
        if abbr_list:
            chosen_variant = random.choice(abbr_list)
            natural_language_str = re.sub(
                intent_type.replace("_", " "),
                chosen_variant,
                natural_language_str,
                flags=re.IGNORECASE
            )

        # Add noise
        natural = inject_noise(natural_language_str)

        # Elaborate intent
        intent_elaboration = elaborate_intent(
            intent_type, sub_intent_type, parameters, platform
        )

        return {
            "uid": str(uuid.uuid4()),
            "natural_language": natural,
            "intent_type": intent_type,
            "intent_sub_type": sub_intent_type,
            "intent_action": action_class,
            "intent_name": f"{intent_type}_{sub_intent_type}_{action_class}",
            "parameters": parameters,
            "intent_elaboration": intent_elaboration,
            "policy": policy
        }

# MAIN EXECUTION BLOCK

if __name__ == "__main__":
    # Load devices
    devices = load_devices("datafortraining/outputs/devices_list.json")

    # Create generator
    generator = IntentGenerator(devices)

    # Number of samples
    N = 5000

    dataset = []
    for _ in range(N):
        intent = generator.generate_intent()
        if intent is not None:
            dataset.append(intent)

    # Save dataset
    with open("datafortraining/outputs/intent_dataset.json", "w") as f:
        json.dump(dataset, f, indent=4)

    print(f"Dataset saved with {len(dataset)} samples.")
