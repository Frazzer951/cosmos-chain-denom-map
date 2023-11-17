import json

from tqdm import tqdm

from download_repo import download_chain_registry
from ibc_asset_loader import load_assets, load_ibc_files
from pydantic_types import IBC, Chain, Channel, Denom, DenomMap
from tqdm_logging import setup_logger

logger = setup_logger("process_chains")


def export_file(file_name, data, min_file=False):
    """Export data to a JSON file."""
    with open(f"{file_name}.json", "w") as f:
        json.dump(data, f, indent=None if min_file else 4, sort_keys=True)


def process_assets_for_chain(chain: Chain, denom_map: DenomMap):
    """Process assets for a given chain."""

    for asset in tqdm(chain.assets, desc=f"Processing assets for {chain.chain_name}", leave=False):
        denoms = {denom_unit.denom.lower(): denom_unit for denom_unit in asset.denom_units}
        display_denom = denoms.get(asset.display.lower())

        # Check aliases if display_denom is not found directly
        if not display_denom:
            for denom_unit in asset.denom_units:
                if denom_unit.aliases and asset.display.lower() in [alias.lower() for alias in denom_unit.aliases]:
                    logger.info(f"Found alias {asset.display} for {asset.name} on {chain.chain_name}")
                    display_denom = denom_unit
                    break

        if not display_denom:
            logger.error(
                f"Display denom {asset.display} not found in denom_units for {asset.name} on {chain.chain_name}"
            )
            continue

        display_decimals = display_denom.exponent
        for denom in denoms:
            if denom not in denom_map.denoms:
                denom_map.denoms[denom] = {}

            if chain.chain_name in denom_map.denoms[denom]:
                logger.warning(f"Denom {denom} for the chain {chain.chain_name} already exists.")
                continue

            decimals = display_decimals - denoms[denom].exponent
            denom_map.denoms[denom][chain.chain_name] = Denom(
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


def process_chains():
    """Process chain data and export to a JSON file."""
    denom_map = DenomMap(denoms={})
    chains = [Chain(**chain_data) for chain_data in load_assets()]

    for chain in tqdm(chains, desc="Processing chains"):
        process_assets_for_chain(chain, denom_map)

    logger.info(f"Found {len(denom_map.denoms)} denoms")
    denom_map_dict = denom_map.model_dump()
    export_file("denom_map", denom_map_dict["denoms"], False)
    export_file("denom_map_min", denom_map_dict["denoms"], True)


def initialize_chain_map(chain_map, chain, port_id, channel_id, connected_chain):
    """Initialize the chain map with given details or update if already present."""
    chain_map.setdefault(chain, {}).setdefault(port_id, {}).setdefault(channel_id, set()).add(connected_chain)


def process_channel(chain_map: dict, channel: Channel, chain: str, from_chain: str, to_chain: str):
    """Process channel data for a given chain."""
    channel_info = getattr(channel, chain)
    channel_id = channel_info.channel_id
    port_id = channel_info.port_id
    initialize_chain_map(chain_map, from_chain, port_id, channel_id, to_chain)


def convert_sets_to_lists(chain_map):
    """Convert sets to lists for JSON serialization."""
    for chain, ports in chain_map.items():
        for port, channels in ports.items():
            for channel, connected_chains in channels.items():
                chain_map[chain][port][channel] = sorted(list(connected_chains))


def process_ibc_files():
    """Process IBC file data and export to a JSON file."""
    ibc_assets = [IBC(**ibc_data) for ibc_data in load_ibc_files()]
    ibc_map = {}

    for ibc_asset in tqdm(ibc_assets, desc="Processing IBC assets"):
        chain_1, chain_2 = ibc_asset.chain_1.chain_name, ibc_asset.chain_2.chain_name

        for channel in ibc_asset.channels:
            process_channel(ibc_map, channel, "chain_1", chain_1, chain_2)
            process_channel(ibc_map, channel, "chain_2", chain_2, chain_1)

    convert_sets_to_lists(ibc_map)

    export_file("ibc_map", ibc_map, False)
    export_file("ibc_map_min", ibc_map, True)


def main(process_chain=True, process_ibc=True):
    """Main function to orchestrate the processing of chain and IBC data."""

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
    main()
    # main(process_chain=True, process_ibc=True)
