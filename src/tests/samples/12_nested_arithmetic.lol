HAI
    WAZZUP
        I HAS A a
        I HAS A b
        I HAS A c
        I HAS A d
        I HAS A result
    BUHBYE

    a R 10
    b R 5
    c R 3
    d R 2

    BTW Deeply nested arithmetic: ((a+b)*(c-d)) + ((a-b)/(c+d))
    result R SUM OF PRODUKT OF SUM OF a AN b AN DIFF OF c AN d AN QUOSHUNT OF DIFF OF a AN b AN SUM OF c AN d
    VISIBLE "Complex nested: " + result

    BTW Multiple levels: a + (b * (c + (d * (a - b))))
    result R SUM OF a AN PRODUKT OF b AN SUM OF c AN PRODUKT OF d AN DIFF OF a AN b
    VISIBLE "Deep nesting: " + result

    BTW Mixed operations: max(a, min(b, max(c, d))) - min(a, max(b, min(c, d)))
    result R DIFF OF BIGGR OF a AN SMALLR OF b AN BIGGR OF c AN d AN SMALLR OF a AN BIGGR OF b AN SMALLR OF c AN d
    VISIBLE "Nested min/max: " + result

    BTW Power-like: (a^2 + b^2) * (c^2 + d^2)
    result R PRODUKT OF SUM OF PRODUKT OF a AN a AN PRODUKT OF b AN b AN SUM OF PRODUKT OF c AN c AN PRODUKT OF d AN d
    VISIBLE "Sum of squares product: " + result

    BTW Complex fraction: (a*b + c*d) / (a+b)
    result R QUOSHUNT OF SUM OF PRODUKT OF a AN b AN PRODUKT OF c AN d AN SUM OF a AN b
    VISIBLE "Complex fraction: " + result

    BTW Nested modulo: ((a % b) % c) + ((b % c) % d)
    result R SUM OF MOD OF MOD OF a AN b AN c AN MOD OF MOD OF b AN c AN d
    VISIBLE "Nested modulo: " + result

KTHXBYE

