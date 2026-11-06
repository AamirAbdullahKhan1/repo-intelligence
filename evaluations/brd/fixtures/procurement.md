# Purchase Approval Portal

Purpose
Employees need a portal to request purchases. Finance reviews expenditure before orders are released. No AI capability is requested.

Requirements
- REQ-01: An employee submits a purchase through the portal. Purchase Management stores the purchase record.
- REQ-02: Finance must approve the purchase before Purchase Management sends the order to the supplier.
- REQ-03: If Finance rejects the purchase, notify the employee without sending an order.
- REQ-04: The supplier integration is required, but no supplier platform has been selected.

Acceptance criteria
Given an unapproved purchase, when release is requested, then the order must not be sent.

Open decisions
The approval amount threshold is not agreed.
