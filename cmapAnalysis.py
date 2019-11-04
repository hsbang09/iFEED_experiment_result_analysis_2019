
ABSTRACT_CONCEPTS = ["Orbit", "Instrument"]
INSTRUMENTS = ['OCE_SPEC','AERO_POL', 'AERO_LID', 'HYP_ERB', 'CPR_RAD', 'VEG_INSAR', 
                'VEG_LID', 'CHEM_UVSPEC', 'CHEM_SWIRSPEC', 'HYP_IMAG','HIRES_SOUND','SAR_ALTIM']
INSTRUMENT_TYPES = ['radar', 'lidar', 'imager']
MEASUREMENTS = ['radiationBudget', 'atmosphericChem', 'atmosphericProp', 'aerosol', 'cloud', 'oceanColor', 'seaSurfaceProp', 
                    'soilMoisture', 'glacierAndIce', 'vegetation', 'topography', 'landCover']
SPECTRAL_REGION = ['VNIR','UV','SWIR','MW','LWIR']
ILLUMINATION_CONDITION = ['active', 'passive']
INSTRUMENT_POWER = ['highPower', 'lowPower']
ORBITS = ['LEO-600-polar', 'SSO-600-AM', 'SSO-600-DD', 'SSO-800-DD', 'SSO-800-PM']
ALTITUDES = ['600km', '800km']
LTAN = ['AM', 'PM', 'dawn-dusk']
ORBIT_TYPES = ['sun-synchronousOrbit', 'polarOrbit']

GROUPS = [
    ABSTRACT_CONCEPTS, 
    INSTRUMENTS, 
    INSTRUMENT_TYPES, 
    MEASUREMENTS, 
    SPECTRAL_REGION, 
    ILLUMINATION_CONDITION, 
    INSTRUMENT_POWER,
    ORBITS, 
    ALTITUDES, 
    LTAN, 
    ORBIT_TYPES
]
GROUP_LABELS = [
    "abstractConcepts", 
    "instruments", 
    "instrumentTypes", 
    "measurements", 
    "spectralRegion", 
    "illuminationCondition", 
    "instrumentPower",
    "orbits", 
    "altitudes", 
    "LTAN", 
    "orbitTypes"
]

instrumentProperties = [INSTRUMENT_TYPES, MEASUREMENTS, SPECTRAL_REGION, ILLUMINATION_CONDITION, INSTRUMENT_POWER]
orbitProperties = [ALTITUDES, LTAN, ORBIT_TYPES]

def getNumEdges(cmapdata):
    return len(cmapdata["edges"])

def getNumNodes(cmapdata):
    return len(cmapdata["nodes"])

def numHighLevelConceptUsed(cmapdata):
    edges = cmapdata["edges"]
    lowLevelConcepts = INSTRUMENTS + ORBITS
    highLevelConcepts = set()
    for edge in edges:
        n1 = edge['fromLabel']
        n2 = edge['toLabel']
        if n1 in lowLevelConcepts or n1 in highLevelConcepts:
            pass
        else:
            highLevelConcepts.add(n1)

        if n2 in lowLevelConcepts or n2 in highLevelConcepts:
            pass
        else:
            highLevelConcepts.add(n1)
    return len(highLevelConcepts)

def getNumEdges2HighLevelFeatures(cmapdata):
    edges = cmapdata["edges"]

    lowLevelConcepts = INSTRUMENTS + ORBITS
    nHighLevelConcepts = 0
    for edge in edges:
        n1 = edge['fromLabel']
        n2 = edge['toLabel']
        if n1 in lowLevelConcepts and n2 in lowLevelConcepts:
            pass
        else:
            nHighLevelConcepts += 1
    return nHighLevelConcepts
        



