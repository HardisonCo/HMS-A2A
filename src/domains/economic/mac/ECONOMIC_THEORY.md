# Mathematical Foundations of the Market Network Economic Model

This document provides the formal mathematical foundations underlying the Market Network architecture implemented in the MAC system.

## 1. Market Network Utility Functions

### 1.1 Network Utility Maximization

The system aims to maximize total utility across all agents, subject to constraints:

$$\max_{x \in X} \sum_{i=1}^{N} U_i(x_i)$$

Where:
- $U_i(x_i)$ is the utility function for agent $i$
- $x_i$ is the resource allocation vector for agent $i$
- $X$ is the feasible set of allocations based on constraints

### 1.2 Agent Utility Function

Each agent's utility follows a modified Cobb-Douglas utility function with network effects:

$$U_i(x_i, G) = \prod_{j=1}^{R} x_{ij}^{\alpha_{ij}} \cdot N_i(G)^{\beta_i}$$

Where:
- $x_{ij}$ is the allocation of resource $j$ to agent $i$
- $\alpha_{ij}$ is the preference weight for resource $j$ by agent $i$
- $N_i(G)$ is the network effect function for agent $i$ in network $G$
- $\beta_i$ is the network effect sensitivity parameter for agent $i$

## 2. Market Clearing Mechanisms

### 2.1 Continuous Double Auction

The price discovery mechanism in a continuous double auction follows:

$$P_t = \frac{1}{2}(B_t + A_t)$$

Where:
- $P_t$ is the transaction price at time $t$
- $B_t$ is the highest bid price
- $A_t$ is the lowest ask price

For a transaction to occur:

$$B_t \geq A_t$$

### 2.2 Call Market Mechanism

In a call market, the clearing price $P^*$ is determined by solving:

$$\arg\min_{P} |D(P) - S(P)|$$

Where:
- $D(P)$ is the demand function at price $P$
- $S(P)$ is the supply function at price $P$

The quantity traded is:

$$Q^* = \min(D(P^*), S(P^*))$$

### 2.3 Market Maker

The market maker sets bid and ask prices with a spread:

$$P_{bid} = P_{ref} \cdot (1 - \delta/2)$$
$$P_{ask} = P_{ref} \cdot (1 + \delta/2)$$

Where:
- $P_{ref}$ is the reference price
- $\delta$ is the spread parameter

## 3. Network Effects Models

### 3.1 Direct Network Effects (Metcalfe's Law)

The value of a network with direct effects scales quadratically with the number of users:

$$V(n) = \gamma \cdot n^2$$

Where:
- $n$ is the number of network participants
- $\gamma$ is a scaling parameter

### 3.2 Odlyzko's Correction to Metcalfe's Law

A more conservative estimate of network value:

$$V(n) = \gamma \cdot n \log(n)$$

### 3.3 Local Network Effects

The value to an agent depends on their local neighborhood:

$$V_i(G) = \gamma \sum_{j \in N_i} w_{ij} \cdot v_j$$

Where:
- $N_i$ is the set of neighbors of agent $i$
- $w_{ij}$ is the edge weight between agents $i$ and $j$
- $v_j$ is the intrinsic value of agent $j$

### 3.4 Learning Network Effects

Knowledge accumulation follows:

$$K_i(t+1) = K_i(t) + \lambda_i \left( \frac{\sum_{j \in N_i} w_{ij} \cdot K_j(t)}{|N_i|} - K_i(t) \right)$$

Where:
- $K_i(t)$ is the knowledge level of agent $i$ at time $t$
- $\lambda_i$ is the learning rate of agent $i$

## 4. Import Certificate System

### 4.1 Certificate Price Determination

The price of import certificates follows:

$$P_{IC} = \alpha \cdot \frac{GDP}{Imports - Exports} + \beta$$

Where:
- $\alpha$ is a scaling parameter
- $\beta$ is a base price component
- $GDP$ is the total economic output of the system

### 4.2 Supply-Demand Dynamics

The price adjusts based on the ratio of supply to demand:

$$P_t = P_{t-1} \cdot e^{-\kappa (S_t/D_t - 1)}$$

Where:
- $S_t$ is the supply of certificates at time $t$
- $D_t$ is the demand for certificates at time $t$
- $\kappa$ is the price sensitivity parameter

### 4.3 Certificate Balance Effect on Trade

Trade balance is maintained through:

$$Imports \leq Exports$$

Since imports require certificates that must be earned through exports.

## 5. Deal Value Function (DVF)

### 5.1 General Form

The Deal Value Function calculates the total value of a deal:

$$DVF = \sum_{i=1}^{D} (V_i \cdot W_i \cdot P_i \cdot C_i \cdot M_i) - TC$$

Where:
- $V_i$ is the intrinsic value of dimension $i$
- $W_i$ is the weight of dimension $i$
- $P_i$ is the probability of success for dimension $i$
- $C_i$ is the confidence factor for dimension $i$
- $M_i$ is the margin of safety for dimension $i$
- $TC$ is the transaction cost
- $D$ is the number of value dimensions

### 5.2 Stakeholder-Specific DVF

Each stakeholder's individual DVF is:

$$DVF_s = \sum_{i=1}^{D} (V_{si} \cdot W_{si} \cdot P_{si} \cdot C_{si} \cdot M_{si}) - TC_s$$

