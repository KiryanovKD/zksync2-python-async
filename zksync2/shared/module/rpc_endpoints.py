from web3.types import RPCEndpoint

zks_estimate_fee_rpc = RPCEndpoint("zks_estimateFee")
zks_main_contract_rpc = RPCEndpoint("zks_getMainContract")
zks_get_confirmed_tokens_rpc = RPCEndpoint("zks_getConfirmedTokens")
zks_get_token_price_rpc = RPCEndpoint("zks_getTokenPrice")
zks_l1_chain_id_rpc = RPCEndpoint("zks_L1ChainId")
zks_get_all_account_balances_rpc = RPCEndpoint("zks_getAllAccountBalances")
zks_get_bridge_contracts_rpc = RPCEndpoint("zks_getBridgeContracts")
zks_get_l2_to_l1_msg_proof_prc = RPCEndpoint("zks_getL2ToL1MsgProof")
zks_get_l2_to_l1_log_proof_prc = RPCEndpoint("zks_getL2ToL1LogProof")
eth_estimate_gas_rpc = RPCEndpoint("eth_estimateGas")

zks_set_contract_debug_info_rpc = RPCEndpoint("zks_setContractDebugInfo")
zks_get_contract_debug_info_rpc = RPCEndpoint("zks_getContractDebugInfo")
zks_get_transaction_trace_rpc = RPCEndpoint("zks_getTransactionTrace")
zks_get_testnet_paymaster_address = RPCEndpoint("zks_getTestnetPaymaster")
