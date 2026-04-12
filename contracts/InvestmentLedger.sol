pragma solidity ^0.8.0;

contract InvestmentLedger {
    event InvestmentMade(
        address investor,
        address startupOwner,
        uint256 startupId,
        uint256 amount,
        string notes,
        uint256 timestamp
    );

    function recordInvestment(
        address startupOwner,
        uint256 startupId,
        uint256 amount,
        string memory notes
    ) external {
        emit InvestmentMade(msg.sender, startupOwner, startupId, amount, notes, block.timestamp);
    }
}
