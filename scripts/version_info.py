"""
Contributors List
Format = [ Name, Blog-url, Twitter-handle, Github-url]
Leave blank if not available
"""

leapp_name = 'ALEAPP'
leapp_version = '2026.2.0'

# Minimum protobuf runtime required by the regenerated *_pb2 bindings and the
# security pin in requirements.txt. The PyPI 'blackboxprotobuf' package
# force-downgrades protobuf to 3.10.0 when installed into the same
# environment; ALEAPP uses the vendored scripts/blackboxprotobuf instead.
minimum_protobuf_version = '5.29.6'


def check_runtime_dependencies():
    """Warn loudly if the environment drifted from the pinned dependencies.

    Called at startup by both aleapp.py and aleappGUI.py. Returns a list of
    human-readable problem strings, empty when the environment is healthy.
    """
    problems = []

    def version_tuple(version):
        return tuple(int(part) for part in version.split('.')[:3] if part.isdigit())

    try:
        from google.protobuf import __version__ as protobuf_version
    except ImportError:
        problems.append("protobuf is not installed. Run: pip install -r requirements.txt")
    else:
        if version_tuple(protobuf_version) < version_tuple(minimum_protobuf_version):
            problems.append(
                f"protobuf {protobuf_version} is older than the required {minimum_protobuf_version}. "
                "Another package (commonly the PyPI 'blackboxprotobuf') likely downgraded it. "
                "Protobuf-based artifacts will fail and patched CVEs are reintroduced. "
                f"Fix with: pip install protobuf=={minimum_protobuf_version}")

    try:
        from PIL import Image  # noqa: F401  pylint: disable=unused-import
    except ImportError:
        problems.append("Pillow is not installed or broken. Run: pip install -r requirements.txt")

    for problem in problems:
        print(f"DEPENDENCY WARNING: {problem}")
    return problems

aleapp_contributors = [
    ['Alexis Brignoni', 'https://abrignoni.com', '@AlexisBrignoni', 'https://github.com/abrignoni'],
    ['Yogesh Khatri', 'https://swiftforensics.com', '@SwiftForensics', 'https://github.com/ydkhatri'],
    ['Alex Caithness', 'https://www.linkedin.com/in/alex-caithness-a7504151/', '@kviddy', 'https://github.com/cclgroupltd'],
    ['Kevin Pagano', 'https://stark4n6.com', '@KevinPagano3', 'https://github.com/stark4n6'],
    ['Josh Hickman', 'https://thebinaryhick.blog/', '@josh_hickman1', ''],
    ['Troy Schnack', 'https://troy4n6.blogspot.com/', '@TroySchnack', ''],
    ['B Krishna Sai Nihith', 'https://g4rud4.gitlab.io', '@_Nihith', 'https://github.com/bolisettynihith'],
    ['Geraldine Blay', 'https://gforce4n6.blogspot.com', '@i_am_the_gia', ''],
    ['Bo Amos', '', '@Bo_Knows_65', ''],
    ['Andrea Canepa', '', '', 'https://github.com/A-725-K'],
    ['Incidentalchewtoy', 'https://theincidentalchewtoy.wordpress.com/', '@4n6chewtoy', ''],
    ['LoicForensics', '', '', ''],
    ['Fabian Nunes', 'https://www.linkedin.com/in/fabian-nunes/', '', 'https://github.com/fabian-nunes'],
    ['Evangelos Dragonas', 'https://atropos4n6.com/', '@theAtropos4n6', 'https://github.com/theAtropos4n6'],
    ['James Habben', 'https://4n6ir.com/', '@JamesHabben', 'https://github.com/JamesHabben'],
    ['Matt Beers', 'https://www.linkedin.com/in/mattbeersii', '', 'https://github.com/dabeersboys'],
    ['Heather Charpentier', 'https://www.linkedin.com/in/heather-charpentier-bb28b031/', '', 'https://github.com/charpy4n6'],
    ['Panos Nakoutis', '', '@4n6equals10', ''],
    ['Johann Polewczyk', 'https://www.linkedin.com/in/johann-polewczyk-6a905425/', '@johannplw', 'https://github.com/Johann-PLW'],
    ['Bruno Fischer', 'https://german4n6.blogspot.com/', '', 'https://github.com/BrunoFischerGermany'],
    ['Marco Neumann', 'https://bebinary4n6.blogspot.com/', '@kalinko4n6', 'https://github.com/kalink0'],
    ['Marc Seguin', 'https://segumarc.com', '@segumarc', 'https://github.com/segumarc'],
    ['Anthony Reince', 'https://www.linkedin.com/in/anthony-reince-a60115239/', '', ''],
    ['Damien Attoe', 'https://digital4n6withdamien.blogspot.com/', '@AttoeDamien', 'https://github.com/SpyderForensics'],
    ['Anna Kirpichnikova', 'https://www.linkedin.com/in/anna-kirpichnikova-a4819a10b/', '', 'https://github.com/annkirpv'],
    ['Christian Peter', 'https://www.linkedin.com/in/christian-peter-49b4ab182/', '@DasZamomin', 'https://github.com/prosch88'],
    ['Jérôme Arn', 'https://www.linkedin.com/in/j%C3%A9r%C3%B4me-a-dfir/', '@theTul1p3', 'https://github.com/Th3Tul1p3'],
    ['Nicolai Martini', '', '', 'https://github.com/NicolaiMartini/']
]
