# BB84 Lab — Python / Qiskit / AerSimulator

A runnable reconstruction and extension of the BB84 code shown in the supplied **Quantum Key Distribution (QKD)** study PDF, especially the screenshot on page 17. New reconstruction, October 2026; the original project folder was unavailable.

## Recovered flow and additions

The screenshot contains `QuantumCircuit(1, 1)`, X/H gates, random Alice/Bob bases, `transpile`, `AerSimulator.run(..., shots=1)`, key sifting and sample-error calculation. `measure_qiskit` preserves that circuit flow in a testable function.

New work adds a seeded reference backend, an intercept/resend stage, structured results, bounded sample sizes and automated tests. The screenshot's minimum-five sample could exceed the available sifted bits in a small run; sampling is now clamped and exposed sample positions are removed from the remaining positions.

## Run

Python 3.12+; no IBM account or quantum hardware.

```sh
pip install -r requirements.txt
python bb84.py --photons 256
python bb84.py --photons 1000 --eve
python bb84.py --backend reference --photons 20000 --eve
python -m unittest discover -s tests -v
```

The reference backend needs only the standard library. The default Qiskit backend runs actual one-qubit circuits in a local Aer simulator. Seven tests include two actual Aer checks.

## Reading the result

- `sifted`: positions with matching Alice/Bob bases.
- `sample_qber`: observed error fraction in the publicly exposed sample.
- `sifted_qber_for_analysis`: full simulated sifted error fraction, available here because the simulator knows every outcome.
- `remaining`: positions after removing the exposed sample.

For ideal full intercept/resend, the sifted QBER approaches **25%**, not 50%: Eve uses the wrong basis about half the time, and half of those measurements cause a sifted error. Small samples fluctuate. An observed error rate alone cannot distinguish channel noise from an eavesdropper.

This is a protocol teaching simulation. It does not implement authenticated classical communication, error correction, privacy amplification, finite-key security analysis or a production secret-key system. Deterministic simulation seeds are used for reproducible experiments.

Primary references: [IBM Quantum QKD module](https://quantum.cloud.ibm.com/learning/modules/computer-science/quantum-key-distribution), [Aer simulator documentation](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html).
