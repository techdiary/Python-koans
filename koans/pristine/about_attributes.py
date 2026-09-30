# Axiom: attribute lookup looks on the instance first, then walks the class MRO. The first match wins. A function found on the class becomes a bound method when looked up through an instance.

from koans.engine import Koan, blank, expects

__ = blank


class AboutAttributes(Koan):
    # Bridge: JS and Java each give a class one parent. Python walks the MRO. C3 can place a later base before a shared ancestor.
    @expects("mro", hint="Say which classes are searched after the instance, and in what order.")
    def test_lookup_walks_the_mro(self):
        class A:
            color = "a"

        class B(A):
            pass

        class C(A):
            color = "c"

        class D(B, C):
            pass

        self.assertEqual([cls.__name__ for cls in D.__mro__ if cls is not object], __)
        self.assertEqual(D().color, __)
        self.because(__)

    @expects("shadow", hint="Say which object holds the attribute after the assignment.")
    def test_an_instance_attribute_hides_the_class_attribute(self):
        class A:
            color = "a"

        item = A()
        item.color = "own"
        self.assertEqual(item.color, __)
        self.assertEqual(A.color, __)
        self.because(__)

    @expects("bound method", hint="Say what you get when you look up a function through an instance.")
    def test_lookup_through_an_instance_binds_the_function(self):
        class A:
            def label(self) -> str:
                return "a"

        item = A()
        method = item.label
        self.assertEqual(method(), __)
        self.assertEqual(A.label(item), __)
        self.assertEqual(method.__func__ is A.label, __)
        self.because(__)
