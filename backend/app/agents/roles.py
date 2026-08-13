"""Agent roles and tool permissions — keeps farmers from getting filesystem access."""

from enum import StrEnum


class AgentRole(StrEnum):
    FARMER = "farmer"
    SHOPKEEPER = "shopkeeper"
    TEACHER = "teacher"
    DRIVER = "driver"
    POLITICIAN = "politician"
    SARPANCH = "sarpanch"
    GRAM_SEVAK = "gram_sevak"
    CONTRACTOR = "contractor"
    MILKMAN = "milkman"
    MECHANIC = "mechanic"
    HOMEMAKER = "homemaker"
    STUDENT = "student"
    BUSINESS_OWNER = "business_owner"
    SOFTWARE_FOUNDER = "software_founder"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    DEFAULT = "villager"


# Base economic tools available to most working adults
_ECONOMY = frozenset(
    {
        "buy_asset",
        "sell_asset",
        "take_loan",
        "repay_loan",
        "start_construction",
        "complete_construction",
    }
)

_BUSINESS = _ECONOMY | frozenset({"create_business", "create_project", "hire_worker", "fire_worker"})

# Code / web / filesystem — software roles only
_TECH = frozenset(
    {
        "search_web",
        "read_file",
        "write_file",
        "edit_file",
        "execute_python",
    }
)

ROLE_PERMISSIONS: dict[AgentRole, frozenset[str]] = {
    AgentRole.FARMER: _ECONOMY,
    AgentRole.SHOPKEEPER: _BUSINESS,
    AgentRole.TEACHER: _ECONOMY | frozenset({"create_project"}),
    AgentRole.DRIVER: _ECONOMY,
    AgentRole.POLITICIAN: _ECONOMY | frozenset({"create_project"}),
    AgentRole.SARPANCH: _ECONOMY | frozenset({"create_project", "hire_worker"}),
    AgentRole.GRAM_SEVAK: _ECONOMY,
    AgentRole.CONTRACTOR: _BUSINESS | frozenset({"start_construction", "complete_construction"}),
    AgentRole.MILKMAN: _ECONOMY | frozenset({"create_business"}),
    AgentRole.MECHANIC: _ECONOMY | frozenset({"create_business"}),
    AgentRole.HOMEMAKER: frozenset({"buy_asset", "sell_asset", "take_loan", "repay_loan"}),
    AgentRole.STUDENT: frozenset(),
    AgentRole.BUSINESS_OWNER: _BUSINESS,
    AgentRole.SOFTWARE_FOUNDER: _BUSINESS | _TECH,
    AgentRole.DEVELOPER: _TECH | frozenset({"create_project"}),
    AgentRole.RESEARCHER: frozenset({"search_web", "read_file", "create_project"}),
    AgentRole.DEFAULT: _ECONOMY,
}


_OCCUPATION_ROLE_MAP: dict[str, AgentRole] = {
    "Farmer": AgentRole.FARMER,
    "Farm helper": AgentRole.FARMER,
    "Shopkeeper": AgentRole.SHOPKEEPER,
    "Teacher": AgentRole.TEACHER,
    "Driver": AgentRole.DRIVER,
    "Politician": AgentRole.POLITICIAN,
    "Sarpanch": AgentRole.SARPANCH,
    "Gram Sevak": AgentRole.GRAM_SEVAK,
    "Contractor": AgentRole.CONTRACTOR,
    "Milkman": AgentRole.MILKMAN,
    "Mechanic": AgentRole.MECHANIC,
    "Homemaker": AgentRole.HOMEMAKER,
    "Student": AgentRole.STUDENT,
    "Retired": AgentRole.DEFAULT,
    "Doctor": AgentRole.BUSINESS_OWNER,
    "Carpenter": AgentRole.CONTRACTOR,
    "Electrician": AgentRole.MECHANIC,
    "Tailor": AgentRole.SHOPKEEPER,
}


def infer_role_from_occupation(occupation: str) -> AgentRole:
    return _OCCUPATION_ROLE_MAP.get(occupation, AgentRole.DEFAULT)


def permissions_for_role(role: AgentRole | str) -> frozenset[str]:
    if isinstance(role, str):
        try:
            role = AgentRole(role)
        except ValueError:
            role = AgentRole.DEFAULT
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[AgentRole.DEFAULT])
