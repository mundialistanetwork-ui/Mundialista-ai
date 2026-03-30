"""
Task 12: Matplotlib Fundamentals
=================================
"""
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# ── PART A: Bar chart of goals scored ──────────────────────────
matches = ["vs HON", "vs MEX", "vs CRC", "vs PAN",
           "vs CAN", "vs TRI", "vs SLV"]
goals = [1, 0, 2, 1, 0, 3, 2]

fig, ax = plt.subplots(figsize=(10, 4))
colors = ["green" if g > 0 else "red" for g in goals]
ax.bar(matches, goals, color=colors)
ax.set_xlabel("Match")
ax.set_ylabel("Goals Scored")
ax.set_title("Jamaica — Goals Scored in Last 7 Matches")
plt.tight_layout()
plt.savefig("task12_bar_chart.png", dpi=150)
plt.show()

# ── PART B: Line chart — cumulative goals ──────────────────────
cumulative = np.cumsum(goals)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(matches, cumulative, marker="o", color="blue", linewidth=2)
ax.axhline(y=sum(goals)/7, color="red", linestyle="--", label=f"Average ({sum(goals)/7:.1f})")
ax.set_xlabel("Match")
ax.set_ylabel("Cumulative Goals")
ax.set_title("Jamaica — Cumulative Goals Over Last 7 Matches")
ax.legend()
plt.tight_layout()
plt.savefig("task12_line_chart.png", dpi=150)
plt.show()

# ── PART C: Histogram ──────────────────────────────────────────
rng = np.random.default_rng(42)
samples = rng.poisson(1.3, size=10000)

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(samples, bins=np.arange(-0.5, samples.max()+1.5, 1), 
        edgecolor="black", color="skyblue")
ax.axvline(x=samples.mean(), color="red", linestyle="--", 
           label=f"Mean ({samples.mean():.2f})")
ax.set_xlabel("Goals")
ax.set_ylabel("Frequency")
ax.set_title("Distribution of Goals (λ=1.3, 10000 samples)")
ax.legend()
plt.tight_layout()
plt.savefig("task12_histogram.png", dpi=150)
plt.show()

# ── PART D: Subplots ───────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Bar chart
colors = ["green" if g > 0 else "red" for g in goals]
axes[0].bar(matches, goals, color=colors)
axes[0].set_title("Goals Scored")
axes[0].tick_params(axis='x', rotation=45)

# Line chart
axes[1].plot(matches, cumulative, marker="o", color="blue")
axes[1].axhline(y=sum(goals)/7, color="red", linestyle="--")
axes[1].set_title("Cumulative Goals")
axes[1].tick_params(axis='x', rotation=45)

# Histogram
axes[2].hist(samples, bins=np.arange(-0.5, samples.max()+1.5, 1),
             edgecolor="black", color="skyblue")
axes[2].axvline(x=samples.mean(), color="red", linestyle="--")
axes[2].set_title("Goal Distribution")

plt.tight_layout()
plt.savefig("task12_subplots.png", dpi=150)
plt.show()

# ── PART E: Heatmap preview ────────────────────────────────────
matrix = rng.integers(0, 20, size=(5, 5))

fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(matrix, annot=True, fmt="d", cmap="YlOrRd",
            xticklabels=[f"H={i}" for i in range(5)],
            yticklabels=[f"A={i}" for i in range(5)],
            ax=ax)
ax.set_title("Preview: Scoreline Heatmap")
plt.tight_layout()
plt.savefig("task12_heatmap.png", dpi=150)
plt.show()

print("All 5 charts saved! ✅")