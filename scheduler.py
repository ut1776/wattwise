"""
WattWise: Carbon-aware GPU workload scheduler
Phase 1: Core simulation and scheduling logic (no AI yet)
"""

import random
from dataclasses import dataclass, field
from typing import List


@dataclass
class Job:
    name: str
    priority: int          # 1 = low, 5 = high (high priority = less flexible)
    duration_hours: float
    gpu_count: int
    deadline_hour: int      # must finish by this hour in the 24h window
    started_hour: int = None  # filled in once scheduled


def generate_job_queue(num_jobs: int = 8, seed: int = 42) -> List[Job]:
    """Create a simulated queue of GPU jobs."""
    random.seed(seed)
    job_types = [
        "LLM fine-tuning", "Batch inference", "Model eval",
        "Data preprocessing", "Embedding generation", "A/B test run",
        "Nightly retrain", "Vector index build"
    ]
    jobs = []
    for i in range(num_jobs):
        jobs.append(Job(
            name=f"{random.choice(job_types)} #{i+1}",
            priority=random.randint(1, 5),
            duration_hours=round(random.uniform(0.5, 4.0), 1),
            gpu_count=random.choice([1, 2, 4, 8]),
            deadline_hour=random.randint(6, 23),
        ))
    return jobs


def generate_carbon_curve(seed: int = 7) -> List[float]:
    """
    Simulate a realistic 24-hour grid carbon-intensity curve
    (gCO2/kWh). Real curves dip at night/midday (solar/wind heavy)
    and peak in morning/evening demand spikes.
    """
    random.seed(seed)
    base = [
        420, 400, 380, 360, 350, 360,     # 0-5am: low demand, low carbon
        420, 480, 520, 500, 460, 400,     # 6-11am: morning ramp, peak carbon
        350, 320, 300, 310, 340, 400,     # 12-5pm: solar dip, then rising
        470, 510, 500, 470, 450, 430      # 6-11pm: evening peak, tapering
    ]
    # add small random noise per hour
    return [round(v + random.uniform(-15, 15), 1) for v in base]


def naive_schedule(jobs: List[Job]) -> List[Job]:
    """Baseline: run everything immediately at hour 0."""
    for job in jobs:
        job.started_hour = 0
    return jobs


def find_best_start_hour(job: Job, carbon_curve: List[float]) -> int:
    """
    Find the lowest-carbon hour to start this job such that
    it still finishes before its deadline.
    """
    latest_start = max(0, job.deadline_hour - int(job.duration_hours) - 1)
    candidate_hours = range(0, latest_start + 1)
    if not candidate_hours:
        return 0

    best_hour = min(
        candidate_hours,
        key=lambda h: carbon_curve[h % 24]
    )
    return best_hour


def carbon_aware_schedule(jobs: List[Job], carbon_curve: List[float]) -> List[Job]:
    """
    Smart scheduling: high-priority jobs run ASAP (little flexibility),
    low-priority jobs shift to the cleanest available window.
    """
    for job in jobs:
        if job.priority >= 4:
            # High priority: run now, no delay
            job.started_hour = 0
        else:
            # Lower priority: find the greenest slot before deadline
            job.started_hour = find_best_start_hour(job, carbon_curve)
    return jobs


def estimate_carbon_used(job: Job, carbon_curve: List[float]) -> float:
    """
    Rough carbon estimate: intensity at start hour * duration * gpu power draw.
    Assumes ~0.3 kW per GPU as a simple constant.
    """
    kw_per_gpu = 0.3
    power_kw = job.gpu_count * kw_per_gpu
    intensity = carbon_curve[job.started_hour % 24]
    return round(intensity * power_kw * job.duration_hours, 1)  # gCO2


def total_carbon(jobs: List[Job], carbon_curve: List[float]) -> float:
    return round(sum(estimate_carbon_used(j, carbon_curve) for j in jobs), 1)


if __name__ == "__main__":
    jobs = generate_job_queue()
    carbon_curve = generate_carbon_curve()

    # Baseline: naive scheduling
    naive_jobs = [Job(**vars(j)) for j in jobs]
    naive_schedule(naive_jobs)
    naive_total = total_carbon(naive_jobs, carbon_curve)

    # Smart: carbon-aware scheduling
    smart_jobs = [Job(**vars(j)) for j in jobs]
    carbon_aware_schedule(smart_jobs, carbon_curve)
    smart_total = total_carbon(smart_jobs, carbon_curve)

    print("=== WattWise Scheduling Simulation ===\n")
    print(f"{'Job':<25} {'Priority':<9} {'Naive Start':<12} {'Smart Start':<12}")
    for n, s in zip(naive_jobs, smart_jobs):
        print(f"{n.name:<25} {n.priority:<9} {n.started_hour:<12} {s.started_hour:<12}")

    print(f"\nNaive total carbon:  {naive_total} gCO2")
    print(f"Smart total carbon:  {smart_total} gCO2")
    savings_pct = round((1 - smart_total / naive_total) * 100, 1)
    print(f"Carbon saved:        {savings_pct}%")
        # Export data for the dashboard
    import json

    def job_to_dict(job, carbon_curve):
        return {
            "name": job.name,
            "priority": job.priority,
            "duration_hours": job.duration_hours,
            "gpu_count": job.gpu_count,
            "deadline_hour": job.deadline_hour,
            "started_hour": job.started_hour,
            "carbon_gCO2": estimate_carbon_used(job, carbon_curve),
        }

    dashboard_data = {
        "carbon_curve": carbon_curve,
        "naive_jobs": [job_to_dict(j, carbon_curve) for j in naive_jobs],
        "smart_jobs": [job_to_dict(j, carbon_curve) for j in smart_jobs],
        "naive_total": naive_total,
        "smart_total": smart_total,
        "savings_pct": savings_pct,
    }

    with open("dashboard_data.json", "w") as f:
        json.dump(dashboard_data, f, indent=2)

    print("\nDashboard data written to dashboard_data.json")