from build.Util import *
from build.RearrangeType import RearrangeType


class Function:
    def __init__(self, function, point, order, functype, title, variable):
        assert FuncTypes.isIn(functype)

        self.circuit = None
        self.horner_coeffs = None
        self.doubleNAND_coeffs = None
        self.poli_coeffs = None
        self.taylor_coeffs = None
        self.taylorString = None
        self.rearrangeString = None
        self.CRN = None
        self.traceString = None
        self.traceValue = None
        self.rearrangeType = None
        self.function = function
        self.point = point
        self.order = order
        self.functype = functype
        self.title = title
        self.variable = variable

    def generateCoeffs(self):
        print("-" * 100)
        print("Taylor Coeffs")
        print("")
        self.taylor_coeffs = make_taylor_coeffs(self)
        for index in self.taylor_coeffs:
            print(index, ": ", self.taylor_coeffs[index])

        print("-" * 100)
        print("Polynomial Coeffs")
        print("")
        self.poli_coeffs = make_polynomial(self)
        for index in self.poli_coeffs:
            print(index, ": ", self.poli_coeffs[index])

        self.taylorString = taylorToPolyStr(self)
        print("Taylor Polynomial String: " + self.taylorString)

        self.rearrangeType = self.determineRearrangement()

        if self.rearrangeType == RearrangeType.DOUBLE_NAND:
            print("-" * 100)
            print("Double NAND Expansion Coeffs")
            print("")
            self.doubleNAND_coeffs = makeDoubleNAND(self)
            for index in self.doubleNAND_coeffs:
                print(index, ": ", self.doubleNAND_coeffs[index])
            print("Rearrangement String: " + self.rearrangeString)
        if self.rearrangeType == RearrangeType.HORNER:
            print("-" * 100)
            print("Horner Expansion Coeffs")
            print("")
            self.horner_coeffs = make_horner(self)
            for index in self.horner_coeffs:
                print(index, ": ", self.horner_coeffs[index])
            self.rearrangeString = hornerFunctionToStr(self)
            print("Rearrangement String" + self.rearrangeString)

    def determineRearrangement(self):
        # HORNER:      alternating signs, coeff decreases as power increases
        # DOUBLE NAND: 0 <= coeffs <= infinity, 0 <= sum <= 1
        alternatingSign = 1
        decreasingCoeffs = 1
        allPositive = 1
        poli_total = 0.0

        for index in self.poli_coeffs:
            if allPositive == 0:
                break

            poli_total = poli_total + self.poli_coeffs[index]

            if self.poli_coeffs[index] > 0:
                allPositive = 1
            else:
                allPositive = 0

        lastValue = 0
        for index in self.poli_coeffs:
            if decreasingCoeffs == 0:
                break

            if self.poli_coeffs[index] == 0:
                continue

            if lastValue == 0:
                lastValue = round(abs(self.poli_coeffs[index]), 4)
                continue

            if abs(lastValue) < round(abs(self.poli_coeffs[index]), 4):
                decreasingCoeffs = 0
                print(abs(lastValue), "is less than", round(abs(self.poli_coeffs[index]), 4))
                continue

            if abs(lastValue) > round(abs(self.poli_coeffs[index]), 4):
                lastValue = round(abs(self.poli_coeffs[index]), 4)
                print(abs(lastValue), "is greater than", round(abs(self.poli_coeffs[index]), 4))
                continue

            if abs(lastValue) == round(abs(self.poli_coeffs[index]), 4):
                continue

        lastValue = 0
        for index in self.poli_coeffs:
            if alternatingSign == 0:
                break
            if self.poli_coeffs[index] != 0:
                if self.poli_coeffs[index] < 0 < lastValue or self.poli_coeffs[index] > 0 > lastValue:
                    alternatingSign = 1
                    lastValue = self.poli_coeffs[index]
                if lastValue == 0:
                    continue
                else:
                    alternatingSign = 0

        print("-" * 100)
        print("Alternating: " + alternatingSign.__str__())
        print("Decreasing: " + decreasingCoeffs.__str__())
        print("Coeff Sum: " + poli_total.__str__())
        print("All Positive: " + allPositive.__str__())

        if 0 <= poli_total <= 1 and allPositive == 1:
            print("Rearrangement Type => Double NAND Replacement")
            print("-" * 100)
            return RearrangeType.DOUBLE_NAND
        if alternatingSign == 1 and decreasingCoeffs == 1:
            print("Rearrangement Type => Horner")
            print("-" * 100)
            return RearrangeType.HORNER
        else:
            print("Rearrangement Type => Unknown")
            print("-" * 100)
            return RearrangeType.UNKNOWN

    def findNextNonZeroPoliValue(current):
        for i in self.poli_coeffs:
            if current > i:
                if self.poli_coeffs[i] != 0:
                    return self.poli_coeffs[i]

    def generateCircuit(self):
        if self.rearrangeType == RearrangeType.DOUBLE_NAND:
            self.circuit = doubleNAND_to_circuit(self)
        if self.rearrangeType == RearrangeType.HORNER:
            self.circuit = horner_to_circuit(self)

        # self.circuit = removeFrivolous(self.circuit)
        if self.rearrangeType != RearrangeType.UNKNOWN:
            show_graph(self)

    def generateReactions(self):
        if self.rearrangeType != RearrangeType.UNKNOWN:
            self.CRN = make_reactions(self.circuit)

    def generateTrace(self):
        if self.rearrangeType == RearrangeType.DOUBLE_NAND:
            pass
        if self.rearrangeType == RearrangeType.HORNER:
            self.traceString = hornerFunctionToStrForceX(self)
            x = self.point
            self.traceValue = eval(self.traceString)

    def isSinusoidal(self):
        if self.functype == FuncTypes.SINUSOIDAL:
            return 1
        elif self.functype == FuncTypes.SINE:
            return 1
        elif self.functype == FuncTypes.COSINE:
            return 1
        else:
            return 0

    def isExponential(self):
        if self.functype == FuncTypes.EXPONENTIAL:
            return 1
        else:
            return 0

    def isLogarithmic(self):
        if self.functype == FuncTypes.LOGARITHMIC:
            return 1
        else:
            return 0
