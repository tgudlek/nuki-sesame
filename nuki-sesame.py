#!/usr/bin/env python3

import argparse

from src.api.client import NukiClient
from src.models.smartlock_authorization_model import SmartlockAuthorizationModel
from src.models.smartlock_model import SmartlockModel
from src.utils import (
    exit_with_status,
    generate_random_code,
    pick_smartlock,
    prompt_for_password,
    pick_authorized_code,
)


def main():
    parser = argparse.ArgumentParser(description="Interact with Nuki Web API.")
    subparsers = parser.add_subparsers(dest="command", help="the command to execute")

    login_parser = subparsers.add_parser(
        "auth", help="To save or check the authentication token."
    )
    login_parser.add_argument(
        "--check_only",
        action="store_true",
        help="checks the validity of the token without saving it.",
    )

    code_parser = subparsers.add_parser(
        "code", help="Interact with authorization codes."
    )
    code_subparsers = code_parser.add_subparsers(
        dest="subcommand", help="Code-related commands"
    )

    code_add_parser = code_subparsers.add_parser("add")
    code_add_parser.add_argument(
        "--smartlock_id",
        type=int,
        help="the ID of the smartlock to authorize. "
        "if not provided, the user will be prompted to choose if there are more than one",
    )
    code_add_parser.add_argument(
        "--code",
        type=int,
        help="the code for the new authorization. if not provided, one will be generated randomly",
    )
    code_add_parser.add_argument(
        "--duration",
        type=str,
        default="1h",
        help="the duration for the new authorization",
    )

    code_delete_parser = code_subparsers.add_parser("delete")
    code_delete_parser.add_argument(
        "--smartlock_id",
        type=int,
        help="the ID of the smartlock to delete the code from. "
        "if not provided, the user will be prompted to choose if there are more than one",
    )
    code_delete_parser.add_argument(
        "--code",
        type=int,
        help="the code of the authorization to delete. if not provided, the user will be prompted to choose",
    )

    lock_parser = subparsers.add_parser("lock", help="Lock a smartlock.")
    lock_parser.add_argument(
        "--smartlock_id",
        type=int,
        help="the ID of the smartlock to lock. "
        "if not provided, the user will be prompted to choose if there are more than one",
    )

    unlock_parser = subparsers.add_parser("unlock", help="Unlock a smartlock.")
    unlock_parser.add_argument(
        "--smartlock_id",
        type=int,
        help="the ID of the smartlock to unlock. "
        "if not provided, the user will be prompted to choose if there are more than one",
    )

    for subparser in [
        login_parser,
        code_add_parser,
        code_delete_parser,
        lock_parser,
        unlock_parser,
    ]:
        subparser.add_argument(
            "--token_path",
            default="~/.nuki/bearer_token",
            help="path to the token file",
        )
        subparser.add_argument(
            "--debug", action="store_true", help="print full error traceback"
        )

    args = parser.parse_args()

    if args.debug:
        import logging
        import http.client

        # Enable debugging at http.client level (requests -> urllib3 -> http.client)
        http.client.HTTPConnection.debuglevel = 1

        # Initialize logging
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    try:
        if args.command == "auth":
            if args.check_only:
                token = prompt_for_password("Enter the authentication token: ")
                client = NukiClient(token)
                client.check_auth()
                exit_with_status(True, "The token is valid.")
            else:
                token = prompt_for_password("Enter the authentication token: ")
                client = NukiClient(token)
                client.check_auth()
                client.store_locally(args.token_path)
                exit_with_status(True, "Token saved successfully.")
        else:
            client = NukiClient.load(args.token_path)
            smartlock = (
                SmartlockModel.get_by_id(client, args.smartlock_id)
                if args.smartlock_id
                else pick_smartlock(nuki_client=client)
            )

            if args.command == "code":
                if args.subcommand == "add":
                    code = args.code if args.code else generate_random_code()

                    SmartlockAuthorizationModel.create_code(
                        nuki_client=client,
                        smartlock=smartlock,
                        code=code,
                        duration=args.duration,
                    )

                    exit_with_status(
                        True,
                        f"Authorization created successfully. {smartlock}, Code: {code}, Duration: {args.duration}",
                    )
                elif args.subcommand == "delete":
                    smartlock_authorization = (
                        SmartlockAuthorizationModel.get_by_code(
                            nuki_client=client, smartlock=smartlock, code=args.code
                        )
                        if args.code
                        else pick_authorized_code(
                            nuki_client=client, smartlock=smartlock
                        )
                    )

                    SmartlockAuthorizationModel.delete(
                        nuki_client=client,
                        smartlock=smartlock,
                        code=smartlock_authorization.code,
                    )

                    exit_with_status(
                        True,
                        f"Authorization deleted successfully. {smartlock_authorization}",
                    )
            elif args.command == "lock":
                smartlock.trigger_lock(nuki_client=client)
                exit_with_status(True, f"{smartlock} locked!")
            elif args.command == "unlock":
                smartlock.trigger_unlock(nuki_client=client)
                exit_with_status(True, f"{smartlock} unlocked!")

    except Exception as e:
        exit_with_status(False, f"{type(e).__name__}: {str(e)}", args.debug, e)


if __name__ == "__main__":
    main()
