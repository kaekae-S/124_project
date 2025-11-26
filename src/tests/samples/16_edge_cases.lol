HAI
    WAZZUP
        I HAS A x
        I HAS A y
        I HAS A z
        I HAS A i
    BUHBYE

    BTW Empty loop (should not execute)
    i R 0
    IM IN YR empty_loop UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 0
        VISIBLE "This should not print"
    IM OUTTA YR empty_loop

    BTW Single iteration loop
    i R 0
    IM IN YR single_loop UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 1
        VISIBLE "Single iteration: " + i
    IM OUTTA YR single_loop

    BTW Division by zero handling (should be tested)
    x R 10
    y R 0
    BTW QUOSHUNT OF x AN y  BTW This might cause error

    BTW Modulo by zero handling
    BTW MOD OF x AN y  BTW This might cause error

    BTW Nested empty conditionals
    BOTH SAEM 0 AN 1
    O RLY?
        YA RLY
            BOTH SAEM 0 AN 1
            O RLY?
                YA RLY
                    VISIBLE "Nested true"
                NO WAI
                    VISIBLE "Nested false"
            OIC
        NO WAI
            VISIBLE "Outer false"
    OIC

    BTW Very deep nesting (4 levels)
    x R 1
    BOTH SAEM x AN 1
    O RLY?
        YA RLY
            BOTH SAEM x AN 1
            O RLY?
                YA RLY
                    BOTH SAEM x AN 1
                    O RLY?
                        YA RLY
                            BOTH SAEM x AN 1
                            O RLY?
                                YA RLY
                                    VISIBLE "4 levels deep!"
                                NO WAI
                                    VISIBLE "Level 4 false"
                            OIC
                        NO WAI
                            VISIBLE "Level 3 false"
                    OIC
                NO WAI
                    VISIBLE "Level 2 false"
            OIC
        NO WAI
            VISIBLE "Level 1 false"
    OIC

    BTW Zero and negative number handling
    x R 0
    y R -5
    VISIBLE "Zero: " + x
    VISIBLE "Negative: " + y
    VISIBLE "Sum: " + SUM OF x AN y
    VISIBLE "Product: " + PRODUKT OF x AN y

    BTW Very large nested arithmetic
    x R 100
    y R 200
    z R 300
    VISIBLE SUM OF PRODUKT OF SUM OF x AN y AN SUM OF y AN z AN PRODUKT OF SUM OF x AN z AN SUM OF SUM OF x AN y AN z

KTHXBYE

