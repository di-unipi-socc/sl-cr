%%% query:
% initial_state(S), crSep(S, Sok, Sko).
% initial_state(S), cr(S, Sok, Sko, SFinal).
%
% Atteso:
% - n1: cap=2, richieste = 2        → OK
% - n2: cap=4, richieste = 2+3 = 5  → OVERLOAD
% → Sok contiene solo c1 su n1,
%   Sko contiene c2 e c3 su n2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Nodes (5)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
node(n1).
node(n2).
node(n3).
node(n4).
node(n5).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Components (3)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
component(c1).
component(c2).
component(c3).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Hardware Requests
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
req_hw(c1, 2).
req_hw(c2, 2).
req_hw(c3, 3).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Initial state
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
initial_state(s(P, R)) :-
    placement(P),
    caplist(R).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Node capacities
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
caplist([
  r(n1,2),   % n1 può ospitare fino a 2 unità
  r(n2,4),   % n2 può ospitare fino a 4 unità (ma gliene chiediamo 5)
  r(n3,5),
  r(n4,3),
  r(n5,6)
]).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Placement (intentionally unbalanced)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
placement([
  c(c1,n1),  % n1: req = 2, cap = 2  → OK
  c(c2,n2),  % n2: req parziale = 2
  c(c3,n2)   % n2: 2+3 = 5 > 4      → OVERLOAD
]).
