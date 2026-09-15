from collections.abc import Sequence
import random

import z3

OPS_OPERATORS = {
    "+": "ops_add",
    "-": "ops_sub",
    "*": "ops_mul",
    "&": "ops_and",
    "|": "ops_or",
    "^": "ops_xor",
}


class System:
    def __init__(self, solution: Sequence[int]) -> None:
        self._solution = solution

    def generate(
        self,
        operators: Sequence[str] = ("+", "-", "*", "&", "|", "^"),
    ) -> Sequence[tuple[str, str, int]]:
        def random_variable() -> str:
            return f"x[{random.randint(1, len(self._solution)) - 1}]"

        def random_operator() -> str:
            return random.choice(operators)

        def generate_equation() -> tuple[str, str, int]:
            ARITY = 4  # Number of variables in an equation

            expression = random_variable()
            ops_expresion = expression
            for _ in range(ARITY - 1):
                operator = random_operator()
                variable = random_variable()
                expression = f"({expression}{operator}{variable})"
                ops_expresion = f"{OPS_OPERATORS[operator]}({ops_expresion},{variable})"

            x = self._solution  # Alias solution to x -- leverage eval
            return (expression, ops_expresion, eval(expression))

        system = []
        while not self.verify(system):
            system.append(generate_equation())
        return system

    def verify(self, equations: Sequence[tuple[str, str, int]]) -> bool:
        x = [z3.BitVec(f"x[{i}]", 8) for i in range(len(self._solution))]

        solver = z3.Solver()
        for expression, _, expected in equations:
            z3_expresssion = eval(expression)
            solver.add(z3_expresssion == expected)

        if solver.check() != z3.sat:
            return False

        model = solver.model()
        for variable, truth in zip(x, self._solution):
            ref: z3.BitVecNumRef = model[variable]  # type: ignore
            if ref is None or ref.as_long() != truth:
                return False
        return True


FLAG = b"L3AK{R3m0V&_Qu@n~iF!3rs}"
system = System(FLAG).generate()
for _, ops_expr, sol in system:
    print(f"{ops_expr}=={sol}")
print(len(system))
