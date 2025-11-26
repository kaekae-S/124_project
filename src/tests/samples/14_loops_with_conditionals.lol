HAI
    WAZZUP
        I HAS A i
        I HAS A j
        I HAS A sum
        I HAS A count
    BUHBYE

    BTW Loop with nested if-else
    sum R 0
    IM IN YR loop1 UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 10
        BOTH SAEM MOD OF i AN 2 AN 0
        O RLY?
            YA RLY
                sum R SUM OF sum AN i
                VISIBLE "Even: " + i
            NO WAI
                VISIBLE "Odd: " + i
        OIC
    IM OUTTA YR loop1
    VISIBLE "Sum of evens: " + sum

    BTW Nested loop with nested conditional
    count R 0
    IM IN YR outer UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 5
        IM IN YR inner UPPIN YR j WILE BOTH SAEM j AN SMALLR OF j AN 5
            BIGGR OF SUM OF i AN j AN 5
            O RLY?
                YA RLY
                    count R SUM OF count AN 1
                    VISIBLE "i+j > 5: " + i + "+" + j + "=" + SUM OF i AN j
                NO WAI
                    VISIBLE "i+j <= 5: " + i + "+" + j
            OIC
        IM OUTTA YR inner
    IM OUTTA YR outer
    VISIBLE "Count of pairs where i+j > 5: " + count

    BTW Loop with switch inside
    IM IN YR switch_loop UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 5
        i
        WTF?
            OMG 0
                VISIBLE "Zero"
                GTFO
            OMG 1
                VISIBLE "One"
                GTFO
            OMG 2
                VISIBLE "Two"
                GTFO
            OMGWTF
                VISIBLE "Other: " + i
        OIC
    IM OUTTA YR switch_loop

    BTW Conditional with loop inside
    BOTH SAEM 1 AN 1
    O RLY?
        YA RLY
            IM IN YR nested_loop UPPIN YR j WILE BOTH SAEM j AN SMALLR OF j AN 3
                VISIBLE "Nested loop iteration: " + j
            IM OUTTA YR nested_loop
        NO WAI
            VISIBLE "This won't execute"
    OIC

KTHXBYE

