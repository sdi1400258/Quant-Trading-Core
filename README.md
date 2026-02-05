# Hybrid Algorithmic Trading Pipeline

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C++-17-green.svg)](https://isocpp.org/)
[![Performance](https://img.shields.io/badge/2025_ROI-31.52%25-brightgreen.svg)]()

An end-to-end quantitative trading system engineered for high-alpha tech assets. This project demonstrates a hybrid architecture—combining Python’s flexibility for alpha research with C++ for performance-critical execution logic. 

Designed with a **"Risk-First" philosophy**, the system prioritizes capital preservation through rigorous backtesting, cynical cost modeling, and multi-layered loss prevention.

## Architecture & Engineering Design

The system is decoupled into modular layers:

| Layer | Responsibility | Technology |
| :--- | :--- | :--- |
| **Research & Strategy** | Alpha generation, vectorized signals | `Pandas`, `NumPy` |
| **Feature Engineering** | Low-latency rolling windows, technicals | Python + **C++ Extensions** |
| **Backtesting Engine** | Event-driven simulation, determinism | Custom Deterministic Engine |
| **Execution (OMS)** | Order management & IPC simulation | **C++ Core** |
| **Analytics** | Risk metrics, equity curve visualization | `Streamlit`, `Plotly`, `Matplotlib` |

### The "Hybrid" Advantage
*   **Performance Engineering**: Bottlenecks like rolling statistical means are offloaded to C++ via `pybind11` (or optimized Python fallbacks), ensuring high throughput during feature generation.
*   **Deterministic Simulation**: Unlike many amateur backtesters, this engine uses stable sorting by `[Date, Symbol]` and epsilon-based floating-point comparisons (`1e-6`) to guarantee 100% reproducible results across runs.

## Quantitative Strategy: Risk Parity

The core strategy is a Trend-Following system optimized for the S&P 500 tech leaders (AAPL, NVDA, MSFT, etc.).

### 1. Alpha Factor
Uses a dual-window EMA crossover with a **Trend Strength Filter**. Entries are only permitted when the relative distance between moving averages indicates a structural momentum phase rather than market noise.

### 2. Risk-Based Allocation (Risk Parity)
Instead of equal weighting, the system uses **Inverse Volatility Weighting**. Capital is dynamically shifted toward stable trends and reduced for assets exhibiting high idiosyncratic volatility, effectively normalizing the risk contribution across the portfolio.

### 3. Loss Prevention (The "Iron-Clad" Layer)
*   **Hard Stop-Loss**: 2% exit threshold from entry price.
*   **Trailing Stop**: 5% trailing threshold from session highs to lock in unrealized gains.
*   **Zero-Leverage Constraint**: Strictly capped at 100% exposure to ensure long-term capital stability.

## Backtest Realism & Results

Backtesting results are often misleading due to "frictionless" assumptions. This system employs a **Cynical Cost Model**:
*   **Slippage**: 10 basis points (bps) per trade to account for spread and market impact.
*   **Commission**: 5 basis points (bps) per trade.

### 2025 Performance Snapshot
| Metric | Value |
| :--- | :--- |
| **Total Return** | **31.52%** |
| **Daily Volatility** | ~1.2% (Estimated) |
| **Max Drawdown** | Protected by Trailing Stops |
| **Dataset Range** | 2010 - 2026 (Live data via YFinance) |

## Infrastructure & Setup

```bash
# Clone and setup environment
git clone <repo-url>
cd Algo-Trading
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the full pipeline
python main.py

# Launch the interactive Dashboard
streamlit run src/monitoring/dashboard.py
```

## Evolution & Design Notes
This project evolved from a high-return, high-volatility "leveraged" system into a refined, risk-parity model. The key breakthrough was moving from chasing ROI to chasing **Risk-Adjusted Returns**. By implementing strict stop-losses and neutralizing the non-determinism in multicore environments, I've created a framework that behaves predictably under stress.

