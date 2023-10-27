import json
import os

from tqdm import tqdm

from download_repo import download_chain_registry
from load_asset_files import load_assets
from pydantic_types import Chain, Denom, DenomMap
from tqdm_logging import setup_logger

logger = setup_logger('process_chains')


def export_file(file_name, data, min_file=False):
    logger.info("Writing denom_map.json")
    with open(f"{file_name}.json", "w") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))
    if min_file:
        logger.info("Writing denom_map_min.json")
        with open(f"{file_name}_min.json", "w") as f:
            f.write(json.dumps(data, sort_keys=True))


def process_chains(force_update=False):
    if force_update:
        # Delete commit_id.json if it exists to force an update
        if os.path.exists("commit_id.json"):
            os.remove("commit_id.json")

    new_changes = download_chain_registry()

    if new_changes:
        denom_map = DenomMap(denoms={})
        chains_raw = load_assets()
        chains = [Chain(**chain_data) for chain_data in chains_raw]

        for chain in tqdm(chains, desc="Processing chains"):
            for asset in tqdm(chain.assets, desc=f"Processing assets for {chain.chain_name}", leave=False):
                denoms = {denom_unit.denom.lower(): denom_unit for denom_unit in asset.denom_units}
                base_denom = denoms.get(asset.base.lower())
                if not base_denom:
                    logger.error(f"Base denom {asset.base} not found in denom_units for {asset.name}")
                    continue

                display_decimals = base_denom.exponent
                for denom in denoms:
                    denom_key = f'{denom}_{chain.chain_name}'
                    if denom_key in denom_map:
                        logger.warning(f"Denom {denom_key} already exists in denom_map")
                        continue

                    decimals = display_decimals - denoms[denom].exponent
                    denom_map.denoms[denom_key] = Denom(
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

        logger.info(f'Found {len(denom_map.denoms)} denoms')

        # Write denoms to file
        denom_map_dict = denom_map.model_dump()
        export_file('denom_map', denom_map_dict['denoms'], True)


if __name__ == "__main__":
    process_chains(True)
