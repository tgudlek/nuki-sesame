import random
import sys
import traceback
from collections import namedtuple
from typing import List, Optional

import inquirer
from colorama import Fore, Style

from src.api.client import NukiClient
from src.models.smartlock_authorization_model import SmartlockAuthorizationModel
from src.models.smartlock_model import SmartlockModel

DropdownOption = namedtuple("Option", ["name", "value"])


def prompt_for_password(prompt: str) -> str:
    questions = [inquirer.Password("password", message=prompt)]
    answers = inquirer.prompt(questions)
    return answers["password"]


def generate_random_code() -> int:
    """Generates a random 6-digit integer that does not contain the digit '0' or start with '12'."""
    while True:
        # Generate a random 6-digit integer
        random_number = random.randint(100000, 999999)

        # Check if the number meets the conditions
        if "0" not in str(random_number) and not str(random_number).startswith("12"):
            return random_number


def _prompt_user_selection(prompt: str, options: List[DropdownOption]) -> any:
    questions = [inquirer.List("selected_option", message=prompt, choices=options)]
    answers = inquirer.prompt(questions)
    selected_option = answers["selected_option"]

    return selected_option


def pick_smartlock(nuki_client: NukiClient) -> SmartlockModel:
    smartlocks = SmartlockModel.get_all(nuki_client)

    if len(smartlocks) == 1:
        return smartlocks[0]

    dropdown_options = [
        DropdownOption(f"{smartlock.name} ({smartlock.id})", smartlock)
        for smartlock in smartlocks
    ]
    return _prompt_user_selection("Please choose a smartlock", dropdown_options)


def pick_authorized_code(
    nuki_client: NukiClient, smartlock: SmartlockModel
) -> SmartlockAuthorizationModel:
    authorizations = SmartlockAuthorizationModel.get_all(nuki_client, smartlock)

    if not authorizations:
        raise Exception(
            f"No authorized codes found for smartlock with ID {smartlock.id}."
        )

    dropdown_options = [
        DropdownOption(f"{auth.name} ({auth.code})", auth) for auth in authorizations
    ]
    return _prompt_user_selection("Please choose an authorized code", dropdown_options)


def exit_with_status(
    is_success: bool,
    message: str,
    debug: Optional[bool] = False,
    exception: Optional[Exception] = None,
) -> None:
    status, color = ("SUCCESS", Fore.GREEN) if is_success else ("ERROR", Fore.RED)

    if not is_success and debug and exception:
        traceback.print_exc()

    print(
        f"{Style.BRIGHT}[{color}{status}{Style.RESET_ALL}{Style.BRIGHT}]{Style.RESET_ALL} {message}"
    )

    if not is_success:
        sys.exit(1)
    sys.exit(0)
