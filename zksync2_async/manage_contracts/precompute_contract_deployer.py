from eth_typing import HexStr
from typing import Optional
from web3.types import Nonce, TxReceipt
from eth_utils.crypto import keccak

from zksync2_async.module.zksync_web3 import AsyncZkSyncWeb3
from zksync2_async.utils.abi import contract_deployer_abi_default
from zksync2_async.core.utils import pad_front_bytes, to_bytes, int_to_bytes, hash_byte_code
from zksync2_async.manage_contracts.contract_encoder_base import BaseContractEncoder


class AsyncPrecomputeContractDeployer:
    DEFAULT_SALT = b'\0' * 32
    CREATE_FUNC = "create"
    CREATE2_FUNC = "create2"
    MAX_BYTE_CODE_LENGTH = 2 ** 16
    EMPTY_BYTES = b''

    CREATE_PREFIX = keccak(text="zksyncCreate")
    CREATE2_PREFIX = keccak(text="zksyncCreate2")

    def __init__(self, web3: AsyncZkSyncWeb3, abi: Optional[dict] = None):
        self.web3 = web3
        if abi is None:
            abi = contract_deployer_abi_default()
        self.contract_encoder = BaseContractEncoder(self.web3, abi)

    def encode_create2(self, bytecode: bytes,
                       call_data: Optional[bytes] = None,
                       salt: Optional[bytes] = None) -> HexStr:

        if salt is None:
            salt = self.DEFAULT_SALT
        if call_data is None:
            call_data = self.EMPTY_BYTES

        if len(salt) != 32:
            raise OverflowError("Salt data must be 32 length")

        bytecode_hash = hash_byte_code(bytecode)
        args = (
            salt,
            bytecode_hash,
            call_data
        )
        return self.contract_encoder.encode_method(fn_name=self.CREATE2_FUNC, args=args)

    def encode_create(self, bytecode: bytes, call_data: Optional[bytes] = None, salt_data: Optional[bytes] = None):
        if salt_data is None:
            salt_data = self.DEFAULT_SALT
        if call_data is None:
            call_data = self.EMPTY_BYTES

        if len(salt_data) != 32:
            raise OverflowError("Salt data must be 32 length")

        bytecode_hash = hash_byte_code(bytecode)
        args = (
            salt_data,
            bytecode_hash,
            call_data
        )
        return self.contract_encoder.encode_method(fn_name=self.CREATE_FUNC, args=args)

    def compute_l2_create_address(self, sender: HexStr, nonce: Nonce) -> HexStr:
        sender_bytes = to_bytes(sender)
        sender_bytes = pad_front_bytes(sender_bytes, 32)
        nonce = int_to_bytes(nonce)
        nonce_bytes = pad_front_bytes(nonce, 32)
        result = self.CREATE_PREFIX + sender_bytes + nonce_bytes
        sha_result = keccak(result)
        address = sha_result[12:]
        address = "0x" + address.hex()
        return HexStr(AsyncZkSyncWeb3.to_checksum_address(address))

    def compute_l2_create2_address(self,
                                   sender: HexStr,
                                   bytecode: bytes,
                                   constructor: bytes,
                                   salt: bytes):
        if len(salt) != 32:
            raise OverflowError("Salt data must be 32 length")

        sender_bytes = to_bytes(sender)
        sender_bytes = pad_front_bytes(sender_bytes, 32)
        bytecode_hash = hash_byte_code(bytecode)
        ctor_hash = keccak(constructor)
        result = self.CREATE2_PREFIX + sender_bytes + salt + bytecode_hash + ctor_hash
        sha_result = keccak(result)
        address = sha_result[12:]
        address = "0x" + address.hex()
        return HexStr(AsyncZkSyncWeb3.to_checksum_address(address))

    def extract_contract_address(self, receipt: TxReceipt) -> HexStr:
        result = self.contract_encoder.contract.events.ContractDeployed().process_receipt(receipt)
        entry = result[1]["args"]
        addr = entry["contractAddress"]
        return addr

