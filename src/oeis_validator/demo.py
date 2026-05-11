from __future__ import annotations

DEMO_GOOD: str = """\
%I A123456
%S A123456 1,1,2,5,14,42,132,429,1430,4862,16796,58786,208012,742900,
%T A123456 2674440,9694845,35357670,129644790,477638700,1767263190
%N A123456 Catalan numbers: a(n) = binomial(2n,n)/(n+1).
%C A123456 Named after Eugene Charles Catalan (1814-1894).
%D A123456 R. P. Stanley, Enumerative Combinatorics, Vol. 2, Cambridge, 1999, p. 219.
%H A123456 N. J. A. Sloane, <a href="/A123456/b123456.txt">Table of n, a(n) for n = 0..1000</a>
%H A123456 Wikipedia, <a href="https://en.wikipedia.org/wiki/Catalan_number">Catalan number</a>
%F A123456 a(n) = binomial(2*n,n)/(n+1).
%F A123456 G.f.: A(x) = (1 - sqrt(1-4*x))/(2*x).
%e A123456 a(3) = C(6,3)/4 = 20/4 = 5.
%o A123456 (PARI) a(n) = binomial(2*n,n)/(n+1) \\\\ N. J. A. Sloane, Jan 01 2020
%Y A123456 Cf. A000108, A001700.
%K A123456 nonn,easy,core
%O A123456 0,3
%A A123456 N. J. A. Sloane
"""

DEMO_BAD: str = """\
%I A654321
%S A654321 1, 2, 3
%N A654321 Integers from 1 to 3 (bad example)
%D A654321 See https://example.com for more info.
%H A654321 http://example.com/no-anchor
%F A654321 a_n = n.
%o A654321 n+1 for n in range(1,4)
%Y A654321 A123,A1234567,A123456,A123456
%O A654321 1,99
%K A654321 nonn,sign,more,full
"""
