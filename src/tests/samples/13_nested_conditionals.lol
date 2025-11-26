HAI
    WAZZUP
        I HAS A x
        I HAS A y
        I HAS A z
        I HAS A result
    BUHBYE

    x R 10
    y R 5
    z R 3

    BTW Nested if-else: if x > y then if y > z else if z > x
    BIGGR OF x AN y
    O RLY?
        YA RLY
            BIGGR OF y AN z
            O RLY?
                YA RLY
                    VISIBLE "x > y and y > z"
                NO WAI
                    SMALLR OF z AN x
                    O RLY?
                        YA RLY
                            VISIBLE "x > y but y <= z, and z < x"
                        NO WAI
                            VISIBLE "x > y but y <= z, and z >= x"
                    OIC
            OIC
        NO WAI
            VISIBLE "x <= y"
    OIC

    BTW Triple nested conditional
    BOTH SAEM x AN 10
    O RLY?
        YA RLY
            BOTH SAEM y AN 5
            O RLY?
                YA RLY
                    BOTH SAEM z AN 3
                    O RLY?
                        YA RLY
                            VISIBLE "All match!"
                        NO WAI
                            VISIBLE "x=10, y=5, but z != 3"
                    OIC
                NO WAI
                    VISIBLE "x=10, but y != 5"
            OIC
        NO WAI
            VISIBLE "x != 10"
    OIC

    BTW Nested with arithmetic in conditions
    BIGGR OF SUM OF x AN y AN PRODUKT OF z AN 2
    O RLY?
        YA RLY
            DIFFRINT QUOSHUNT OF x AN y AN 2
            O RLY?
                YA RLY
                    VISIBLE "x+y > z*2 and x/y != 2"
                NO WAI
                    VISIBLE "x+y > z*2 but x/y == 2"
            OIC
        NO WAI
            VISIBLE "x+y <= z*2"
    OIC

KTHXBYE

