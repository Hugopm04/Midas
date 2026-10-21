# Midas

A crypto-trading agent I wrote in 2022, the summer before starting university, to teach myself reinforcement
learning and neural networks. It never traded real money: it reads live prices and trades in simulation.

> **Written by me, by hand, without AI tools.** It is a lab notebook rather than a product: each `Midas 0.x.py` is a
> complete snapshot of one step, and `Historial de Versiones.txt` is the changelog. Code, comments and changelog are
> in Spanish.

## How it evolved

| Version | Step |
|---|---|
| 0.0–0.1 | Read the price of Bitcoin, then of any cryptocurrency, from Binance's public ticker API |
| 0.2–0.4 | Plot the price, first after the fact and then live, with a second subplot for its rate of change |
| 0.5 | **Tabular Q-learning** with an ε-greedy policy. The state is the price derivative, its mean and the price variance. The agent is punished for losing money and also for not making it, so that it does not learn to stay idle. The Q-table is saved to `.npy` |
| 0.6 | Separate buy and sell positions: one has to be closed before another is opened. The agent also sees the profit or loss of its open position |
| 0.7 | Loads saved Q-tables; fixes a bug that made the derivative drift downwards forever; rewards or punishes holding depending on whether the position is winning |
| 0.8 | Restart with a **feed-forward neural network written from scratch in NumPy** (sigmoid activations, backpropagation), trained on datasets built from live prices: the price, its rate of change and the rate of change of that |
| 0.9 | Networks with any number of layers, and a generational loop that keeps the best networks. Left unfinished |

## Running it

```sh
pip install requests numpy matplotlib scipy
python "Midas 0.7.py"   # or any other version
```

The scripts call Binance's public price endpoint, so they need an internet connection. The datasets, trained networks
and Q-tables (hundreds of `.npy` files) are not included; versions 0.8 and 0.9 regenerate them with their own
functions.
