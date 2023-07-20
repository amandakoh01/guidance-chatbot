# Define functions for tools
def getReadiness(unit):
    if unit.lower() == "3rd division":
        return {"section 1": "REDCON-1", "section 2": "REDCON-2"}
    else:
        return "Unknown unit"
    
def getOrbat(unit):
    if unit.lower() == "3rd division":
        return "1 tank"
    else:
        return "Unknown unit"
    
def getIncident(location):
    if location.lower() == "changi naval base":
        return "2 unauthorised men spotted"
    else:
        return "Unknown location"

# Tool names + descriptions
toolNames = ['Get Readiness', 'Get Orbat', 'Get Incident']
toolDescriptions = [
    "only if the user specifically asks for the readiness condition (REDCON) of a unit. The input to this tool should be the unit required in the following format: '1st division'.",
    "only if the user specifically asks for the order of battle (orbat) of a unit. The input to this tool should be the unit required in the following format: 'first division'.",
    "only if the user specifically asks for the last incident report at a location. The input to this tool should be the location required."
]

# Put tools in a dictionary mapping from the tool name to the function
toolDict = {
    'Get Readiness': getReadiness,
    'Get Orbat': getOrbat,
    'Get Incident': getIncident
}