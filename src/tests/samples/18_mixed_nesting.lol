HAI
    WAZZUP
        I HAS A i
        I HAS A j
        I HAS A result
        I HAS A x
        I HAS A y
    BUHBYE

    BTW Loop with nested conditional with nested arithmetic
    result R 0
    IM IN YR outer UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 4
        BIGGR OF i AN 1
        O RLY?
            YA RLY
                IM IN YR inner UPPIN YR j WILE BOTH SAEM j AN SMALLR OF j AN 3
                    BIGGR OF PRODUKT OF i AN j AN 2
                    O RLY?
                        YA RLY
                            result R SUM OF result AN PRODUKT OF SUM OF i AN j AN DIFF OF i AN j
                            VISIBLE "i=" + i + " j=" + j + " result=" + result
                        NO WAI
                            VISIBLE "i*j <= 2: " + i + "*" + j
                    OIC
                IM OUTTA YR inner
            NO WAI
                VISIBLE "i <= 1: " + i
        OIC
    IM OUTTA YR outer

    BTW Switch with nested loops
    x R 2
    x
    WTF?
        OMG 1
            IM IN YR loop1 UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 2
                VISIBLE "Case 1, iteration " + i
            IM OUTTA YR loop1
            GTFO
        OMG 2
            IM IN YR loop2 UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 3
                IM IN YR nested UPPIN YR j WILE BOTH SAEM j AN SMALLR OF j AN 2
                    VISIBLE "Case 2, i=" + i + " j=" + j
                IM OUTTA YR nested
            IM OUTTA YR loop2
            GTFO
        OMGWTF
            VISIBLE "Default case"
    OIC

    BTW Conditional with nested switch with nested arithmetic
    y R 5
    BIGGR OF y AN 3
    O RLY?
        YA RLY
            MOD OF y AN 2
            WTF?
                OMG 0
                    VISIBLE "Even: " + SUM OF PRODUKT OF y AN y AN QUOSHUNT OF y AN 2
                    GTFO
                OMG 1
                    VISIBLE "Odd: " + DIFF OF PRODUKT OF y AN y AN QUOSHUNT OF y AN 2
                    GTFO
                OMGWTF
                    VISIBLE "Unexpected modulo result"
            OIC
        NO WAI
            VISIBLE "y <= 3"
    OIC

    BTW Loop with switch with conditional
    IM IN YR complex UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 5
        i
        WTF?
            OMG 0
            OMG 2
            OMG 4
                BOTH SAEM MOD OF i AN 2 AN 0
                O RLY?
                    YA RLY
                        VISIBLE "Even index: " + i
                    NO WAI
                        VISIBLE "Odd index: " + i
                OIC
                GTFO
            OMG 1
            OMG 3
                VISIBLE "Odd case: " + i
                GTFO
            OMGWTF
                VISIBLE "Other: " + i
        OIC
    IM OUTTA YR complex

KTHXBYE

