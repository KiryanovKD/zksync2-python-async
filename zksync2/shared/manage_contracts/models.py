from dataclasses import dataclass
from typing import List
from eth_typing import HexStr

@dataclass
class StoredBlockInfo:
    blockNumber: int
    blockHash: bytes
    indexRepeatedStorageChanges: int
    numberOfLayer1Txs: int
    priorityOperationsHash: bytes
    l2LogsTreeRoot: bytes
    timestamp: int
    commitment: bytes


@dataclass
class CommitBlockInfo:
    blockNumber: int
    timestamp: int
    indexRepeatedStorageChanges: int
    numberOfLayer1Txs: int
    l2LogsTreeRoot: bytes
    priorityOperationsHash: bytes
    initialStorageChanges: bytes
    repeatedStorageChanges: bytes
    l2Logs: bytes
    l2ArbitraryLengthMessages: List[bytes]
    factoryDeps: List[bytes]


@dataclass
class FacetCut:
    facet: HexStr
    action: int
    isFreezable: bool
    selectors: bytes


@dataclass
class DiamondCutData:
    facetCuts: List[FacetCut]
    initAddress: HexStr
    initCalldata: bytes


@dataclass
class Facet:
    addr: HexStr
    selectors: List[bytes]


@dataclass
class VerifierParams:
    recursionNodeLevelVkHash: bytes
    recursionLeafLevelVkHash: bytes
    recursionCircuitsSetVksHash: bytes
