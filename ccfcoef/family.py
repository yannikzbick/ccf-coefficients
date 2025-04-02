from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class Family:
    name: str
    short: str


# TODO: Change name
CPU_FAMILIES = [
    Family(name='EPYC 1st Gen', short='amd-epyc-gen1'),
    Family(name='EPYC 2nd Gen', short='amd-epyc-gen2'),
    Family(name='EPYC 3rd Gen', short='amd-epyc-gen3'),
    Family(name='Neoverse N1', short='arm-neoverse-n1'),
    Family(name='Sandy Bridge', short='intel-sandybridge'),
    Family(name='Ivy Bridge', short='intel-ivybridge'),
    Family(name='Haswell', short='intel-haswell'),
    Family(name='Broadwell', short='intel-broadwell'),
    Family(name='Skylake (Server)', short='intel-skylake-server'),
    Family(name='Skylake (Client)', short='intel-skylake-client'),
    Family(name='Skylake', short='intel-skylake'),
    Family(name='Cascade Lake', short='intel-cascadelake'),
    Family(name='Coffee Lake', short='intel-coffeelake'),
    Family(name='Ice Lake', short='intel-icelake'),
    Family(name='Ryzen 1st Gen', short='amd-ryzen-gen1'),
    Family(name='Pre Ryzen', short='amd-pre-ryzen'),
    Family(name='Ryzen 2nd Gen', short='amd-ryzen-gen2'),
    Family(name='Ryzen 5th Gen', short='amd-ryzen-gen5'),
    Family(name='EPYC 4th Gen', short='amd-epyc-gen4'),
    Family(name='Embedded', short='amd-embedded'),
    Family(name='Ryzen 3rd Gen', short='amd-ryzen-gen3'),
    Family(name='Ryzen 4th Gen', short='amd-ryzen-gen4'),
    Family(name='Threadripper 1st Gen', short='amd-threadripper-gen1'),
    Family(name='Threadripper 2nd Gen', short='amd-threadripper-gen2'),
    Family(name='Threadripper 3rd Gen', short='amd-threadripper-gen3'),
    Family(name='Alder Lake', short='intel-alderlake'),
    Family(name='Kaby Lake', short='intel-kabylake'),
    Family(name='Comet Lake', short='intel-cometlake'),
    Family(name='Tiger Lake', short='intel-tigerlake'),
    Family(name='Raptor Lake', short='intel-raptorlake'),
    Family(name='Cannon Lake', short='intel-cannonlake'),
    Family(name='Whiskey Lake', short='intel-whiskeylake'),
    Family(name='Rocket Lake', short='intel-rocketlake'),
    Family(name='Saphire Rapids', short='intel-sapphirerapids'),
    Family(name='Cooper Lake', short='intel-cooperlake'),
    Family(name='Knightsmill', short='intel-knightsmill'),
    Family(name='Cortex', short='arm-cortex'),
    Family(name='Neoverse N1', short='arm-neoverse-n1'),
    Family(name='Neoverse v1', short='arm-neoverse-v1'),
    Family(name='Enhanced Neoverse v1', short='arm-enhanced-neoverse-v1'),
    Family(name='Neoverse v2', short='arm-neoverse-v2'),
    Family(name='Emerald Rapids', short='intel-emeraldrapids')
]


BOAVIZTA_CODENAME_TO_ARCHITECTURE_MAP = {
    'bristolridge': 'amd-ryzen-gen1',
    'carrizo': 'amd-pre-ryzen',
    'stoneyridge': 'amd-pre-ryzen',
    'ravenridge': 'amd-ryzen-gen1',
    'ravenridge2': 'amd-ryzen-gen2',
    'dali': 'amd-ryzen-gen2',
    'mendocino': 'amd-ryzen-gen5',
    'rome': 'amd-epyc-gen2',
    'turin': 'amd-epyc-gen5',
    'naples': 'amd-epyc-gen1',
    'milan': 'amd-epyc-gen3',
    'milanx': 'amd-epyc-gen3',
    'genoa': 'amd-epyc-gen4',
    'snowyowl': 'amd-embedded',
    'summitridge': 'amd-ryzen-gen1',
    'pinnacleridge': 'amd-ryzen-gen2',
    'matisse': 'amd-ryzen-gen3',
    # TODO: Check entries with numbers
    'matisse2': 'amd-ryzen-gen3',
    'picasso': 'amd-ryzen-gen2',
    'renoir': 'amd-ryzen-gen3',
    'cezanne': 'amd-ryzen-gen4',
    'lucienne': 'amd-ryzen-gen4',
    'barcelo': 'amd-ryzen-gen5',
    'rembrandt': 'amd-ryzen-gen5',
    'vermeer': 'amd-ryzen-gen5',
    'raphael': 'amd-ryzen-gen5',
    'phoenix': 'amd-ryzen-gen5',
    'dragonrange': 'amd-ryzen-gen5',
    'bandedkestrel': 'amd-embedded',
    'greathornedowl': 'amd-embedded',
    'whitehaven': 'amd-threadripper-gen1',
    'colfax': 'amd-threadripper-gen1',
    'castlepeak': 'amd-threadripper-gen2',
    'chagallpro': 'amd-threadripper-gen3',
    'gracemont': 'intel-alderlake',
    'skylake': 'intel-skylake',
    'coffeelake': 'intel-coffeelake',
    'ivybridge': 'intel-ivybridge',
    'haswell': 'intel-haswell',
    'kabylake': 'intel-kabylake',
    # TODO: one entry includes kaby lake g, fix
    'kabylakeg': 'intel-kabylake',
    'alderlake': 'intel-alderlake',
    'cometlake': 'intel-cometlake',
    'broadwell': 'intel-broadwell',
    'icelake': 'intel-icelake',
    'tigerlake': 'intel-tigerlake',
    'raptorlake': 'intel-raptorlake',
    'cannonlake': 'intel-cannonlake',
    'whiskeylake': 'intel-whiskeylake',
    'rocketlake': 'intel-rocketlake',
    'cascadelake': 'intel-cascadelake',
    'sapphirerapids': 'intel-sapphirerapids',
    'sapphirerapidshbm': 'intel-sapphirerapids',
    'emeraldrapids': 'intel-emeraldrapids',
    'sandybridge': 'intel-sandybridge',
    'cooperlake': 'intel-cooperlake',
    'knightsmill': 'intel-knightsmill',
    'graviton': 'arm-cortex',
    'graviton2': 'arm-neoverse-n1',
    'graviton3': 'arm-neoverse-v1',
    'graviton3e': 'arm-enhanced-neoverse-v1',
    'graviton4': 'arm-neoverse-v2',
}





#