import json
from time import sleep

import requests

TRACKER_ENDPOINT = "https://tracker.icon.community/api/v1"
LIMIT = 100

START_TIMESTAMP = 1657800000
END_TIMESTAMP = 1657886400


def main():

    ACTIVE_ADDRESSES = set()

    timestamp_range = (START_TIMESTAMP, END_TIMESTAMP)

    start_block = _convert_timestamp_to_block(timestamp_range[0])
    end_block = _convert_timestamp_to_block(timestamp_range[1])

    print(f"Block Range: {start_block} - {end_block}")

    sleep(2)

    i = 0
    while True:
        skip = LIMIT * i
        addresses = _get_addresses(start_block, end_block, skip)
        if addresses is None:
            break
        else:
            ACTIVE_ADDRESSES.update(addresses)
            print(len(ACTIVE_ADDRESSES))
        i += 1

    active_addresses_json = {
        "count": len(ACTIVE_ADDRESSES),
        "addresses": ACTIVE_ADDRESSES,
    }

    filename = f"active-addresses-{START_TIMESTAMP}-{END_TIMESTAMP}.json"
    print("Writing addresses to ./{filename}...")
    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(active_addresses_json, f, ensure_ascii=False, indent=4)

    return None


def _get_addresses(start_block, end_block, skip):
    while True:
        try:
            url = f"{TRACKER_ENDPOINT}/transactions?start_block_number={start_block}&end_block_number={end_block}&limit={LIMIT}&skip={skip}"
            r = requests.get(url)
            data = r.json()
            if len(data) > 0:
                addresses = set(
                    [
                        transaction["from_address"]
                        for transaction in data
                        if transaction["from_address"] != ""
                    ]
                )
                return addresses
            else:
                return None
        except:
            sleep(1)
            continue


def _convert_timestamp_to_block(timestamp: int) -> int:
    """
    Returns block height for the provided timestamp.

    Args:
        timestamp (int): Unix timestamp in seconds (must be greater than 1516819217)

    Returns:
        int: Block height for the provided timestamp.
    """
    url = f"{TRACKER_ENDPOINT}/blocks/timestamp/{timestamp * 1000000}/"  # Convert timestamp from s to ms.
    r = requests.get(url)
    data = r.json()
    return data["number"]


if __name__ == "__main__":
    main()
