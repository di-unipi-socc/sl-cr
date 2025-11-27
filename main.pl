:- set_prolog_flag(stack_limit, 20_000_000_000).

%%%%%%%%%%%%%% Infix ★ star operator %%%%%%%%%%%%%%%%%%%%%%%
:- op(500, xfy, ★). 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 

wf(State) :- deploymentOk(State), nodesOk(State).

% checks deployment policies for all components
deploymentOk(s(P,_)) :- deploymentOk(P).
deploymentOk([c(C,N)|Cs]) :-
    delta(C, N), deploymentOk(Cs).
deploymentOk([]).

% checks node capacity constraints for all nodes
nodesOk(State) :- nodes(Ns), nodesOk(Ns, State).

nodesOk([N|Ns], State) :-
    nodeOk(N, State), nodesOk(Ns, State).
nodesOk([], _).

nodeOk(N, s(P,R)) :-
    findall(H, (member(c(C,N), P), req_hw(C, H)), Hs),
    sum_list(Hs, Used), cap(N, R, Cap), Used =< Cap.

% checks that σ = σ1 \oplus σ2 holds
sep(s(P,R), s(P1,R1), s(P2,R2)) :-
    ground(P1), ground(R1), ground(P2), ground(R2), 
    is_set(P1), is_set(P2), 
    union(P1, P2, P),
    intersection(P1, P2, []),
    checkCap(R, s(P1,R1), s(P2,R2)).
% generates separations (ACHTUNG! it is EXP-time for large inputs!)
sep(s(P,R), s(P1,R1), s(P2,R2)) :-
    part(P, P1, P2), split(R, R1, R2). 

% checks capacity constraints for separated states
checkCap(R, s(_P1,R1), s(_P2,R2)) :- nodes(Ns), checkNodesCap(Ns, R, R1, R2).

checkNodesCap([N|Ns], R, R1, R2) :-
    cap(N, R,  Cap), cap(N, R1, Cap1), cap(N, R2, Cap2),
    Cap1 + Cap2 =< Cap,
    checkNodesCap(Ns, R, R1, R2).
checkNodesCap([], _, _, _).

% separating conjunction
holds(F1 ★ F2, S) :-
    sep(S, S1, S2),
    holds(F1, S1),
    holds(F2, S2).

% holds(wf ★ wf, s([c(c1,n1),c(c2,n2)], [r(n1,100), r(n2,100)]), S1, S2).
holds(F1 ★ F2, S, S1, S2) :-
    sep(S, S1, S2), 
    holds(F1, S1), holds(F2, S2).

% formula satisfaction
holds(wf, S) :- wf(S).
holds(emp, s([],_R)).
holds(not(F), S) :- \+ holds(F, S).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% continuous reasoning  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
crSep(s(P,R), s(Pok,Rok), s(Pko,Rko)) :-
    partition(componentOk(s(P,R)), P, Pok, Pko),
    ok(Pok, R, Rok), ko(R, Rok, Rko).

cr(s(P, R), Sok, Sko, Sok) :-
    crSep(s(P, R), Sok, Sko), holds(emp, Sko), wf(Sok).
cr(s(P, R), s(Pok,Rok), s(PkoFixed,Rko), s(Pnew, R)) :-
    crSep(s(P, R), s(Pok,Rok), s(Pko,Rko)), 
    holds(wf ★ not(wf), s(P, R), s(Pok,Rok), s(Pko,Rko)),  writeln('Repairing:'), writeln(s(Pko,Rko)),
    repair(Pko, Rko, PkoFixed),
    append(Pok, PkoFixed, Ptmp), sort(Ptmp, Pnew),      
    wf(s(Pnew,R)).

repair(Pko, Rko, PkoFixed) :-
    repairComponents(Pko, Rko, [], PAcc), 
    sort(PAcc, PkoFixed).

repairComponents([c(C,_)|Rest], Rko, PAcc, PFinal) :-
    node(N),  delta(C, N),
    req_hw(C, H), cap(N, Rko, CapN),
    used_on_node(PAcc, N, Used),
    CapN - Used >= H,
    repairComponents(Rest, Rko, [c(C,N)|PAcc], PFinal).
repairComponents([], _, P, P).

componentOk(S, c(C,N)) :- nodeOk(N, S), delta(C, N).

%%%%%%%%%%%%%%%% Utilities %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ok(Pok, _R, Rok) :- nodes(Ns), findall(r(N,Used), ( member(N, Ns), used_on_node(Pok, N, Used) ), Rok).

ko(R, Rok, Rko) :- findall(r(N,CapKo),( member(r(N,Cap), R), cap(N, Rok, Used), CapKo is Cap - Used ), Rko).
  
used_on_node(P, N, Used) :- findall(H, ( member(c(C,N), P), req_hw(C, H) ), Hs), sum_list(Hs, Used).

components(Cs) :- findall(C, component(C), Cs).

nodes(Ns) :- findall(N, node(N), Ns).

cap(N, R, C) :- member(r(N,C), R).

delta(C,N) :- component(C), node(N).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% generating resource separations %%%%%%%%%%%%%%%%%%%%%%%%%%%%
part([X|Xs], [X|L1], L2) :-
    part(Xs, L1, L2).
part([X|Xs], L1, [X|L2]) :-
    part(Xs, L1, L2).
part([], [], []).

split([r(N,C)|Rs], [r(N,C1)|R1], [r(N,C2)|R2]) :-
    between(0, C, C1), Max2 is C - C1, between(0, Max2, C2),
    split(Rs, R1, R2).
split([], [], []).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
