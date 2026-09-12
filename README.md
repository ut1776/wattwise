# ⚡ WattWise

**AI-powered carbon-aware GPU workload scheduler**

WattWise decides when to run GPU workloads based on the grid's carbon intensity — shifting flexible, low-priority jobs to cleaner windows while letting high-priority jobs run immediately. It cuts carbon emissions from AI compute without adding delay to what matters.

Built for the **Nebius x NVIDIA Global AI Hackathon** (Coding and Agentic Engineering Track).

## What it does

- Simulates a queue of GPU jobs (priority, duration, GPU count, deadline)
- Simulates a realistic 24-hour grid carbon-intensity curve
- Compares two scheduling strategies:
  - **Naive**: run everything immediately
  - **WattWise**: high-priority jobs run now; flexible jobs shift to the lowest-carbon window before their deadline
- Displays results on a live dashboard: job queue, carbon curve, and total carbon saved

In our test run, WattWise cut carbon emissions by **18.3%** versus naive scheduling, with zero impact on high-priority jobs.

## NVIDIA Nemotron integration (coming soon)

WattWise will use an NVIDIA Nemotron model, served via **Nebius Token Factory**, to generate plain-language explanations for each scheduling decision.

## How to run it

**Requirements:** Python 3.10+

1. Clone the repo:
