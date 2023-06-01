# usable-itdk
Parse [CAIDA ITDK](https://www.caida.org/catalog/datasets/internet-topology-data-kit/) files into a database

## notes
https://www.crummy.com/software/BeautifulSoup/bs4/doc/
https://docs.python.org/3/library/sqlite3.html
https://docs.python.org/3/library/http.server.html
https://python.igraph.org/en/stable/
https://plotly.com/python/
https://docs.python.org/3/library/os.path.html
https://docs.python.org/3/library/stdtypes.html

https://dash.plotly.com/

### CAIDA recipe
https://catalog.caida.org/recipe/parse_the_itdk

### excerpt from discussion on CAIDA Mattermost

question regarding hyperlinks:
I understand the "multiple non-aliased predecessors" definition, however I still don't fully understand what probe outputs get you a hyperlink-classified occurrence 

K gave me an example:  

imagine two separate traceroutes:  A B C * * * F
and A B D * * * F
we would make a hyperlink among D, C, F  .
this is how we describe it on  https://www.caida.org/archive/topo_comparison/  to describe figure 3b

K wants to make sure she is explaining it correctly to me

to make sure i understand
*we can't use a placeholder node because it's multiple hops and so hyperlinks represent ambiguity of multiple entities
*we do not know how D and C relate to each other besides being upstream of F in this direction, and we can't say any thing about the reverse direction of F to D or F to C

bradley
1:21 PM
@kkeys @young when/how are hyper links inferred in the ITDK 
	
kkeys
2:23 PM
k's example is wrong.  Figure 3 and the text with it are correct (if a bit unclear: the left side of the figure shows sequential traceroute hops, and the right side shows routers, their interfaces, and IP links between the interfaces).  Remember, traceroutes (usually) see the incoming interface of each router, but links are between an outgoing interface of one router and an incoming interface of the next router.  And without additional information (from a traceroute in the opposite direction), the outbound interfaces will have unknown addresses.  In figure 3, there's a hyperlink among (?,?,B) because we weren't able to prove the two routers on the left are the same router.  If they are the same router, and the two ?'s are the same interface, then the inferred hyperlink is really just a (?,B) IP link.  But if the two routers are different, the (?,?,B) hyperlink really is a IP-level hyperlink, i.e. there are 3 routers and addresses (?,?,B) are on the same IP subnet (perhaps all connected to the same layer 2 switch).

	
allison
2:43 PM
so just to make sure i understand

X -- B
Y -- B

we know that (X, B) and (Y, B) are valid directed edges
the known here is the inbound address of B
the unknown is the outbound addresses of X and Y that they use when talking to B's known inbound address
if you can run a traceroute that moves in the opposite direction on that interface of B, you will find either one address that connects to both X and Y's neighbors, in which case X and Y are collapsed into a single node, or two different addresses, in which case they are left separate
if you can't get a trace to run in the opposite direction, the reality remains ambiguous and is then designated a hyperlink
	
k.c
2:49 PM
so brad said this to me earlier, that the way allison knows about a node in the links file is e.g., "a hyper link from ITDK-2020-08/midar-iff.links.bz2 is "link L43:  N6369892:1.1.1.5 N110677 N110678 N110679" which contains a link shared between 4 nodes"  @kkeys is that correct?  

	
kkeys
3:01 PM
The letters X,Y,B here are referring to interfaces (IP addresses), not nodes (routers).  I would rephrase @allison's first point to:  we know that (Nx,Nb) and (Ny,Nb) are valid directed edges, where Nx is a node that has an interface address X, etc.

@k.c's example L43 is, yes, a link between 4 nodes, or more precisely, a link between interface 1.1.1.5 of node N6369892 and unknown interfaces of nodes N110677, N110678, N110679.

## ITDK File Formats
**The following is an excerpt from ITDK release README files**

Each router-level topology is provided in two files, one giving the
nodes and another giving the links.  There are also files that
assign ASes and geolocation to each node.


IPv4 Router Topology (MIDAR + iffinder alias resolution):
========================================================

midar-iff.nodes
midar-iff.links
midar-iff.nodes.as
midar-iff.nodes.geo

IPv6 Router Topology (speedtrap IPv6 alias resolution):
======================================================

speedtrap.nodes
speedtrap.links
speedtrap.nodes.as
speedtrap.nodes.geo


File Formats:
============

.nodes

     The nodes file lists the set of interfaces that were inferred to
     be on each router.

      Format: node <node_id>:   <i1>   <i2>   ...   <in>
     Example: node N33382:  4.71.46.6 192.8.96.6 0.4.233.32

     Each line indicates that a node node_id has interfaces i_1 to i_n.
     Interface addresses in 224.0.0.0/3 (IANA reserved space for multicast)
     are not real addresses.  They were artificially generated to identify
     potentially unique non-responding interfaces in traceroute paths.

     The IPv6 dataset uses IPv6 multicast addresses (FF00::/8) to indicate
     non-responding interfaces in traceroute paths.

       NOTE: In ITDK release 2013-04 and earlier, we used addresses in
             0.0.0.0/8 instead of 224.0.0.0/3 for these non-real addresses.


.links

     The links file lists the set of routers and router interfaces
     that were inferred to be sharing each link.  Note that these are
     IP layer links, not physical cables or graph edges.  More than
     two nodes can share the same IP link if the nodes are all
     connected to the same layer 2 switch (POS, ATM, Ethernet, etc).

      Format: link <link_id>:   <N1>:i1   <N2>:i2   [<N3>:[i3] .. [<Nm>:[im]]
     Example: link L104:  N242484:211.79.48.158 N1847:211.79.48.157 N5849773

     Each line indicates that a link link_id connects nodes N_1 to
     N_m.  If it is known which router interface is connected to the
     link, then the interface address is given after the node ID
     separated by a colon (e.g., "N1:1.2.3.4"); otherwise, only the
     node ID is given (e.g., "N1").

     By joining the node and link data, one can obtain the _known_ and
     _inferred_ interfaces of each router.  Known interfaces actually
     appeared in some traceroute path.  Inferred interfaces arise when
     we know that some router N_1 connects to a known interface i_2 of
     another router N_2, but we never saw an actual interface on the
     former router.  The interfaces on an IP link are typically
     assigned IP addresses from the same prefix, so we assume that
     router N_1 must have an inferred interface from the same prefix
     as i_2.


.nodes.as

     The node-AS file assigns an AS to each node found in the nodes
     file.  We used bdrmapIT to infer the owner AS of each node.

      Format: node.AS   <node_id>   <AS>   <heuristic-tag>
     Example: node.AS N39 17645 refinement

     Each line indicates that the node node_id is owned/operated by
     the given AS, tagged with the heuristic that bdrmapIT used. There
     are five possible heuristic tags:

        1. origins: AS inferred based on the AS announcing the
	   longest matching prefixes for the router interface IP
	   addresses.

        2. lasthop: AS inferred based on the destination AS of the
	   IP addresses tracerouted.

        3. refinement: AS inferred based on the ASes of surrounding
	   routers.

        4. as-hints: AS hints embedded in PTR records checked with
	   bdrmapIT.

        5. unknown: routers that bdrmapIT could not infer an AS for.


.nodes.geo

     The node-geolocation file contains an inferred geographic
     location of each node in the nodes file, where possible.

      Format: node.geo <node_id>:   <continent>   <country>   <region> \
              <city>   <latitude>   <longitude>  <method>
     Example: node.geo N15:  NA  US  HI  Honolulu  21.2890  -157.8028  maxmind

     Each line indicates that the node node_id has the given
     geographic location.  Columns after the colon are tab-separated.
     The fields have the following meanings:

       <continent>: a two-letter continent code

		    * AF: Africa
    		    * AN: Antarctica
    		    * AS: Asia
		    * EU: Europe
		    * NA: North America
		    * OC: Oceania
		    * SA: South America

       <country>: a two-letter ISO 3166 Country Code.

       <region>: a two or three alphanumeric region code.

       <city>: city or town in ISO-8859-1 encoding (up to 255 characters).

       <latitude> and <longitude>: signed floating point numbers.

       <method>: the geolocation method which inferred the location

                    * hoiho: inferred using Hoiho's rules
		    * ix: inferred based on the known location of an IXP
		    * maxmind: inferred using maxmind


.ifaces

     This file provides additional information about all interfaces
     included in the provided router-level graphs:

      Format:  <address> [<node_id>] [<link_id>] [T] [D]

     Each of the fields in square brackets may or may not be present.

     Example:  1.0.174.107 N34980480 D
     Example:  1.0.101.6 N18137917 L537067 T

     Example:  1.28.124.57 N45020
     Example:  11.3.4.2 N18137965 L537125 T D
     Example:  1.0.175.90

     <node_id> starts with "N" and identifies the node (alias set) to which
     the address belongs.  An address may not have a node_id if no aliases
     were found.

     <link_id> starts with "L" and identifies the link to which the address is
     attached, if known.  An address will not have a link_id if it was
     obtained from a source other than traceroute or appeared only as the
     first public address in a traceroute (i.e., the source and all other hops
     preceeding this address were either private addresses or nonresponsive).

     "T" indicates that the address appeared in at least one traceroute as a
     transit hop, i.e. preceeded by at least one (public or private) address
     (including the source) and followed by at least one public address
     (including the destination).  An address does not qualify as a transit
     hop if it was seen only in these situations: it was obtained from a
     source other than traceroute; it was the source or destination of a
     traceroute; or it was the last responding public address to appear in a
     traceroute.

     "D" indicates that the address appeared in at least one traceroute as a
     responding destination hop.

     "T" and "D" are not mutually exclusive -- an address may have been a
     transit hop in one traceroute and the destination in another.

     An interface address will have "T" but not "L<link_id>" if it appeared
     only as the first public address in a traceroute.


