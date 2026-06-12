from arguments import Arguments
from logging import Logger, getLogger, basicConfig, DEBUG

ARGUMENTS = Arguments.get_arguments()
IMAGE_EXTENSIONS: list[str] = [".jpg", ".png", ".jpeg", ".webp"]
LOGGER: Logger = getLogger(__name__)
MAXIMUM_IMAGE_COUNT_PER_DIRECTORY: int = ARGUMENTS.count
DIRECTORY_NAMES = (
    "akaname",  # the filth-licker demon
    "akkorokamui",  # giant octopus sea deity
    "amazake-babaa",  # old hag who spreads disease
    "ame-onna",  # rain woman spirit
    "ao-andon",  # blue lantern ghost
    "baku",  # dream-eating chimera
    "bakeneko",  # shape-shifting cat
    "bakekujira",  # ghost whale skeleton
    "byakko",  # white tiger celestial
    "datsue-ba",  # underworld hag
    "gashadokuro",  # giant starving skeleton
    "hakutaku",  # wise beast of knowledge
    "hannya",  # jealous serpent demoness
    "hitotsume-kozo",  # one-eyed monk spirit
    "isonade",  # barb-tailed sea beast
    "ittan-momen",  # flying cloth strangler
    "jorogumo",  # spider woman shapeshifter
    "jubokko",  # vampire tree
    "kappa",  # water-dwelling trickster
    "karasu-tengu",  # crow goblin warrior
    "katawaguruma",  # half-wheel wailing woman
    "kijo",  # mountain ogress
    "kirin",  # divine chimeric unicorn
    "kitsune",  # nine-tailed fox spirit
    "komainu",  # lion-dog guardian
    "kubire-oni",  # strangling demon
    "kurama tengu",  # great mountain goblin
    "kyokotsu",  # well-dwelling bone ghost
    "mizuchi",  # water dragon deity
    "namahage",  # demon of laziness
    "ningyo",  # fish-human oracle being
    "nue",  # chimeric nightmare beast
    "nukekubi",  # flying severed head
    "oni",  # horned club-wielding demon
    "otoroshi",  # shaggy shrine guardian
    "raiju",  # lightning beast
    "rokurokubi",  # stretch-necked woman
    "ryujin",  # dragon king of the sea
    "shachihoko",  # carp-tiger storm guardian
    "shikigami",  # summoned spirit servant
    "shinigami",  # death god
    "shiro-uneri",  # possessed dishcloth specter
    "shunobon",  # red-headed lantern ghost
    "tanuki",  # shape-shifting raccoon dog
    "tengu",  # winged mountain demon
    "tsuchigumo",  # earth spider demon lord
    "umi-bozu",  # ocean monk colossus
    "yamata-no-orochi",  # eight-headed dragon serpent
    "yatagarasu",  # three-legged solar crow
    "yuki-onna",  # snow woman of death
)
basicConfig(
    level=DEBUG,
    format="[%(levelname)s] - [%(asctime)s] - [%(message)s]",
    datefmt="%I:%M:%S %p",
)
