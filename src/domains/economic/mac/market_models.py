"""
Market Models for Agent-Based Computational Economics (ACE).

This module provides specialized market models to enhance the ACE simulation capabilities
of the Economist Agent, implementing advanced market mechanisms based on the economic
principles defined in econ.data.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple, Set, Union, Protocol
import math
import random
import numpy as np
from collections import defaultdict, deque
from enum import Enum


class MarketType(Enum):
    """Types of markets in the economic model."""
    RESOURCE_MARKET = "resource_market"
    CERTIFICATE_MARKET = "certificate_market"
    TASK_MARKET = "task_market"
    KNOWLEDGE_MARKET = "knowledge_market"
    SERVICE_MARKET = "service_market"


class MarketMechanism(Enum):
    """Market clearing mechanisms."""
    AUCTION = "auction"
    CONTINUOUS_DOUBLE_AUCTION = "continuous_double_auction"
    DEALER = "dealer"
    CALL_MARKET = "call_market"
    NEGOTIATION = "negotiation"


class Order:
    """
    Market order for trading resources, certificates, or services.
    """
    
    def __init__(
        self, 
        order_id: str,
        agent_id: str,
        order_type: str,  # "buy" or "sell"
        market_type: MarketType,
        asset_type: str,
        quantity: float,
        price: float,
        time_in_force: int = -1  # -1 means good until canceled
    ):
        """
        Initialize a market order.
        
        Args:
            order_id: Unique identifier for this order
            agent_id: ID of agent placing the order
            order_type: "buy" or "sell"
            market_type: Type of market
            asset_type: Type of asset being traded
            quantity: Amount to buy/sell
            price: Price per unit
            time_in_force: How long the order is valid (-1 = good until canceled)
        """
        self.order_id = order_id
        self.agent_id = agent_id
        self.order_type = order_type
        self.market_type = market_type
        self.asset_type = asset_type
        self.quantity = quantity
        self.price = price
        self.time_in_force = time_in_force
        self.timestamp = 0  # Will be set when added to market
        self.status = "active"  # active, filled, partial, canceled
        self.filled_quantity = 0.0
        
    def __repr__(self):
        """String representation of the order."""
        return f"Order({self.order_id}, {self.agent_id}, {self.order_type}, {self.asset_type}, {self.quantity}, {self.price})"


class Transaction:
    """
    Record of a completed market transaction.
    """
    
    def __init__(
        self,
        transaction_id: str,
        buyer_id: str,
        seller_id: str,
        asset_type: str,
        quantity: float,
        price: float,
        buyer_order_id: Optional[str] = None,
        seller_order_id: Optional[str] = None
    ):
        """
        Initialize a transaction record.
        
        Args:
            transaction_id: Unique identifier for this transaction
            buyer_id: ID of buying agent
            seller_id: ID of selling agent
            asset_type: Type of asset traded
            quantity: Amount traded
            price: Price per unit
            buyer_order_id: ID of buyer's order
            seller_order_id: ID of seller's order
        """
        self.transaction_id = transaction_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.asset_type = asset_type
        self.quantity = quantity
        self.price = price
        self.buyer_order_id = buyer_order_id
        self.seller_order_id = seller_order_id
        self.timestamp = 0  # Will be set when recorded
        self.value = quantity * price
        
    def __repr__(self):
        """String representation of the transaction."""
        return f"Transaction({self.transaction_id}, {self.buyer_id}->{self.seller_id}, {self.asset_type}, {self.quantity}@{self.price})"


class Market:
    """
    Base market class for trading assets in the agent-based economy.
    """
    
    def __init__(
        self,
        market_id: str,
        market_type: MarketType,
        asset_type: str,
        mechanism: MarketMechanism,
        config: Dict[str, Any] = None
    ):
        """
        Initialize a market.
        
        Args:
            market_id: Unique identifier for this market
            market_type: Type of market
            asset_type: Type of asset traded in this market
            mechanism: Market clearing mechanism
            config: Additional configuration parameters
        """
        self.market_id = market_id
        self.market_type = market_type
        self.asset_type = asset_type
        self.mechanism = mechanism
        self.config = config or {}
        
        # Market state
        self.buy_orders = []
        self.sell_orders = []
        self.transaction_history = deque(maxlen=self.config.get("history_length", 100))
        self.price_history = deque(maxlen=self.config.get("history_length", 100))
        self.time_step = 0
        
        # Market statistics
        self.statistics = {
            "volume": 0.0,
            "value": 0.0,
            "last_price": None,
            "high_price": None,
            "low_price": None,
            "spread": None,
            "volatility": 0.0
        }
        
    def add_order(self, order: Order) -> bool:
        """
        Add an order to the market.
        
        Args:
            order: The order to add
            
        Returns:
            Whether the order was accepted
        """
        # Validate order
        if not self._validate_order(order):
            return False
        
        # Set timestamp
        order.timestamp = self.time_step
        
        # Add to appropriate order book
        if order.order_type == "buy":
            self.buy_orders.append(order)
            # Sort buy orders by price (highest first) and time (oldest first)
            self.buy_orders.sort(key=lambda o: (-o.price, o.timestamp))
        else:
            self.sell_orders.append(order)
            # Sort sell orders by price (lowest first) and time (oldest first)
            self.sell_orders.sort(key=lambda o: (o.price, o.timestamp))
        
        # Update statistics
        self._update_statistics()
        
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order in the market.
        
        Args:
            order_id: ID of order to cancel
            
        Returns:
            Whether the order was found and canceled
        """
        # Check buy orders
        for order in self.buy_orders:
            if order.order_id == order_id and order.status == "active":
                order.status = "canceled"
                return True
        
        # Check sell orders
        for order in self.sell_orders:
            if order.order_id == order_id and order.status == "active":
                order.status = "canceled"
                return True
        
        return False
    
    def match_orders(self) -> List[Transaction]:
        """
        Match compatible buy and sell orders to create transactions.
        
        Returns:
            List of completed transactions
        """
        transactions = []
        
        # Implementation depends on market mechanism
        if self.mechanism == MarketMechanism.CONTINUOUS_DOUBLE_AUCTION:
            transactions = self._match_continuous_double_auction()
        elif self.mechanism == MarketMechanism.CALL_MARKET:
            transactions = self._match_call_market()
        elif self.mechanism == MarketMechanism.AUCTION:
            transactions = self._match_auction()
        elif self.mechanism == MarketMechanism.DEALER:
            transactions = self._match_dealer()
        elif self.mechanism == MarketMechanism.NEGOTIATION:
            transactions = self._match_negotiation()
        
        # Update market statistics
        if transactions:
            self._update_statistics()
            
            # Set transaction timestamps
            for transaction in transactions:
                transaction.timestamp = self.time_step
            
            # Add to history
            self.transaction_history.extend(transactions)
        
        return transactions
    
    def get_market_data(self) -> Dict[str, Any]:
        """
        Get current market data.
        
        Returns:
            Dictionary of market data
        """
        # Get current best prices
        best_bid = max(self.buy_orders, key=lambda o: o.price).price if self.buy_orders else None
        best_ask = min(self.sell_orders, key=lambda o: o.price).price if self.sell_orders else None
        
        spread = best_ask - best_bid if (best_bid is not None and best_ask is not None) else None
        
        return {
            "market_id": self.market_id,
            "asset_type": self.asset_type,
            "time_step": self.time_step,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "order_book_depth": {
                "buy": len(self.buy_orders),
                "sell": len(self.sell_orders)
            },
            "volume": self.statistics["volume"],
            "last_price": self.statistics["last_price"],
            "price_change": self._calculate_price_change(),
            "volatility": self.statistics["volatility"]
        }
    
    def step(self) -> List[Transaction]:
        """
        Advance the market by one time step.
        
        Returns:
            Transactions completed in this step
        """
        # Increment time step
        self.time_step += 1
        
        # Expire orders
        self._expire_orders()
        
        # Match orders
        transactions = self.match_orders()
        
        # Update price history
        if self.statistics["last_price"] is not None:
            self.price_history.append((self.time_step, self.statistics["last_price"]))
        
        return transactions
    
    def _validate_order(self, order: Order) -> bool:
        """
        Validate an order before adding it to the market.
        
        Args:
            order: Order to validate
            
        Returns:
            Whether the order is valid
        """
        # Check order type
        if order.order_type not in ["buy", "sell"]:
            return False
        
        # Check quantity
        if order.quantity <= 0:
            return False
        
        # Check price
        if order.price <= 0:
            return False
        
        # Check market type
        if order.market_type != self.market_type:
            return False
        
        # Check asset type
        if order.asset_type != self.asset_type:
            return False
        
        return True
    
    def _expire_orders(self) -> None:
        """Remove expired orders from the order books."""
        # Filter buy orders
        self.buy_orders = [
            order for order in self.buy_orders 
            if order.status == "active" and (order.time_in_force == -1 or self.time_step - order.timestamp < order.time_in_force)
        ]
        
        # Filter sell orders
        self.sell_orders = [
            order for order in self.sell_orders 
            if order.status == "active" and (order.time_in_force == -1 or self.time_step - order.timestamp < order.time_in_force)
        ]
    
    def _update_statistics(self) -> None:
        """Update market statistics."""
        # Update spread
        best_bid = max(self.buy_orders, key=lambda o: o.price).price if self.buy_orders else None
        best_ask = min(self.sell_orders, key=lambda o: o.price).price if self.sell_orders else None
        
        self.statistics["spread"] = best_ask - best_bid if (best_bid is not None and best_ask is not None) else None
        
        # Update price stats based on transactions
        if self.transaction_history:
            last_transactions = list(self.transaction_history)[-10:]
            prices = [t.price for t in last_transactions]
            
            self.statistics["last_price"] = prices[-1]
            self.statistics["high_price"] = max(prices)
            self.statistics["low_price"] = min(prices)
            
            # Calculate volatility as standard deviation of price changes
            if len(prices) > 1:
                price_changes = [prices[i]/prices[i-1] - 1 for i in range(1, len(prices))]
                self.statistics["volatility"] = np.std(price_changes) if price_changes else 0.0
            
            # Update volume
            recent_volume = sum(t.quantity for t in last_transactions)
            self.statistics["volume"] = recent_volume
            
            # Update value
            recent_value = sum(t.value for t in last_transactions)
            self.statistics["value"] = recent_value
    
    def _calculate_price_change(self) -> Optional[float]:
        """
        Calculate recent price change.
        
        Returns:
            Percentage price change or None if not enough data
        """
        if len(self.price_history) < 2:
            return None
        
        current_price = self.price_history[-1][1]
        previous_price = self.price_history[-2][1]
        
        if previous_price == 0:
            return None
        
        return (current_price / previous_price) - 1
    
    def _match_continuous_double_auction(self) -> List[Transaction]:
        """
        Match orders using continuous double auction mechanism.
        
        Returns:
            List of transactions
        """
        transactions = []
        
        # Keep matching until no more matches are possible
        while True:
            # Get highest bid and lowest ask
            active_bids = [o for o in self.buy_orders if o.status == "active"]
            active_asks = [o for o in self.sell_orders if o.status == "active"]
            
            if not active_bids or not active_asks:
                break
                
            highest_bid = max(active_bids, key=lambda o: o.price)
            lowest_ask = min(active_asks, key=lambda o: o.price)
            
            # Check if orders can be matched
            if highest_bid.price >= lowest_ask.price:
                # Determine quantity and price
                quantity = min(highest_bid.quantity - highest_bid.filled_quantity,
                              lowest_ask.quantity - lowest_ask.filled_quantity)
                
                # Use midpoint pricing
                price = (highest_bid.price + lowest_ask.price) / 2
                
                # Create transaction
                transaction = Transaction(
                    transaction_id=f"tx_{self.market_id}_{self.time_step}_{len(transactions)}",
                    buyer_id=highest_bid.agent_id,
                    seller_id=lowest_ask.agent_id,
                    asset_type=self.asset_type,
                    quantity=quantity,
                    price=price,
                    buyer_order_id=highest_bid.order_id,
                    seller_order_id=lowest_ask.order_id
                )
                
                # Update order status
                highest_bid.filled_quantity += quantity
                lowest_ask.filled_quantity += quantity
                
                if highest_bid.filled_quantity >= highest_bid.quantity:
                    highest_bid.status = "filled"
                else:
                    highest_bid.status = "partial"
                    
                if lowest_ask.filled_quantity >= lowest_ask.quantity:
                    lowest_ask.status = "filled"
                else:
                    lowest_ask.status = "partial"
                
                # Add transaction
                transactions.append(transaction)
            else:
                # No more matches possible
                break
        
        # Clean up order books
        self.buy_orders = [o for o in self.buy_orders if o.status in ["active", "partial"]]
        self.sell_orders = [o for o in self.sell_orders if o.status in ["active", "partial"]]
        
        return transactions
    
    def _match_call_market(self) -> List[Transaction]:
        """
        Match orders using call market mechanism (single clearing price).
        
        Returns:
            List of transactions
        """
        transactions = []
        
        # Only execute if we have both buy and sell orders
        if not self.buy_orders or not self.sell_orders:
            return transactions
        
        active_bids = [o for o in self.buy_orders if o.status == "active"]
        active_asks = [o for o in self.sell_orders if o.status == "active"]
        
        # Sort by price
        sorted_bids = sorted(active_bids, key=lambda o: -o.price)
        sorted_asks = sorted(active_asks, key=lambda o: o.price)
        
        # Find clearing price and quantity
        supply_curve = []
        demand_curve = []
        
        # Build supply curve
        cumulative_quantity = 0.0
        for ask in sorted_asks:
            cumulative_quantity += ask.quantity
            supply_curve.append((ask.price, cumulative_quantity))
        
        # Build demand curve
        cumulative_quantity = 0.0
        for bid in sorted_bids:
            cumulative_quantity += bid.quantity
            demand_curve.append((bid.price, cumulative_quantity))
        
        # Find intersection
        clearing_price = None
        clearing_quantity = 0.0
        
        for i, (bid_price, bid_quantity) in enumerate(demand_curve):
            for j, (ask_price, ask_quantity) in enumerate(supply_curve):
                if bid_price >= ask_price:
                    # Potential clearing point
                    max_quantity = min(bid_quantity, ask_quantity)
                    
                    if max_quantity > clearing_quantity:
                        clearing_quantity = max_quantity
                        # Use midpoint price as clearing price
                        clearing_price = (bid_price + ask_price) / 2
        
        # Execute transactions at clearing price
        if clearing_price is not None and clearing_quantity > 0:
            remaining_quantity = clearing_quantity
            bid_index = 0
            
            # Match bids starting from highest price
            while remaining_quantity > 0 and bid_index < len(sorted_bids):
                bid = sorted_bids[bid_index]
                
                # Find matching asks
                ask_index = 0
                bid_quantity = bid.quantity - bid.filled_quantity
                bid_quantity = min(bid_quantity, remaining_quantity)
                
                while bid_quantity > 0 and ask_index < len(sorted_asks):
                    ask = sorted_asks[ask_index]
                    
                    if bid.price >= ask.price:
                        ask_quantity = ask.quantity - ask.filled_quantity
                        match_quantity = min(bid_quantity, ask_quantity)
                        
                        if match_quantity > 0:
                            # Create transaction
                            transaction = Transaction(
                                transaction_id=f"tx_{self.market_id}_{self.time_step}_{len(transactions)}",
                                buyer_id=bid.agent_id,
                                seller_id=ask.agent_id,
                                asset_type=self.asset_type,
                                quantity=match_quantity,
                                price=clearing_price,
                                buyer_order_id=bid.order_id,
                                seller_order_id=ask.order_id
                            )
                            
                            # Update order status
                            bid.filled_quantity += match_quantity
                            ask.filled_quantity += match_quantity
                            
                            if bid.filled_quantity >= bid.quantity:
                                bid.status = "filled"
                            else:
                                bid.status = "partial"
                                
                            if ask.filled_quantity >= ask.quantity:
                                ask.status = "filled"
                            else:
                                ask.status = "partial"
                            
                            # Update remaining quantities
                            bid_quantity -= match_quantity
                            remaining_quantity -= match_quantity
                            
                            # Add transaction
                            transactions.append(transaction)
                    
                    ask_index += 1
                
                bid_index += 1
        
        # Clean up order books
        self.buy_orders = [o for o in self.buy_orders if o.status in ["active", "partial"]]
        self.sell_orders = [o for o in self.sell_orders if o.status in ["active", "partial"]]
        
        return transactions
    
    def _match_auction(self) -> List[Transaction]:
        """
        Match orders using simple auction mechanism.
        
        Returns:
            List of transactions
        """
        # This is a simplified version where highest bidder gets priority
        return self._match_continuous_double_auction()
    
    def _match_dealer(self) -> List[Transaction]:
        """
        Match orders using dealer mechanism (market maker).
        
        Returns:
            List of transactions
        """
        transactions = []
        
        # In a dealer market, a market maker provides liquidity
        # For simplicity, we'll simulate a simple market maker strategy
        if not self.buy_orders and not self.sell_orders:
            return transactions
            
        # Determine dealer's bid and ask prices
        last_price = self.statistics["last_price"]
        if last_price is None:
            if self.buy_orders:
                highest_bid = max(self.buy_orders, key=lambda o: o.price)
                last_price = highest_bid.price
            elif self.sell_orders:
                lowest_ask = min(self.sell_orders, key=lambda o: o.price)
                last_price = lowest_ask.price
            else:
                last_price = 100.0  # Default starting price
        
        # Dealer's spread (configured or default)
        dealer_spread = self.config.get("dealer_spread", 0.05)
        
        # Calculate dealer bid and ask
        dealer_bid = last_price * (1 - dealer_spread/2)
        dealer_ask = last_price * (1 + dealer_spread/2)
        
        # Match sell orders against dealer bid
        for sell_order in [o for o in self.sell_orders if o.status == "active"]:
            if sell_order.price <= dealer_bid:
                # Create transaction
                transaction = Transaction(
                    transaction_id=f"tx_{self.market_id}_{self.time_step}_{len(transactions)}",
                    buyer_id="dealer",
                    seller_id=sell_order.agent_id,
                    asset_type=self.asset_type,
                    quantity=sell_order.quantity,
                    price=dealer_bid,
                    buyer_order_id=None,
                    seller_order_id=sell_order.order_id
                )
                
                # Update order status
                sell_order.filled_quantity = sell_order.quantity
                sell_order.status = "filled"
                
                # Add transaction
                transactions.append(transaction)
        
        # Match buy orders against dealer ask
        for buy_order in [o for o in self.buy_orders if o.status == "active"]:
            if buy_order.price >= dealer_ask:
                # Create transaction
                transaction = Transaction(
                    transaction_id=f"tx_{self.market_id}_{self.time_step}_{len(transactions)}",
                    buyer_id=buy_order.agent_id,
                    seller_id="dealer",
                    asset_type=self.asset_type,
                    quantity=buy_order.quantity,
                    price=dealer_ask,
                    buyer_order_id=buy_order.order_id,
                    seller_order_id=None
                )
                
                # Update order status
                buy_order.filled_quantity = buy_order.quantity
                buy_order.status = "filled"
                
                # Add transaction
                transactions.append(transaction)
        
        # Clean up order books
        self.buy_orders = [o for o in self.buy_orders if o.status in ["active", "partial"]]
        self.sell_orders = [o for o in self.sell_orders if o.status in ["active", "partial"]]
        
        return transactions
    
    def _match_negotiation(self) -> List[Transaction]:
        """
        Match orders using negotiation mechanism.
        
        Returns:
            List of transactions
        """
        # Negotiation markets typically involve bilateral bargaining
        # Here we'll implement a simple bargaining process
        transactions = []
        
        # Only proceed if we have both buy and sell orders
        if not self.buy_orders or not self.sell_orders:
            return transactions
        
        # For each buyer, find potential sellers
        for buy_order in [o for o in self.buy_orders if o.status == "active"]:
            # Find all compatible sellers
            compatible_sellers = [
                o for o in self.sell_orders 
                if o.status == "active" and o.asset_type == buy_order.asset_type
            ]
            
            if not compatible_sellers:
                continue
                
            # Sort by price (lowest first)
            compatible_sellers.sort(key=lambda o: o.price)
            
            # Negotiate with each seller
            for sell_order in compatible_sellers:
                # Calculate bargaining range
                max_price = buy_order.price
                min_price = sell_order.price
                
                if max_price < min_price:
                    # No bargaining range
                    continue
                
                # Simple bargaining model: price converges to midpoint
                bargaining_steps = min(3, self.config.get("bargaining_steps", 3))
                
                buyer_concession_rate = random.uniform(0.3, 0.7)
                seller_concession_rate = random.uniform(0.3, 0.7)
                
                buyer_price = max_price
                seller_price = min_price
                
                # Simulate bargaining process
                for _ in range(bargaining_steps):
                    # Buyer and seller both make concessions
                    price_gap = buyer_price - seller_price
                    buyer_price -= price_gap * buyer_concession_rate
                    seller_price += price_gap * seller_concession_rate
                    
                    # Check if prices have converged
                    if abs(buyer_price - seller_price) < 0.01:
                        break
                
                # Final negotiated price
                final_price = (buyer_price + seller_price) / 2
                
                # Check if both parties accept the final price
                if final_price <= max_price and final_price >= min_price:
                    # Determine quantity
                    quantity = min(buy_order.quantity - buy_order.filled_quantity,
                                  sell_order.quantity - sell_order.filled_quantity)
                    
                    if quantity > 0:
                        # Create transaction
                        transaction = Transaction(
                            transaction_id=f"tx_{self.market_id}_{self.time_step}_{len(transactions)}",
                            buyer_id=buy_order.agent_id,
                            seller_id=sell_order.agent_id,
                            asset_type=self.asset_type,
                            quantity=quantity,
                            price=final_price,
                            buyer_order_id=buy_order.order_id,
                            seller_order_id=sell_order.order_id
                        )
                        
                        # Update order status
                        buy_order.filled_quantity += quantity
                        sell_order.filled_quantity += quantity
                        
                        if buy_order.filled_quantity >= buy_order.quantity:
                            buy_order.status = "filled"
                        else:
                            buy_order.status = "partial"
                            
                        if sell_order.filled_quantity >= sell_order.quantity:
                            sell_order.status = "filled"
                        else:
                            sell_order.status = "partial"
                        
                        # Add transaction
                        transactions.append(transaction)
                        
                        # If buyer's order is filled, break out of seller loop
                        if buy_order.status == "filled":
                            break
        
        # Clean up order books
        self.buy_orders = [o for o in self.buy_orders if o.status in ["active", "partial"]]
        self.sell_orders = [o for o in self.sell_orders if o.status in ["active", "partial"]]
        
        return transactions


