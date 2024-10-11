import re

# Define categories of objects and actions
light_sources = ["lamp", "bulb", "neon", "sconce", "brazier"]
barriers = ["gate", "curtains", "garage-door", "blinds", "window", "shutter", 
            "trapdoor", "portcullis", "drawbridge", "blast-door", "airlock"]
thermal_devices = ["oven", "thermostat", "electric-blanket", "incinerator", "reactor-core"]
appliances = ["coffee-maker", "oven", "air-conditioner", "centrifuge", "synchrotron", "laser-cannon"]
states = ["on", "off"]  # States for devices (on/off)
barrier_actions = ["lock", "unlock", "open", "close"]  # Actions for barriers
comparators = ["less-than", "greater-than", "equal-to"]  # Comparison operators for conditions

command_pattern = ["set", "turn", "lock", "unlock", "open", "close"]  # Keywords for commands


# Helper function for parsing and validating time conditions
def parse_time_condition(time_str):
    match = re.match(r"(\d{1,2}):(\d{2})\s?(am|pm)", time_str)  # Match time format (e.g., "12:30 pm")
    if match:
        hour, minute, period = match.groups()
        hour = int(hour)
        minute = int(minute)
        
        # Check if the hour and minute are valid
        if hour < 1 or hour > 12 or minute < 0 or minute > 59:
            return None  # Invalid time
        
        # Convert time to 24-hour format
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        return hour, minute
    return None  # Time format does not match


# Function to check the validity of conditions (e.g., temperature or time)
def check_conditions(when_condition=None, until_condition=None):

    if when_condition and until_condition:
        # Match temperature conditions (e.g., "current-temperature less-than 300K")
        temp_match_when = re.match(r"current-temperature (less-than|greater-than|equal-to) (\d+)\s*[kK]", when_condition)
        time_match_when = parse_time_condition(when_condition)
        temp_match_until = re.match(r"current-temperature (less-than|greater-than|equal-to) (\d+)\s*[kK]", until_condition)
        time_match_until = parse_time_condition(until_condition)

        # If valid temperature or time conditions are present, return False
        if (temp_match_when and temp_match_until) or (temp_match_when and time_match_until) or (time_match_when and temp_match_until) or (time_match_when and time_match_until):
            return False
        else:
            return "Invalid 'when or until' condition."

    if when_condition and not until_condition:
        return "Please enter until condition"  # Return error if only 'when' is provided

    # Check 'when' condition
    if when_condition:
        temp_match = re.match(r"current-temperature (less-than|greater-than|equal-to) (\d+)\s*[kK]", when_condition)
        if temp_match:
            return False
        else:
            time_match = parse_time_condition(when_condition)
            if time_match:
                return False
            else:
                return "Invalid 'when' condition."  # Return error if invalid

    # Check 'until' condition
    if until_condition:
        temp_match = re.match(r"current-temperature (less-than|greater-than|equal-to) (\d+)\s*[kK]", until_condition)
        if temp_match:
            return False
        else:
            time_match = parse_time_condition(until_condition)
            if time_match:
                return False
            else:
                return "Invalid 'until' condition."  # Return error if invalid
            
    return False  # Return False if no conditions provided


# Function to parse and execute commands
def parse_command(command):
    command = command.strip().lower()

    # Define regular expressions for different command patterns
    lighting_pattern = rf'.*?turn ({"|".join(light_sources)}) ({("|".join(states))})'
    thermal_pattern = rf'.*?set ({("|".join(thermal_devices))}) to (\d+)\s*[kK]'
    barrier_pattern = rf'.*?({"|".join(barrier_actions)}) ({"|".join(barriers)})'
    appliance_pattern = rf'.*?turn ({("|".join(appliances))}) ({("|".join(states))})'

    # Find 'when' and 'until' conditions in the command
    if 'until ' in command:
        until_start = command.index('until ') + len('until ')
        until_condition = command[until_start:].strip()
        command = command[:until_start - len('until ')].strip()  # Remove 'until' condition from command
    else:
        until_condition = None
    
    if 'when ' in command:
        when_start = command.index('when ') + len('when ')
        when_condition = command[when_start:].strip()
        command = command[:when_start - len('when ')].strip()  # Remove 'when' condition from command
    else:
        when_condition = None
    
    location = False  # Variable to store location keyword
    
    # Find the keyword for the action in the command
    for action in command_pattern:
        index = command.find(action)
        if index != -1:
            location = command[:index].strip()
    
    if location:
        # If no space in the location, proceed
        if ' ' not in location:
            # Match thermal device command (e.g., "set oven to 300K")
            if re.match(thermal_pattern, command):
                device, temperature = re.findall(thermal_pattern, command)[0]
                if not check_conditions(when_condition, until_condition):
                    return f"{device.capitalize()} set to {temperature} K" + (f" when {when_condition}" if when_condition else "") + (f" until {until_condition}" if until_condition else "") + "."
                elif check_conditions(when_condition, until_condition):
                    return f"{check_conditions(when_condition, until_condition)}"
            
            # Match lighting command (e.g., "turn lamp on")
            elif re.match(lighting_pattern, command):
                light_source, state = re.findall(lighting_pattern, command)[0]
                if not check_conditions(when_condition, until_condition):
                    return f"{light_source.capitalize()} turned {state}" + (f" when {when_condition}" if when_condition else "") + (f" until {until_condition}" if until_condition else "") + "."
                elif check_conditions(when_condition, until_condition):
                    return f"{check_conditions(when_condition, until_condition)}"
            
            # Match barrier command (e.g., "open gate")
            elif re.match(barrier_pattern, command):
                action, barrier = re.findall(barrier_pattern, command)[0]
                if not check_conditions(when_condition, until_condition):
                    return f"{barrier.capitalize()} {action}" + (f" when {when_condition}" if when_condition else "") + (f" until {until_condition}" if until_condition else "") + "."
                elif check_conditions(when_condition, until_condition):
                    return f"{check_conditions(when_condition, until_condition)}"
                
            # Match appliance command (e.g., "turn oven on")
            elif re.match(appliance_pattern, command):
                appliance, state = re.findall(appliance_pattern, command)[0]
                if not check_conditions(when_condition, until_condition):
                    return f"{appliance.capitalize()} turned {state}" + (f" when {when_condition}" if when_condition else "") + (f" until {until_condition}" if until_condition else "") + "."
                elif check_conditions(when_condition, until_condition):
                    return f"{check_conditions(when_condition, until_condition)}"
                
            else:
                return "Invalid command."  # Return error if command does not match any pattern
        else:
            return "Invalid location with space in it."  # Return error if location contains spaces
    else:
        return "Invalid command."


# REPL loop to continuously accept user commands
def repl():
    print("Enter your command (type 'exit' to quit):")
    while True:
        command = input("> ")
        if command.lower() == "exit":
            break
        response = parse_command(command)  # Parse and process the command
        print(response)


# Run the REPL loop when script is executed directly
if __name__ == "__main__":
    repl()
