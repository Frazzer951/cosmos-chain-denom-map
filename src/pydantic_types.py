from typing import Dict, List, Optional

from pydantic import BaseModel


class DenomUnit(BaseModel):
    denom: str
    exponent: int
    aliases: Optional[List[str]] = None


class Asset(BaseModel):
    description: Optional[str] = None
    denom_units: List[DenomUnit]
    type_asset: Optional[str] = None
    address: Optional[str] = None
    base: str
    name: str
    display: str
    symbol: str
    traces: Optional[List[Dict]] = None
    ibc: Optional[Dict] = None
    logo_URIs: Optional[Dict[str, str]] = None
    images: Optional[List[Dict[str, str | Dict]]] = None
    coingecko_id: Optional[str] = None
    keywords: Optional[List[str]] = None


class Chain(BaseModel):
    chain_name: str
    assets: List[Asset]


class Denom(BaseModel):
    denom: str
    name: str
    symbol: str
    decimals: int
    chain: str
    description: Optional[str]
    aliases: Optional[List[str]]
    type_asset: Optional[str]
    address: Optional[str]
    traces: Optional[List[Dict]]
    ibc: Optional[Dict]
    logo_URIs: Optional[Dict[str, str]]
    images: Optional[List[Dict[str, str | Dict]]]
    coingecko_id: Optional[str]
    keywords: Optional[List[str]]


class DenomMap(BaseModel):
    denoms: Dict[str, Denom]


class ChainInfo(BaseModel):
    chain_name: str
    client_id: str
    connection_id: str


class ChannelInfo(BaseModel):
    channel_id: str
    port_id: str
    client_id: Optional[str] = None
    connection_id: Optional[str] = None


class Channel(BaseModel):
    chain_1: ChannelInfo
    chain_2: ChannelInfo
    ordering: str
    version: str
    description: Optional[str] = None
    tags: Optional[Dict] = None


class IBC(BaseModel):
    chain_1: ChainInfo
    chain_2: ChainInfo
    channels: List[Channel]