class NetworkEffect:
    """
    Models network effects in the agent-based economy.
    """
    
    def __init__(
        self,
        effect_id: str,
        effect_type: str,
        strength: float,
        affected_resources: List[str],
        config: Dict[str, Any] = None
    ):
        """
        Initialize a network effect.
        
        Args:
            effect_id: Unique identifier for this effect
            effect_type: Type of network effect (e.g., "adoption", "productivity")
            strength: Strength of the effect [0, 1]
            affected_resources: Resources affected by this network effect
            config: Additional configuration parameters
        """
        self.effect_id = effect_id
        self.effect_type = effect_type
        self.strength = strength
        self.affected_resources = affected_resources
        self.config = config or {}
        
        # Network state
        self.adopters = set()
        self.activation_threshold = self.config.get("activation_threshold", 0.2)
        self.is_active = False
        self.influence_matrix = {}
        
    def add_adopter(self, agent_id: str) -> None:
        """
        Add an agent as an adopter of this network.
        
        Args:
            agent_id: ID of the adopting agent
        """
        self.adopters.add(agent_id)
        
    def remove_adopter(self, agent_id: str) -> None:
        """
        Remove an agent from adopters.
        
        Args:
            agent_id: ID of the agent to remove
        """
        if agent_id in self.adopters:
            self.adopters.remove(agent_id)
    
    def set_influence(self, agent_id: str, influence: float) -> None:
        """
        Set the influence level of an agent in this network.
        
        Args:
            agent_id: ID of the agent
            influence: Influence level [0, 1]
        """
        self.influence_matrix[agent_id] = max(0.0, min(1.0, influence))
    
    def calculate_network_value(self, total_agents: int) -> float:
        """
        Calculate the value of the network based on adoption rate.
        
        Args:
            total_agents: Total number of agents in the system
            
        Returns:
            Network value
        """
        if total_agents == 0:
            return 0.0
            
        # Calculate adoption rate
        adoption_rate = len(self.adopters) / total_agents
        
        # Check if network effect is active
        self.is_active = adoption_rate >= self.activation_threshold
        
        if not self.is_active:
            return 0.0
        
        # Calculate network value using a generalized Metcalfe's Law
        # V(n) = n^β where β is between 1 and 2
        beta = self.config.get("metcalfe_exponent", 1.8)
        network_size = len(self.adopters)
        
        # Basic network value
        basic_value = network_size ** beta
        
        # Adjust for influence if available
        if self.influence_matrix:
            total_influence = sum(self.influence_matrix.values())
            influence_multiplier = 1.0 + (total_influence / len(self.influence_matrix)) * 0.5
            return basic_value * influence_multiplier
        
        return basic_value
    
    def apply_network_effect(self, resource_values: Dict[str, float]) -> Dict[str, float]:
        """
        Apply network effects to resource values.
        
        Args:
            resource_values: Current resource values
            
        Returns:
            Modified resource values
        """
        if not self.is_active:
            return resource_values.copy()
        
        result = resource_values.copy()
        
        for resource in self.affected_resources:
            if resource in result:
                # Apply network effect multiplier
                effect_multiplier = 1.0 + (self.strength * self.config.get("effect_multiplier", 0.2))
                result[resource] = result[resource] * effect_multiplier
        
        return result


