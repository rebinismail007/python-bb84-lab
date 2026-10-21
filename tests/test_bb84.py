import unittest
from bb84 import measure_qiskit, measure_reference, simulate

class ReferenceTests(unittest.TestCase):
    def test_same_basis_recovers_each_encoded_bit(self):
        self.assertEqual(measure_reference([0, 1, 0, 1], [0, 0, 1, 1], [0, 0, 1, 1], 7), [0, 1, 0, 1])

    def test_ideal_channel_has_no_sifted_errors(self):
        report = simulate(4000)
        self.assertEqual(report["sifted_qber_for_analysis"], 0)
        self.assertTrue(report["remaining_agreement"])

    def test_full_intercept_resend_approaches_one_quarter_sifted_errors(self):
        report = simulate(20000, seed=13, eve=True)
        self.assertTrue(.22 < report["sifted_qber_for_analysis"] < .28)

    def test_sampled_bits_are_removed_and_small_runs_do_not_over_sample(self):
        for n in [1, 2, 3, 30, 100]:
            report = simulate(n)
            self.assertFalse(set(report["sample_positions"]) & set(report["remaining_positions"]))
            self.assertEqual(report["sampled"] + report["remaining"], report["sifted"])

    def test_reproducibility_and_input_validation(self):
        self.assertEqual(simulate(100, 9, True), simulate(100, 9, True))
        for n in [0, -2, 100001, True]:
            with self.assertRaises(ValueError): simulate(n)
        with self.assertRaises(ValueError): simulate(10, -1)

class QiskitTests(unittest.TestCase):
    def test_actual_aer_circuits_recover_all_four_matching_basis_states(self):
        self.assertEqual(measure_qiskit([0, 1, 0, 1], [0, 0, 1, 1], [0, 0, 1, 1], 42), [0, 1, 0, 1])

    def test_actual_aer_noiseless_run_and_intercept_resend(self):
        self.assertEqual(simulate(64, backend="qiskit")["sifted_qber_for_analysis"], 0)
        report = simulate(1000, seed=17, eve=True, backend="qiskit")
        self.assertTrue(.17 < report["sifted_qber_for_analysis"] < .33)

if __name__ == "__main__": unittest.main()
