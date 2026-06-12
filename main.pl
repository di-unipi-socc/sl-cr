:- set_prolog_flag(stack_limit, 20_000_000_000).
:- use_module(library(apply)).  % per partition/4
:- discontiguous sep/3.

%%%%%%%%%%%%%% Infix ★ star operator %%%%%%%%%%%%%%%%%%%%%%%
:- op(500, xfy, ★). 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 

wf(State) :- deploymentPoliciesOk(State), resourcesOk(State).

% checks deployment policies for all components
deploymentPoliciesOk(s(P,_)) :- deploymentPoliciesOk(P).
deploymentPoliciesOk([c(C,N)|Cs]) :-
    pi(C, N), deploymentPoliciesOk(Cs).
deploymentPoliciesOk([]).

% checks node capacity constraints for all nodes
resourcesOk(State) :- allNodes(Ns), resourcesOk(Ns, State).
resourcesOk([N|Ns], State) :-
    hardwareOk(N, State), resourcesOk(Ns, State).
resourcesOk([], _).

% checks that σ = σ1 \oplus σ2 holds
sep(s(P,R), s(P1,R1), s(P2,R2)) :-
    ground(P1), ground(R1), ground(P2), ground(R2), 
    is_set(P1), is_set(P2), 
    union(P1, P2, P),
    intersection(P1, P2, []),
    checkNodesCap(R, s(P1,R1), s(P2,R2)).

% checks capacity constraints for separated states
checkNodesCap(R, s(_,R1), s(_,R2)) :- allNodes(Ns), checkNodesCap(Ns, R, R1, R2).

checkNodesCap([N|Ns], R, R1, R2) :-
    cap(N, R,  Cap), cap(N, R1, Cap1), cap(N, R2, Cap2),
    Cap >= Cap1 + Cap2,
    checkNodesCap(Ns, R, R1, R2).
checkNodesCap([], _, _, _).

% separating conjunction
% holds(wf ★ wf, s([c(c1,n1),c(c2,n2)], [r(n1,100), r(n2,100)]), S1, S2).
holds(F1 ★ F2, S, S1, S2) :-
    sep(S, S1, S2), holds(F1, S1), holds(F2, S2).

holds(F1 ★ F2, S) :-
    sep(S, S1, S2), holds(F1, S1), holds(F2, S2).

% formula satisfaction
holds(wf, S) :- wf(S).
holds(emp, s([],_)).
holds(not(F), S) :- \+ holds(F, S).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% continuous reasoning  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
crSep(s(P,R), s(Pok,Rok), s(Pko,Rko)) :-
    partition(placementOk(s(P,R)), P, Pok, Pko),              % applies placementOk/2 to all c(C,N) in state s(P,R)
    ok(Pok, R, Rok), ko(R, Rok, Rko).

cr(s(P, R), Sok, Sko, Sok) :-
    crSep(s(P, R), Sok, Sko), holds(emp, Sko), wf(Sok), chi(s(Pnew,R)).
cr(s(P, R), s(Pok,Rok), s(Pko,Rko), s(Pnew, R)) :-
    crSep(s(P, R), s(Pok,Rok), s(Pko,Rko)),                   % performs a CR separation  
    holds(wf ★ not(wf), s(P, R), s(Pok,Rok), s(Pko,Rko)),     % checks that Sko is not well-formed (not strictly needed: crSep/3 already ensures this)
    repair(Pko, Rko, PkoFixed),                               % repairs the faulty part Sko to obtain SkoFixed
    union(Pok, PkoFixed, Ptmp), sort(Ptmp, Pnew),
    wf(s(Pnew,R)), chi(s(Pnew,R)).                            % checks that the repaired state is well-formed (not strictly needed: repair/3 already ensures this)                       

repair(Pko, Rko, PkoFixed) :- repairComponents(Pko, Rko, [], PkoFixed).
repairComponents([c(C,_)|Rest], Rko, PAcc, PFinal) :-
    node(N), pi(C, N),
    hardwareOk(N, s([c(C,N)|PAcc], Rko)), 
    repairComponents(Rest, Rko, [c(C,N)|PAcc], PFinal).
repairComponents([], _, P, P).

%%%%%%%%%%%%%%%% Utilities %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ok(Pok, _, Rok) :- allNodes(Ns), findall(r(N,Used), ( member(N, Ns), usedHardware(Pok, N, Used) ), Rok).

ko(R, Rok, Rko) :- findall(r(N,CapKo),( member(r(N,Cap), R), cap(N, Rok, Used), CapKo is Cap - Used ), Rko).

hardwareOk(N, s(P,R)) :- usedHardware(P, N, Used), cap(N, R, Cap), Used =< Cap.
  
usedHardware(P, N, Used) :- findall(H, ( member(c(C,N), P), req_hw(C, H) ), Hs), sum_list(Hs, Used).

placementOk(S, c(C,N)) :- hardwareOk(N, S), pi(C, N).

components(Cs) :- findall(C, component(C), Cs). 

allNodes(Ns) :- findall(N, node(N), Ns).

cap(N, R, C) :- member(r(N,C), R).

pi(C,N) :- component(C), node(N).

chi(S) :- true. % dummy predicate, needs to be instantiated with cross-partition checks for more complex examples
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% generates separations (ACHTUNG! it is EXP-time for large inputs!)
sep(s(P,R), s(P1,R1), s(P2,R2)) :-
    part(P, P1, P2), split(R, R1, R2). 

part([X|Xs], [X|L1], L2) :- part(Xs, L1, L2).
part([X|Xs], L1, [X|L2]) :- part(Xs, L1, L2).
part([], [], []).

split([r(N,C)|Rs], [r(N,C1)|R1], [r(N,C2)|R2]) :-
    between(0, C, C1), Max2 is C - C1, between(0, Max2, C2), 
    split(Rs, R1, R2).
split([], [], []).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%