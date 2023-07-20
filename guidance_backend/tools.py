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
        return """ Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et accumsan leo. Etiam non turpis ut ex fringilla blandit mollis at dolor. Quisque dignissim tortor et consequat porttitor. Nullam congue lacus sapien, nec lacinia sem consectetur eu. Phasellus efficitur quam blandit lorem elementum, sed placerat eros elementum. Nam dignissim egestas eros, sed pellentesque orci venenatis eget. Ut in turpis vehicula, facilisis nisi a, sagittis lectus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Phasellus dignissim ipsum libero, vitae congue orci feugiat a. In ullamcorper maximus mi, aliquam rutrum ligula luctus id. Praesent vel justo at ante molestie convallis. Integer faucibus leo lorem, at sodales lacus finibus et.
Morbi imperdiet felis lectus, a tempus orci cursus aliquet. Cras lobortis tellus nec tellus tincidunt, in euismod magna tristique. Curabitur ac sagittis tellus. Mauris porta eu neque finibus ultrices. Aliquam dapibus viverra nisl at tempor. Curabitur bibendum tempus nunc. Proin ultrices posuere dolor, ac semper dui scelerisque eu. Sed orci neque, pellentesque eget aliquam non, posuere ac nibh. Donec vitae varius mi, vel blandit mauris. Proin non dignissim lorem, ac posuere lacus. Praesent sem tellus, pharetra ut tellus a, euismod elementum magna. Pellentesque vitae dictum lectus, vel gravida est. Cras dapibus scelerisque bibendum. Nulla at dignissim augue. Donec porta at lectus quis euismod."""
    
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