class ImportCertificateSystem:
    """
    Implementation of the Import Certificate system proposed by Warren Buffett.
    
    This system creates a market-based mechanism for balancing trade by requiring
    importers to purchase certificates from exporters, with the certificate value
    equal to the export value.
    """
    
    def __init__(
        self,
        initial_price: float = 1.0,
        certificate_duration: int = 100,  # Time steps before expiration
        config: Dict[str, Any] = None
    ):
        """
        Initialize the Import Certificate system.
        
        Args:
            initial_price: Initial price of certificates
            certificate_duration: How long certificates are valid before expiring
            config: Additional configuration parameters
        """
        self.config = config or {}
        self.certificate_market = Market(
            market_id="import_certificates",
            market_type=MarketType.CERTIFICATE_MARKET,
            asset_type="import_certificate",
            mechanism=MarketMechanism.CONTINUOUS_DOUBLE_AUCTION
        )
        
        # Certificate state
        self.issued_certificates = {}
        self.expired_certificates = {}
        self.used_certificates = {}
        self.current_price = initial_price
        self.certificate_duration = certificate_duration
        self.time_step = 0
        
        # Trade balance tracking
        self.exports = defaultdict(float)
        self.imports = defaultdict(float)
        self.trade_balance = 0.0
        
    def issue_certificate(self, agent_id: str, export_value: float) -> Dict[str, Any]:
        """
        Issue a certificate to an exporter.
        
        Args:
            agent_id: ID of the exporting agent
            export_value: Value of the export
            
        Returns:
            Certificate information
        """
        certificate_id = f"IC_{self.time_step}_{agent_id}_{len(self.issued_certificates)}"
        
        # Create certificate
        certificate = {
            "certificate_id": certificate_id,
            "agent_id": agent_id,
            "value": export_value,
            "issued_at": self.time_step,
            "expires_at": self.time_step + self.certificate_duration,
            "status": "active",
            "current_owner": agent_id
        }
        
        # Store certificate
        self.issued_certificates[certificate_id] = certificate
        
        # Update export tracking
        self.exports[agent_id] += export_value
        self.trade_balance += export_value
        
        return certificate
    
    def validate_import(self, agent_id: str, import_value: float) -> bool:
        """
        Validate if an agent has sufficient certificates for an import.
        
        Args:
            agent_id: ID of the importing agent
            import_value: Value of the import
            
        Returns:
            Whether the agent has sufficient certificates
        """
        # Find active certificates owned by this agent
        agent_certificates = self._get_agent_certificates(agent_id)
        
        # Calculate total certificate value
        total_value = sum(cert["value"] for cert in agent_certificates)
        
        # Check if sufficient
        return total_value >= import_value
    
    def use_certificates(self, agent_id: str, import_value: float) -> Dict[str, Any]:
        """
        Use certificates for an import.
        
        Args:
            agent_id: ID of the importing agent
            import_value: Value of the import
            
        Returns:
            Result of certificate usage
        """
        # Check if agent has sufficient certificates
        if not self.validate_import(agent_id, import_value):
            return {
                "success": False,
                "message": "Insufficient certificate value for import",
                "available_value": sum(cert["value"] for cert in self._get_agent_certificates(agent_id)),
                "required_value": import_value
            }
        
        # Get agent's certificates
        agent_certificates = self._get_agent_certificates(agent_id)
        
        # Sort by expiration date (use oldest first)
        agent_certificates.sort(key=lambda c: c["expires_at"])
        
        remaining_value = import_value
        used_certificates = []
        
        for cert in agent_certificates:
            if remaining_value <= 0:
                break
                
            if cert["value"] <= remaining_value:
                # Use entire certificate
                cert["status"] = "used"
                self.used_certificates[cert["certificate_id"]] = cert
                used_certificates.append(cert["certificate_id"])
                remaining_value -= cert["value"]
            else:
                # Split certificate
                new_cert_id = f"IC_{self.time_step}_{agent_id}_split_{len(self.issued_certificates)}"
                
                # Create new certificate with remaining value
                new_cert = cert.copy()
                new_cert["certificate_id"] = new_cert_id
                new_cert["value"] = cert["value"] - remaining_value
                
                # Update original certificate
                cert["value"] = remaining_value
                cert["status"] = "used"
                
                # Store certificates
                self.used_certificates[cert["certificate_id"]] = cert
                self.issued_certificates[new_cert_id] = new_cert
                used_certificates.append(cert["certificate_id"])
                
                remaining_value = 0
        
        # Update import tracking
        self.imports[agent_id] += import_value
        self.trade_balance -= import_value
        
        return {
            "success": True,
            "message": "Certificates used successfully",
            "used_value": import_value,
            "used_certificates": used_certificates
        }
    
    def transfer_certificate(self, certificate_id: str, from_agent: str, to_agent: str) -> Dict[str, Any]:
        """
        Transfer a certificate between agents.
        
        Args:
            certificate_id: ID of certificate to transfer
            from_agent: Current owner
            to_agent: New owner
            
        Returns:
            Result of transfer operation
        """
        # Check if certificate exists and is active
        if certificate_id not in self.issued_certificates:
            return {
                "success": False,
                "message": f"Certificate {certificate_id} not found"
            }
            
        cert = self.issued_certificates[certificate_id]
        
        if cert["status"] != "active":
            return {
                "success": False,
                "message": f"Certificate {certificate_id} is not active"
            }
            
        if cert["current_owner"] != from_agent:
            return {
                "success": False,
                "message": f"Certificate {certificate_id} is not owned by {from_agent}"
            }
            
        # Transfer certificate
        cert["current_owner"] = to_agent
        
        return {
            "success": True,
            "message": f"Certificate {certificate_id} transferred from {from_agent} to {to_agent}",
            "certificate": cert
        }
    
    def step(self) -> Dict[str, Any]:
        """
        Advance the certificate system by one time step.
        
        Returns:
            Status of the certificate system
        """
        self.time_step += 1
        
        # Expire certificates
        self._expire_certificates()
        
        # Update certificate market
        market_transactions = self.certificate_market.step()
        
        # Process market transactions
        for tx in market_transactions:
            # Find certificate(s) to transfer
            if tx.asset_type == "import_certificate":
                # Transfer certificate ownership based on market transaction
                pass  # Implementation would depend on how certificates are tracked in the market
        
        # Calculate current certificate price
        if market_transactions:
            self.current_price = market_transactions[-1].price
        
        return {
            "time_step": self.time_step,
            "active_certificates": sum(1 for cert in self.issued_certificates.values() if cert["status"] == "active"),
            "total_certificate_value": sum(cert["value"] for cert in self.issued_certificates.values() if cert["status"] == "active"),
            "current_price": self.current_price,
            "trade_balance": self.trade_balance,
            "market_transactions": len(market_transactions)
        }
    
    def get_system_state(self) -> Dict[str, Any]:
        """
        Get current state of the certificate system.
        
        Returns:
            Certificate system state
        """
        return {
            "time_step": self.time_step,
            "certificates": {
                "active": sum(1 for cert in self.issued_certificates.values() if cert["status"] == "active"),
                "used": len(self.used_certificates),
                "expired": len(self.expired_certificates),
                "total_issued": len(self.issued_certificates)
            },
            "certificate_value": {
                "active": sum(cert["value"] for cert in self.issued_certificates.values() if cert["status"] == "active"),
                "used": sum(cert["value"] for cert in self.used_certificates.values()),
                "expired": sum(cert["value"] for cert in self.expired_certificates.values())
            },
            "market": self.certificate_market.get_market_data(),
            "trade_balance": self.trade_balance,
            "current_price": self.current_price,
            "exports": dict(self.exports),
            "imports": dict(self.imports)
        }
    
    def _get_agent_certificates(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all active certificates owned by an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of certificates
        """
        return [
            cert for cert in self.issued_certificates.values()
            if cert["current_owner"] == agent_id and cert["status"] == "active"
        ]
    
    def _expire_certificates(self) -> None:
        """Expire certificates that have reached their expiration date."""
        for cert_id, cert in list(self.issued_certificates.items()):
            if cert["status"] == "active" and cert["expires_at"] <= self.time_step:
                # Expire certificate
                cert["status"] = "expired"
                self.expired_certificates[cert_id] = cert
"""