#
# Graph: ./datasets/facebook/facebook_random.edgelist -> facebook_random facebook_random. A=0.001, K=10-1.5-100M, Cvr=10, SzFrc=0.001 G(4039, 96234) (Mon Sep  8 15:19:13 2025)
#

set title "Graph: ./datasets/facebook/facebook_random.edgelist -> facebook_random facebook_random. A=0.001, K=10-1.5-100M, Cvr=10, SzFrc=0.001 G(4039, 96234)"
set key bottom right
set logscale xy 10
set format x "10^{%L}"
set mxtics 10
set format y "10^{%L}"
set mytics 10
set grid
set xlabel "k (number of nodes in the cluster)"
set ylabel "{/Symbol \F} (conductance)"
set tics scale 2
set terminal png font arial 10 size 1000,800
set output 'ncp.facebook_random.png'
plot 	"ncp.facebook_random.tab" using 1:2 title "ORIGINAL MIN (4039, 96234)" with lines lw 1
