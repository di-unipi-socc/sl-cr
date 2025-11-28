%%% query:
% initial_state(S), crSep(S, Sok, Sko).
% initial_state(S), cr(S, Sok, Sko, Sfixed).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Nodes (100)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
node(n1).  node(n2).  node(n3).  node(n4).  node(n5).
node(n6).  node(n7).  node(n8).  node(n9).  node(n10).
node(n11). node(n12). node(n13). node(n14). node(n15).
node(n16). node(n17). node(n18). node(n19). node(n20).
node(n21). node(n22). node(n23). node(n24). node(n25).
node(n26). node(n27). node(n28). node(n29). node(n30).
node(n31). node(n32). node(n33). node(n34). node(n35).
node(n36). node(n37). node(n38). node(n39). node(n40).
node(n41). node(n42). node(n43). node(n44). node(n45).
node(n46). node(n47). node(n48). node(n49). node(n50).
node(n51). node(n52). node(n53). node(n54). node(n55).
node(n56). node(n57). node(n58). node(n59). node(n60).
node(n61). node(n62). node(n63). node(n64). node(n65).
node(n66). node(n67). node(n68). node(n69). node(n70).
node(n71). node(n72). node(n73). node(n74). node(n75).
node(n76). node(n77). node(n78). node(n79). node(n80).
node(n81). node(n82). node(n83). node(n84). node(n85).
node(n86). node(n87). node(n88). node(n89). node(n90).
node(n91). node(n92). node(n93). node(n94). node(n95).
node(n96). node(n97). node(n98). node(n99). node(n100).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Components (10)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
component(c1).
component(c2).
component(c3).
component(c4).
component(c5).
component(c6).
component(c7).
component(c8).
component(c9).
component(c10).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Hardware Requests
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
req_hw(c1, 1).
req_hw(c2, 2).
req_hw(c3, 3).
req_hw(c4, 4).
req_hw(c5, 1).
req_hw(c6, 2).
req_hw(c7, 3).
req_hw(c8, 4).
req_hw(c9, 5).
req_hw(c10,6).

initial_state(s(P, R)) :-
    placement(P), caplist(R).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Node capacities
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
caplist([
  r(n1,5), r(n2,4), r(n3,6), r(n4,3), r(n5,8),
  r(n6,5), r(n7,4), r(n8,7), r(n9,6), r(n10,5),
  r(n11,4), r(n12,7), r(n13,3), r(n14,8), r(n15,6),
  r(n16,5), r(n17,4), r(n18,7), r(n19,6), r(n20,5),
  r(n21,4), r(n22,8), r(n23,5), r(n24,6), r(n25,7),
  r(n26,4), r(n27,6), r(n28,5), r(n29,8), r(n30,3),
  r(n31,7), r(n32,5), r(n33,6), r(n34,4), r(n35,8),
  r(n36,5), r(n37,6), r(n38,4), r(n39,7), r(n40,5),
  r(n41,6), r(n42,4), r(n43,5), r(n44,7), r(n45,8),
  r(n46,3), r(n47,5), r(n48,6), r(n49,7), r(n50,4),
  r(n51,8), r(n52,6), r(n53,4), r(n54,5), r(n55,7),
  r(n56,6), r(n57,4), r(n58,8), r(n59,5), r(n60,7),
  r(n61,4), r(n62,5), r(n63,7), r(n64,6), r(n65,8),
  r(n66,4), r(n67,6), r(n68,5), r(n69,7), r(n70,4),
  r(n71,8), r(n72,6), r(n73,5), r(n74,7), r(n75,4),
  r(n76,6), r(n77,5), r(n78,7), r(n79,4), r(n80,8),
  r(n81,6), r(n82,5), r(n83,7), r(n84,4), r(n85,8),
  r(n86,6), r(n87,5), r(n88,7), r(n89,4), r(n90,8),
  r(n91,6), r(n92,5), r(n93,7), r(n94,4), r(n95,8),
  r(n96,6), r(n97,5), r(n98,7), r(n99,4), r(n100,8)
]).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Placement (intentionally unbalanced)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
placement([
  c(c1,n3),
  c(c2,n3),
  c(c3,n3),    % n3 overloaded (6 capacity, 1+2+3 = 6 OK, but adding c4 below breaks)
  c(c4,n3),
  c(c5,n10),
  c(c6,n20),
  c(c7,n21),
  c(c8,n50),
  c(c9,n70),
  c(c10,n70)   % n70 overloaded (capacity 4, requires 5+6)
]).
