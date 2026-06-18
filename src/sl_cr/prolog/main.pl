:- set_prolog_flag(answer_write_options,[max_depth(0)]). % write answers' text entirely
:- set_prolog_flag(stack_limit, 128 000 000 000).
:- set_prolog_flag(last_call_optimisation, true).
:- use_module(library(apply)).  % per partition/4

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% continuous reasoning  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Lemma 3.10
crSep(s(P,R), s(Pok,Rok), s(Pko,Rko)) :-
    partition(placementOk(s(P,R)), P, Pok, Pko),  % applies placementOk/2 to all c(C,N) in state s(P,R)
    rOk(Pok, P, Rok), rKo(R, Rok, Rko).           % computes Rok and Rko based on Pok and R

% Corollary 3.11
cr(s(P, R), Sok, s([],_), Sok) :- crSep(s(P, R), Sok, s([],_)). 
cr(s(P, R), s(Pok,Rok), s(Pko,Rko), s(Pnew, R)) :-
    crSep(s(P, R), s(Pok,Rok), s(Pko,Rko)),                   % performs a CR separation  
    repair(Pko, Rko, PkoFixed),   % Corollary 3.11            % repairs the faulty part Sko to obtain SkoFixed
    union(Pok, PkoFixed, Ptmp), sort(Ptmp, Pnew).

repair(Pko, Rko, PkoFixed) :- repairComponents(Pko, Rko, [], PkoFixed).
repairComponents([c(C,_)|Rest], Rko, PAcc, PFinal) :-
    component(C), node(N), pi(C, N),
    hardwareOk(N, s([c(C,N)|PAcc], Rko)), 
    repairComponents(Rest, Rko, [c(C,N)|PAcc], PFinal).
repairComponents([], _, P, P).

%%%%%%%%%%%%%%%% Utilities %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
rOk(Pok, _, Rok) :- allNodes(Ns), findall(r(N,Used), ( member(N, Ns), usedHardware(Pok, N, Used) ), Rok).

rKo(R, Rok, Rko) :- findall(r(N,CapKo),( member(r(N,Cap), R), cap(N, Rok, Used), CapKo is Cap - Used ), Rko).

hardwareOk(N, s(P,R)) :- usedHardware(P, N, Used), cap(N, R, Cap), Used =< Cap.
  
usedHardware(P, N, Used) :- findall(H, ( member(c(C,N), P), req_hw(C, H) ), Hs), sum_list(Hs, Used).

placementOk(S, c(C,N)) :- hardwareOk(N, S), pi(C, N).

allNodes(Ns) :- findall(N, node(N), Ns).

cap(N, R, C) :- member(r(N,C), R).

pi(_,_) :- true. % can capture deployment constraints, e.g., pi(C,N) :- allowed(C,N).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%