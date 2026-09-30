# Axiom: super() does not mean the textually written parent. It continues along the MRO of the instance the call started on.

from koans.engine import Koan, blank, expects

__ = blank


class AboutInheritance(Koan):
    # Bridge: Java super and JS super mean the single parent. Python super() follows the MRO of the instance, so a D can run B and then C.
    @expects("mro", hint="Say whose method order super() continues.")
    def test_super_follows_the_instance_mro(self):
        class A:
            def collect(self) -> list[str]:
                return ["A"]

        class B(A):
            def collect(self) -> list[str]:
                return ["B"] + super().collect()

        class C(A):
            def collect(self) -> list[str]:
                return ["C"] + super().collect()

        class D(B, C):
            def collect(self) -> list[str]:
                return ["D"] + super().collect()

        self.assertEqual(D().collect(), __)
        self.assertEqual(B().collect(), __)
        self.because(__)
