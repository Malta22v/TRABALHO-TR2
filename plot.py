import matplotlib
matplotlib.use('Agg')

import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_throughput():

    os.makedirs("graphs", exist_ok=True)

    df = pd.read_csv("logs/metrics.csv")

    plt.figure(figsize=(10, 5))

    plt.plot(df["segment"], df["throughput_kbps"])

    plt.xlabel("Segmento")
    plt.ylabel("Throughput (kbps)")
    plt.title("Throughput por Segmento")

    plt.grid(True)

    plt.savefig("graphs/throughput.png")