Where:
- $V_{si}$ is the stakeholder's allocated returns in dimension $i$
- $W_{si}$ is the stakeholder's preference for dimension $i$
- $TC_s$ is the stakeholder's allocated costs

### 5.3 Win-Win Condition

A deal is win-win if all stakeholders have positive DVF:

$$\forall s \in S, DVF_s > 0$$

Where $S$ is the set of all stakeholders.

## 6. Knowledge Diffusion

### 6.1 Bass Diffusion Model

Knowledge adoption follows:

$$\frac{dA(t)}{dt} = (p + q \cdot \frac{A(t)}{N}) \cdot (N - A(t))$$

Where:
- $A(t)$ is the number of adopters at time $t$
- $N$ is the total population
- $p$ is the coefficient of innovation
- $q$ is the coefficient of imitation

### 6.2 Domain-Specific Knowledge Diffusion

For a specific knowledge domain $d$:

$$K_{id}(t+1) = K_{id}(t) + \lambda_i \cdot (1 - K_{id}(t)) \cdot \left( p_i + q_i \frac{\sum_{j \in N_i} w_{ij}K_{jd}(t)}{|N_i|} \right)$$

Where:
- $K_{id}(t)$ is agent $i$'s knowledge in domain $d$ at time $t$
- $p_i$ is agent $i$'s independent learning rate
- $q_i$ is agent $i$'s social learning rate

## 7. Resource Allocation Optimization

### 7.1 General Resource Allocation Problem

$$\max \sum_{i=1}^{N} \sum_{j=1}^{R} U_{ij}(x_{ij})$$

Subject to:

$$\sum_{i=1}^{N} x_{ij} \leq C_j, \forall j \in \{1,2,...,R\}$$
$$x_{ij} \geq 0, \forall i,j$$

Where:
- $x_{ij}$ is the allocation of resource $j$ to agent $i$
- $U_{ij}$ is the utility function for agent $i$ from resource $j$
- $C_j$ is the capacity constraint for resource $j$

### 7.2 Priority-Based Allocation

$$x_{ij} = \min\left(r_{ij}, C_j \cdot \frac{p_i \cdot r_{ij}}{\sum_{k=1}^{N} p_k \cdot r_{kj}}\right)$$

Where:
- $r_{ij}$ is the requested amount of resource $j$ by agent $i$
- $p_i$ is the priority score of agent $i$

### 7.3 Fair Share Allocation

$$x_{ij} = \min\left(r_{ij}, \frac{C_j}{N} - a_{ij}\right)$$

Where:
- $a_{ij}$ is the amount of resource $j$ already allocated to agent $i$

## 8. Economic Metrics

### 8.1 System Efficiency

$$E = \frac{\sum_{i=1}^{N} U_i(x_i)}{\max_{x' \in X} \sum_{i=1}^{N} U_i(x'_i)}$$

### 8.2 Fairness (Jain's Index)

$$F = \frac{(\sum_{i=1}^{N} U_i)^2}{N \cdot \sum_{i=1}^{N} U_i^2}$$

### 8.3 Gini Coefficient

$$G = \frac{\sum_{i=1}^{N} \sum_{j=1}^{N} |x_i - x_j|}{2N^2\bar{x}}$$

Where:
- $x_i$ is the allocation to agent $i$
- $\bar{x}$ is the mean allocation

## 9. Agent-Based Computational Economics (ACE)

### 9.1 Agent Decision Rule

Agent $i$ makes decisions by solving:

$$\max_{a_i \in A_i} E[U_i(a_i, a_{-i}, s)]$$

Where:
- $a_i$ is the action chosen by agent $i$
- $a_{-i}$ represents the actions of all other agents
- $s$ is the current state
- $A_i$ is the action space of agent $i$

### 9.2 Learning Dynamics

Agents update their strategy through reinforcement learning:

$$Q_i(s, a) \leftarrow (1 - \alpha) \cdot Q_i(s, a) + \alpha \cdot [r_i(s, a, s') + \gamma \cdot \max_{a'} Q_i(s', a')]$$

Where:
- $Q_i(s, a)$ is the expected utility of action $a$ in state $s$
- $\alpha$ is the learning rate
- $r_i(s, a, s')$ is the reward received
- $\gamma$ is the discount factor

### 9.3 Bounded Rationality

Due to bounded rationality, agents make decisions with noise:

$$P(a|s) = \frac{e^{Q(s,a)/\tau}}{\sum_{a' \in A} e^{Q(s,a')/\tau}}$$

Where:
- $\tau$ is the temperature parameter controlling the randomness

## 10. Transaction Network Analysis

### 10.1 Centrality Measures

#### 10.1.1 Degree Centrality

$$C_D(i) = \frac{d_i}{n-1}$$

Where:
- $d_i$ is the degree of node $i$
- $n$ is the number of nodes

#### 10.1.2 Eigenvector Centrality

$$C_E(i) = \frac{1}{\lambda} \sum_{j \in N_i} C_E(j)$$

Where:
- $\lambda$ is the largest eigenvalue of the adjacency matrix

### 10.2 Community Detection

The modularity of a partition is:

$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

Where:
- $A_{ij}$ is the adjacency matrix
- $k_i$ is the degree of node $i$
- $m$ is the total number of edges
- $c_i$ is the community of node $i$
- $\delta(c_i, c_j)$ is 1 if $c_i = c_j$ and 0 otherwise