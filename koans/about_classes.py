# Axiom: the class body runs once, when the class statement executes. Names assigned there live on the class and are shared. Assigning through self stores an entry on that instance, which shadows the class attribute.

from koans.engine import Koan, blank, expects

__ = blank


class AboutClasses(Koan):
    @expects("class body", hint="Say when those statements run.")
    def test_the_class_body_runs_at_definition(self):
        log = []

        class Bowl:
            log.append("body")
            kind = "ceramic"

        self.assertEqual(log, __)
        self.assertEqual(Bowl.kind, __)
        self.because(__)

    # Bridge: a Java field initializer and a JS class field both run for each new instance. An assignment in a Python class body runs once, on the class.
    @expects("shared", hint="Say where that list lives, and who sees the append.")
    def test_a_class_attribute_is_shared(self):
        class Bowl:
            items: list[str] = []

            def add(self, item: str) -> None:
                self.items.append(item)

        left = Bowl()
        right = Bowl()
        left.add("spoon")
        self.assertEqual(right.items, __)
        self.assertEqual(left.items is Bowl.items, __)
        self.because(__)

    @expects("__dict__", hint="Say where the assignment through self stores the attribute.")
    def test_assignment_on_self_fills_the_instance_dict(self):
        class Bowl:
            kind = "ceramic"

        bowl = Bowl()
        self.assertEqual(bowl.kind, __)
        self.assertEqual("kind" in bowl.__dict__, __)
        bowl.kind = "wood"
        self.assertEqual(bowl.__dict__["kind"], __)
        self.assertEqual(Bowl.kind, __)
        self.because(__)
