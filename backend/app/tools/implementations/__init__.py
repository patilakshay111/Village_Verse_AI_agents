from app.tools.implementations.business import create_business
from app.tools.implementations.construction import complete_construction, start_construction
from app.tools.implementations.economy import buy_asset, repay_loan, sell_asset, take_loan
from app.tools.implementations.files import edit_file, read_file, write_file
from app.tools.implementations.projects import create_project
from app.tools.implementations.web import execute_python, search_web
from app.tools.implementations.workforce import fire_worker, hire_worker
from app.tools.registry import ToolRegistry


def register_all_tools(registry: ToolRegistry) -> None:
    registry.register("search_web", search_web)
    registry.register("read_file", read_file)
    registry.register("write_file", write_file)
    registry.register("edit_file", edit_file)
    registry.register("execute_python", execute_python)
    registry.register("create_project", create_project)
    registry.register("create_business", create_business)
    registry.register("buy_asset", buy_asset)
    registry.register("sell_asset", sell_asset)
    registry.register("take_loan", take_loan)
    registry.register("repay_loan", repay_loan)
    registry.register("hire_worker", hire_worker)
    registry.register("fire_worker", fire_worker)
    registry.register("start_construction", start_construction)
    registry.register("complete_construction", complete_construction)
