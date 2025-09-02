def tg_send(*args, bot_token: str, chat_id: str) -> None:
    from contextlib import suppress
    import requests
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning

    urllib3.disable_warnings(InsecureRequestWarning)
    json = {'chat_id': chat_id, 'text': ' '.join([str(i) for i in args])}
    with suppress(Exception):
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=json, verify=False, timeout=3)
