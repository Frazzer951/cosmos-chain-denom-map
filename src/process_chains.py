import json
import os

from tqdm import tqdm

from download_repo import download_chain_registry
from ibc_asset_loader import load_assets, load_ibc_files
from pydantic_types import IBC, Chain, Denom, DenomMap
from tqdm_logging import setup_logger

logger = setup_logger('process_chains')


def export_file(file_name, data, min_file=False):
    with open(f"{file_name}.json", "w") as f:
        json.dump(data, f, indent=None if min_file else 4, sort_keys=True)


def process_assets_for_chain(chain: Chain):
    denoms_for_chain = {}

    for asset in tqdm(chain.assets, desc=f"Processing assets for {chain.chain_name}", leave=False):
        denoms = {denom_unit.denom.lower(): denom_unit for denom_unit in asset.denom_units}
        display_denom = denoms.get(asset.display.lower())

        # If asset.display.lower() didn't match a denom, check aliases
        if not display_denom:
            for denom_unit in asset.denom_units:
                if denom_unit.aliases:
                    if asset.display.lower() in [alias.lower() for alias in denom_unit.aliases]:
                        logger.info(f'Found alias {asset.display} for {asset.name} on {chain.chain_name}')
                        display_denom = denom_unit
                        break

        if not display_denom:
            logger.error(
                f"Display denom {asset.display} not found in denom_units for {asset.name} on {chain.chain_name}")
            continue

        display_decimals = display_denom.exponent
        for denom in denoms:
            denom_key = f'{denom}_{chain.chain_name}'
            if denom_key in denoms_for_chain:
                logger.warning(f"Denom {denom_key} already exists for the chain {chain.chain_name}")
                continue

            decimals = display_decimals - denoms[denom].exponent
            denoms_for_chain[denom_key] = Denom(
                denom=denoms[denom].denom,
                name=asset.name,
                symbol=asset.symbol,
                decimals=decimals,
                chain=chain.chain_name,
                description=asset.description,
                aliases=denoms[denom].aliases,
                type_asset=asset.type_asset,
                address=asset.address,
                traces=asset.traces,
                ibc=asset.ibc,
                logo_URIs=asset.logo_URIs,
                images=asset.images,
                coingecko_id=asset.coingecko_id,
                keywords=asset.keywords,
            )

    return denoms_for_chain


def process_chains():
    denom_map = DenomMap(denoms={})
    chains = [Chain(**chain_data) for chain_data in load_assets()]

    for chain in tqdm(chains, desc="Processing chains"):
        denom_map.denoms.update(process_assets_for_chain(chain))

    logger.info(f'Found {len(denom_map.denoms)} denoms')
    denom_map_dict = denom_map.model_dump()
    export_file('denom_map', denom_map_dict['denoms'], False)
    export_file('denom_map_min', denom_map_dict['denoms'], True)


def process_ibc_files():
    ibc_assets = [IBC(**ibc_data) for ibc_data in load_ibc_files()]

    ibc_map = {}

    for ibc_asset in tqdm(ibc_assets, desc="Processing IBC assets"):
        chain_1 = ibc_asset.chain_1.chain_name
        chain_2 = ibc_asset.chain_2.chain_name

        for channel in ibc_asset.channels:
            # Process Chain 1
            chain_1_channel_id = channel.chain_1.channel_id
            chain_1_port_id = channel.chain_1.port_id

            if chain_1 not in ibc_map:
                ibc_map[chain_1] = {}

            if chain_1_port_id not in ibc_map[chain_1]:
                ibc_map[chain_1][chain_1_port_id] = {}

            ibc_map[chain_1][chain_1_port_id].setdefault(chain_1_channel_id, set()).add(chain_2)

            # Process Chain 2
            chain_2_channel_id = channel.chain_2.channel_id
            chain_2_port_id = channel.chain_2.port_id

            if chain_2 not in ibc_map:
                ibc_map[chain_2] = {}

            if chain_2_port_id not in ibc_map[chain_2]:
                ibc_map[chain_2][chain_2_port_id] = {}

            ibc_map[chain_2][chain_2_port_id].setdefault(chain_2_channel_id, set()).add(chain_1)

    # Convert sets to lists for JSON serialization
    for chain, ports in ibc_map.items():
        for port, channels in ports.items():
            for channel, connected_chains in channels.items():
                ibc_map[chain][port][channel] = list(connected_chains)

    export_file('ibc_map', ibc_map, False)
    export_file('ibc_map_min', ibc_map, True)


def main(process_chain=True, process_ibc=True, force_update=False):
    if force_update and os.path.exists("commit_id.json"):
        os.remove("commit_id.json")

    if not download_chain_registry():
        logger.info("No new changes to process.")
        return

    if process_chain:
        logger.info("Processing chains...")
        process_chains()
    if process_ibc:
        logger.info("Processing IBC files...")
        process_ibc_files()


if __name__ == "__main__":
    main(process_chain=False, process_ibc=True, force_update=True)
