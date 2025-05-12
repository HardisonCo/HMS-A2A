"""
Import Certificate System for the Trade Balance System.

This module implements Warren Buffett's Import Certificate system for balancing
international trade, providing certificate issuance, validation, and trading
mechanisms.
"""

import datetime
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from trade_balance.interfaces import (
    Certificate, CertificateStatus, CertificateAction,
    ICertificateSystem, Result
)


class CertificateManager(ICertificateSystem):
    """
    Implementation of the Import Certificate System based on
    Warren Buffett's balanced trade approach.
    """
    
    def __init__(self):
        """Initialize the certificate manager."""
        self.certificates: Dict[str, Certificate] = {}
        self.owner_certificates: Dict[str, List[str]] = {}
    
    def issue_certificate(
        self,
        owner: str,
        value: float,
        duration_days: int = 180
    ) -> Certificate:
        """
        Issue a new certificate.
        
        Args:
            owner: Certificate owner
            value: Certificate value
            duration_days: Certificate validity duration in days
            
        Returns:
            Issued certificate
        """
        # Generate certificate ID
        cert_id = f"IC-{uuid.uuid4().hex[:8]}-{owner[:3]}-{int(value):08d}"
        
        # Calculate expiry date
        today = datetime.datetime.now()
        expiry = today + datetime.timedelta(days=duration_days)
        
        # Create certificate history
        history = [
            CertificateAction(
                timestamp=today.isoformat(),
                action="issued",
                value=value
            )
        ]
        
        # Create certificate
        certificate = Certificate(
            id=cert_id,
            owner=owner,
            value=value,
            issued_date=today.isoformat(),
            expiry_date=expiry.isoformat(),
            issuing_authority="USTDA",
            status=CertificateStatus.ACTIVE,
            history=history
        )
        
        # Store certificate
        self.certificates[cert_id] = certificate
        
        # Add to owner's certificates
        if owner not in self.owner_certificates:
            self.owner_certificates[owner] = []
        
        self.owner_certificates[owner].append(cert_id)
        
        return certificate
    
    def verify_certificate(self, certificate_id: str) -> bool:
        """
        Verify a certificate is valid.
        
        Args:
            certificate_id: Certificate ID
            
        Returns:
            True if certificate is valid, False otherwise
        """
        # Check if certificate exists
        if certificate_id not in self.certificates:
            return False
        
        certificate = self.certificates[certificate_id]
        
        # Check status
        if certificate.status != CertificateStatus.ACTIVE:
            return False
        
        # Check expiration
        now = datetime.datetime.now()
        expiry = datetime.datetime.fromisoformat(certificate.expiry_date)
        
        return now <= expiry
    
    def transfer_certificate(
        self,
        certificate_id: str,
        new_owner: str
    ) -> Certificate:
        """
        Transfer a certificate to a new owner.
        
        Args:
            certificate_id: Certificate ID
            new_owner: New owner ID
            
        Returns:
            Updated certificate
        """
        # Check if certificate exists and is valid
        if not self.verify_certificate(certificate_id):
            raise ValueError(f"Certificate {certificate_id} is not valid for transfer")
        
        certificate = self.certificates[certificate_id]
        old_owner = certificate.owner
        
        # Update owner
        certificate.owner = new_owner
        
        # Add transfer action to history
        certificate.history.append(
            CertificateAction(
                timestamp=datetime.datetime.now().isoformat(),
                action="transferred",
                value=certificate.value,
                details={"from": old_owner, "to": new_owner}
            )
        )
        
        # Update owner_certificates
        if old_owner in self.owner_certificates and certificate_id in self.owner_certificates[old_owner]:
            self.owner_certificates[old_owner].remove(certificate_id)
        
        if new_owner not in self.owner_certificates:
            self.owner_certificates[new_owner] = []
        
        self.owner_certificates[new_owner].append(certificate_id)
        
        # Update the certificate in storage
        self.certificates[certificate_id] = certificate
        
        return certificate
    
    def use_certificate(
        self,
        certificate_id: str,
        amount: float,
        transaction_id: Optional[str] = None
    ) -> bool:
        """
        Use some or all of a certificate's value.
        
        Args:
            certificate_id: Certificate ID
            amount: Amount to use
            transaction_id: Associated transaction ID
            
        Returns:
            True if certificate was used successfully, False otherwise
        """
        # Check if certificate exists and is valid
        if not self.verify_certificate(certificate_id):
            return False
        
        certificate = self.certificates[certificate_id]
        
        # Check if amount is valid
        if amount <= 0 or amount > certificate.value:
            return False
        
        # Create usage action
        usage_action = CertificateAction(
            timestamp=datetime.datetime.now().isoformat(),
            action="used",
            value=amount,
            details={"transaction_id": transaction_id} if transaction_id else None
        )
        
        # Update certificate
        certificate.history.append(usage_action)
        
        # If entire value is used, mark as used
        if amount >= certificate.value:
            certificate.status = CertificateStatus.USED
            certificate.value = 0
        else:
            # Otherwise, reduce value
            certificate.value -= amount
        
        # Update the certificate in storage
        self.certificates[certificate_id] = certificate
        
        return True
    
    def get_certificate(self, certificate_id: str) -> Optional[Certificate]:
        """
        Get a certificate by ID.
        
        Args:
            certificate_id: Certificate ID
            
        Returns:
            Certificate if found, None otherwise
        """
        return self.certificates.get(certificate_id)
    
    def get_certificates_by_owner(self, owner: str) -> List[Certificate]:
        """
        Get all certificates for an owner.
        
        Args:
            owner: Owner ID
            
        Returns:
            List of certificates
        """
        if owner not in self.owner_certificates:
            return []
        
        return [
            self.certificates[cert_id]
            for cert_id in self.owner_certificates[owner]
            if cert_id in self.certificates
        ]
    
    def get_available_value(self, owner: str) -> float:
        """
        Get total available certificate value for an owner.
        
        Args:
            owner: Owner ID
            
        Returns:
            Total available value
        """
        certificates = self.get_certificates_by_owner(owner)
        
        return sum(
            cert.value
            for cert in certificates
            if cert.status == CertificateStatus.ACTIVE
        )
    
    def validate_transaction(
        self,
        buyer: str,
        seller: str,
        value: float,
        transaction_id: str
    ) -> Result:
        """
        Validate and process a transaction using certificates.
        
        Args:
            buyer: Buyer ID
            seller: Seller ID
            value: Transaction value
            transaction_id: Transaction ID
            
        Returns:
            Result object with validation status and details
        """
        # Check if buyer has sufficient certificate value
        available_value = self.get_available_value(buyer)
        
        if available_value < value:
            return Result(
                success=False,
                error=f"Insufficient certificate value: {available_value} < {value}",
                details={
                    "available_value": available_value,
                    "required_value": value,
                    "buyer": buyer,
                    "seller": seller
                }
            )
        
        # Find certificates to use
        certificates_to_use = []
        remaining_value = value
        
        # Get active certificates for the buyer
        buyer_certificates = [
            cert for cert in self.get_certificates_by_owner(buyer)
            if cert.status == CertificateStatus.ACTIVE
        ]
        
        # Sort by expiry date (use certificates expiring soonest first)
        buyer_certificates.sort(
            key=lambda cert: datetime.datetime.fromisoformat(cert.expiry_date)
        )
        
        # Allocate certificates
        for cert in buyer_certificates:
            if remaining_value <= 0:
                break
            
            # Use all or part of this certificate
            use_amount = min(cert.value, remaining_value)
            certificates_to_use.append((cert.id, use_amount))
            remaining_value -= use_amount
        
        # If we couldn't cover the full value, return an error
        if remaining_value > 0:
            return Result(
                success=False,
                error=f"Could not allocate certificates for full value",
                details={
                    "allocated_value": value - remaining_value,
                    "remaining_value": remaining_value,
                    "buyer": buyer,
                    "seller": seller
                }
            )
        
        # Use the certificates
        used_certificates = []
        for cert_id, use_amount in certificates_to_use:
            if self.use_certificate(cert_id, use_amount, transaction_id):
                used_certificates.append({
                    "certificate_id": cert_id,
                    "amount": use_amount
                })
        
        return Result(
            success=True,
            value={
                "transaction_id": transaction_id,
                "buyer": buyer,
                "seller": seller,
                "value": value,
                "used_certificates": used_certificates
            }
        )
    
    def revoke_certificate(
        self,
        certificate_id: str,
        reason: str
    ) -> bool:
        """
        Revoke a certificate.
        
        Args:
            certificate_id: Certificate ID
            reason: Reason for revocation
            
        Returns:
            True if certificate was revoked successfully, False otherwise
        """
        # Check if certificate exists
        if certificate_id not in self.certificates:
            return False
        
        certificate = self.certificates[certificate_id]
        
        # Only active certificates can be revoked
        if certificate.status != CertificateStatus.ACTIVE:
            return False
        
        # Add revocation action to history
        certificate.history.append(
            CertificateAction(
                timestamp=datetime.datetime.now().isoformat(),
                action="revoked",
                value=certificate.value,
                details={"reason": reason}
            )
        )
        
        # Update status
        certificate.status = CertificateStatus.REVOKED
        
        # Update the certificate in storage
        self.certificates[certificate_id] = certificate
        
        return True
    
    def check_expired_certificates(self) -> List[str]:
        """
        Check for and mark expired certificates.
        
        Returns:
            List of expired certificate IDs
        """
        now = datetime.datetime.now()
        expired_certificates = []
        
        for cert_id, certificate in self.certificates.items():
            # Skip certificates that are already marked as expired or used or revoked
            if certificate.status != CertificateStatus.ACTIVE:
                continue
            
            # Check if expired
            expiry = datetime.datetime.fromisoformat(certificate.expiry_date)
            if now > expiry:
                # Mark as expired
                certificate.status = CertificateStatus.EXPIRED
                
                # Add expiration action to history
                certificate.history.append(
                    CertificateAction(
                        timestamp=now.isoformat(),
                        action="expired",
                        value=certificate.value
                    )
                )
                
                # Update the certificate in storage
                self.certificates[cert_id] = certificate
                
                expired_certificates.append(cert_id)
        
        return expired_certificates
    
    def generate_activity_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        owner: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an activity report for certificates.
        
        Args:
            start_date: Start date for the report (ISO format)
            end_date: End date for the report (ISO format)
            owner: Filter by owner
            
        Returns:
            Report data
        """
        # Parse dates if provided
        start_datetime = None
        if start_date:
            start_datetime = datetime.datetime.fromisoformat(start_date)
        
        end_datetime = None
        if end_date:
            end_datetime = datetime.datetime.fromisoformat(end_date)
        else:
            end_datetime = datetime.datetime.now()
        
        # Filter certificates by owner if provided
        certificates_to_check = []
        if owner:
            certificates_to_check = self.get_certificates_by_owner(owner)
        else:
            certificates_to_check = list(self.certificates.values())
        
        # Initialize report data
        report = {
            "period": {
                "start": start_date if start_date else "beginning",
                "end": end_date if end_date else end_datetime.isoformat()
            },
            "certificates": {
                "total": len(certificates_to_check),
                "active": 0,
                "used": 0,
                "expired": 0,
                "revoked": 0
            },
            "value": {
                "total_issued": 0.0,
                "total_used": 0.0,
                "total_available": 0.0,
                "total_expired": 0.0
            },
            "activity": {
                "issued": 0,
                "used": 0,
                "transferred": 0,
                "expired": 0,
                "revoked": 0
            }
        }
        
        # Process certificates
        for cert in certificates_to_check:
            # Count by status
            if cert.status == CertificateStatus.ACTIVE:
                report["certificates"]["active"] += 1
                report["value"]["total_available"] += cert.value
            elif cert.status == CertificateStatus.USED:
                report["certificates"]["used"] += 1
            elif cert.status == CertificateStatus.EXPIRED:
                report["certificates"]["expired"] += 1
                report["value"]["total_expired"] += cert.value
            elif cert.status == CertificateStatus.REVOKED:
                report["certificates"]["revoked"] += 1
            
            # Process history entries
            for entry in cert.history:
                entry_datetime = datetime.datetime.fromisoformat(entry.timestamp)
                
                # Skip entries outside the date range
                if start_datetime and entry_datetime < start_datetime:
                    continue
                if entry_datetime > end_datetime:
                    continue
                
                # Update activity counters
                if entry.action == "issued":
                    report["activity"]["issued"] += 1
                    report["value"]["total_issued"] += entry.value
                elif entry.action == "used":
                    report["activity"]["used"] += 1
                    report["value"]["total_used"] += entry.value
                elif entry.action == "transferred":
                    report["activity"]["transferred"] += 1
                elif entry.action == "expired":
                    report["activity"]["expired"] += 1
                elif entry.action == "revoked":
                    report["activity"]["revoked"] += 1
        
        return report


class ImportCertificateSystem:
    """
    High-level Import Certificate System that enforces trade balance
    by requiring imports to be matched with certificates.
    """
    
    def __init__(self):
        """Initialize the Import Certificate System."""
        self.certificate_manager = CertificateManager()
        self.trade_flows: Dict[str, Dict[str, float]] = {}  # country -> {partner -> value}
    
    def issue_export_certificates(
        self,
        exporter: str,
        importer: str,
        value: float,
        trade_date: Optional[str] = None
    ) -> Certificate:
        """
        Issue export certificates based on trade flows.
        
        Args:
            exporter: Exporting country or entity
            importer: Importing country or entity
            value: Export value
            trade_date: Date of trade (ISO format)
            
        Returns:
            Issued certificate
        """
        # Record trade flow
        if exporter not in self.trade_flows:
            self.trade_flows[exporter] = {}
        
        if importer not in self.trade_flows[exporter]:
            self.trade_flows[exporter][importer] = 0.0
        
        self.trade_flows[exporter][importer] += value
        
        # Issue certificate to exporter
        certificate = self.certificate_manager.issue_certificate(
            owner=exporter,
            value=value
        )
        
        return certificate
    
    def validate_import(
        self,
        importer: str,
        value: float
    ) -> bool:
        """
        Validate that an importer has sufficient certificates for an import.
        
        Args:
            importer: Importing entity
            value: Import value
            
        Returns:
            True if the import is valid, False otherwise
        """
        return self.certificate_manager.get_available_value(importer) >= value
    
    def process_import(
        self,
        importer: str,
        exporter: str,
        value: float,
        transaction_id: str
    ) -> Result:
        """
        Process an import by using certificates.
        
        Args:
            importer: Importing entity
            exporter: Exporting entity
            value: Import value
            transaction_id: Transaction ID
            
        Returns:
            Result object with processing status and details
        """
        # Validate and use certificates
        result = self.certificate_manager.validate_transaction(
            buyer=importer,
            seller=exporter,
            value=value,
            transaction_id=transaction_id
        )
        
        # Record trade flow if successful
        if result.success:
            if importer not in self.trade_flows:
                self.trade_flows[importer] = {}
            
            if exporter not in self.trade_flows[importer]:
                self.trade_flows[importer][exporter] = 0.0
            
            self.trade_flows[importer][exporter] += value
        
        return result
    
    def get_trade_balance(
        self,
        country_a: str,
        country_b: str
    ) -> float:
        """
        Calculate the trade balance between two countries.
        
        Args:
            country_a: First country
            country_b: Second country
            
        Returns:
            Trade balance from country_a's perspective (exports - imports)
        """
        # Get exports from A to B
        exports_a_to_b = 0.0
        if country_a in self.trade_flows and country_b in self.trade_flows[country_a]:
            exports_a_to_b = self.trade_flows[country_a][country_b]
        
        # Get imports from B to A
        imports_b_to_a = 0.0
        if country_b in self.trade_flows and country_a in self.trade_flows[country_b]:
            imports_b_to_a = self.trade_flows[country_b][country_a]
        
        # Calculate balance
        return exports_a_to_b - imports_b_to_a
    
    def get_certificate_statistics(
        self,
        owner: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get certificate statistics.
        
        Args:
            owner: Filter by owner
            
        Returns:
            Certificate statistics
        """
        return self.certificate_manager.generate_activity_report(owner=owner)
    
    def calculate_war_score(
        self,
        country_a: str,
        country_b: str
    ) -> float:
        """
        Calculate WAR score for trade relationship.
        
        Args:
            country_a: First country
            country_b: Second country
            
        Returns:
            WAR score (0-5 scale)
        """
        # Get total trade
        exports_a_to_b = 0.0
        if country_a in self.trade_flows and country_b in self.trade_flows[country_a]:
            exports_a_to_b = self.trade_flows[country_a][country_b]
        
        imports_b_to_a = 0.0
        if country_b in self.trade_flows and country_a in self.trade_flows[country_b]:
            imports_b_to_a = self.trade_flows[country_b][country_a]
        
        total_trade = exports_a_to_b + imports_b_to_a
        
        if total_trade == 0:
            return 2.5  # Neutral score if no trade
        
        # Calculate trade balance ratio
        trade_balance = exports_a_to_b - imports_b_to_a
        trade_balance_ratio = abs(trade_balance) / total_trade
        
        # Calculate WAR score components
        balance_score = 1.0 - trade_balance_ratio  # 0 (completely imbalanced) to 1 (perfectly balanced)
        
        # Scale to 0-5 range (2.5 is neutral)
        war_score = 2.5 + balance_score * 2.5
        
        return war_score