# R0 Reject / Do-Not-Port Ledger

**Document ID:** GS-R0-REJECT-001  
**Version:** 0.1  
**Status:** IN PROGRESS  
**Date:** 2026-08-24

This ledger exists to prevent legacy baggage from entering the Grant Sector product merely because it exists in `larger-lab`.

| Item | Source | Disposition | Reason |
|---|---|---|---|
| Pure CEREBUS/MVE strategy logic | trading branches | REJECT for this product | Trading-domain specific |
| Capital-routing trading logic | `capital-routing` | REJECT for this product | Trading-domain specific |
| Crypto strategy/data logic | crypto branches | REJECT for this product | Trading-domain specific |
| Broker/MT5 live-execution logic | trading runtime | REJECT for this product | Capital-bearing market domain |

Generic infrastructure embedded in these branches may still be salvaged separately.
