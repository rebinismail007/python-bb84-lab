"""Reconstruct a study BB84 demo, with an optional intercept/resend experiment."""
from __future__ import annotations
import argparse
import json
import random

def measure_reference(bits, prepared_bases, measured_bases, seed):
    rng = random.Random(seed)
    return [bit if prepared == measured else rng.randrange(2)
            for bit, prepared, measured in zip(bits, prepared_bases, measured_bases)]

def measure_qiskit(bits, prepared_bases, measured_bases, seed):
    # The PDF's page-17 flow: X/H preparation, H for X-basis readout,
    # one classical measurement per circuit, transpile, then AerSimulator.
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    circuits = []
    for bit, prepared, measured in zip(bits, prepared_bases, measured_bases):
        circuit = QuantumCircuit(1, 1)
        if bit:
            circuit.x(0)
        if prepared:
            circuit.h(0)
        if measured:
            circuit.h(0)
        circuit.measure(0, 0)
        circuits.append(circuit)
    if not circuits:
        return []
    simulator = AerSimulator(max_parallel_threads=1, max_parallel_experiments=1)
    compiled = transpile(circuits, simulator, seed_transpiler=seed, num_processes=1)
    result = simulator.run(compiled, shots=1, seed_simulator=seed).result()
    return [int(next(iter(result.get_counts(i)))) for i in range(len(circuits))]

def simulate(count=256, seed=42, eve=False, backend="reference"):
    if type(count) is not int or not 1 <= count <= 100_000:
        raise ValueError("Photon count must be an integer from 1 to 100000.")
    if type(seed) is not int or not 0 <= seed < 2**31:
        raise ValueError("Seed must be an integer from 0 to 2147483647.")
    if backend not in ("reference", "qiskit"):
        raise ValueError("Unknown simulation backend.")
    rng = random.Random(seed)
    alice_bits = [rng.randrange(2) for _ in range(count)]
    alice_bases = [rng.randrange(2) for _ in range(count)]
    bob_bases = [rng.randrange(2) for _ in range(count)]
    measure = measure_qiskit if backend == "qiskit" else measure_reference
    sent_bits, sent_bases = alice_bits, alice_bases
    if eve:
        eve_bases = [rng.randrange(2) for _ in range(count)]
        sent_bits = measure(alice_bits, alice_bases, eve_bases, seed + 1)
        sent_bases = eve_bases
    bob_bits = measure(sent_bits, sent_bases, bob_bases, seed + 2)
    sifted = [i for i in range(count) if alice_bases[i] == bob_bases[i]]
    sample_size = min(len(sifted), max(1, len(sifted) // 5))
    sample = rng.sample(sifted, sample_size)
    exposed = set(sample)
    remaining = [i for i in sifted if i not in exposed]
    sample_errors = sum(alice_bits[i] != bob_bits[i] for i in sample)
    all_errors = sum(alice_bits[i] != bob_bits[i] for i in sifted)
    return {
        "backend": backend, "seed": seed, "eve_enabled": bool(eve), "sent": count,
        "sifted": len(sifted), "sampled": len(sample), "remaining": len(remaining),
        "sample_positions": sample, "remaining_positions": remaining,
        "sample_errors": sample_errors,
        "sample_qber": sample_errors / len(sample) if sample else None,
        "sifted_qber_for_analysis": all_errors / len(sifted) if sifted else None,
        "remaining_agreement": all(alice_bits[i] == bob_bits[i] for i in remaining) if remaining else None,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--photons", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--eve", action="store_true")
    parser.add_argument("--backend", choices=["reference", "qiskit"], default="qiskit")
    args = parser.parse_args()
    try:
        print(json.dumps(simulate(args.photons, args.seed, args.eve, args.backend), indent=2))
        return 0
    except (ValueError, ImportError) as error:
        parser.exit(2, f"Error: {error}\n")

if __name__ == "__main__":
    raise SystemExit(main())
