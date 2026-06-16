"""
Blue Moon Portal - AI Agent with Full Data Flywheel Integration

Now includes automatic trajectory recording for the self-improving data flywheel.
"""

import asyncio
import json
import logging
import re
from typing import Optional
from datetime import datetime

from coastal_alpine_core.security import SecurityGuard, SecurityResult
from coastal_alpine_core.telemetry import TelemetryTracker
from coastal_alpine_core.flywheel import DataFlywheel, Trajectory

logger = logging.getLogger(__name__)
security_guard = SecurityGuard()


class AIAgent:
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "gemma4:e4b", flywheel: Optional[DataFlywheel] = None):
        self.ollama_host = ollama_host
        self.model = model
        self.client = ollama.Client(host=ollama_host)
        self.flywheel = flywheel or DataFlywheel(storage_path="flywheel_blue_moon.jsonl")
        logger.info(f"AI Agent initialized with full flywheel support")

    async def generate_optimization_plan(self, sensor_analysis: dict, visual_analysis: dict, audio_analysis: dict) -> dict:
        prompt = f"""Microgreen optimization..."""

        # Security check
        sec_result = security_guard.check_prompt(prompt)
        if not sec_result.is_safe:
            return self._generate_default_plan()

        measurement = TelemetryTracker.measure_latency("generate_optimization_plan")

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(self.client.generate, self.model, prompt, stream=False),
                timeout=60.0
            )

            # ... existing plan parsing and validation logic ...

            plan = validated_plan.dict()

            # === FULL FLYWHEEL INTEGRATION ===
            try:
                traj = Trajectory(
                    trajectory_id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    action="generate_optimization_plan",
                    input_summary=str(sensor_analysis)[:200],
                    output_summary=str(plan)[:300],
                    outcome="success",
                    latency_seconds=0.0,
                    estimated_energy_joules=0.0,
                    metadata={"plan_id": plan.get("plan_id"), "requires_human_review": plan.get("requires_human_review", False)}
                )
                self.flywheel.record_trajectory(traj)
            except Exception as e:
                logger.warning(f"Flywheel recording failed: {e}")

            TelemetryTracker.complete_measurement(measurement, include_system_metrics=True)
            return plan

        except Exception:
            return self._generate_default_plan()

    # record_hardware_outcome can be called from main.py after enforce_plan()
    def record_hardware_result(self, plan_id: str, action: str, success: bool, **kwargs):
        self.flywheel.record_hardware_outcome(plan_id, action, success, **kwargs)
