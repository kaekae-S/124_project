HAI
    WAZZUP
        I HAS A i
        I HAS A j
        I HAS A k
        I HAS A count
    BUHBYE

    count R 0

    BTW Triple nested loop
    IM IN YR outer UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 3
        IM IN YR middle UPPIN YR j WILE BOTH SAEM j AN SMALLR OF j AN 2
            IM IN YR inner UPPIN YR k WILE BOTH SAEM k AN SMALLR OF k AN 2
                count R SUM OF count AN 1
                VISIBLE "i=" + i + " j=" + j + " k=" + k + " count=" + count
            IM OUTTA YR inner
        IM OUTTA YR middle
    IM OUTTA YR outer

    VISIBLE "Total iterations: " + count

    BTW Nested loops with different types
    i R 0
    j R 5
    IM IN YR up_loop UPPIN YR i WILE BOTH SAEM i AN SMALLR OF i AN 3
        IM IN YR down_loop NERFIN YR j TIL BOTH SAEM j AN 2
            VISIBLE "Up: " + i + " Down: " + j
        IM OUTTA YR down_loop
    IM OUTTA YR up_loop

KTHXBYE

